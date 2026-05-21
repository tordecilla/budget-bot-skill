# Budget Bot Codex Plugin

Codex plugin wrapper for the portable Budget Bot skill in the parent folder.

The canonical skill files live at:

```text
skills/budget-bot/
```

This plugin vendors those files under:

```text
skills/budget-bot/plugins/budget-bot/skills/budget-bot/
```

## Install

After this repository is pushed, add it as a Codex plugin marketplace:

```sh
codex plugin marketplace add tordecilla/budget-bot-skill
```

Then install the plugin:

```sh
codex plugin add budget-bot@budget-bot
```

Restart Codex after installation, then ask:

```text
Start the setup.
```

## Update

Refresh the marketplace snapshot and reinstall the plugin:

```sh
codex plugin marketplace upgrade budget-bot
codex plugin remove budget-bot
codex plugin add budget-bot@budget-bot
```

Restart Codex after updating if prompted.

## Sync

After changing the canonical skill, refresh the plugin copy from the repository root:

```sh
python skills/budget-bot/plugins/budget-bot/scripts/sync_skill.py
```

