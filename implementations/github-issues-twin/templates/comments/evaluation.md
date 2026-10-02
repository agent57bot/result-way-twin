<!--
GitHub Issues Twin profile — evaluation comment.
Result outcome and Way outcome stay separate fields.
-->

Evaluation of the Result and the Way.

```bve-interchange
{
  "format": "bve-interchange",
  "format_version": "1.0",
  "document_id": "example/twin-store/1/comment/6",
  "created_at": "2026-10-02T13:30:00Z",
  "records": [
    {
      "kind": "evaluation",
      "id": "example/twin-store/1/evaluation",
      "schema_version": 1,
      "version": 1,
      "created_at": "2026-10-02T13:30:00Z",
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
        "result_ref": {
          "id": "example/twin-store/1/result",
          "kind": "result",
          "version": 1
        },
        "plan_ref": {
          "id": "example/twin-store/1/plan",
          "kind": "plan",
          "version": 2
        },
        "execution_ref": {
          "id": "example/twin-store/1/execution",
          "kind": "execution",
          "version": 1
        },
        "result": {
          "outcome": "achieved",
          "rationale": "The status document matches the acceptance criterion."
        },
        "way": {
          "outcome": "met",
          "rationale": "The approved file-scope check was carried out.",
          "comparisons": {}
        }
      }
    }
  ]
}
```
