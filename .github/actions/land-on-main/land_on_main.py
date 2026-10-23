#!/usr/bin/env python3
"""Land a generated commit on protected main without a PAT or a human.

GITHUB_TOKEN pushes do not start other workflows, and GITHUB_TOKEN pull
requests start CI only after a person approves the run. workflow_dispatch is
the exception that does start a run. This script commits on a short-lived
branch, dispatches ci.yml there, waits until the GitHub Actions check named
"tests" (app id 15368) is success on that exact SHA, then fast-forwards main.

Classic branch protection on this repo matches that check name and app on the
commit being pushed. There is no ruleset. A fast-forward pushes the same SHA
the check ran on, so the required check already exists and is up to date with
main (strict) as long as main has not moved. If it has, regenerate once and
try again. Never force-push.
"""
import json, os, pathlib, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

CHECK_NAME = "tests"
CHECK_APP_ID = 15368
API = "https://api.github.com"


class LandError(Exception):
    pass


class Retry(Exception):
    pass


class PushRejected(Exception):
    def __init__(self, kind, text):
        super().__init__(text)
        self.kind = kind
        self.text = text


class LandConfig:
    def __init__(self, slug, run_id, message, paths, git_name, git_email, regenerate,
                 timeout=1200, interval=10, push_lag=15, workflow="ci.yml"):
        self.slug = slug
        self.run_id = str(run_id)
        self.message = message
        self.paths = list(paths)
        self.git_name = git_name
        self.git_email = git_email
        self.regenerate = regenerate
        self.timeout = timeout
        self.interval = interval
        self.push_lag = push_lag
        self.workflow = workflow


def log(msg):
    print(msg, flush=True)


def app_id_of(run):
    app = run.get("app")
    value = app.get("id") if isinstance(app, dict) else None
    if value is None:
        value = run.get("app_id")
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def latest_required_check(runs, name=CHECK_NAME, app_id=CHECK_APP_ID):
    matching = [r for r in runs if r.get("name") == name and app_id_of(r) == app_id]
    if not matching:
        return None
    return max(matching, key=lambda r: r.get("id") or 0)


def classify_checks(runs, name=CHECK_NAME, app_id=CHECK_APP_ID):
    """success only for a completed success from the Actions app.

    Skipped and neutral count as success for branch protection, but they mean
    the tests job did not run. A generated commit has to actually pass.
    The required context is the job id "tests"; "ci / tests" would not satisfy it.
    """
    latest = latest_required_check(runs, name, app_id)
    if latest is None:
        return "missing"
    if latest.get("status") != "completed":
        return "pending"
    if latest.get("conclusion") == "success":
        return "success"
    return "failure"


def classify_push_failure(text):
    low = (text or "").lower()
    # A non-fast-forward means main moved. Prefer that over GH006 when both
    # appear, so the caller regenerates instead of treating it as a bad check.
    if "non-fast-forward" in low or "fetch first" in low or "behind its remote" in low:
        return "moved"
    if "gh006" in low or "protected branch" in low or "required status check" in low:
        return "checks"
    return "other"


def wait_for_tests(github, sha, clock, timeout, interval):
    deadline = clock.now() + timeout
    while True:
        runs = github.check_runs(sha)
        state = classify_checks(runs)
        latest = latest_required_check(runs)
        url = (latest or {}).get("html_url") or ""
        log("land: tests on %s is %s%s" % (sha, state, (" " + url) if url else ""))
        if state == "success":
            return
        if state == "failure":
            raise LandError("tests check failed on %s; main was not updated" % sha)
        remaining = deadline - clock.now()
        if remaining <= 0:
            raise LandError("timed out waiting for the tests check on %s" % sha)
        clock.sleep(min(interval, remaining))


def push_main(repo, github, clock, cfg, sha, base):
    """Fast-forward main. Raise Retry if main moved. Raise LandError otherwise.

    One extra push covers the short gap where the check is visible to the API
    but the protected-branch hook has not seen it yet. That second push is not
    the regenerate retry.
    """
    try:
        repo.push_ref(sha, "main")
        return
    except PushRejected as e:
        if e.kind == "moved":
            raise Retry()
        if e.kind != "checks":
            raise LandError("push to main failed: %s" % e.text[-500:])
    log("land: main rejected %s; waiting %ss for the tests check to be visible" % (sha, cfg.push_lag))
    clock.sleep(cfg.push_lag)
    if classify_checks(github.check_runs(sha)) != "success":
        raise LandError("tests check was not success on %s after main rejected the push" % sha)
    if repo.fetch_main() != base:
        raise Retry()
    try:
        repo.push_ref(sha, "main")
    except PushRejected as e:
        if e.kind == "moved":
            raise Retry()
        raise LandError(
            "main rejected %s after tests passed. If the hook still says the tests "
            "check is expected, workflow_dispatch checks are not accepted by this "
            "branch protection. Not force-pushing. Remote said: %s" % (sha, e.text[-500:]))


def land(cfg, repo, github, clock):
    previous = None
    for attempt in (1, 2):
        if previous:
            repo.delete_ref(previous)
        base = repo.fetch_main()
        branch = "land/%s/%s/%d" % (cfg.slug, cfg.run_id, attempt)
        previous = branch
        log("land: attempt %d base %s branch %s" % (attempt, base, branch))
        repo.prepare(branch, base, cfg.paths)
        repo.run(cfg.regenerate)
        sha = repo.commit_paths(cfg.paths, cfg.message, cfg.git_name, cfg.git_email)
        if sha is None:
            log("land: no changes")
            return "noop"
        log("land: committed %s" % sha)
        repo.push_ref(sha, branch)
        github.dispatch(cfg.workflow, branch)
        wait_for_tests(github, sha, clock, cfg.timeout, cfg.interval)
        current = repo.fetch_main()
        if current != base:
            if attempt == 2:
                raise LandError("main moved again after regenerating (%s -> %s); not pushing %s" % (base, current, sha))
            log("land: main moved during checks (%s -> %s), regenerating" % (base, current))
            continue
        try:
            push_main(repo, github, clock, cfg, sha, base)
        except Retry:
            if attempt == 2:
                raise LandError("main moved again while fast-forwarding %s" % sha)
            log("land: main moved during push, regenerating")
            continue
        repo.delete_ref(branch)
        log("land: fast-forwarded main to %s" % sha)
        return "landed"
    raise LandError("failed to land on main")


class RealClock:
    def now(self):
        return time.monotonic()

    def sleep(self, seconds):
        time.sleep(seconds)


class GitRepo:
    def __init__(self, cwd=None):
        self.cwd = cwd or os.getcwd()

    def git(self, *args, check=True):
        proc = subprocess.run(["git", *args], cwd=self.cwd, text=True, capture_output=True)
        if check and proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip()
            raise LandError("git %s failed: %s" % (" ".join(args), detail[-500:]))
        return proc

    def fetch_main(self):
        self.git("fetch", "--depth=1", "origin", "main")
        return self.git("rev-parse", "origin/main").stdout.strip()

    def prepare(self, branch, sha, paths):
        self.git("checkout", "--force", "-B", branch, sha)
        self.git("reset", "--hard", sha)
        if paths:
            # Drop untracked generator output from a previous attempt so a
            # retry cannot commit leftovers on top of the new main.
            self.git("clean", "-fd", "--", *paths)

    def run(self, command):
        proc = subprocess.run(command, cwd=self.cwd, shell=True)
        if proc.returncode != 0:
            raise LandError("regenerate command failed (%s)" % proc.returncode)

    def commit_paths(self, paths, message, name, email):
        self.git("config", "user.name", name)
        self.git("config", "user.email", email)
        self.git("add", "--", *paths)
        diff = self.git("diff", "--cached", "--quiet", check=False)
        if diff.returncode == 0:
            return None
        if diff.returncode != 1:
            raise LandError("git diff --cached failed: %s" % (diff.stderr or "")[-500:])
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def push_ref(self, sha, ref):
        spec = "%s:refs/heads/%s" % (sha, ref)
        proc = self.git("push", "origin", spec, check=False)
        if proc.returncode == 0:
            return
        text = (proc.stderr or "") + (proc.stdout or "")
        raise PushRejected(classify_push_failure(text), text)

    def delete_ref(self, ref):
        proc = self.git("push", "origin", "--delete", ref, check=False)
        if proc.returncode != 0:
            log("WARN could not delete %s: %s" % (ref, (proc.stderr or "").strip()[-300:]))


class ApiError(Exception):
    def __init__(self, status, body):
        super().__init__("GitHub API %s: %s" % (status, body))
        self.status = status
        self.body = body


class GitHubClient:
    def __init__(self, repo, token):
        self.repo = repo
        self.token = token

    def request(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(API + path, data=data, method=method, headers={
            "Authorization": "Bearer " + self.token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "pilotless-land",
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            raise ApiError(e.code, e.read().decode()[:800])

    def dispatch(self, workflow, ref):
        path = "/repos/%s/actions/workflows/%s/dispatches" % (self.repo, urllib.parse.quote(workflow))
        last = None
        for attempt in range(5):
            try:
                self.request("POST", path, {"ref": ref})
                log("land: dispatched %s on %s" % (workflow, ref))
                return
            except ApiError as e:
                last = e
                # The ref can take a moment to be visible after the push.
                if e.status == 404 and attempt < 4:
                    time.sleep(2)
                    continue
                raise LandError("could not dispatch %s on %s: %s" % (workflow, ref, e))
        raise LandError("could not dispatch %s on %s: %s" % (workflow, ref, last))

    def check_runs(self, sha):
        path = "/repos/%s/commits/%s/check-runs?check_name=%s&per_page=100" % (
            self.repo, urllib.parse.quote(sha), urllib.parse.quote(CHECK_NAME))
        data = self.request("GET", path)
        return (data or {}).get("check_runs") or []


def config_from_env(env=None):
    env = os.environ if env is None else env

    def need(key):
        val = (env.get(key) or "").strip()
        if not val:
            raise LandError("missing %s" % key)
        return val

    slug = need("LAND_SLUG")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,40}", slug):
        raise LandError("LAND_SLUG must be a short lowercase token")
    run_id = (env.get("GITHUB_RUN_ID") or "").strip()
    if not re.fullmatch(r"[0-9]+", run_id):
        raise LandError("GITHUB_RUN_ID is missing")
    paths = []
    for line in need("LAND_PATHS").splitlines():
        path = line.strip()
        if not path:
            continue
        if path.startswith("/") or ".." in pathlib.PurePosixPath(path).parts:
            raise LandError("unsafe path %s" % path)
        paths.append(path)
    if not paths:
        raise LandError("LAND_PATHS is empty")
    token = (env.get("GH_TOKEN") or env.get("GITHUB_TOKEN") or "").strip()
    repo = (env.get("GITHUB_REPOSITORY") or "").strip()
    if not token or not repo:
        raise LandError("GH_TOKEN and GITHUB_REPOSITORY are required")
    return LandConfig(
        slug=slug, run_id=run_id, message=need("LAND_COMMIT_MESSAGE"), paths=paths,
        git_name=need("LAND_GIT_NAME"), git_email=need("LAND_GIT_EMAIL"),
        regenerate=need("LAND_REGENERATE")), token, repo


def main():
    try:
        cfg, token, repo = config_from_env()
        result = land(cfg, GitRepo(), GitHubClient(repo, token), RealClock())
    except LandError as e:
        print("ERROR " + str(e), file=sys.stderr)
        return 1
    log("land: %s" % result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
