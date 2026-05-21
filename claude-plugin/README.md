# Budget Bot Claude Plugin

Claude Code plugin wrapper for the portable Budget Bot skill in the parent folder.

The canonical skill files live at:

```text
skills/budget-bot/
```

This plugin vendors those files under:

```text
skills/budget-bot/claude-plugin/skills/budget-bot/
```

## Install From GitHub

After this repository is pushed, add it as a Claude Code plugin marketplace:

```text
/plugin marketplace add tordecilla/budget-bot-skill
```

Then install the plugin:

```text
/plugin install budget-bot@budget-bot
```

Restart Claude Code after installation, then invoke:

```text
/budget-bot
```

## Sync

After changing the canonical skill, refresh the plugin copy from the repository root:

```sh
python skills/budget-bot/claude-plugin/scripts/sync_skill.py
```

## Local Test

From the repository root:

```sh
claude --plugin-dir skills/budget-bot/claude-plugin
```

