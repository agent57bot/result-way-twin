# result-way-twin

This repository is a **Twin store** for Result/Way pilots. A Result is a GitHub Issue. Way lifecycle records are comments on that Issue. The log is append-only.

This repository is not the protocol. The normative interchange schema and the GitHub Issues Twin profile live in [result-way-protocol](https://github.com/agent57bot/result-way-protocol), path [`implementations/github-issues-twin/`](https://github.com/agent57bot/result-way-protocol/tree/e90afd0c0ef11fd6a614fc5be4d67f0a323d1568/implementations/github-issues-twin).

Files copied from that profile are recorded in [VENDOR.md](VENDOR.md). Protocol commit: `e90afd0c0ef11fd6a614fc5be4d67f0a323d1568`.

How to open a Result, append plan and review comments, and run the checker: [docs/PILOT.md](docs/PILOT.md).

## What is in this store

| Path | Role |
| --- | --- |
| `schemas/bve-interchange.schema.json` | Vendored interchange schema, byte-for-byte from the protocol commit above |
| `implementations/github-issues-twin/scripts/` | Profile checker and its Python requirements |
| `implementations/github-issues-twin/templates/` | Result issue body, comment templates, and label names |
| `.github/ISSUE_TEMPLATE/result-issue.md` | The profile Result issue template, installed for new Issues |
| `.github/workflows/validate-twin.yml` | Validates an Issue log when the Issue or a comment is opened or edited |
| `.github/workflows/checker-self-test.yml` | Runs the checker `--self-test` on pull requests and pushes to `main` |
| [docs/LABELS.md](docs/LABELS.md) | Label names from `templates/labels.json`, and how to create them |

The minimal log under `implementations/github-issues-twin/examples/minimal-log/` is a fixture for the checker. It is not a live Issue.
