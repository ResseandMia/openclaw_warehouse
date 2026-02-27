# learning-loop

Purpose: make every non-trivial run produce reusable, versioned learnings (memory + skill updates).

Use when:
- You are about to run a multi-step task (coding, ops, automation) that may error or require iterations.
- You want the agent to get better over time, not just finish once.

## Operating rule (the loop)

For every run, follow this exact sequence:

1) Plan
- Write a short Plan with:
  - goal
  - scope/non-goals
  - concrete steps
  - expected outputs
  - safety notes (destructive commands, secrets)
  - verification commands

2) Execute
- Run the steps.
- Prefer small, reversible changes.
- Capture important command output (errors, version info).

3) Debug (if needed)
- When an error occurs:
  - capture the exact error text
  - collect context: OS, runtime, versions, env vars *names only*, config paths
  - propose the smallest fix

4) Verify
- Run the verification commands from Plan.
- If verification fails, return to (3).

5) Distill
- Produce two artifacts:
  - Memory note: what happened + the final "known-good" recipe.
  - Skill delta: what should be added/changed so next time succeeds faster.

6) Sync
- Apply the skill delta to the relevant skill docs/scripts.
- Commit + push (when a remote exists).

## What to write down (template)

Create one "run note" per task in `memory/YYYY-MM-DD.md`:

- Context: what you were trying to do
- Commands/steps that worked
- Pitfalls: symptoms -> root cause
- Fix: exact change, with file paths
- Verify: commands + expected output

## Helper commands

Append a run note:

```bash
./scripts/oclog.sh "<short title>" <<'EOF'
<context + what happened>
EOF
```

Create a new skill delta entry (manual edit):
- edit the target skill's `SKILL.md`
- add/update a "Known issues" or "Troubleshooting" section

## Post-run checklist (mandatory)

After every non-trivial skill execution, ask yourself:

- [ ] Did I encounter any new pitfall or error? → Write it down (memory + skill)
- [ ] Did I find a better way to do something? → Update the skill's "known-good steps"
- [ ] Did the skill doc change? → Commit + push to GitHub
- [ ] Did I update memory? → Both daily file AND relevant skill doc

Rule: skill updates and memory updates are ALWAYS dual-written.
Rule: every skill update MUST be pushed to GitHub.

## Safety rules

- Never paste secrets into chat or into workspace files.
- When logging env, log only variable names, not values.
- Prefer `kill <pid>` over `pkill` unless you are sure.
