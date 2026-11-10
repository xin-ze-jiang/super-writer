---
applyTo: "**/deck.json, **/*.pptx, **/slides/**"
description: 生成/修改演示文稿时套用 sj-ppt 技能
---

# sj-ppt

> 本文件由 `scripts/gen-adapters.py` 从 `skills/*/SKILL.md` 自动生成，请勿手工编辑。
> 改技能请改 `SKILL.md`，然后运行 `python scripts/gen-adapters.py`。

- **什么时候用**：需要"看上去像比赛答辩"的演示文稿：视觉统一、留白充足、数据在动、老师能打开可编辑的 pptx。
- **技能目录名**：`sj-ppt`（目录内 `SKILL.md` 是完整说明，先读它再动手）
- **关键命令**：
  - `node scripts/build_html.mjs deck.json out/index.html`
  - `python scripts/build_pptx.py deck.json out/主题.pptx`
  - `node scripts/check.mjs out/index.html`
- **产物**：`out/index.html`、`out/主题.pptx`

放置：项目 `.github/instructions/sj-ppt.instructions.md`（按 `applyTo` 自动生效）。
