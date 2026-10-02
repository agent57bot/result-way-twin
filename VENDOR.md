# Vendored files

Source: [agent57bot/result-way-protocol](https://github.com/agent57bot/result-way-protocol) `main` at commit `e90afd0c0ef11fd6a614fc5be4d67f0a323d1568` (`Add GitHub Issues Twin implementation profile`).

Profile path: `implementations/github-issues-twin/`.

These blobs match that commit. Do not edit them in place. Take a newer copy from a later protocol commit and update this file.

| Path in this repository | Protocol path | Blob SHA |
| --- | --- | --- |
| `schemas/bve-interchange.schema.json` | `schemas/bve-interchange.schema.json` | `74bdbe0f9a4fbb22be000277f1f5ea123e30408d` |
| `implementations/github-issues-twin/scripts/validate_github_issues_twin.py` | same | `2e068f00be0d358861d02b65ff958e6c2e62f63a` |
| `implementations/github-issues-twin/scripts/requirements.txt` | same | `ad4d4990b4ae775afd04c409d74d74533ee2d552` |
| `implementations/github-issues-twin/templates/labels.json` | same | `bd101ee428656d462c52ee20114950b18a1ab31e` |
| `implementations/github-issues-twin/templates/result-issue.md` | same | `8e8e3d5e07405a5cfec5d6a352b921bc2733a9e9` |
| `implementations/github-issues-twin/templates/comments/*.md` | same | see protocol tree `22323616b43d4ff3ea19ffa33ea24dd4341a6292` (templates directory) |
| `implementations/github-issues-twin/examples/minimal-log/` | same | fixture only |
| `examples/04-portable-interchange/artifacts/bve-interchange.json` | `examples/04-portable-interchange/artifacts/bve-interchange.json` | `1608722fd91bff615b142eabe2b41b7f8a5780aa` |
| `.github/workflows/validate-twin.yml` | `implementations/github-issues-twin/workflows/validate-twin.yml` | `79e84e8884f7e03575af1a2493eb85dc9c1f5114` |
| `.github/ISSUE_TEMPLATE/result-issue.md` | `implementations/github-issues-twin/templates/result-issue.md` | `8e8e3d5e07405a5cfec5d6a352b921bc2733a9e9` |

The checker script resolves its profile directory and repository root from its own path (`parents[1]` and `parents[3]`). It stays at `implementations/github-issues-twin/scripts/` so `--self-test` finds the templates, the minimal log, `schemas/bve-interchange.schema.json`, and the portable interchange example. The workflow template already uses those paths, so it is copied without path edits.

`examples/04-portable-interchange/artifacts/bve-interchange.json` is the protocol's portable interchange example. `--self-test` schema-checks that file. It is not a GitHub Issue in this store.
