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

The runtime workflow is the same across coding agents. Only discovery paths and environment helpers differ.

## Runtime Requirements

Budget Bot requires:

- Python 3.10 or newer.
- Python's standard `sqlite3` module, which is included with normal Python installs.
- Python package dependencies from `requirements.txt`, currently `openpyxl`.

Install Python package dependencies from the skill directory or repository root:

```sh
python -m pip install -r skills/budget-bot/requirements.txt
```

PowerShell:

```powershell
python -m pip install -r skills\budget-bot\requirements.txt
```

## Generic Shell Use

Set `BUDGET_BOT_SKILL_DIR` to the installed skill directory when your agent does not expose a tool-specific skill-path variable.

POSIX shell:

```sh
export BUDGET_BOT_SKILL_DIR="/path/to/budget-bot"
python "$BUDGET_BOT_SKILL_DIR/scripts/build_budget_sqlite.py" --xlsx-dir raw --sqlite-dir sqlite
```

PowerShell:

```powershell
$env:BUDGET_BOT_SKILL_DIR = "C:\path\to\budget-bot"
python "$env:BUDGET_BOT_SKILL_DIR\scripts\build_budget_sqlite.py" --xlsx-dir raw --sqlite-dir sqlite
```

If the agent is explicitly pointed at a project-local skill folder, resolve bundled scripts relative to that loaded `SKILL.md` path.

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
