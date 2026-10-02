# Labels

Labels are a browsing aid. They do not approve a plan or select a version. Names come from `implementations/github-issues-twin/templates/labels.json`, copied from the GitHub Issues Twin profile.

| Label | Use |
| --- | --- |
| `rw:kind:result` | Every Result issue |
| `rw:status:intake` | Opening result only |
| `rw:status:planning` | Latest authoritative record is a draft plan |
| `rw:status:review` | Latest authoritative record is a review |
| `rw:status:execution` | Latest authoritative record is an execution |
| `rw:status:verification` | Latest authoritative record is a verification |
| `rw:status:evaluation` | Latest authoritative record is an evaluation |
| `rw:status:closed` | Work on this Result issue is finished |
| `rw:latest:plan` | Optional mirror: newest authoritative record is a plan |
| `rw:latest:review` | Optional mirror: newest authoritative record is a review |
| `rw:latest:execution` | Optional mirror: newest authoritative record is an execution |
| `rw:latest:verification` | Optional mirror: newest authoritative record is a verification |
| `rw:latest:evaluation` | Optional mirror: newest authoritative record is an evaluation |
| `rw:latest:improvement` | Optional mirror: newest authoritative record is an improvement |
| `rw:latest:event` | Optional mirror: newest authoritative record is an event |
| `rw:latest:result` | Optional mirror: newest authoritative record is a new result version |

Keep a single `rw:status:*` label on the issue.

## Create them

GitHub Actions on this repository do not create labels. From a checkout, with `gh` authenticated for this repository:

```bash
scripts/create_labels.sh
```

The script reads `implementations/github-issues-twin/templates/labels.json` and creates or updates each label on `agent57bot/result-way-twin`. Pass another `owner/name` as the first argument to target a different repository.
