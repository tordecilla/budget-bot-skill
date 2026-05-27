# Budget Bot Skill

Use this skill for Philippine GAA/NEP budget spreadsheet files. It builds SQLite databases, generates Markdown lookups, and creates a project-level data profile.

Current version: `0.2.1`

## Requirements

- Python 3.10 or newer.
- Python's standard `sqlite3` module, which is included with normal Python installs.
- Python package dependencies listed in `requirements.txt`.

Install Python package dependencies:

```sh
python -m pip install -r skills/budget-bot/requirements.txt
```

PowerShell:

```powershell
python -m pip install -r skills\budget-bot\requirements.txt
```

## Install

Install the skill by placing this folder somewhere your coding agent can read it. These examples use only shell commands; adjust the destination to match your agent's skill directory.

POSIX shell:

```sh
SKILL_DIR="${BUDGET_BOT_SKILL_DIR:-$HOME/.local/share/skills/budget-bot}"
mkdir -p "$(dirname "$SKILL_DIR")"
cp -R skills/budget-bot "$SKILL_DIR"
```

PowerShell:

```powershell
$SkillDir = if ($env:BUDGET_BOT_SKILL_DIR) { $env:BUDGET_BOT_SKILL_DIR } else { Join-Path $HOME ".local\share\skills\budget-bot" }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $SkillDir) | Out-Null
Copy-Item -Recurse -Force -Path skills\budget-bot -Destination $SkillDir
```

Then point your agent at the installed `SKILL.md` or ask it to use the `budget-bot` skill if it auto-discovers skills from that directory.

## Update

Refresh your local repository, then copy the skill folder again.

```sh
git pull
SKILL_DIR="${BUDGET_BOT_SKILL_DIR:-$HOME/.local/share/skills/budget-bot}"
rm -rf "$SKILL_DIR"
mkdir -p "$(dirname "$SKILL_DIR")"
cp -R skills/budget-bot "$SKILL_DIR"
```

PowerShell:

```powershell
git pull
$SkillDir = if ($env:BUDGET_BOT_SKILL_DIR) { $env:BUDGET_BOT_SKILL_DIR } else { Join-Path $HOME ".local\share\skills\budget-bot" }
if (Test-Path -LiteralPath $SkillDir) { Remove-Item -LiteralPath $SkillDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $SkillDir) | Out-Null
Copy-Item -Recurse -Force -Path skills\budget-bot -Destination $SkillDir
```

Restart or reload your agent if it caches skill files.

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
4. Generate department/agency Markdown lookups.
5. Create or update `BUDGET_BOT_PROJECT.md`.
6. Validate that the SQLite tables can be queried.

If no XLSX files are present, the agent should create the folders and tell the user to place the DBM budget XLSX files in `raw/xlsx/`.

## Project Folders

```text
raw/xlsx/     official GAA, NEP, or other budget XLSX files
sqlite/       generated year-specific SQLite databases
lookups/      generated department/agency Markdown lookup files
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
python /path/to/budget-bot/scripts/build_department_agency_lookup.py --sqlite-dir sqlite --output lookups/department_agency_lookup.md
```

## Project Profile

Create or update `BUDGET_BOT_PROJECT.md` with:

- available budget years and source files,
- default year behavior,
- lookup Markdown paths,
- known project-local agency or department notes.

Reusable investigation rules live in `references/budget_bot_instructions.md`.
