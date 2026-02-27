#!/usr/bin/env bash
set -euo pipefail

TITLE="${1:-run}"

# ISO date in local timezone.
DAY="$(date +%F)"
TS="$(date +%F\ %T)"

mkdir -p "memory"
FILE="memory/${DAY}.md"

{
  echo ""
  echo "## ${TS} - ${TITLE}"
  echo ""
  cat
  echo ""
} >>"${FILE}"

echo "wrote ${FILE}" >&2
