#!/bin/bash
set -euo pipefail

BASE_URL="${1:-https://mimosa-atelier.onrender.com}"
ENDPOINT="${BASE_URL%/}/payments/webhook/stripe/"

echo "Checking webhook endpoint reachability: $ENDPOINT"

HTTP_CODE=$(curl -s -o /tmp/stripe_webhook_check_body.txt -w "%{http_code}" \
  -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{"ping":true}')

echo "HTTP code: $HTTP_CODE"
echo "Response body:"
cat /tmp/stripe_webhook_check_body.txt
echo ""

if [[ "$HTTP_CODE" == "400" || "$HTTP_CODE" == "500" || "$HTTP_CODE" == "200" ]]; then
  echo "Endpoint is reachable. Next step: validate real signed events via Stripe CLI."
  echo "Run: stripe listen --events checkout.session.completed --forward-to $ENDPOINT"
  exit 0
fi

if [[ "$HTTP_CODE" == "301" || "$HTTP_CODE" == "302" || "$HTTP_CODE" == "307" || "$HTTP_CODE" == "308" ]]; then
  echo "Endpoint responded with redirect ($HTTP_CODE), which is expected when HTTPS redirect is enabled."
  echo "Use HTTPS base URL for production check."
  exit 0
fi

echo "Unexpected HTTP status. Check BASE_URL and deployment health."
exit 1
