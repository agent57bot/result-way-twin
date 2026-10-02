#!/usr/bin/env bash
# Create or update GitHub Issues Twin labels from the vendored labels.json.
# Requires the GitHub CLI (`gh`) and jq, authenticated for the target repository.
set -euo pipefail

repo="${1:-agent57bot/result-way-twin}"
root="$(cd "$(dirname "$0")/.." && pwd)"
labels="${root}/implementations/github-issues-twin/templates/labels.json"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh is not installed" >&2
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "jq is not installed" >&2
  exit 1
fi

count=0
while IFS= read -r row; do
  name="$(jq -r '.name' <<<"$row")"
  color="$(jq -r '.color' <<<"$row")"
  description="$(jq -r '.description' <<<"$row")"
  gh label create "$name" --repo "$repo" --color "$color" --description "$description" --force
  count=$((count + 1))
done < <(jq -c '.[]' "$labels")

echo "created or updated ${count} labels on ${repo}"
