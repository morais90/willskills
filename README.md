# willskills

Reusable [Claude Code](https://code.claude.com) plugins and GitHub Actions, shared across projects.

## `willskills` plugin

A high-signal pull-request reviewer. It fans out to five specialized reviewer subagents (code quality, security, test coverage, performance, documentation accuracy), then posts only **verified, noteworthy** findings as inline comments — no summaries, no nitpicks, no re-raising of points already settled.

Command: `/willskills:review-pr <pr-context-file>`

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
      - uses: morais90/willskills/pr-review@main
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

The action checks out the PR, gathers the diff **and the existing review threads** into a single context file, then runs the `willskills` plugin against it — so the reviewer subagents never call `gh` themselves (no duplication) and the lead reviewer can see what was already raised and skip it.

### Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `claude_code_oauth_token` | yes | — | Claude Code OAuth token |
| `model` | no | `claude-opus-4-8` | Model id used for the review |

### Requirements

- This repository must be **public** (or, if private, grant the calling repos access under Settings → Actions and provide a token the action can use to clone the marketplace).

## Repository layout

```
pr-review/action.yml                # the reusable composite action
.claude-plugin/marketplace.json     # marketplace manifest
plugins/willskills/
  ├── .claude-plugin/plugin.json
  ├── commands/review-pr.md         # the /willskills:review-pr command
  └── agents/                       # the five reviewer subagents
```
