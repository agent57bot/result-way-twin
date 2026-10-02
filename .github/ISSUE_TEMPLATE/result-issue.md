<!--
GitHub Issues Twin profile — opening Result issue.
Copy this body into a new GitHub issue. Keep exactly one bve-interchange fence.
Replace the example ids, timestamps, prose, and provenance before posting.
The fence is the record. Prose around it is optional context for readers.
-->

Publish a portable status document.

This issue is one Result. Append Way records as comments. A new version is a new comment.

```bve-interchange
{
  "format": "bve-interchange",
  "format_version": "1.0",
  "document_id": "example/twin-store/1/body",
  "created_at": "2026-10-02T13:00:00Z",
  "records": [
    {
      "kind": "result",
      "id": "example/twin-store/1/result",
      "schema_version": 1,
      "version": 1,
      "created_at": "2026-10-02T13:00:00Z",
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
        "description": "Create a status document that can be verified independently of the implementation that produced it.",
        "classification": "TASK",
        "target": {
          "type": "git-repository",
          "locator": "example/status-repository"
        },
        "acceptance_criteria": [
          {
            "id": "status-exists",
            "description": "STATUS.md exists and contains the current completion state."
          }
        ]
      }
    }
  ]
}
```
