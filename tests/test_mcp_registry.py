"""Guards the MCP Registry listing decided in 0056.

The server document is remote-only, the publish workflow is manual,
and it authenticates with GitHub OIDC rather than a new secret.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

SCHEMA = "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
SERVER_NAME = "io.github.pilotless-studio/roadmap"
WEBSITE = "https://pilotless.nl/?src=mcp-registry"
REMOTE = "https://pilotless.nl/mcp"
AMD64_SHA = "5dc2fd415369c73551259f31cd33e2aacc9e0d1021e7f08fef1492d93b781628"


def read(rel):
    return (ROOT / rel).read_text()


class McpRegistryTests(unittest.TestCase):
    def test_server_json_is_remote_only(self):
        doc = json.loads(read("server.json"))
        self.assertEqual(doc["$schema"], SCHEMA)
        self.assertEqual(doc["name"], SERVER_NAME)
        self.assertRegex(doc["name"], r"^[a-zA-Z0-9.-]+/[a-zA-Z0-9._-]+$")
        self.assertEqual(doc["name"].count("/"), 1)
        description = doc["description"]
        self.assertGreaterEqual(len(description), 1)
        self.assertLessEqual(len(description), 100)
        self.assertIn("roadmap:read", description)
        self.assertNotIn("package", description.lower())
        self.assertEqual(doc["version"], "0.1.0")
        self.assertNotRegex(doc["version"], r"[\^~*]|latest|>=|\|\|")
        self.assertEqual(doc["websiteUrl"], WEBSITE)
        self.assertNotIn("packages", doc)
        self.assertNotIn("repository", doc)
        self.assertEqual(
            doc["remotes"],
            [{"type": "streamable-http", "url": REMOTE}],
        )
        self.assertRegex("mcp-registry", r"^[a-z0-9.-]{1,32}$")

    def test_publish_workflow_is_dispatch_only_oidc(self):
        text = read(".github/workflows/publish-mcp.yml")
        self.assertIn("name: Publish to MCP Registry", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("push:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("id-token: write", text)
        self.assertIn("contents: read", text)
        self.assertNotIn("contents: write", text)
        self.assertIn("mcp-publisher login github-oidc", text)
        self.assertNotIn("--token", text)
        self.assertNotIn("secrets.", text)
        self.assertIn("MCP_PUBLISHER_VERSION: v1.8.4", text)
        self.assertIn(AMD64_SHA, text)
        self.assertIn("sha256sum -c -", text)
        self.assertIn("./mcp-publisher validate server.json", text)
        self.assertIn("./mcp-publisher publish server.json", text)
        self.assertIn('refs/heads/main', text)
        self.assertNotIn("releases/latest", text)

    def test_decision_0056_appended(self):
        text = read("DECISIONS.md")
        old = "## 0055-publish-directory-delete-roadmap-mirror"
        new = "## 0056-list-roadmap-mcp-in-registry"
        self.assertLess(text.index(old), text.index(new))
        block = text.split(new, 1)[1]
        start = block.index("```json") + len("```json")
        body = block[start:block.index("```", start)]
        decision = json.loads(body)
        for key in (
            "context",
            "date",
            "decision",
            "reasoning",
            "expectations",
            "falsifiable_by",
            "evidence",
            "cost",
            "status",
            "title",
        ):
            self.assertIn(key, decision)
        self.assertEqual(decision["date"], "2026-10-25")
        self.assertEqual(decision["status"], "decided")
        joined = json.dumps(decision)
        self.assertIn(SERVER_NAME, joined)
        self.assertIn("src=mcp-registry", joined)
        self.assertIn("2026-11-01", joined)
        self.assertNotIn("PAT", decision["cost"])

    def test_state_notes_pending_publish(self):
        text = read("STATE.md")
        self.assertIn("pending publish", text)
        self.assertIn(SERVER_NAME, text)
        self.assertIn("0056", text)
        next_step = text.split("## Next step", 1)[1].split("## ", 1)[0]
        product = text.split("## Product", 1)[1].split("## ", 1)[0]
        self.assertIn("pending publish", next_step)
        self.assertIn("pending publish", product)
        self.assertRegex(next_step, re.compile(r"pending publish", re.I))


if __name__ == "__main__":
    unittest.main()
