"""Guards the publish path decided in 0055.

The status directory must deploy to GitHub Pages and must not push to main.
The roadmap mirror and the land-on-main action stay deleted.
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(rel):
    return (ROOT / rel).read_text()


class PublishWorkflowTests(unittest.TestCase):
    def test_roadmap_mirror_is_gone(self):
        self.assertFalse((ROOT / "ROADMAP.md").exists())
        self.assertFalse((ROOT / ".github/workflows/roadmap.yml").exists())
        self.assertFalse((ROOT / ".github/actions/land-on-main").exists())
        for rel in ("README.md", "STATE.md"):
            self.assertNotIn("ROADMAP.md", read(rel), rel)
        self.assertIn("https://pilotless.nl/roadmap.md", read("README.md"))
        self.assertIn("https://pilotless.nl/roadmap.md", read("STATE.md"))

    def test_ci_is_pull_request_only(self):
        text = read(".github/workflows/ci.yml")
        self.assertNotIn("workflow_dispatch", text)
        self.assertIn("pull_request:", text)
        # The required check context is this job id. There is no job-level name.
        self.assertIn("\n  tests:\n", text)

    def test_weekly_directory_deploys_pages_and_does_not_push(self):
        text = read(".github/workflows/weekly-directory.yml")
        self.assertIn("name: weekly status directory", text)
        self.assertIn("cron: '17 6 * * 4'", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("contents: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("land-on-main", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)
        self.assertIn("actions/deploy-pages@", text)
        self.assertIn("actions/upload-pages-artifact@", text)
        self.assertIn("actions/jekyll-build-pages@", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("python3 scripts/gen_status_directory.py", text)
        self.assertIn("python3 scripts/gen_unowned.py", text)
        self.assertIn("python3 scripts/gen_sitemap.py", text)
        self.assertIn("python3 scripts/ping_indexnow.py", text)
        self.assertIn("build_type", text)

    def test_decision_0055_appended_and_0054_untouched(self):
        text = read("DECISIONS.md")
        old = '## 0054-generated-commits-pass-tests-before-main'
        new = '## 0055-publish-directory-delete-roadmap-mirror'
        self.assertIn(old, text)
        self.assertLess(text.index(old), text.index(new))
        self.assertIn(
            '"title": "Generated commits reach main only after the tests check passes on that SHA"',
            text,
        )
        block = text.split(new, 1)[1]
        start = block.index("```json") + len("```json")
        body = block[start:block.index("```", start)]
        decision = json.loads(body)
        self.assertEqual(decision["status"], "decided")
        self.assertEqual(decision["date"], "2026-10-23")
        self.assertIn("0054", " ".join(decision["decision"]))
        self.assertIn("https://pilotless.nl/roadmap.md", " ".join(decision["decision"]))
        self.assertNotIn("contents: write", " ".join(decision["decision"]))


if __name__ == "__main__":
    unittest.main()
