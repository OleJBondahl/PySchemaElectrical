#!/bin/bash
# Post-edit hook: run ruff format, ruff check, and ty check on edited Python files.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only run on Python files
if [[ "$FILE_PATH" != *.py ]]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR" || exit 0

uv run ruff format "$FILE_PATH" 2>&1
uv run ruff check --fix "$FILE_PATH" 2>&1
uv run ty check "$FILE_PATH" 2>&1
