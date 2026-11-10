#!/usr/bin/env bash
# 把本仓库的技能安装到主流 AI 工具的配置目录（macOS / Linux / WSL）。
#
# 用法：
#   ./install.sh                       # auto：只装检测到的工具
#   ./install.sh --target all          # 全装，缺目录就创建
#   ./install.sh --target claude,cursor
#   ./install.sh claude                # 位置参数等价于 --target
#   ./install.sh --home /tmp/testhome  # 覆盖用户主目录（测试用）
#
# 支持：trae claude cursor codex cline gemini copilot windsurf
set -euo pipefail

TARGET="auto"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME}"

usage() {
  sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

while [ $# -gt 0 ]; do
  case "$1" in
    --target=*) TARGET="${1#*=}"; shift ;;
    --target|-t) TARGET="${2:-}"; shift 2 ;;
    --home=*) HOME_DIR="${1#*=}"; shift ;;
    --home) HOME_DIR="${2:-}"; shift 2 ;;
    --repo=*) REPO="${1#*=}"; shift ;;
    --repo) REPO="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "[错误] 未知参数：$1" >&2; usage >&2; exit 2 ;;
    *) TARGET="$1"; shift ;;
  esac
done

if [ ! -d "$REPO/skills" ]; then
  echo "[错误] 找不到技能目录：$REPO/skills" >&2
  exit 1
fi

ALL_NAMES="trae claude cursor codex cline gemini copilot windsurf"

label_for() {
  case "$1" in
    trae) echo "Trae" ;;
    claude) echo "Claude Code" ;;
    cursor) echo "Cursor" ;;
    codex) echo "OpenAI Codex CLI" ;;
    cline) echo "Cline" ;;
    gemini) echo "Gemini CLI" ;;
    copilot) echo "GitHub Copilot" ;;
    windsurf) echo "Windsurf" ;;
  esac
}

dir_for() {
  case "$1" in
    trae)
      if [ -d "$HOME_DIR/.trae-cn" ]; then echo "$HOME_DIR/.trae-cn/skills"
      else echo "$HOME_DIR/.trae/skills"; fi ;;
    claude) echo "$HOME_DIR/.claude/skills" ;;
    cursor) echo "$HOME_DIR/.cursor/skills" ;;
    codex) echo "$HOME_DIR/.agents/skills" ;;
    cline) echo "$HOME_DIR/.cline/skills" ;;
    gemini) echo "$HOME_DIR/.gemini/skills" ;;
    copilot) echo "$HOME_DIR/.copilot/skills" ;;
    windsurf) echo "$HOME_DIR/.codeium/windsurf/skills" ;;
  esac
}

detect_paths() {
  case "$1" in
    trae) echo "$HOME_DIR/.trae-cn $HOME_DIR/.trae" ;;
    codex) echo "$HOME_DIR/.codex" ;;
    windsurf) echo "$HOME_DIR/.codeium/windsurf" ;;
    *) echo "$HOME_DIR/.$1" ;;
  esac
}

trigger_for() {
  case "$1" in
    latex-paper) echo "「把这份实验报告排成 PDF」或「用 latex-paper 编译这个 .tex」" ;;
    sj-ppt) echo "「用 sj-ppt 做一个 12 页答辩 PPT」" ;;
    promptlab) echo "「帮我写/改一条即梦提示词」" ;;
    *) echo "" ;;
  esac
}

update_codex_agents() {
  local adapter="$REPO/adapters/codex/AGENTS.md"
  local agents="$HOME_DIR/.codex/AGENTS.md"
  if [ ! -f "$adapter" ]; then
    echo "  [跳过] 没有找到 adapters/codex/AGENTS.md，未追加全局指令"
    return
  fi
  mkdir -p "$(dirname "$agents")"
  local tmp
  tmp="$(mktemp)"
  if [ -f "$agents" ]; then
    awk '/<!-- super-writer:begin -->/{skip=1} !skip{print} /<!-- super-writer:end -->/{skip=0}' "$agents" > "$tmp"
  fi
  if [ -s "$tmp" ]; then printf '\n' >> "$tmp"; fi
  {
    printf '%s\n' '<!-- super-writer:begin -->'
    cat "$adapter"
    printf '%s\n' '<!-- super-writer:end -->'
  } >> "$tmp"
  mv "$tmp" "$agents"
  echo "  [OK] AGENTS.md -> $agents"
}

install_skills() {
  local name="$1"
  local dest
  dest="$(dir_for "$name")"
  mkdir -p "$dest"
  printf '\n[%s] %s\n' "$name" "$dest"
  local src sn trig
  for src in "$REPO"/skills/*/; do
    [ -d "$src" ] || continue
    src="${src%/}"
    sn="$(basename "$src")"
    rm -rf "$dest/$sn"
    cp -R "$src" "$dest/$sn"
    # 本地产物 / 缓存不带走
    rm -rf "$dest/$sn/output" "$dest/$sn/out" "$dest/$sn/__pycache__" "$dest/$sn/.venv"
    printf '  [OK] %-12s -> %s\n' "$sn" "$dest/$sn"
    trig="$(trigger_for "$sn")"
    [ -n "$trig" ] && printf '       触发：%s\n' "$trig"
  done
  if [ "$name" = "codex" ]; then update_codex_agents; fi
}

# ---- 解析目标 ----
want="$(echo "$TARGET" | tr ',' ' ' | tr '[:upper:]' '[:lower:]')"
selected=""
skipped=""

case " $want " in
  *" all "*)
    selected="$ALL_NAMES" ;;
  *" auto "*)
    for n in $ALL_NAMES; do
      hit=0
      for d in $(detect_paths "$n"); do
        [ -d "$d" ] && hit=1
      done
      if [ "$hit" = "1" ]; then selected="$selected $n"; else skipped="$skipped $n"; fi
    done ;;
  *)
    for n in $want; do
      if echo " $ALL_NAMES " | grep -qw "$n"; then
        selected="$selected $n"
      else
        echo "[忽略] 未知目标：$n（可用：all, auto, $ALL_NAMES）" >&2
      fi
    done ;;
esac

selected="$(echo "$selected" | xargs 2>/dev/null || true)"
skipped="$(echo "$skipped" | xargs 2>/dev/null || true)"

echo "仓库：$REPO"
echo "技能：$(cd "$REPO/skills" && ls -1d */ 2>/dev/null | tr -d '/' | tr '\n' ' ')"
echo "目标：${selected:-无}"

if [ -n "$skipped" ]; then
  echo ""
  echo "[跳过] 未检测到：$skipped"
  echo "       需要全装请用：./install.sh --target all"
fi

if [ -z "$selected" ]; then
  echo ""
  echo "没有可安装的目标，未做任何修改。"
  exit 0
fi

for n in $selected; do
  install_skills "$n"
done

echo ""
echo "完成。技能在新对话/新会话中生效；重复执行会原地覆盖，不会产生重复目录。"
