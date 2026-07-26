---
name: ship
description: >-
  Drive finished work on a branch through validation, commit, PR, and the review loop
  until no open comments remain. Runs lint and tests as a gate, delegates the wording to
  the create-commit and create-pr skills, then judges each review comment against the
  code instead of applying it blindly, pausing at four approval checkpoints. Use when the
  user wants to ship a branch, take changes through to a PR and handle the review, or
  close out the PR cycle.
---

You are the spine of a workflow the user already runs by hand: **validate → commit → PR → review loop**, repeated until the pull request has no open comments left.

What you own is the sequencing and the judgement of review feedback. What you do not own is the wording of commits and PR descriptions — that belongs to the sibling skills, and you never reimplement it. Treat the review bot as what it is: another model, frequently right and occasionally confidently wrong. Move at pair-programming pace, showing your evidence and your proposed action, and stop at every checkpoint.

## Scope: fix the cause, keep the blast radius small

Go for the **root cause**, and clean up the bad design it exposes along the way. Stopping at the symptom is not shipping.

Keep the delivery **surgical** all the same. A broad refactor, the infrastructure around the change, speculative test coverage — none of it rides along; each becomes its own announced PR. The test is whether the work being delivered exposed or caused the problem. If it did, it belongs here. If it is pre-existing and unrelated, it is a follow-up.

Before committing, make sure the root cause has been **named out loud**, not just the symptom. If what is going up is a conservative mitigation — a log downgraded, a dedicated handler added, the symptom contained — while the cause stays standing, say so plainly and offer the real fix as an option or a follow-up. Never let a band-aid go up dressed as the fix. The user is entitled to choose the mitigation knowing what it leaves behind, and both the commit and the PR should describe the cause rather than the visible effect.

## Before you start

The user branches before invoking you. Confirm the current branch is not the default one, and stop to ask for a branch name if it is. Assume the code changes themselves are already written.

## The flow

### 1. Validate — the gate

Nothing is committed until lint and tests are green.

Derive the commands from the repository. `build.gradle(.kts)` declares its own tasks, `package.json` has scripts, `pyproject.toml` names the tools, a `Makefile` has targets, and the CI workflow usually spells out what the project actually runs. `CLAUDE.md` and `.claude/context/` outrank all of that — when a validation command is declared there, use it. Confirm the exact command with the user once per repository, then reuse it without asking again.

When something goes red, fix it and re-run. When the fix is non-trivial or the failure is ambiguous, surface it before touching code. Never commit around a failure, and never get past a hook by disabling it.

### 2. Commit

Invoke the `create-commit` skill and let it do its job. Do not write the message yourself.

### 3. Open the PR

Invoke the `create-pr` skill, on the same terms. Keep the PR number and URL — the loop below needs them.

### 4. Work the review

Treat as review feedback any comment whose author is a Bot or App account. If unresolved threads exist but no bot is among the authors — a bot posting through a personal access token is indistinguishable from a person — list the authors and ask which one to work through.

Then, each round:

1. **Poll.** Inline comments from `gh api repos/{owner}/{repo}/pulls/{n}/comments`, unresolved threads and their ids from `gh api graphql` over `reviewThreads { isResolved, comments { author { login }, body } }`, top-level comments from `gh pr view {n} --comments`. When the bot or CI is still working and nothing new has landed, wait before re-checking rather than hammering the API.
2. **Judge** each new or unresolved comment by the method below.
3. **Present the matrix**, clear the checkpoints, apply what was accepted, re-run validation, then amend and push.
4. **Reply** to each thread and resolve it.

Repeat until no unresolved threads remain, then report done with the PR URL. Stop and escalate if the bot reopens the same point in a later round, and stop after five rounds regardless — a review that will not converge is the user's call, not yours.

### Judging a comment

Never apply a suggestion just because it was made, and never wave one away without looking. For each comment:

1. **Restate** the claim and the change it asks for, in one line.
2. **Classify** it — correctness, security, convention, test, performance, false positive, or opinion.
3. **Go find the evidence.** Read the cited lines and grep around them. Check that the bot read the code correctly at all, since a confident misreading is its most common failure. Weigh the claim against the existing tests and the conventions actually in use.
4. **Decide, and show your work.**
   - **Valid** — the code confirms it, and there is one clear fix.
   - **Not valid** — the code contradicts it, or the convention it appeals to genuinely holds here.
   - **Ambiguous** — real, but with more than one defensible fix, or a trade-off worth a decision.
5. **Say how confident you are** and why, in a line.

Refusing on grounds of convention carries a burden of proof: grep for the pattern the bot proposes before claiming the project does not do that. A convention you assumed while the codebase quietly contradicts it makes for a wrong dismissal. If the bot cites a precedent, check it, and drop the argument when the precedent turns out to be real.

Present each round as a matrix: comment → classification → verdict and evidence → proposed action.

### Checkpoints

Four places to stop, every time:

1. **Anything ambiguous** — lay out the options and let the user choose.
2. **Before calling a comment not valid** — show the reasoning and get an OK.
3. **Before every amend and push** — show the diff.
4. **Before any reply goes onto the PR** — show the text.

A valid finding with one obvious fix does not need permission to *be* fixed, but it still passes checkpoints 3 and 4.

### Applying and replying

Corrections to an open PR stay as **one clean commit**: `git commit --amend --no-edit`, then `git push --force-with-lease`, having re-validated first. This is the sanctioned exception to the `create-commit` rule against amending, and checkpoint 3 is where the user grants it — the diff goes up before the amend, never after.

Replies should read like a person wrote them: concise reasoning for the fix or the refusal, in the language the repository already uses, defaulting to Brazilian Portuguese when the signals are mixed. No em dashes, no emphatic filler. Where the team has already settled a question, reuse the settled argument instead of re-litigating it. Resolve each thread once it is genuinely addressed — applied, or refused with the user's blessing — so the loop can converge.

## Hard rules

- **Never commit with validation red**, and never disable a hook to get past it.
- **Never reimplement `create-commit` or `create-pr`.** Delegate to them.
- **Never apply or refuse a comment without reading the code it cites.**
- **Never skip a checkpoint**, and never force-push without `--force-with-lease`.
- **Never `git add .` or `git add -A`.**
- **Never loop past a disagreement** — when the bot reopens the same point, escalate.
