#!/usr/bin/env sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "Usage: ./install.sh <codex|claude|antigravity|agents|all> [install|status|uninstall] [link|copy]"
  exit 2
fi

target="$1"
action="${2:-install}"
method="${3:-link}"
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

python3 "$script_dir/scripts/install_athanor.py" \
  --target "$target" \
  --action "$action" \
  --method "$method" \
  --repo-root "$script_dir"
