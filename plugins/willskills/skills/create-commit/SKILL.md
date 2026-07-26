---
name: create-commit
description: Commit staged changes as a conventional commit with a short, plainly written body that explains why the change was made. Use when the user asks to commit, to write a commit message, or to stage and commit specific files.
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(git symbolic-ref:*), Bash(git commit:*), Read, Grep, Glob
---

You turn the change in front of you into one well-formed conventional commit. The diff already records **what** changed — the body exists to explain **why**, in a couple of plain sentences a teammate can read months from now. Everything else is noise.

Optional argument: paths to stage. Stage exactly those when given; commit what is already staged when not.

## Procedure

1. **Check the state.** Run `git status`. If the branch is the default one (`git symbolic-ref refs/remotes/origin/HEAD`, else `main`/`master`), say so and offer to branch before committing — do not commit to it silently.
2. **Stage.** With paths given, `git add <paths>` — but if unrelated changes were already staged, stop and point them out rather than sweeping them into this commit. With no paths, use what is staged; if nothing is staged, list the modified files and ask what to include instead of just stopping.
3. **Read the change.** `git diff --cached`, plus `git diff --cached --stat` for shape. Read the surrounding code where the diff alone does not tell you the purpose. You read the detail so you can leave it out with confidence, not so you can repeat it.
4. **Check it is one commit.** If the staged changes serve two unrelated purposes, say so and propose how to split them. One commit, one reason.
5. **Choose type and scope.** From the table below. Derive the scope from the module or directory that actually changed; omit it when the change is repo-wide.
6. **Write the message** following the writing rules, then commit with a quoted heredoc so nothing in the body gets interpolated:

   ```bash
   git commit -F - <<'EOF'
   <type>(<scope>): <subject>

   Body explaining why, wrapped at 72 characters.
   EOF
   ```
7. **Handle hooks.** If a pre-commit hook rewrites files, stage its corrections and retry once. If it fails for any other reason, report the error — never reach for `--no-verify`.
8. **Report** the resulting hash and subject.

## Writing rules

**Subject:** imperative mood — "Fix", not "Fixed" or "Fixes". Aim for 50 characters including the type and scope; never exceed 72. No trailing period.

**Body: prose, not inventory.** A short paragraph explaining what prompted the change, the way you would tell a colleague. Wrap at 72 characters. Skip the body entirely when the subject genuinely says everything — a one-line commit is fine, a padded one is not.

Bad — a list of the diff the reader already has:

```
- Fixed null check
- Updated imports
- Added error handling
```

Good — the reason it needed doing:

```
The old code crashed whenever the API came back empty, which was easy to
hit on a fresh account. It now checks the response first and returns an
empty list instead.
```

**Stay light on the technical detail.** Aim for something a teammate who knows the product but not this corner of the code can follow. Skip the class names, the patterns and the step-by-step of how it works — that is what the diff is for. Mention an implementation decision only when it was a real choice between options and the reason is not obvious from the code; one sentence, then move on.

**Match the repository's language.** Read recent `git log` subjects and write in that language. Default to Brazilian Portuguese when the signals are ambiguous. The examples above illustrate shape, not language.

## Commit types

| Type | Purpose |
|------|---------|
| `feat` | New features |
| `fix` | Bug fixes |
| `docs` | Documentation |
| `refactor` | Code restructuring |
| `test` | Test changes |
| `chore` | Maintenance |
| `perf` | Performance |
| `style` | Formatting |
| `build` | Build system |
| `ci` | CI configuration |

## Hard rules

- **Never `git add .`, `git add -A`, or `git commit -am`.** Stage deliberately, by path.
- **Never `--no-verify`**, and never amend, force-push, or rewrite an existing commit unless asked outright.
- **Never add AI attribution or co-authorship trailers.**
- **Never write a generic subject.** "updates", "fixes", "changes" describe nothing. Short is the goal, vague is not — a brief subject still names the actual change.
- Never commit to the default branch without flagging it first.
