<!--
GitHub Issues Twin profile — a new Result version.
Same logical id, higher version, posted as a new comment. Leave the issue body unchanged.
-->

Result version 2. The issue body still holds version 1.

```bve-interchange
{
  "format": "bve-interchange",
  "format_version": "1.0",
  "document_id": "example/twin-store/1/comment/9",
  "created_at": "2026-10-02T13:45:00Z",
  "records": [
    {
      "kind": "result",
      "id": "example/twin-store/1/result",
      "schema_version": 1,
      "version": 2,
      "created_at": "2026-10-02T13:45:00Z",
      "provenance": {
        "producer": "intake-agent",
        "agent": "intake-agent",
        "extensions": {
          "github.com/agent57bot/result-way-protocol:github-issues-actor": {
            "team": "intake",
            "role": "result-author"
          }
        }
      },
      "spec": {
        "title": "Publish a portable status document",
        "description": "Create a status document that can be verified independently of the implementation that produced it. The completion state names the protocol commit it describes.",
        "classification": "TASK",
        "target": {
          "type": "git-repository",
          "locator": "example/status-repository"
        },
        "acceptance_criteria": [
          {
            "id": "status-exists",
            "description": "STATUS.md exists and contains the current completion state, including the protocol commit."
          }
        ]
      }
    }
  ]
}
```
