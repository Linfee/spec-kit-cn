#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [ -z "${GH_TOKEN:-}" ] && [ -z "${GITHUB_TOKEN:-}" ] && command -v gh >/dev/null 2>&1; then
  GH_TOKEN="$(gh auth token 2>/dev/null || true)"
  if [ -n "$GH_TOKEN" ]; then
    export GH_TOKEN
  fi
fi

TMP_DIR="$(mktemp -d)"
DIST_SNAPSHOT="$TMP_DIR/dist-before.txt"
if [ -d dist ]; then
  ls -1 dist >"$DIST_SNAPSHOT"
else
  : >"$DIST_SNAPSHOT"
fi

cleanup() {
  if [ -d dist ]; then
    while IFS= read -r item; do
      [ -n "$item" ] || continue
      grep -qxF "$item" "$DIST_SNAPSHOT" && continue
      rm -f "dist/$item"
    done < <(ls -1 dist)
    rmdir dist 2>/dev/null || true
  fi
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "[1/7] Ruff"
uvx ruff check src/ tests/

echo "[2/7] Pytest"
uv sync --extra test
uv run pytest

echo "[3/7] CLI smoke"
uv run specify-cn --help >/dev/null
uv run specify-cn check --help >/dev/null

echo "[4/7] init e2e (all agents, sh)"
agents=(
  claude copilot gemini cursor-agent qwen opencode codex windsurf kilocode
  auggie codebuddy qodercli roo amp shai tabnine kiro-cli agy bob vibe kimi
)

tested_agents=0
skipped_agents=0

for agent in "${agents[@]}"; do
  template_agent="$agent"
  if [ "$agent" = "qodercli" ]; then
    template_agent="qoder"
  fi

  echo "  - validating $agent (sh)"
  target="$TMP_DIR/init-$agent-sh"
  log="$TMP_DIR/init-$agent-sh.log"

  # codex and agy require --ai-skills flag
  extra_flags=""
  if [ "$agent" = "codex" ] || [ "$agent" = "agy" ]; then
    extra_flags="--ai-skills"
  fi

  if ! uv run specify-cn init "$target" --ai "$agent" --ignore-agent-tools --no-git --script sh $extra_flags >"$log" 2>&1; then
    if grep -q "No matching release asset found" "$log"; then
      echo "    skipped $agent (sh): latest release has no matching template asset"
      skipped_agents=$((skipped_agents + 1))
      continue
    fi
    echo "init failed for $agent (sh):"
    cat "$log"
    exit 1
  fi
  tested_agents=$((tested_agents + 1))

  test -f "$target/.specify/templates/spec-template.md"
  test -f "$target/.specify/templates/plan-template.md"
  test -f "$target/.specify/memory/constitution.md"

  case "$agent" in
    claude) test -d "$target/.claude/commands" ;;
    copilot) test -d "$target/.github/agents" ;;
    gemini) test -d "$target/.gemini/commands" ;;
    cursor-agent) test -d "$target/.cursor/commands" ;;
    qwen) test -d "$target/.qwen/commands" ;;
    opencode) test -d "$target/.opencode/command" ;;
    codex) test -d "$target/.agents/skills" ;;
    windsurf) test -d "$target/.windsurf/workflows" ;;
    kilocode) test -d "$target/.kilocode/workflows" ;;
    auggie) test -d "$target/.augment/commands" ;;
    codebuddy) test -d "$target/.codebuddy/commands" ;;
    qodercli) test -d "$target/.qoder/commands" ;;
    roo) test -d "$target/.roo/commands" ;;
    amp) test -d "$target/.agents/commands" ;;
    shai) test -d "$target/.shai/commands" ;;
    tabnine) test -d "$target/.tabnine/agent/commands" ;;
    kiro-cli) test -d "$target/.kiro/prompts" ;;
    agy) test -d "$target/.agents/skills" ;;
    bob) test -d "$target/.bob/commands" ;;
    vibe) test -d "$target/.vibe/prompts" ;;
    kimi) test -d "$target/.kimi/skills" ;;
  esac
done

if [ "$tested_agents" -eq 0 ]; then
  echo "No agents were validated in sh mode"
  exit 1
fi
if [ "$skipped_agents" -gt 0 ]; then
  echo "Skipped $skipped_agents agent(s) in sh mode due to missing release assets"
fi

echo "[5/7] script variant smoke (ps)"
for agent in claude copilot kiro-cli; do
  echo "  - validating $agent (ps)"
  target="$TMP_DIR/init-$agent-ps"
  log="$TMP_DIR/init-$agent-ps.log"
  if ! uv run specify-cn init "$target" --ai "$agent" --ignore-agent-tools --no-git --script ps >"$log" 2>&1; then
    if grep -q "No matching release asset found" "$log"; then
      echo "    skipped $agent (ps): latest release has no matching template asset"
      continue
    fi
    echo "init failed for $agent (ps):"
    cat "$log"
    exit 1
  fi
  test -f "$target/.specify/scripts/powershell/setup-plan.ps1"
done

echo "[6/7] build"
uv build >/dev/null

echo "[7/7] wheel install smoke"
WHEEL_PATH="$(ls -1t dist/specify_cn_cli-*.whl | head -n 1)"
python3 -m venv "$TMP_DIR/wheel-venv"
"$TMP_DIR/wheel-venv/bin/pip" install "$WHEEL_PATH" >/dev/null
"$TMP_DIR/wheel-venv/bin/specify-cn" --help >/dev/null

echo "Release validation passed"
