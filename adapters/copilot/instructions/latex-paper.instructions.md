---
applyTo: "**/*.tex, **/*.bib, **/*.cls, **/*.sty"
description: 排版/编译 LaTeX 时套用 latex-paper 技能
---

# latex-paper

> 本文件由 `scripts/gen-adapters.py` 从 `skills/*/SKILL.md` 自动生成，请勿手工编辑。
> 改技能请改 `SKILL.md`，然后运行 `python scripts/gen-adapters.py`。

- **什么时候用**：中文课程论文、实验报告、平时作业、数学建模国赛（CUMCM）、本科毕业论文、IEEE / ACM 英文会议论文、MCM/ICM 美赛、Elsevier / IEEE 期刊投稿初稿；任何"把内容排成论文/报告 PDF"的需求；LaTeX 报错排查；改字号、页边距、行距、字体、参考文献样式。
- **技能目录名**：`latex-paper`（目录内 `SKILL.md` 是完整说明，先读它再动手）
- **关键命令**：
  - `powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Skill 'scripts\build.ps1') $dst`
  - `.\scripts\build.ps1 cn-cumcm              # 按模板名（只在 templates 下找）`
  - `.\scripts\build.ps1 'D:\...\我的作业'      # 按目录路径（作业目录用这个）`
  - `.\scripts\build.ps1 -All                  # 依次编译 templates 下全部 10 套，出汇总表`
  - `.\scripts\build.ps1 cn-cumcm -KeepAux     # 保留 .aux/.log/.bcf 等中间文件，排错用`
- **产物**：`output\<文件夹名>.pdf`、`output\<文件夹名>.log`

放置：项目 `.github/instructions/latex-paper.instructions.md`（按 `applyTo` 自动生效）。
