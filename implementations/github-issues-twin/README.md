# Vendored GitHub Issues Twin files

Copied from [result-way-protocol `implementations/github-issues-twin/`](https://github.com/agent57bot/result-way-protocol/tree/e90afd0c0ef11fd6a614fc5be4d67f0a323d1568/implementations/github-issues-twin) at commit `e90afd0c0ef11fd6a614fc5be4d67f0a323d1568`.

This directory is the checker, templates, and fixture the Twin store runs. It is not a second copy of the protocol. The store overview is the [repository README](../../README.md). The pilot steps are [docs/PILOT.md](../../docs/PILOT.md).

## Checker

From the repository root:

```bash
python3 -m pip install -r implementations/github-issues-twin/scripts/requirements.txt
python3 implementations/github-issues-twin/scripts/validate_github_issues_twin.py --self-test
```
