# OpenClaw x Cloud Code: Webhooks ("Zero Polling") Playbook

Goal: stop burning model tokens by polling long-running Cloud Code jobs. Switch to an event-driven pattern:
- OpenClaw dispatches work once.
- Cloud Code runs to completion.
- Cloud Code calls back into OpenClaw via `POST /hooks/*`.

## One-line takeaway
Use callback hooks (`stop` as primary + `session end` as fallback) to notify OpenClaw exactly once per run (O(1) cost), instead of periodic polling (O(runtime)).

## When to use
- Cloud Code runs that take minutes+ (compile/test/scrape), and you currently poll status.
- Any workflow where "keep checking" drives token burn or rate-limit risk.

## Architecture
- Gateway exposes webhook ingress at `http(s)://<gateway-host>:<port>/hooks/*`.
- Cloud Code has two callbacks:
  - `stop`: success path
  - `session end`: safety net if `stop` doesn't fire (crash/kill)

## Step 1: Enable OpenClaw webhook ingress
Config reference: OpenClaw docs `docs/automation/webhook.md`.

```json5
{
  hooks: {
    enabled: true,
    token: "${OPENCLAW_HOOKS_TOKEN}",
    path: "/hooks",

    // Recommended hardening (optional)
    defaultSessionKey: "hook:ingress",
    allowRequestSessionKey: false,
    allowedSessionKeyPrefixes: ["hook:"],

    // Optional: restrict explicit agent routing
    allowedAgentIds: ["hooks", "main"]
  }
}
```

Notes:
- Every request must include the token. Prefer `Authorization: Bearer <token>`.
- Query-string tokens are rejected (`?token=...`).

## Step 2: Verify `/hooks/wake` works
From any machine that can reach the gateway:

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"text":"[wake test] Cloud Code hook","mode":"now"}'
```

Expected:
- HTTP 200
- Gateway emits the system event and (with `mode=now`) triggers an immediate heartbeat.

## Step 3: Choose callback endpoint
Pick one based on how much you want OpenClaw to do.

### Option A (lightweight): `POST /hooks/wake`
Use when you only need a "job finished" event.

Payload:
```json
{ "text": "Cloud Code job finished: <run-id>", "mode": "now" }
```

### Option B (actionable): `POST /hooks/agent`
Use when you want OpenClaw to process results and optionally deliver a message to a channel.

Example:

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "CloudCode",
    "message": "Summarize this result and propose next steps:\n\n<PASTE RESULT HERE>",
    "agentId": "hooks",
    "wakeMode": "now",
    "deliver": true,
    "channel": "discord",
    "to": "channel:1476965845560463482"
  }'
```

Expected:
- HTTP 202 (async)
- An isolated agent run starts.

## Step 4: Cloud Code hook script (reference)
In Cloud Code, create a hook script that:
1) loads the run output (`result.json` or `summary.md`)
2) calls OpenClaw webhook once

Example (POSIX shell; keep payload small):

```bash
#!/usr/bin/env bash
set -euo pipefail

GATEWAY_URL="${OPENCLAW_GATEWAY_URL:-http://127.0.0.1:18789}"
HOOKS_TOKEN="${OPENCLAW_HOOKS_TOKEN:?missing OPENCLAW_HOOKS_TOKEN}"
RESULT_PATH="${1:-result.txt}"
RUN_ID="${2:-unknown-run}"
MARKER_DIR="${3:-.}"
MARKER_FILE="$MARKER_DIR/.openclaw_hook_sent_$RUN_ID"

# Idempotency: don't send twice.
if [ -f "$MARKER_FILE" ]; then
  exit 0
fi

touch "$MARKER_FILE"

if [ -f "$RESULT_PATH" ]; then
  RESULT_CONTENT="$(head -c 8000 "$RESULT_PATH")"
else
  RESULT_CONTENT="(missing result file: $RESULT_PATH)"
fi

# Write JSON to a file to avoid shell escaping edge cases.
PAYLOAD_FILE="$(mktemp)"
cat > "$PAYLOAD_FILE" <<EOF
{
  "name": "CloudCode",
  "message": "Cloud Code job finished. runId=$RUN_ID\n\nResult (truncated):\n\n$RESULT_CONTENT",
  "agentId": "hooks",
  "wakeMode": "now",
  "deliver": true,
  "channel": "discord",
  "to": "channel:1476965845560463482"
}
EOF

curl -sS -X POST "$GATEWAY_URL/hooks/agent" \
  -H "Authorization: Bearer $HOOKS_TOKEN" \
  -H 'Content-Type: application/json' \
  -d @"$PAYLOAD_FILE"
```

Implementation notes:
- Prefer sending links (artifact URL) over embedding huge logs.
- If your gateway is not reachable from Cloud Code, expose it via reverse proxy/Tailscale.

## Step 5: Register two Cloud Code callbacks
- Primary: `stop` hook -> calls the script.
- Fallback: `session end` hook -> calls the script with a different marker/run id.

## Verification
- Run a 1-2 minute Cloud Code job.
- Confirm:
  - only one completion notification arrives
  - no periodic "polling" requests happen during the run

## Failure modes
- 401: token missing/wrong; check `Authorization` header.
- 429: too many auth failures; wait per `Retry-After`, fix token, retry.
- No callback: gateway not reachable (bind/port/firewall); rerun the curl verify from the same network.
- Duplicate notifications: both `stop` and `session end` fired; use marker-file idempotency.

## Rollback
- Disable ingress: set `hooks.enabled=false` (or remove `hooks` block) and restart gateway.
- Remove Cloud Code hook registrations; revert to polling if needed.

## References
- OpenClaw webhook ingress docs: `docs/automation/webhook.md`
- Hook packs (agent-side hooks): `docs/cli/hooks.md`
- Webhook helpers (e.g. Gmail Pub/Sub): `docs/cli/webhooks.md`
