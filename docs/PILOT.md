# Pilot: open a Result and check the log

This store follows the GitHub Issues Twin profile at [result-way-protocol `implementations/github-issues-twin/`](https://github.com/agent57bot/result-way-protocol/tree/e90afd0c0ef11fd6a614fc5be4d67f0a323d1568/implementations/github-issues-twin) (commit `e90afd0c0ef11fd6a614fc5be4d67f0a323d1568`). The profile document is the rule set. This page is the pilot procedure.

## Open a Result issue

1. Create an Issue from the **result-issue** template (`.github/ISSUE_TEMPLATE/result-issue.md`).
2. Set the title to `Result: {spec.title}`. The title is for people. Identity is the record `id` and `version`.
3. Keep exactly one `bve-interchange` fence in the body, holding the opening `result` record. The other allowed form is a single line `Result-Record: https://...` whose target is one interchange document containing only that result.
4. Replace the example ids, timestamps, prose, and provenance before posting. `provenance.producer` and `provenance.agent` are required. `team` and `role` go in the extension `github.com/agent57bot/result-way-protocol:github-issues-actor`.
5. Apply `rw:kind:result` and `rw:status:intake`. Label names are in [LABELS.md](LABELS.md). Labels do not grant authority.

A second Result is a new Issue. Do not put another result `id` on this Issue.

## Append plan and review comments

Leave the issue body and earlier comments unedited. A new version is a new comment with a complete interchange document.

Copy one fence from `implementations/github-issues-twin/templates/comments/`:

| Comment | Template |
| --- | --- |
| Draft plan | `plan.md` |
| Red Team review of that draft | `review-red-team.md` |
| Approved plan (next version of the same plan id) | `plan-approved.md` |

The minimal sequence is draft plan, then a passing review whose producer is not the plan producer, then an approved plan that cites that review. The same documents are in the fixture `implementations/github-issues-twin/examples/minimal-log/`. That fixture is not a live Issue.

Other comment kinds (execution, verification, evaluation, improvement, event, result revision) have templates in the same directory. Each comment carries exactly one `bve-interchange` fence. A `json` fence is prose. A comment with no fence is invalid.

## Run the checker

Self-test (schema example, templates, minimal log, and the profile's negative cases):

```bash
python3 -m pip install -r implementations/github-issues-twin/scripts/requirements.txt
python3 implementations/github-issues-twin/scripts/validate_github_issues_twin.py --self-test
```

Against a live Issue in this repository (requires `gh` auth that can read Issues):

```bash
python3 implementations/github-issues-twin/scripts/validate_github_issues_twin.py \
  --schema schemas/bve-interchange.schema.json \
  --repository agent57bot/result-way-twin \
  --issue NUMBER
```

`.github/workflows/validate-twin.yml` runs that live check when an Issue is opened or edited and when a comment is created or edited. It uses `GITHUB_TOKEN` with read access to contents and Issues. Enable GitHub Actions on this repository if that workflow does not run.

`.github/workflows/checker-self-test.yml` runs `--self-test` on pull requests and on pushes to `main`.
