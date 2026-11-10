# 跨工具支持：各 AI 工具的规则/技能文件位置

查证日期：**2026-11-10**。以下结论均来自各工具官方文档（链接见文末），不是凭记忆写的；工具改版后请以官方文档为准并更新本表。

## 一、结论速查

| 工具 | 级别 | 技能目录（SKILL.md） | 单文件规则/指令 | 是否多文件 |
|---|---|---|---|---|
| Claude Code | 用户级 | `~/.claude/skills/<name>/SKILL.md` | — | 是：每个技能一个目录，目录内可带 `scripts/`、`references/` |
| Claude Code | 项目级 | `.claude/skills/<name>/SKILL.md` | `CLAUDE.md`（上下文） | 是 |
| Trae | 用户级 | `~/.trae-cn/skills/<name>/SKILL.md`（国内版）、`~/.trae/skills/`（国际版） | — | 是 |
| Cursor | 用户级 | `~/.cursor/skills/<name>/SKILL.md`、`~/.agents/skills/<name>/SKILL.md` | 无文件级用户规则（Team/User Rules 走账号） | 是，技能支持嵌套子目录 |
| Cursor | 项目级 | `.cursor/skills/<name>/`、`.agents/skills/<name>/` | `.cursor/rules/*.mdc` | 是：`rules/` 下可放多个 `.mdc` |
| OpenAI Codex CLI | 用户级 | `~/.codex/skills/`（第三方实践）、`~/.agents/skills/` | `~/.codex/AGENTS.md`（有 `AGENTS.override.md` 时优先） | 是：全局 + 项目逐级向下合并 |
| OpenAI Codex CLI | 项目级 | `.agents/skills/` | 项目根 `AGENTS.md`（可逐级子目录） | 是 |
| Cline | 用户级 | `~/.cline/skills/<name>/SKILL.md` | `~/Documents/Cline/Rules/`（Windows `Documents\Cline\Rules`）、`~/.cline/rules/` | 是 |
| Cline | 项目级 | `.cline/skills/<name>/`、`.clinerules/skills/` | `.clinerules/`、`.cline/rules/`、`AGENTS.md` | 是 |
| Gemini CLI | 用户级 | `~/.gemini/skills/<name>/`（`~/.agents/skills/` 为别名） | `~/.gemini/GEMINI.md` | 是：层级合并 |
| Gemini CLI | 项目级 | `.gemini/skills/<name>/`、`.agents/skills/` | `./GEMINI.md`（子目录可再分层） | 是 |
| GitHub Copilot | 用户级 | `~/.copilot/skills/`、`~/.claude/skills/`、`~/.agents/skills/` | `~/.copilot/copilot-instructions.md`、`~/.copilot/instructions/**/*.instructions.md` | 是 |
| GitHub Copilot | 项目级 | `.github/skills/`、`.claude/skills/`、`.agents/skills/` | `.github/copilot-instructions.md`、`AGENTS.md`、`.github/instructions/**/*.instructions.md` | 是 |
| Windsurf | 用户级 | `~/.codeium/windsurf/skills/<name>/` | `~/.codeium/windsurf/memories/global_rules.md`（单文件、始终生效、≤6000 字符） | 技能可多目录；global_rules 只能一个文件 |
| Windsurf | 项目级 | `.windsurf/skills/<name>/`、`.agents/skills/` | `.windsurf/rules/*.md`（单文件 ≤12000 字符）、任意 `AGENTS.md` | 是 |

> Trae 没有公开的技能规范文档，表中路径按本机实际安装目录（`~/.trae-cn/skills/`、`~/.trae/skills/`）记录，不是查证来的。

## 二、frontmatter 要求

### 通用 SKILL.md（Claude Code / Cursor / Cline / Gemini / Copilot / Windsurf / Trae）

```yaml
---
name: skill-name        # 必填，kebab-case，必须与所在目录名一致
description: 做什么 + 什么时候用   # 必填，建议 <1024 字符，不含 XML 标签（< >）
---
```

其余字段（`license`、`allowed-tools`、`disable-model-invocation` 等）均为可选，各工具支持程度不一，super-writer 只用 `name` + `description`，保证全平台可读。

### 各单文件格式

| 文件 | frontmatter | 说明 |
|---|---|---|
| Cursor `*.mdc` | `description` / `globs` / `alwaysApply` | 三个字段组合决定生效方式：`alwaysApply: true` 每会话生效；`globs` 命中文件生效；只写 `description` 由 Agent 判断；都没有则仅 `@` 提及时生效。**扩展名必须是 `.mdc`，`.md` 会被忽略** |
| Cline 规则 | 可选 YAML `paths:` | 纯 Markdown 也可用 |
| Copilot `*.instructions.md` | `applyTo`（逗号分隔多个 glob）、`description` | 定向指令，按匹配文件自动生效 |
| Copilot `copilot-instructions.md` | 无 frontmatter | 仓库/个人级常驻指令 |
| `AGENTS.md` | 无 frontmatter | Codex 全局 + 项目逐级合并；Cline / Copilot / Windsurf / Gemini 也会读项目根的 |
| `GEMINI.md` | 无 frontmatter | 全局 + 项目层级合并 |
| Windsurf `global_rules.md` | 无 frontmatter | 始终生效，6000 字符硬上限 |

## 三、super-writer 据此采用的策略

1. **`skills/*/SKILL.md` 是唯一内容源**，不维护第二份正文。
2. **6/7 个工具原生支持 SKILL.md 目录**（Claude、Trae、Cursor、Cline、Gemini、Copilot、Windsurf），所以安装脚本的主动作是**复制整个技能目录**，脚本、模板、references 一起带过去。
3. Codex 以 `AGENTS.md` 为主，安装时额外把索引追加进 `~/.codex/AGENTS.md`，并把技能复制到 `~/.agents/skills/`（多工具共用目录）。
4. `adapters/` 只放**换格式的索引文件**（Cursor `.mdc`、`AGENTS.md`、`GEMINI.md`、Cline 规则、Copilot 指令、Windsurf 片段），由 `scripts/gen-adapters.py` 从 SKILL.md 提取「何时用 / 关键命令 / 产物」生成，不复制正文。

## 四、来源

- Claude Code Skills：<https://code.claude.com/docs/en/skills>
- Claude 技能创作规范（frontmatter 必填项）：<https://claude.com/docs/skills/how-to>
- Cursor Rules：<https://cursor.com/docs/context/rules>
- Cursor 规则格式（`.mdc`、三字段组合）：<https://cursor.com/docs/reference/plugins.md>
- Codex `AGENTS.md` 层级：<https://learn.microsoft.com/azure/foundry/openai/how-to/codex>
- Cline 规则：<https://docs.cline.bot/customization/cline-rules>
- Cline 配置/技能：<https://docs.cline.bot/features/skills>、<https://docs.cline.bot/getting-started/config>
- Gemini CLI 技能：<https://geminicli.com/docs/cli/skills/>
- Gemini CLI 上下文（GEMINI.md）：<https://geminicli.com/docs/cli/tutorials/memory-management/>
- VS Code Copilot Agent Skills：<https://code.visualstudio.com/docs/copilot/customization/agent-skills>
- Copilot 技能路径（工作区/个人）：<https://learn.microsoft.com/visualstudio/ide/copilot-agent-skills>
- Windsurf Rules / Memories：<https://docs.windsurf.com/windsurf/cascade/memories>
- Windsurf Skills：<https://docs.windsurf.com/windsurf/cascade/skills>
