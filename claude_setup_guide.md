# Claude Code Setup Guide — PySchemaElectrical

How to set up Claude Code in VS Code (Max subscription) to systematically work through `todo.md` using an **Opus 4.6 orchestrator** with **Sonnet sub-agents**.

---

## 1. Prerequisites

- **VS Code 1.98.0+** with Claude Code extension installed
- **Claude Max subscription** (gives access to Opus 4.6, Sonnet, and Haiku)
- **uv** installed for Python dependency management
- Repository cloned with `uv sync` already run

---

## 2. Project Settings

Claude Code uses a layered settings system. For this project you need two files:

### `.claude/settings.json` — Shared project settings (commit to git)

This file is read by every Claude Code session in this repo. It tells sub-agents how to behave.

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(uv run pytest:*)",
      "Bash(uv run ruff:*)",
      "Bash(uv run ty:*)",
      "Bash(uv run:*)",
      "Bash(PYTEST_UPDATE_SNAPSHOTS=1 uv run pytest:*)",
      "Bash(PYTHONIOENCODING=utf-8 uv run:*)",
      "Bash(uv pip install:*)",
      "Bash(uv sync:*)",
      "Bash(python:*)",
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git stash:*)",
      "Bash(grep:*)",
      "Bash(find:*)",
      "Read(src/**)",
      "Read(tests/**)",
      "Read(CLAUDE.md)",
      "Read(todo.md)",
      "Read(pyproject.toml)",
      "Edit(src/**)",
      "Edit(tests/**)",
      "Edit(todo.md)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push:*)",
      "Bash(git reset --hard:*)",
      "Bash(git checkout -- *)",
      "Read(.env*)"
    ]
  },
  "respectGitignore": true
}
```

**What this does:**
- Pre-approves all the tools sub-agents need (pytest, ruff, ty, git, file edits)
- Blocks destructive commands (force push, hard reset, rm -rf)
- Blocks reading secrets
- Allows editing source, tests, and `todo.md` without prompts

### `.claude/settings.local.json` — Your personal overrides (gitignored)

Your existing file already has good permissions. Enhance it:

```json
{
  "permissions": {
    "allow": [
      "Bash(dir /B \"c:\\\\Users\\\\OleJohanBondahl\\\\Documents\\\\GitHub_ZEN\\\\PySchemaElectrical\")",
      "Bash(uv run pytest:*)",
      "Bash(python -m pytest:*)",
      "Bash(py -m pytest:*)",
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git stash:*)",
      "Bash(git rm:*)",
      "Bash(PYTEST_UPDATE_SNAPSHOTS=1 uv run pytest:*)",
      "Bash(uv run:*)",
      "Bash(PYTHONIOENCODING=utf-8 uv run:*)",
      "Bash(uv pip install:*)",
      "Bash(grep:*)",
      "Bash(python:*)",
      "Bash(find:*)"
    ],
    "defaultMode": "acceptEdits"
  }
}
```

**Key addition:** `"defaultMode": "acceptEdits"` — auto-accepts file edits so you don't have to approve every single change. You'll still be prompted for any Bash command not in the allow list.

---

## 3. VS Code Extension Settings

Open VS Code settings (`Ctrl+,`) and search for "Claude Code":

| Setting | Value | Why |
|---------|-------|-----|
| `claudeCode.selectedModel` | `opus` | Opus 4.6 as the main orchestrator |
| `claudeCode.initialPermissionMode` | `acceptEdits` | Auto-accept edits, prompt for other actions |
| `claudeCode.autosave` | `true` | Save files before Claude reads them |
| `claudeCode.preferredLocation` | `panel` | Bottom panel gives more horizontal space |

---

## 4. The Orchestration Model

### How it works

```
You (human)
  │
  ▼
Opus 4.6 (orchestrator) ── reads CLAUDE.md + todo.md
  │                         plans task execution order
  │                         manages state and progress
  │
  ├──► Sonnet sub-agent ── Task 3.1: Fix None-safety
  ├──► Sonnet sub-agent ── Task 3.2: Fix motor.py types
  ├──► Sonnet sub-agent ── Task 3.3: Fix TerminalBlock
  │         (parallel — independent tasks)
  │
  ▼
Opus reviews results, runs verification
  │
  ├──► Sonnet sub-agent ── Task 7.1: Add validation
  │         (serial — depends on type fixes being done)
  │
  ▼
Opus updates todo.md, reports summary
```

**Opus (orchestrator)** handles:
- Reading `todo.md` and deciding task order
- Identifying which tasks can run in parallel vs serial
- Spawning Sonnet sub-agents via the `Task` tool with `model: "sonnet"`
- Running verification after sub-agents complete (pytest, ruff, ty)
- Updating `todo.md` checkboxes and notes
- Reporting progress to you

**Sonnet (sub-agents)** handle:
- Focused, single-task code changes
- Running task-specific tests
- Returning results to the orchestrator

### Why this split works

- **Opus** is better at planning, reasoning about dependencies, and quality control
- **Sonnet** is faster and cheaper for focused code edits
- Sub-agents get their own context window, so the orchestrator doesn't fill up with code details
- Parallel sub-agents = faster completion

---

## 5. How to Prompt the Orchestrator

### Starting a work session

Open Claude Code in VS Code and use a prompt like this:

```
Work through the tasks in @todo.md systematically.

Rules:
1. Read CLAUDE.md and todo.md first to understand the project and task list
2. Skip any task marked as "pending Q[n] answer" — those are blocked
3. Use Sonnet sub-agents (model: "sonnet") for each individual task
4. Run independent tasks in parallel where possible
5. After each task completes, verify with: uv run pytest, uv run ruff check, uv run ty check
6. Update todo.md checkboxes as tasks complete: change [ ] to [x]
7. If a sub-agent's changes break tests, fix them before moving on
8. Start with Tier 1 tasks (Section 2 and 3), then Tier 2

Do NOT modify any code that isn't directly related to the task at hand.
Do NOT push to git — I'll review and commit manually.
```

### Running a specific tier

```
Work through Tier 1 tasks from @todo.md (Sections 2 and 3).
Use Sonnet sub-agents for each task. Tasks 3.1, 3.2, 3.3, and 3.4 are
independent — run them in parallel. Task 3.5 depends on my Q4 answer, skip it.
After all tasks complete, run the full test suite and type checker to verify.
Update todo.md with results.
```

### Running a single task

```
Execute Task 3.1 from @todo.md: Fix None-safety in builder.py and project.py.
Use a Sonnet sub-agent. After changes, run pytest and ty check to verify.
Mark the task complete in todo.md if everything passes.
```

### Quality control pass

```
Run a quality control check on all changes made today:
1. uv run pytest — all 219+ tests must pass
2. uv run ty check — diagnostic count should be lower than 54
3. uv run ruff check — no new violations
4. Review the git diff for any unintended changes
Report results and update todo.md with the current diagnostic counts.
```

---

## 6. Task Dependency Map

This is the execution order from `todo.md`. Tasks on the same line can run in parallel.

```
TIER 1 — Bugs & Type Safety
───────────────────────────
Parallel:  3.1 (builder None-safety)  |  3.2 (motor types)  |  3.3 (TerminalBlock)  |  3.4 (merge_circuits)
Serial:    2 (text_anchor bug) — needs Q1 answer first
Serial:    3.5 (autonumbering state) — needs Q4 answer first
Serial:    3.6 (test type errors) — after 3.1–3.4 done

TIER 2 — Quality & Robustness
──────────────────────────────
Parallel:  4.1 (param annotations)  |  4.2 (return annotations)  |  7.1 (input validation)
Serial:    4.3 (replace Any) — after 4.1
Parallel:  7.2 (file I/O errors)  |  7.3 (renderer silent failure)  |  7.4 (port matching)
Serial:    8.1 (Raises docstrings) — after 7.1–7.4
Serial:    8.2 (exception naming) — needs Q7 answer
Parallel:  5.1 (complexity reduction) — independent, large task

TIER 3 — Test Coverage
──────────────────────
Parallel:  9.1 (builder tests)  |  9.3 (system tests)  |  9.4 (analysis tests)  |  9.5 (layout tests)
Serial:    9.2 (project tests) — after 9.1 (builder patterns needed)
Parallel:  9.6 (std_circuits tests)  |  9.7 (typst tests)  |  9.8 (transform tests)

TIER 4 — API Improvements
─────────────────────────
Parallel:  11.1 (BuildResult accessors)  |  11.3 (tag shorthand)  |  11.4 (StandardPins)
Serial:    11.2 (get_terminals) — after 11.1
Serial:    11.5 (DeviceTemplate) — needs Q8 answer
Parallel:  11.6 (CSV merge)  |  11.7 (PLC connections) — needs Q8 answer

TIER 5 — Cleanup
────────────────
Parallel:  5.2 (line length)  |  6.2 (commented code)  |  10.1 (wire_labels naming)  |  10.2 (constants)
Serial:    5.3 (future imports) — needs Q3 answer
Serial:    6.1 (dead code) — needs Q5 answer
Serial:    10.3 + 10.4 (CLAUDE.md update) — after all other tasks
```

---

## 7. Verification Protocol

After each task or batch of tasks, the orchestrator should run this verification:

```bash
# 1. All tests pass
uv run pytest

# 2. Type checker — count should decrease or stay same
uv run ty check 2>&1 | tail -1

# 3. Linter — no new violations
uv run ruff check src/

# 4. Review what changed
git diff --stat
```

**Baseline metrics** (from the last audit):
- Tests: 219 passing, 79% coverage
- ty check: ~54 diagnostics
- ruff check (default rules): ~40 issues

After each tier, these numbers should improve (or at worst stay the same).

---

## 8. Optional: Hooks for Auto-formatting

Add to `.claude/settings.json` or `.claude/settings.local.json` to auto-format Python files after every edit:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "FILE=$(echo $CLAUDE_TOOL_INPUT | python -c \"import sys,json; print(json.load(sys.stdin).get('file_path',''))\"); if [[ \"$FILE\" == *.py ]]; then uv run ruff format \"$FILE\" 2>/dev/null; fi; exit 0"
          }
        ]
      }
    ]
  }
}
```

This runs `ruff format` on every Python file Claude edits, keeping formatting consistent without manual effort.

---

## 9. Session Management Tips

### Keep context lean

The orchestrator's context window fills up as it works. To keep it effective:

- **Delegate verbose work to sub-agents** — test output, large file reads, and code exploration should happen in sub-agents, not the main session
- **Use `/compact`** if context gets large mid-session — it summarizes earlier conversation
- **Use `/clear`** between tiers — start fresh with `Work through Tier 2 from @todo.md`
- **Use `/cost`** to monitor token usage

### Resume work across sessions

If you close VS Code and come back later:

```
Continue working through @todo.md. Read it first to see what's been
completed (marked [x]) and what's next. Pick up where we left off.
```

Claude reads the `todo.md` checkboxes and CLAUDE.md to understand current state.

### Review before committing

After the orchestrator finishes a batch of tasks:

1. Run `git diff` to review all changes
2. Run the full verification protocol (Section 7)
3. Commit in logical groups (one commit per todo section)

---

## 10. Answering the Blocking Questions

Several tasks in `todo.md` Section 0 are blocked on your answers. Before starting work, open `todo.md` and fill in the `> **Answer:**` fields for Q1–Q8. Then tell Claude:

```
I've answered the questions in @todo.md Section 0. Read the answers
and unblock any tasks that were waiting on them. Update the task
descriptions if needed based on my answers.
```

This lets the orchestrator plan the full execution without hitting blocked tasks.

---

## Quick Start Checklist

1. [ ] Install Claude Code extension in VS Code (1.98.0+)
2. [ ] Verify Max subscription is active
3. [ ] Create `.claude/settings.json` with the permissions from Section 2
4. [ ] Update `.claude/settings.local.json` with `defaultMode: "acceptEdits"`
5. [ ] Set VS Code extension model to `opus`
6. [ ] Answer Q1–Q8 in `todo.md` Section 0
7. [ ] Open Claude Code panel and paste the orchestration prompt from Section 5
8. [ ] Let Opus work through the tiers, reviewing after each one
9. [ ] Commit changes after verification passes
