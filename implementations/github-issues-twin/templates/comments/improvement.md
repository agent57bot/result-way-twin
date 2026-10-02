<!--
GitHub Issues Twin profile — improvement comment.
-->

Evidence-backed improvement for a later run.

```bve-interchange
{
  "format": "bve-interchange",
  "format_version": "1.0",
  "document_id": "example/twin-store/1/comment/7",
  "created_at": "2026-10-02T13:35:00Z",
  "records": [
    {
      "kind": "improvement",
      "id": "example/twin-store/1/improvement",
      "schema_version": 1,
      "version": 1,
      "created_at": "2026-10-02T13:35:00Z",
      "provenance": {
        "producer": "evaluator-agent",
        "agent": "evaluator-agent",
        "extensions": {
          "github.com/agent57bot/result-way-protocol:github-issues-actor": {
            "team": "evaluation",
            "role": "evaluator"
          }
        }
      },
      "spec": {
        "target": "library",
        "status": "proposed",
        "title": "Reuse exact file-scope verification",
        "proposal": "Add a reusable check that compares the changed-file list with the Result constraints.",
        "rationale": "The Red Team treated file-scope checking as generally useful.",
        "based_on_refs": [
          {
            "id": "example/twin-store/1/review",
            "kind": "review",
            "version": 1
          }
        ]
      }
    }
  ]
}
```
