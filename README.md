# willskills

Reusable [Claude Code](https://code.claude.com) plugins and GitHub Actions, shared across projects.

## `willskills` plugin

### Reviewing a PR

A high-signal pull-request reviewer. It fans out to the reviewer subagents the diff actually calls for — code quality, security, test coverage, performance, documentation accuracy — skipping the ones a given diff has nothing for, then posts only **verified, noteworthy** findings as inline comments — no summaries, no nitpicks, no re-raising of points already settled.

Command: `/willskills:review-pr <pr-context-file>`

### Committing

The `create-commit` skill writes one conventional commit for the change in front of it, with a short body that explains **why** rather than listing the diff. It stages deliberately by path, refuses `git add -A` and `--no-verify`, flags commits going straight to the default branch, and adds no attribution trailers. The one time it stops is at the end, to show the finished message and ask before committing.

Skill: `/willskills:create-commit [files/folders]`

### Opening a PR

The `create-pr` skill opens a pull request for the current branch with a short, plainly written description that explains **why** the change was made rather than restating the diff or walking through the implementation. It follows the project's PR template when one exists, resolves the base branch instead of assuming `main`, and writes in the language the repository already uses. Like the commit skill, it stops once at the end to show the title and body and ask before opening the PR.

Skill: `/willskills:create-pr [title] [base-branch]`

### Shipping a branch

The `ship` skill is the spine over the other three: it gates on lint and tests, delegates the commit and the PR to the skills above, then works the review loop — judging each bot comment against the actual code rather than applying it blindly, and pausing at six approval checkpoints. It reads the validation commands off the repository, with `CLAUDE.md` taking precedence.

Skill: `/willskills:ship`

## Use it in a project

Add a small workflow that calls the `pr-review` action:

```yaml
# .github/workflows/claude-code-review.yml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize, ready_for_review, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      id-token: write
    steps:
      - uses: morais90/willskills/pr-review@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

`@v1` is a floating tag that moves to the latest 1.x release, so you get fixes without opting into a breaking change. Pin an exact `@v1.2.3` if you would rather upgrade deliberately, or `@main` to track unreleased work.

The action checks out the PR, gathers the diff **and the existing review threads** into a single context file, then runs the `willskills` plugin against it — so the reviewer subagents never call `gh` themselves (no duplication) and the lead reviewer can see what was already raised and skip it.

### Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `claude_code_oauth_token` | yes | — | Claude Code OAuth token |
| `model` | no | `claude-opus-5` | Model id used for the review |
| `effort` | no | `high` | Reasoning effort level for the review (`low`, `medium`, `high`, `xhigh`, `max`) |

### Requirements

- This repository must be **public** (or, if private, grant the calling repos access under Settings → Actions and provide a token the action can use to clone the marketplace).

## Versioning

The plugin follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html), and the version lives in both `.claude-plugin/marketplace.json` and `plugins/willskills/.claude-plugin/plugin.json`. Releases are cut by hand from the **Release** workflow (Actions → Release → Run workflow); everything else is derived from the commit history, so conventional commit subjects are what drive the version.

| Commit | Bump |
|--------|------|
| `fix:` | patch |
| `feat:` | minor |
| `feat!:` or a `BREAKING CHANGE:` footer | major |

Running the workflow computes the next version with [git-cliff](https://git-cliff.org), regenerates `CHANGELOG.md`, bumps both manifests, tags `vX.Y.Z`, moves the floating `vX` tag, and publishes a GitHub release with the notes for that version. Tick **dry run** to see the version and notes it would produce without tagging anything.

Between releases, a push to `main` refreshes the *Unreleased* section of `CHANGELOG.md` on its own.

## Repository layout

```
pr-review/action.yml                # the reusable composite action
cliff.toml                          # changelog + version-bump rules
.github/workflows/                  # changelog on push, release on dispatch
.github/scripts/validate_plugin.py  # release gate: manifests, skills, agents
.claude-plugin/marketplace.json     # marketplace manifest
plugins/willskills/
  ├── .claude-plugin/plugin.json
  ├── commands/review-pr.md         # the /willskills:review-pr command
  ├── skills/create-commit/SKILL.md # the create-commit skill
  ├── skills/create-pr/SKILL.md     # the create-pr skill
  ├── skills/ship/SKILL.md          # the ship skill, orchestrating the three above
  └── agents/                       # the five reviewer subagents
```
