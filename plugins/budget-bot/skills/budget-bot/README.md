# Budget Bot Skill

Use this skill for Philippine GAA/NEP budget spreadsheet files. It builds SQLite databases, generates lookup JSONs, and creates a project-level data profile.

Current version: `0.2.0`

## Install

### Codex

Add the GitHub repo as a Codex plugin marketplace:

```sh
codex plugin marketplace add tordecilla/budget-bot-skill
```

Install the plugin:

```sh
codex plugin add budget-bot@budget-bot
```

Restart Codex after installation, then invoke the `budget-bot` skill by asking the agent to start setup.

### Claude Code

Add the GitHub repo as a Claude Code plugin marketplace:

```text
/plugin marketplace add tordecilla/budget-bot-skill
```

Install the plugin:

```text
/plugin install budget-bot@budget-bot
```

Restart Claude Code, then invoke:

```text
/budget-bot
```

## Update

### Codex

Refresh the marketplace snapshot and reinstall the plugin:

```sh
codex plugin marketplace upgrade budget-bot
codex plugin remove budget-bot
codex plugin add budget-bot@budget-bot
```

Restart Codex after the update if prompted.

### Claude Code

Update the installed plugin:

```text
/plugin update budget-bot@budget-bot
```

Restart Claude Code after the update if prompted.

## Setup

Before asking the agent to run setup, download the needed budget documents from DBM and place the XLSX files in `raw/xlsx/`:

```text
https://www.dbm.gov.ph/index.php/budget
```

Then ask your coding agent to use the `budget-bot` skill. For example:

```text
Start the setup.
```

The agent should:

1. Create the project folders.
2. Check for official budget XLSX files under `raw/xlsx/`.
3. Build one SQLite database per year.
4. Generate department/agency lookup JSONs.
5. Create or update `BUDGET_BOT_PROJECT.md`.
6. Validate that the SQLite tables can be queried.

If no XLSX files are present, the agent should create the folders and tell the user to place the DBM budget XLSX files in `raw/xlsx/`.

## Project Folders

```text
raw/xlsx/     official GAA, NEP, or other budget XLSX files
sqlite/       generated year-specific SQLite databases
lookups/      generated department/agency lookup JSON files
reports/      generated analysis outputs
```

## Manual Commands

Manual commands are for debugging or running without an agent. Replace `/path/to/budget-bot` with the installed skill path.

Build all XLSX files in `raw/xlsx/`:

```sh
python /path/to/budget-bot/scripts/build_budget_sqlite.py --xlsx-dir raw/xlsx --sqlite-dir sqlite
```

Generate lookups:

```sh
python /path/to/budget-bot/scripts/build_department_agency_lookup.py --sqlite-dir sqlite --output lookups/department_agency_lookup.json
```

## Project Profile

Create or update `BUDGET_BOT_PROJECT.md` with:

- available budget years and source files,
- default year behavior,
- lookup JSON paths,
- known project-local agency or department notes.

Reusable investigation rules live in `references/budget_bot_instructions.md`.
