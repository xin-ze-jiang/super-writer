#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从一个内容源（skills/*/SKILL.md）生成各 AI 工具的适配文件。

用法：
  python scripts/gen-adapters.py           # 重新生成 adapters/ 下全部文件
  python scripts/gen-adapters.py --check   # 只检查是否有过期文件（CI 用），有则退出码 1

设计原则：SKILL.md 是唯一内容源。这里只做"提取 + 换格式"，
不额外维护第二份正文；改完 SKILL.md 重跑本脚本即可。
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
ADAPTERS = ROOT / "adapters"

# 工具元信息：只写"这份文件该放哪"，不重复技能正文
HEADER_NOTE = (
    "> 本文件由 `scripts/gen-adapters.py` 从 `skills/*/SKILL.md` 自动生成，请勿手工编辑。\n"
    "> 改技能请改 `SKILL.md`，然后运行 `python scripts/gen-adapters.py`。\n"
)


def parse_skill(path: Path):
    """返回 {name, description, when, commands, artifacts, dir_name}"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        raise SystemExit("[错误] %s 缺少 YAML frontmatter" % path)
    fm = m.group(1)
    body = text[m.end():]

    def field(key):
        mm = re.search(r"^%s\s*:\s*(.+)$" % key, fm, re.M)
        if not mm:
            return ""
        v = mm.group(1).strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        return v

    name = field("name") or path.parent.name
    desc = field("description")
    if not desc:
        raise SystemExit("[错误] %s 的 description 为空" % path)

    # 何时用：优先 "**启用**：..." 这一行，退化为标题段落后第一段
    when = ""
    mw = re.search(r"\*\*启用\*\*[：:]\s*(.+)", body)
    if mw:
        when = mw.group(1).strip()
    else:
        mh = re.search(
            r"^##+ [^\n]*(?:适用场景|何时启用|适用)[^\n]*\n+([^\n](?:.|\n)*?)(?:\n\n|\Z)",
            body, re.M)
        if mh:
            when = " ".join(mh.group(1).split())
    if not when:
        when = desc

    # 关键命令：代码块内的行 + 行内反引号里的命令，均需含 scripts/ 或 scripts\
    def usable(s):
        if any(ch in s for ch in "├└│─"):
            return False
        # 纯路径（如 `scripts/check_prompt.py`）不是命令，跳过
        if re.fullmatch(r"\.?[.$\w\\/:-]*scripts[\\/][\w.\-]+", s):
            return False
        return True

    commands = []
    for block in re.findall(r"```[^\n]*\n(.*?)```", body, re.S):
        for line in block.splitlines():
            s = line.strip()
            if re.search(r"scripts[\\/]", s) and not s.startswith("#") and usable(s) and s not in commands:
                commands.append(s)
    for s in re.findall(r"`([^`\n]*scripts[\\/][^`\n]*)`", body):
        s = s.strip()
        if s and not s.startswith("#") and usable(s) and s not in commands:
            commands.append(s)
    commands = commands[:5]

    # 产物位置：只看正文，不看代码块（代码块里多是示例路径）
    prose = re.sub(r"```[^\n]*\n.*?```", "", body, flags=re.S)
    artifacts = []
    for a in re.findall(r"(?:output|out)[\\/][^\s，。；、）)`\"']+", prose):
        a = a.rstrip("。，；")
        if a not in artifacts:
            artifacts.append(a)
    artifacts = artifacts[:3]

    return {
        "name": name,
        "dir": path.parent.name,
        "description": desc,
        "when": when,
        "commands": commands,
        "artifacts": artifacts,
    }


def render_skill_block(s, heading="###"):
    lines = ["%s %s" % (heading, s["name"]), ""]
    lines.append("- **什么时候用**：%s" % s["when"])
    lines.append("- **技能目录名**：`%s`（目录内 `SKILL.md` 是完整说明，先读它再动手）" % s["dir"])
    if s["commands"]:
        lines.append("- **关键命令**：")
        for c in s["commands"]:
            lines.append("  - `%s`" % c)
    lines.append("- **产物**：%s" % ("、".join("`%s`" % a for a in s["artifacts"]) if s["artifacts"] else "对话内直接产出，无文件产物"))
    return "\n".join(lines)


def render_index(skills, heading="##"):
    return "\n\n".join(render_skill_block(s, "###") for s in skills)


def build_files(skills):
    out = {}
    index = render_index(skills)
    names = "、".join(s["name"] for s in skills)

    out["cursor/super-writer.mdc"] = (
        "---\n"
        "description: super-writer 的技能（%s）：LaTeX 论文排版、赛级 PPT 生成、中文 AI 绘画提示词、坐标纸出图。需要排版论文/做答辩 PPT/写绘图提示词/画实验数据图时按需读取对应技能目录下的 SKILL.md。\n"
        "alwaysApply: false\n"
        "---\n\n" % names
    ) + (
        "# super-writer 技能索引（Cursor Rule）\n\n" + HEADER_NOTE + "\n" +
        "放置：项目级 `.cursor/rules/super-writer.mdc`（仅 `.mdc` 会被识别）。\n\n"
        "技能目录放在项目 `.cursor/skills/` 或用户级 `~/.cursor/skills/`（Cursor 原生支持 SKILL.md）。\n\n" +
        index + "\n"
    )

    out["codex/AGENTS.md"] = (
        "# super-writer 技能索引（通用 AGENTS.md）\n\n" + HEADER_NOTE + "\n" +
        "放置：`~/.codex/AGENTS.md`（全局）或项目根 `AGENTS.md`。Cline / Copilot / Windsurf / Gemini 也会自动读取项目根 `AGENTS.md`。\n\n"
        "## 使用方式\n\n"
        "命中下列场景时，先读对应技能目录里的 `SKILL.md`，按里面的流程执行；脚本路径相对于技能目录。\n\n" +
        index + "\n"
    )

    out["cline/super-writer.md"] = (
        "# super-writer 规则（Cline）\n\n" + HEADER_NOTE + "\n" +
        "放置：项目 `.clinerules/super-writer.md`（或 `.cline/rules/`），全局放 Cline Rules 目录。\n\n"
        "Cline 同时原生支持 `SKILL.md`：全局 `~/.cline/skills/<name>/`，项目 `.cline/skills/<name>/`。\n\n" +
        index + "\n"
    )

    out["gemini/GEMINI.md"] = (
        "# super-writer 技能索引（GEMINI.md）\n\n" + HEADER_NOTE + "\n" +
        "放置：全局 `~/.gemini/GEMINI.md`，或项目根 `GEMINI.md`。\n\n"
        "Gemini CLI 也原生支持技能目录：`~/.gemini/skills/<name>/`（或 `~/.agents/skills/`）、项目 `.gemini/skills/`。\n\n" +
        index + "\n"
    )

    out["copilot/copilot-instructions.md"] = (
        "# super-writer 技能索引（GitHub Copilot）\n\n" + HEADER_NOTE + "\n" +
        "放置：项目 `.github/copilot-instructions.md`；个人级 `~/.copilot/copilot-instructions.md`。\n\n"
        "Copilot 也原生支持技能目录：项目 `.github/skills/`、`.claude/skills/`、`.agents/skills/`；个人 `~/.copilot/skills/` 等。\n\n" +
        index + "\n"
    )

    out["copilot/instructions/latex-paper.instructions.md"] = (
        "---\n"
        "applyTo: \"**/*.tex, **/*.bib, **/*.cls, **/*.sty\"\n"
        "description: 排版/编译 LaTeX 时套用 latex-paper 技能\n"
        "---\n\n" +
        "# latex-paper\n\n" + HEADER_NOTE + "\n" +
        render_skill_block(next(s for s in skills if s["name"] == "latex-paper")).replace("### latex-paper\n\n", "") + "\n\n" +
        "放置：项目 `.github/instructions/latex-paper.instructions.md`（按 `applyTo` 自动生效）。\n"
    )

    out["copilot/instructions/sj-ppt.instructions.md"] = (
        "---\n"
        "applyTo: \"**/deck.json, **/*.pptx, **/slides/**\"\n"
        "description: 生成/修改演示文稿时套用 sj-ppt 技能\n"
        "---\n\n" +
        "# sj-ppt\n\n" + HEADER_NOTE + "\n" +
        render_skill_block(next(s for s in skills if s["name"] == "sj-ppt")).replace("### sj-ppt\n\n", "") + "\n\n" +
        "放置：项目 `.github/instructions/sj-ppt.instructions.md`（按 `applyTo` 自动生效）。\n"
    )

    out["windsurf/rules-snippet.md"] = (
        "# super-writer 规则片段（Windsurf）\n\n" + HEADER_NOTE + "\n" +
        "放置：\n\n"
        "- 工作区：`.windsurf/rules/super-writer.md`（单文件上限 12000 字符，frontmatter 可写 `trigger: model_decision`）\n"
        "- 全局：`~/.codeium/windsurf/memories/global_rules.md`（单个文件、始终生效、上限 6000 字符，只贴下面的精简版）\n\n"
        "Windsurf 也原生支持技能目录：`.windsurf/skills/<name>/`、`~/.codeium/windsurf/skills/`。\n\n"
        "## 精简版（贴进 global_rules.md，勿超 6000 字符）\n\n"
        + "\n".join("- **%s**：%s" % (s["name"], s["when"]) for s in skills) + "\n\n"
        + "## 完整版\n\n" + index + "\n"
    )

    out["deepseek/README.md"] = (
        "# super-writer 与 DeepSeek Harness\n\n" + HEADER_NOTE + "\n" +
        "DeepSeek Harness（`dsh`）原生读取 `SKILL.md` 技能目录，**不需要额外的规则文件**，\n"
        "本文件只说明放置位置。\n\n"
        "放置（按 dsh 的发现优先级）：\n\n"
        "- 项目：`<项目根>/.dsh/skills/<技能名>/`（第一优先），其次 `<项目根>/.agents/skills/`\n"
        "- 用户级：`~/.agents/skills/<技能名>/`（`install.ps1` / `install.sh --target deepseek` 装这里，与 Codex 共用，装一份即可）；\n"
        "  dsh 另优先读 `~/.dsh/skills/<技能名>/`，若两处都有同名技能，以 `~/.dsh/skills/` 为准。\n\n"
        "同时指定 `codex,deepseek` 时，两个目标解析到同一目录，脚本只复制一次并提示已去重。\n\n"
        "frontmatter 只要求 `name`（kebab-case）+ `description`，与现有 `SKILL.md` 完全兼容；\n"
        "也支持根目录下平铺的 `<name>.md`，但嵌套子目录不会被发现。\n\n"
        "验证：`npx @deepseek-ai/dsh web` 启动后，在 `/` 命令面板的 Skills 组里应能看到下列技能。\n\n" +
        index + "\n"
    )

    out["README.md"] = (
        "# super-writer · adapters/（各 AI 工具的适配文件）\n\n" + HEADER_NOTE + "\n" +
        "`SKILL.md` 是唯一内容源；本目录只是同一份内容的「换格式」产物，供不支持技能目录、\n"
        "或希望用常驻规则/指令驱动工具的场景使用。\n\n"
        "| 文件 | 放哪 | 谁用 |\n"
        "|---|---|---|\n"
        "| `cursor/super-writer.mdc` | 项目 `.cursor/rules/` | Cursor Rules |\n"
        "| `codex/AGENTS.md` | `~/.codex/AGENTS.md` 或项目根 `AGENTS.md` | Codex CLI、Cline、Copilot、Windsurf、Gemini 的通用 AGENTS.md |\n"
        "| `cline/super-writer.md` | 项目 `.clinerules/` 或全局 Rules 目录 | Cline Rules |\n"
        "| `gemini/GEMINI.md` | `~/.gemini/GEMINI.md` 或项目根 | Gemini CLI 上下文 |\n"
        "| `copilot/copilot-instructions.md` | `.github/copilot-instructions.md` | Copilot 仓库级指令 |\n"
        "| `copilot/instructions/*.instructions.md` | `.github/instructions/` | Copilot 按文件类型定向指令 |\n"
        "| `windsurf/rules-snippet.md` | `.windsurf/rules/` 或 `global_rules.md` | Windsurf Rules |\n"
        "| `deepseek/README.md` | 不用投放（原生读技能目录，与 Codex 共用 `~/.agents/skills/`） | DeepSeek Harness 放置说明 |\n\n"
        "重新生成：\n\n```bash\npython scripts/gen-adapters.py\n```\n"
    )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只检查，不写入")
    args = ap.parse_args()

    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    if not skill_files:
        raise SystemExit("[错误] 没找到 skills/*/SKILL.md")
    skills = [parse_skill(p) for p in skill_files]

    files = build_files(skills)
    stale = []
    for rel, content in files.items():
        target = ADAPTERS / rel
        if args.check:
            old = target.read_text(encoding="utf-8") if target.exists() else None
            if old != content:
                stale.append(rel)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
            print("[生成] adapters/%s" % rel)

    if args.check:
        if stale:
            print("[过期] %s" % ", ".join(stale))
            print("请运行：python scripts/gen-adapters.py")
            return 1
        print("[OK] adapters/ 与 SKILL.md 一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
