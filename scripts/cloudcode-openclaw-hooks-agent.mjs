#!/usr/bin/env node
/**
 * cloudcode-openclaw-hooks-agent.mjs
 *
 * Minimal “zero polling” notifier:
 * - Reads the first N bytes of a result file (default 4096)
 * - POSTs to OpenClaw Gateway /hooks/agent (expects 202)
 * - Idempotent via a per-runId marker file (safe for stop + session_end double hook)
 *
 * Requires:
 *   OPENCLAW_HOOKS_TOKEN   (Bearer token for /hooks/*)
 * Optional:
 *   OPENCLAW_GATEWAY_URL   (default http://127.0.0.1:18789)
 *   OPENCLAW_DELIVER_TO    (default 1476965845560463482 i.e. #delivery-hall channel id)
 *   OPENCLAW_MARKER_DIR    (default .openclaw_hooks)
 */

import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";

function usage(exitCode = 2) {
  const msg = `Usage:
  node scripts/cloudcode-openclaw-hooks-agent.mjs --runId <id> --result <path> [--bytes 4096]

Env:
  OPENCLAW_HOOKS_TOKEN=... (required)
  OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789
  OPENCLAW_DELIVER_TO=1476965845560463482
  OPENCLAW_MARKER_DIR=.openclaw_hooks
`;
  process.stderr.write(msg);
  process.exit(exitCode);
}

function getArg(flag) {
  const i = process.argv.indexOf(flag);
  if (i === -1) return null;
  return process.argv[i + 1] ?? null;
}

async function readPrefix(filePath, maxBytes) {
  try {
    const fh = await fsp.open(filePath, "r");
    try {
      const buf = Buffer.alloc(maxBytes);
      const { bytesRead } = await fh.read(buf, 0, maxBytes, 0);
      return buf.subarray(0, bytesRead).toString("utf8");
    } finally {
      await fh.close();
    }
  } catch (e) {
    return `(result read failed: ${e?.name ?? "Error"}: ${e?.message ?? String(e)})`;
  }
}

async function ensureDir(p) {
  await fsp.mkdir(p, { recursive: true });
}

async function fileExists(p) {
  try {
    await fsp.access(p, fs.constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function acquireLock(lockPath) {
  try {
    const fh = await fsp.open(lockPath, "wx");
    await fh.close();
    return true;
  } catch (e) {
    if (e && typeof e === "object" && "code" in e && e.code === "EEXIST") return false;
    throw e;
  }
}

async function main() {
  const runId = getArg("--runId") ?? getArg("-r");
  const resultPath = getArg("--result") ?? getArg("-f");
  const bytesStr = getArg("--bytes") ?? "4096";
  const maxBytes = Math.max(1, Math.min(64 * 1024, Number.parseInt(bytesStr, 10) || 4096));

  if (!runId || !resultPath) usage();

  const gatewayUrl = process.env.OPENCLAW_GATEWAY_URL || "http://127.0.0.1:18789";
  const token = process.env.OPENCLAW_HOOKS_TOKEN;
  if (!token) {
    process.stderr.write("Missing env OPENCLAW_HOOKS_TOKEN\n");
    process.exit(2);
  }

  // Default to known #delivery-hall in this guild; override when running elsewhere.
  const deliverTo = process.env.OPENCLAW_DELIVER_TO || "1476965845560463482";

  const markerDir = process.env.OPENCLAW_MARKER_DIR || ".openclaw_hooks";
  await ensureDir(markerDir);

  const sentPath = path.join(markerDir, `${runId}.sent`);
  const lockPath = path.join(markerDir, `${runId}.lock`);

  if (await fileExists(sentPath)) {
    process.stdout.write("already-sent\n");
    return;
  }

  const gotLock = await acquireLock(lockPath);
  if (!gotLock) {
    // Another hook handler is sending (or already sent).
    process.stdout.write("locked\n");
    return;
  }

  try {
    const snippet = await readPrefix(resultPath, maxBytes);
    const absResultPath = path.resolve(resultPath);

    const relayText =
      `Cloud Code finished. runId=${runId}\n` +
      `result=${absResultPath} (first ${maxBytes} bytes)\n\n` +
      `--- RESULT (TRUNCATED) ---\n` +
      snippet;

    const payload = {
      name: "CloudCode",
      // Force the hook agent run to act as a dumb relay (no summarization), so the
      // delivered message contains the actual result snippet.
      message:
        "Webhook relay: reply with EXACTLY the following text (verbatim), no extra commentary.\n\n" +
        relayText,
      wakeMode: "now",
      deliver: true,
      channel: "discord",
      to: deliverTo,
    };

    const url = new URL("/hooks/agent", gatewayUrl);
    const res = await fetch(url, {
      method: "POST",
      headers: {
        authorization: `Bearer ${token}`,
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const bodyText = await res.text().catch(() => "");

    if (res.status !== 202) {
      throw new Error(`unexpected status ${res.status}: ${bodyText.slice(0, 400)}`);
    }

    await fsp.writeFile(sentPath, `${new Date().toISOString()}\n`, "utf8");
    process.stdout.write("sent\n");
  } finally {
    // If we failed before writing .sent, remove the lock so the other hook can retry.
    if (!(await fileExists(sentPath))) {
      await fsp.rm(lockPath, { force: true });
    } else {
      await fsp.rm(lockPath, { force: true });
    }
  }
}

main().catch((e) => {
  process.stderr.write(`error: ${e?.message ?? String(e)}\n`);
  process.exit(1);
});
