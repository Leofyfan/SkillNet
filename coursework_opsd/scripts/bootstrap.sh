#!/usr/bin/env bash
set -euo pipefail
assignment_dir="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$assignment_dir/.runtime/tmp" "$assignment_dir/.runtime/cache/pip" "$assignment_dir/logs"
export TMPDIR="$assignment_dir/.runtime/tmp"
export PIP_CACHE_DIR="$assignment_dir/.runtime/cache/pip"
export PYTHONDONTWRITEBYTECODE=1
cd "$assignment_dir"
python3 -m venv "$assignment_dir/.venv"
if [[ -f "$assignment_dir/requirements.lock.txt" ]]; then
  "$assignment_dir/.venv/bin/python" -m pip install -r "$assignment_dir/requirements.lock.txt"
  "$assignment_dir/.venv/bin/python" -m pip install --no-deps -e ./vendor/skillnet-ai
else
  "$assignment_dir/.venv/bin/python" -m pip install -e ./vendor/skillnet-ai 'pymupdf==1.26.7'
fi
"$assignment_dir/.venv/bin/python" -m pip check
