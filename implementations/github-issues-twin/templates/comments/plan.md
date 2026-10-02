<!--
GitHub Issues Twin profile — plan comment (draft).
Post as a new issue comment. One fence only. A later approved version is a new comment.
-->

Draft Way for the portable status document.

```bve-interchange
{
  "format": "bve-interchange",
  "format_version": "1.0",
  "document_id": "example/twin-store/1/comment/1",
  "created_at": "2026-10-02T13:05:00Z",
  "records": [
    {
      "kind": "plan",
      "id": "example/twin-store/1/plan",
      "schema_version": 1,
      "version": 1,
      "created_at": "2026-10-02T13:05:00Z",
      "provenance": {
        "producer": "planner-agent",
        "agent": "planner-agent",
        "extensions": {
          "github.com/agent57bot/result-way-protocol:github-issues-actor": {
            "team": "planning",
            "role": "planner"
          }
        }
      },
      "spec": {
        "result_ref": {
          "id": "example/twin-store/1/result",
          "kind": "result",
          "version": 1,
          "uri": "https://github.com/example/twin-store/issues/1"
        },
        "status": "draft",
        "summary": "Write STATUS.md and verify that it is the only changed file.",
        "steps": [
          {
            "id": "write-status",
            "title": "Write the status document",
            "description": "Create STATUS.md with the requested completion state.",
            "depends_on": [],
            "risks": [
              {
                "id": "scope-drift",
                "description": "The implementation could change unrelated files."
              }
            ],
            "assumptions": [
              "The target repository is writable."
            ],
            "verification": "STATUS.md exists and is the only changed file."
          }
        ]
      }
    }
  ]
}
```
