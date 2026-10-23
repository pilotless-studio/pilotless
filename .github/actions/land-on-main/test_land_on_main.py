# stdlib unittest for landing a generated commit on protected main.
# No network: git uses a local bare repo, GitHub is a fake.
# Run: python3 -m unittest discover -s .github/actions/land-on-main -p 'test_*.py' -v
import os, pathlib, subprocess, tempfile, unittest

import land_on_main as land


ROOT = pathlib.Path(__file__).resolve().parents[3]


def check(name="tests", status="completed", conclusion="success", app=15368, cid=1):
    row = {"id": cid, "name": name, "status": status, "conclusion": conclusion, "head_sha": "sha"}
    if app is not None:
        row["app"] = {"id": app}
    return row


class ClassifyTests(unittest.TestCase):
    def test_success_is_the_latest_tests_check_from_actions(self):
        runs = [
            check(conclusion="failure", cid=1),
            check(conclusion="success", cid=2),
            check(name="ci / tests", conclusion="success", cid=3),
            check(conclusion="success", app=999, cid=4),
        ]
        self.assertEqual(land.classify_checks(runs), "success")

    def test_newer_in_progress_check_is_pending(self):
        runs = [check(conclusion="success", cid=1), check(status="in_progress", conclusion=None, cid=2)]
        self.assertEqual(land.classify_checks(runs), "pending")

    def test_missing_wrong_name_or_app_does_not_count(self):
        self.assertEqual(land.classify_checks([]), "missing")
        self.assertEqual(land.classify_checks([check(name="ci / tests")]), "missing")
        self.assertEqual(land.classify_checks([check(app=1)]), "missing")
        self.assertEqual(land.classify_checks([{"id": 1, "name": "tests", "app_id": 15368,
                                                "status": "completed", "conclusion": "success"}]), "success")

    def test_skipped_or_failed_is_not_a_pass(self):
        self.assertEqual(land.classify_checks([check(conclusion="skipped")]), "failure")
        self.assertEqual(land.classify_checks([check(conclusion="neutral")]), "failure")
        self.assertEqual(land.classify_checks([check(conclusion="failure")]), "failure")

    def test_push_rejection_kinds(self):
        gh006 = "remote: error: GH006: Protected branch update failed for refs/heads/main.\n" \
                "remote: - Required status check \"tests\" is expected.\n" \
                "! [remote rejected] main -> main (protected branch hook declined)\n"
        nonff = "! [rejected] sha -> main (non-fast-forward)\n" \
                "error: failed to push some refs\n"
        self.assertEqual(land.classify_push_failure(gh006), "checks")
        self.assertEqual(land.classify_push_failure(nonff), "moved")
        self.assertEqual(land.classify_push_failure("fatal: authentication failed"), "other")


class FakeClock:
    def __init__(self):
        self.t = 0.0
        self.slept = []

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.t += seconds


class FakeGitHub:
    def __init__(self, states):
        self.states = list(states)
        self.dispatches = []

    def dispatch(self, workflow, ref):
        self.dispatches.append((workflow, ref))

    def check_runs(self, sha):
        state = self.states.pop(0) if self.states else self.states_last
        if not hasattr(self, "states_last"):
            self.states_last = state
        else:
            self.states_last = state
        if state == "success":
            return [check()]
        if state == "failure":
            return [check(conclusion="failure")]
        if state == "pending":
            return [check(status="queued", conclusion=None)]
        return []


class FakeRepo:
    def __init__(self, fetches, dirty=True):
        self.fetches = list(fetches)
        self.dirty = dirty
        self.starts = []
        self.commands = []
        self.commits = []
        self.pushes = []
        self.deleted = []
        self.reject_main = []
        self._n = 0

    def fetch_main(self):
        if not self.fetches:
            raise AssertionError("unexpected fetch")
        return self.fetches.pop(0)

    def prepare(self, branch, sha, paths):
        self.starts.append((branch, sha, tuple(paths)))

    def run(self, command):
        self.commands.append(command)

    def commit_paths(self, paths, message, name, email):
        if not self.dirty:
            return None
        self._n += 1
        sha = "c%d" % self._n
        self.commits.append((sha, message, name, email, tuple(paths)))
        return sha

    def push_ref(self, sha, ref):
        self.pushes.append((sha, ref))
        if ref == "main" and self.reject_main:
            kind = self.reject_main.pop(0)
            if kind:
                raise land.PushRejected(kind, "simulated " + kind)

    def delete_ref(self, ref):
        self.deleted.append(ref)


def cfg():
    return land.LandConfig(
        slug="roadmap", run_id="42", message="Sync ROADMAP.md", paths=["ROADMAP.md"],
        git_name="bot", git_email="bot@example.com", regenerate="curl -o ROADMAP.md",
        timeout=30, interval=10, push_lag=15)


class LandTests(unittest.TestCase):
    def test_noop_does_not_push_or_dispatch(self):
        repo, github = FakeRepo(["base"], dirty=False), FakeGitHub([])
        self.assertEqual(land.land(cfg(), repo, github, FakeClock()), "noop")
        self.assertEqual(repo.pushes, [])
        self.assertEqual(github.dispatches, [])
        self.assertEqual(repo.commands, ["curl -o ROADMAP.md"])

    def test_happy_path_dispatches_ci_then_fast_forwards_main(self):
        repo, github = FakeRepo(["base", "base"]), FakeGitHub(["success"])
        self.assertEqual(land.land(cfg(), repo, github, FakeClock()), "landed")
        self.assertEqual(github.dispatches, [("ci.yml", "land/roadmap/42/1")])
        self.assertEqual(repo.pushes, [("c1", "land/roadmap/42/1"), ("c1", "main")])
        self.assertEqual(repo.deleted, ["land/roadmap/42/1"])

    def test_pending_check_waits_until_success(self):
        clock = FakeClock()
        repo, github = FakeRepo(["base", "base"]), FakeGitHub(["pending", "missing", "success"])
        self.assertEqual(land.land(cfg(), repo, github, clock), "landed")
        self.assertEqual(clock.slept, [10, 10])
        self.assertEqual(repo.pushes[-1], ("c1", "main"))

    def test_failed_tests_never_touch_main(self):
        repo, github = FakeRepo(["base"]), FakeGitHub(["failure"])
        with self.assertRaises(land.LandError):
            land.land(cfg(), repo, github, FakeClock())
        self.assertEqual([ref for _, ref in repo.pushes], ["land/roadmap/42/1"])

    def test_timeout_does_not_push_main(self):
        repo, github = FakeRepo(["base"]), FakeGitHub(["missing"])
        with self.assertRaises(land.LandError):
            land.land(cfg(), repo, github, FakeClock())
        self.assertNotIn("main", [ref for _, ref in repo.pushes])

    def test_main_moved_regenerates_once_then_lands(self):
        repo = FakeRepo(["base", "newer", "newer", "newer"])
        github = FakeGitHub(["success", "success"])
        self.assertEqual(land.land(cfg(), repo, github, FakeClock()), "landed")
        self.assertEqual(len(repo.commands), 2)
        self.assertEqual(repo.pushes, [
            ("c1", "land/roadmap/42/1"),
            ("c2", "land/roadmap/42/2"),
            ("c2", "main"),
        ])
        self.assertIn("land/roadmap/42/1", repo.deleted)

    def test_second_race_fails_without_a_third_try(self):
        repo = FakeRepo(["base", "mid", "mid", "tip"])
        github = FakeGitHub(["success", "success"])
        with self.assertRaises(land.LandError):
            land.land(cfg(), repo, github, FakeClock())
        self.assertNotIn(("c2", "main"), repo.pushes)
        self.assertEqual(len(repo.commands), 2)

    def test_non_fast_forward_push_retries_once(self):
        repo = FakeRepo(["base", "base", "base", "base"])
        repo.reject_main = ["moved", None]
        github = FakeGitHub(["success", "success"])
        self.assertEqual(land.land(cfg(), repo, github, FakeClock()), "landed")
        self.assertEqual([ref for _, ref in repo.pushes], [
            "land/roadmap/42/1", "main", "land/roadmap/42/2", "main"])

    def test_checks_rejection_retries_the_push_once_then_stops(self):
        repo = FakeRepo(["base", "base", "base"])
        repo.reject_main = ["checks", "checks"]
        github = FakeGitHub(["success"])
        clock = FakeClock()
        with self.assertRaises(land.LandError):
            land.land(cfg(), repo, github, clock)
        self.assertEqual(len(repo.commands), 1)
        self.assertEqual(clock.slept, [15])
        self.assertEqual([ref for _, ref in repo.pushes], [
            "land/roadmap/42/1", "main", "main"])

    def test_checks_rejection_then_push_succeeds_without_regenerating(self):
        repo = FakeRepo(["base", "base", "base"])
        repo.reject_main = ["checks", None]
        github = FakeGitHub(["success", "success"])
        self.assertEqual(land.land(cfg(), repo, github, FakeClock()), "landed")
        self.assertEqual(len(repo.commands), 1)


class GitRepoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bare = os.path.join(self.tmp.name, "bare.git")
        self.work = os.path.join(self.tmp.name, "work")
        subprocess.check_call(["git", "init", "--bare", "-b", "main", self.bare])
        subprocess.check_call(["git", "clone", self.bare, self.work])
        self.git("config", "user.name", "seed")
        self.git("config", "user.email", "seed@example.com")
        pathlib.Path(self.work, "ROADMAP.md").write_text("v1\n")
        self.git("add", "ROADMAP.md")
        self.git("commit", "-m", "seed")
        self.git("push", "origin", "HEAD:refs/heads/main")
        self.repo = land.GitRepo(self.work)

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args, cwd=None):
        subprocess.check_call(["git", *args], cwd=cwd or self.work)

    def test_commit_fast_forward_and_reject_when_main_moves(self):
        base = self.repo.fetch_main()
        self.repo.prepare("land/roadmap/7/1", base, ["ROADMAP.md"])
        self.repo.run("printf 'v2\\n' > ROADMAP.md")
        sha = self.repo.commit_paths(["ROADMAP.md"], "sync", "github-actions[bot]", "bot@example.com")
        self.assertIsNotNone(sha)
        self.repo.push_ref(sha, "land/roadmap/7/1")
        self.repo.push_ref(sha, "main")
        self.assertEqual(self.repo.fetch_main(), sha)
        self.repo.delete_ref("land/roadmap/7/1")
        refs = subprocess.check_output(["git", "ls-remote", "--heads", self.bare], text=True)
        self.assertNotIn("land/roadmap/7/1", refs)
        again = self.repo.commit_paths(["ROADMAP.md"], "sync", "github-actions[bot]", "bot@example.com")
        self.assertIsNone(again)

        other = os.path.join(self.tmp.name, "other")
        subprocess.check_call(["git", "clone", self.bare, other])
        subprocess.check_call(["git", "config", "user.name", "other"], cwd=other)
        subprocess.check_call(["git", "config", "user.email", "other@example.com"], cwd=other)
        pathlib.Path(other, "ROADMAP.md").write_text("other\n")
        subprocess.check_call(["git", "add", "ROADMAP.md"], cwd=other)
        subprocess.check_call(["git", "commit", "-m", "other"], cwd=other)
        subprocess.check_call(["git", "push", "origin", "HEAD:refs/heads/main"], cwd=other)
        with self.assertRaises(land.PushRejected) as caught:
            self.repo.push_ref(sha, "main")
        self.assertEqual(caught.exception.kind, "moved")

    def test_prepare_drops_untracked_files_under_the_paths(self):
        base = self.repo.fetch_main()
        docs = pathlib.Path(self.work, "docs")
        docs.mkdir()
        (docs / "extra.md").write_text("junk\n")
        self.repo.prepare("land/weekly/7/1", base, ["docs"])
        self.assertFalse((docs / "extra.md").exists())


class WorkflowContractTests(unittest.TestCase):
    def test_ci_job_stays_tests_and_can_be_dispatched(self):
        text = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("\n  tests:\n", text)
        self.assertNotIn("pull_request_target:", text)

    def test_generators_use_the_shared_action_and_minimal_permissions(self):
        for name in ("roadmap.yml", "weekly-directory.yml"):
            text = (ROOT / ".github/workflows" / name).read_text()
            self.assertIn("./.github/actions/land-on-main", text)
            self.assertIn("contents: write", text)
            self.assertIn("actions: write", text)
            self.assertIn("checks: read", text)
            self.assertNotIn("git push", text)

    def test_action_parses_as_a_composite(self):
        text = (ROOT / ".github/actions/land-on-main/action.yml").read_text()
        self.assertIn("using: composite", text)
        self.assertIn("land_on_main.py", text)


if __name__ == "__main__":
    unittest.main()
