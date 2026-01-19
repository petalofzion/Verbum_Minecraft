#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if ! command -v git >/dev/null 2>&1; then
  echo "git not found; cannot install hooks." >&2
  exit 1
fi

git -C "${repo_root}" config core.hooksPath tools/hooks
echo "Installed git hooks path: tools/hooks"
