# super-writer · adapters/（各 AI 工具的适配文件）

> 本文件由 `scripts/gen-adapters.py` 从 `skills/*/SKILL.md` 自动生成，请勿手工编辑。
> 改技能请改 `SKILL.md`，然后运行 `python scripts/gen-adapters.py`。

`SKILL.md` 是唯一内容源；本目录只是同一份内容的「换格式」产物，供不支持技能目录、
或希望用常驻规则/指令驱动工具的场景使用。

| 文件 | 放哪 | 谁用 |
|---|---|---|
| `cursor/super-writer.mdc` | 项目 `.cursor/rules/` | Cursor Rules |
| `codex/AGENTS.md` | `~/.codex/AGENTS.md` 或项目根 `AGENTS.md` | Codex CLI、Cline、Copilot、Windsurf、Gemini 的通用 AGENTS.md |
| `cline/super-writer.md` | 项目 `.clinerules/` 或全局 Rules 目录 | Cline Rules |
| `gemini/GEMINI.md` | `~/.gemini/GEMINI.md` 或项目根 | Gemini CLI 上下文 |
| `copilot/copilot-instructions.md` | `.github/copilot-instructions.md` | Copilot 仓库级指令 |
| `copilot/instructions/*.instructions.md` | `.github/instructions/` | Copilot 按文件类型定向指令 |
| `windsurf/rules-snippet.md` | `.windsurf/rules/` 或 `global_rules.md` | Windsurf Rules |
| `deepseek/README.md` | 不用投放（原生读技能目录） | DeepSeek Harness 放置说明 |

重新生成：

```bash
python scripts/gen-adapters.py
```
