# super-writer 技能索引（通用 AGENTS.md）

> 本文件由 `scripts/gen-adapters.py` 从 `skills/*/SKILL.md` 自动生成，请勿手工编辑。
> 改技能请改 `SKILL.md`，然后运行 `python scripts/gen-adapters.py`。

放置：`~/.codex/AGENTS.md`（全局）或项目根 `AGENTS.md`。Cline / Copilot / Windsurf / Gemini 也会自动读取项目根 `AGENTS.md`。

## 使用方式

命中下列场景时，先读对应技能目录里的 `SKILL.md`，按里面的流程执行；脚本路径相对于技能目录。

### latex-paper

- **什么时候用**：中文课程论文、实验报告、平时作业、数学建模国赛（CUMCM）、本科毕业论文、IEEE / ACM 英文会议论文、MCM/ICM 美赛、Elsevier / IEEE 期刊投稿初稿；任何"把内容排成论文/报告 PDF"的需求；LaTeX 报错排查；改字号、页边距、行距、字体、参考文献样式。
- **技能目录名**：`latex-paper`（目录内 `SKILL.md` 是完整说明，先读它再动手）
- **关键命令**：
  - `powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Skill 'scripts\build.ps1') $dst`
  - `.\scripts\build.ps1 cn-cumcm              # 按模板名（只在 templates 下找）`
  - `.\scripts\build.ps1 'D:\...\我的作业'      # 按目录路径（作业目录用这个）`
  - `.\scripts\build.ps1 -All                  # 依次编译 templates 下全部 10 套，出汇总表`
  - `.\scripts\build.ps1 cn-cumcm -KeepAux     # 保留 .aux/.log/.bcf 等中间文件，排错用`
- **产物**：`output\<文件夹名>.pdf`、`output\<文件夹名>.log`

### promptlab

- **什么时候用**：用户要写或改 AI 绘画提示词；做场景概念图；做数字人 / 角色设定 / 三视图；做绘本分镜、故事插画；做可进入的 3D 空间前期概念；任何"这组图要长得像同一套"的需求。
- **技能目录名**：`promptlab`（目录内 `SKILL.md` 是完整说明，先读它再动手）
- **关键命令**：
  - `python scripts/check_prompt.py -p "你的提示词"`
  - `python scripts/check_prompt.py -f prompt.txt          # 从文件读`
  - `python scripts/check_prompt.py -b prompts.txt         # 每行一条，批量`
  - `python scripts/check_prompt.py --lang en -p "your prompt"   # 强制英文模式`
- **产物**：对话内直接产出，无文件产物

### sj-ppt

- **什么时候用**：需要"看上去像比赛答辩"的演示文稿：视觉统一、留白充足、数据在动、老师能打开可编辑的 pptx。
- **技能目录名**：`sj-ppt`（目录内 `SKILL.md` 是完整说明，先读它再动手）
- **关键命令**：
  - `node scripts/build_html.mjs deck.json out/index.html`
  - `python scripts/build_pptx.py deck.json out/主题.pptx`
  - `node scripts/check.mjs out/index.html`
- **产物**：`out/index.html`、`out/主题.pptx`
