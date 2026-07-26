---
name: create-pr
description: Open a pull request with a short, plainly written description that explains why the change was made, following the project's PR template. Use when the user asks to create, open, or draft a PR for the current branch, or asks you to write a PR description.
allowed-tools: Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(git branch:*), Bash(git remote:*), Bash(git rev-parse:*), Bash(git symbolic-ref:*), Bash(git push:*), Bash(gh pr view:*), Bash(gh pr create:*), Glob, Read, Write
---

You open a pull request for the current branch. The diff already shows **what** changed — your description exists to explain **why**, in a few plain sentences, so a reviewer arrives already knowing what this is for. Everything else is noise.

Optional arguments, in order: a PR title, then a base branch. Use them when given; derive both when not.

## Procedure

1. **Check the state.** Confirm you are not on the default branch, that the working tree is clean, and that the branch exists on the remote — `git push -u origin HEAD` if it does not. Then run `gh pr view --json url` to check whether a PR is already open; if one is, stop and report its URL instead of creating a second.
2. **Resolve the base branch.** Use the argument if given. Otherwise read `git symbolic-ref refs/remotes/origin/HEAD`, falling back to `main`, then `master`. Refer to it as `<base>` below — never hardcode `main` in the commands you actually run.
3. **Find the template.** Glob these paths in order and use the first hit:
   - `.github/PULL_REQUEST_TEMPLATE.md` and `.github/pull_request_template.md`
   - `.github/PULL_REQUEST_TEMPLATE/*.md` — if several exist, pick the one matching the change, or ask
   - `docs/pull_request_template.md`
   - `PULL_REQUEST_TEMPLATE.md` at the root

   Read it in full. A template that exists is not optional.
4. **Understand the change.** Run `git log --oneline <base>..HEAD`, `git diff --stat <base>...HEAD`, and `git diff <base>...HEAD`. Read enough of the surrounding code to know the *purpose* of the change, not just its mechanics — the problem it solves and anything that would genuinely surprise a reviewer. You read the detail so you can leave it out with confidence, not so you can repeat it.
5. **Write the title and body.** Follow the writing rules below. With a template: fill each section in place, preserve every heading and section, add and remove nothing, and tick the checkboxes the diff actually justifies. Without one, two or three short paragraphs are enough — what prompted the change, then what it does about it, plus a line on anything the reviewer should look at closely or any related issue.
6. **Create it.** Write the body to a temp file and pass `--body-file` — never inline a multi-line body into the shell, where backticks and quotes will mangle it. Show the user the final title and body, then run `gh pr create --base <base> --title "<title>" --body-file <path>` and report the URL.

## Writing rules

**Prose, not inventory.** Write in flowing paragraphs, the way you would explain the change to a colleague over coffee — not the way you would document it. Reach for a bullet list only when the content is genuinely a list.

Bad — a changelog the reviewer can already read in the diff:

```
- Created UserService.ts
- Added fetchUsers()
- Modified index.ts to use the new service
- Removed old code from utils.ts
```

Good — the reasoning behind it, which the diff cannot show:

```
Looking up users was spread across the codebase, so every caller handled
errors a little differently and there was no obvious place to add caching.

This pulls all of it into one service, so from now on there is a single place
to deal with that.

Migrating the remaining callers is a follow-up, to keep this one small — the
old methods still work in the meantime.
```

**Explain the why.** What prompted the change, what it was like before, and what the reviewer would have no way of guessing. That is the whole job.

**Stay light on the technical detail.** Aim for something a teammate who knows the product but not this corner of the code can follow. Skip the class names, the patterns, the library internals and the step-by-step of how it works — the reviewer is about to read all of that anyway. Mention an implementation decision only when it was a real choice between options and the reason is not obvious from the code; one sentence, then move on.

**Keep it short.** Two or three short paragraphs is a complete PR description. If it is growing, you are explaining the code instead of the reason for it.

**Leave out what the diff already says.** No file lists, no line counts, no added-import notes, no names of new functions unless you are explaining why they exist.

**Match the repository's language.** Read the PR template and recent merged PR titles (`git log --oneline <base>` on merge commits) and write the title, body, and every template section in that language. Default to Brazilian Portuguese when the signals are ambiguous. Keep this skill's structure either way — the examples above illustrate shape, not language.

## Hard rules

- **Never create a PR from the default branch**, from a dirty tree, or when one is already open for the branch.
- **Never restructure a template** — no new sections, no renamed headings, no dropped ones, however empty they look.
- **Never write a vague title or body.** "fixes", "updates", and "improvements" describe nothing; if you cannot say why the change was made, read more of the diff. Short is the goal, vague is not — a brief description still names the actual problem.
- **Never force-push, amend, commit, or touch any branch other than the current one.**
- Keep the PR to a single purpose. If the branch clearly does two unrelated things, say so rather than papering over it in the description.
