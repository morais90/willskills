# willskills

[Claude Code](https://code.claude.com) tools for the git workflow, in two pieces:

- A plugin with skills that write commits and pull requests that explain why a change was made, and one that takes a branch all the way to a reviewed PR.
- A GitHub Action that reviews every pull request and comments only on problems it has verified.

You can use either one on its own.

## Install the plugin

Inside Claude Code, add this repository as a marketplace and install the plugin:

```
/plugin marketplace add morais90/willskills
/plugin install willskills@willskills
```

Run `/reload-plugins` (or restart Claude Code) and the skills show up under the `willskills:` prefix. To get a newer release later, run `/plugin marketplace update willskills`.

To set it up for everyone working in a repository, commit this to the repository's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "willskills": {
      "source": { "source": "github", "repo": "morais90/willskills" }
    }
  },
  "enabledPlugins": {
    "willskills@willskills": true
  }
}
```

Claude Code asks each person to trust the marketplace the first time they open the project.

## Skills

### `/willskills:create-commit [files/folders]`

Writes one conventional commit for the current change, with a short body that explains why the change was made. It stages files by path, refuses `git add -A` and `--no-verify`, warns before committing straight to the default branch, and adds no attribution trailers. When the message is ready, it shows it and asks before committing.

### `/willskills:create-pr [title] [base-branch]`

Opens a pull request for the current branch with a short, plain description of why the change was made, leaving the implementation to the diff. It follows the project's PR template when there is one, works out the base branch instead of assuming `main`, and writes in the language the repository already uses. It shows the title and body and asks before opening the PR.

### `/willskills:ship`

Takes a branch from local changes to a reviewed PR. It runs lint and tests first, uses the two skills above for the commit and the PR, then works through the review comments, checking each bot comment against the code before acting on it. It stops for your approval at six points along the way. It finds the lint and test commands in the repository, and `CLAUDE.md` wins when the two disagree.

## Automated PR review

Add this workflow to a repository to have every pull request reviewed:

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

Then add a `CLAUDE_CODE_OAUTH_TOKEN` secret to the repository. You can generate one by running `claude setup-token`.

The reviewer runs only the specialist subagents the diff calls for (code quality, security, test coverage, performance, documentation accuracy), so a docs-only PR doesn't go through a security review. It posts inline comments for findings it has checked against the code, leaves out nitpicks and summaries, and reads the existing review threads so it doesn't raise a point that was already discussed. A PR with nothing worth flagging gets no comments.

`@v1` follows the latest 1.x release, so you get fixes without breaking changes. Pin an exact version such as `@v1.2.3` if you'd rather upgrade on your own schedule.

### Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `claude_code_oauth_token` | yes | — | Claude Code OAuth token |
| `model` | no | `claude-opus-5` | Model used for the review |
| `effort` | no | `high` | Reasoning effort: `low`, `medium`, `high`, `xhigh` or `max` |
