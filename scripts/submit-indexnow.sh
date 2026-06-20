#!/bin/bash
# Submit all sitemap URLs to IndexNow (Bing, Yandex, Seznam, Naver).
# Run this after pushing new or updated content to GitHub Pages.
#
# Usage: ./scripts/submit-indexnow.sh
#
# Expected response: 200 OK or 202 Accepted = success.
# 400 = bad request. 403 = key not found at keyLocation. 422 = URLs/key mismatch.

set -euo pipefail

KEY="81a0509f4d5a4ffbaa72eddaf8c867bb"
HOST="justus.health"
KEY_LOCATION="https://${HOST}/${KEY}.txt"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SITEMAP="${REPO_ROOT}/sitemap.xml"

if [[ ! -f "$SITEMAP" ]]; then
  echo "Error: sitemap.xml not found at $SITEMAP" >&2
  exit 1
fi

# Extract <loc> URLs from sitemap.
URLS=$(grep -oE '<loc>[^<]+</loc>' "$SITEMAP" | sed -E 's|</?loc>||g')

if [[ -z "$URLS" ]]; then
  echo "Error: no URLs found in sitemap.xml" >&2
  exit 1
fi

URL_COUNT=$(echo "$URLS" | wc -l | tr -d ' ')
echo "Submitting $URL_COUNT URLs to IndexNow..."

# Build JSON urlList by quoting each line and joining with commas.
URL_JSON=$(echo "$URLS" | awk 'NF {printf "%s\"%s\"", (NR>1?",":""), $0}')

PAYLOAD=$(cat <<EOF
{
  "host": "${HOST}",
  "key": "${KEY}",
  "keyLocation": "${KEY_LOCATION}",
  "urlList": [${URL_JSON}]
}
EOF
)

# POST to IndexNow. The api.indexnow.org endpoint fans out to all participating
# search engines (Bing, Yandex, Seznam, Naver, etc.) so we only need one call.
HTTP_CODE=$(curl -sS -o /tmp/indexnow-response.txt -w "%{http_code}" \
  -X POST "https://api.indexnow.org/IndexNow" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "$PAYLOAD")

echo "HTTP $HTTP_CODE"
if [[ -s /tmp/indexnow-response.txt ]]; then
  echo "Response:"
  cat /tmp/indexnow-response.txt
  echo
fi

case "$HTTP_CODE" in
  200|202)
    echo "Success."
    ;;
  *)
    echo "Submission failed. See response above." >&2
    exit 1
    ;;
esac
