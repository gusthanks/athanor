#!/usr/bin/env sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "Usage: ./install.sh <codex|claude|antigravity|agents|all> [install|status|refresh|doctor|uninstall] [link|copy] [options]"
  exit 2
fi

target="$1"
shift
action="${1:-install}"
if [ "$#" -gt 0 ]; then shift; fi
method="link"
if [ "$#" -gt 0 ]; then
  case "$1" in
    link|copy)
      method="$1"
      shift
      ;;
  esac
fi
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

python3 "$script_dir/scripts/install_athanor.py" \
  --target "$target" \
  --action "$action" \
  --method "$method" \
  --repo-root "$script_dir" \
  "$@"
