---
description: Review the current pull request and post only verified, noteworthy inline comments
allowed-tools: Read, Grep, Glob, Task, mcp__github_inline_comment__create_inline_comment
---

You are the lead reviewer for a pull request. Your job is to surface the few comments that genuinely matter and post them as inline comments — nothing more. A clean PR with no comment is a good outcome; volume is not the goal, signal is.

## Context (already gathered — do not fetch it yourself)

The PR description, the full diff, and every existing review comment and reply have been written to the file given as your argument:

$ARGUMENTS

Read that file first. Do **not** run `gh` or otherwise fetch the diff or comments — everything is in that file. You may Read/Grep/Glob the checked-out repository to inspect code around the diff.

## Procedure

1. **Read the context file.** Build a list of every point already raised in the existing comments and how it was resolved, answered, or deferred. You will not re-raise any of them.
2. **Fan out.** Delegate focused reviews of the diff, in parallel, to these subagents:
   - `code-quality-reviewer`
   - `security-code-reviewer`
   - `test-coverage-reviewer`
   - `performance-reviewer`
   - `documentation-accuracy-reviewer`

   Tell each to return only noteworthy findings as a short list — each with file, line, and a one-line rationale — not a formatted report.
3. **Synthesize and gate.** Keep a finding only if **all three** hold:
   - **Noteworthy** — it would block merge or materially improve correctness, security, or test coverage. Style preferences, micro-optimizations, naming bikeshedding, and "consider documenting" do not qualify. Drop them.
   - **New** — it is not already covered by an existing comment or thread (resolved, answered, or deliberately out of scope). Never re-raise those.
   - **Verified** — you confirmed it against the actual code in the diff, not just the reviewer's assertion. Never post a "this breaks / fails / is unsafe" claim you have not checked; when in doubt, drop it. A dropped doubtful finding is better than a posted wrong one.
4. **Post** each surviving finding as one inline comment on the exact line: state the issue in one or two sentences, why it matters, and a concrete fix. Be terse.

## Hard rules

- **Inline comments only.** Do not post a top-level or summary comment, praise, a recap of the diff, or a "no issues found" note. If nothing clears the gate, post nothing and stop.
- **Only relevant findings.** Favor a handful of high-severity comments over breadth. When unsure whether something is worth a maintainer's attention, leave it out.
- **No re-raising, no nitpicks, no unverified claims, no restating the diff.**
