<!--
GitHub Issues Twin profile — event comment.
event.spec.actor matches provenance.producer. Sequence increases along the comment log.
-->

Twin event for the opening Result.

```bve-interchange
{
  "format": "bve-interchange",
  "format_version": "1.0",
  "document_id": "example/twin-store/1/comment/8",
  "created_at": "2026-10-02T13:40:00Z",
  "records": [
    {
      "kind": "event",
      "id": "example/twin-store/1/event/1",
      "schema_version": 1,
      "created_at": "2026-10-02T13:40:00Z",
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
        "sequence": 1,
        "event_type": "RESULT_OPENED",
        "actor": "intake-agent",
        "subject_refs": [
          {
            "id": "example/twin-store/1/result",
            "kind": "result",
            "version": 1
          }
        ],
        "payload": {
          "summary": "Opened the Result issue."
        },
        "previous_event_hash": null
      }
    }
  ]
}
```
