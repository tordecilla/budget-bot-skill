# Environment And Installation

Use this reference only when installing the skill, debugging discovery, or resolving paths to bundled scripts. Keep task workflow instructions in `SKILL.md`.

## Shared Skill Layout

The skill folder should contain:

```text
budget-bot/
  SKILL.md
  README.md
  scripts/
  references/
  agents/
```

The runtime workflow is the same for Codex and Claude Code. Only discovery paths and environment helpers differ.

## Codex

Recommended personal install path:

```text
~/.codex/skills/budget-bot/SKILL.md
```

Project-local installs may also work when the agent is explicitly pointed at the skill folder. Resolve bundled scripts relative to the loaded `SKILL.md` path.

## Claude Code

Personal install path:

```text
~/.claude/skills/budget-bot/SKILL.md
```

Project install path:

```text
.claude/skills/budget-bot/SKILL.md
```

Claude Code invokes the skill as:

```text
/budget-bot
```

When the skill is loaded, Claude Code exposes the containing skill directory as:

```text
${CLAUDE_SKILL_DIR}
```

Use that variable for bundled scripts.
