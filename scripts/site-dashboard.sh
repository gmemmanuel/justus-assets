#!/bin/bash
# Generate and open the Justus site-traffic dashboard.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="$(python3 scripts/dashboard/generate.py "$@")"
open "$OUT"
