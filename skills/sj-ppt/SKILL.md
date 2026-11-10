---
name: sj-ppt
description: 赛级 PPT 生产线。用单一 deck.json 内容源同时生成单文件 HTML 演示版与可编辑 .pptx 版，内置统一网格、克制配色、数字滚动/柱状生长/逐项入场动效、pptx 平滑切换与分步出现。适用于答辩、大创汇报、课程汇报等需要"画面优美 + 动态"的场合。
---

# sj-ppt · 赛级 PPT 生产线

## 适用场景

需要"看上去像比赛答辩"的演示文稿：视觉统一、留白充足、数据在动、老师能打开可编辑的 pptx。

## 核心原则

**一份内容源，两份交付。** 所有内容只写在 `deck.json` 里，HTML 与 pptx 都由脚本从它生成；手改 HTML 或 pptx 会导致两版不一致，改内容必须回改 JSON 再重跑。

## 工作流

1. 先确认：场合、页数、汇报时长、是否有学校模板/校徽、风格取向。
2. 写 `deck.json`（结构见下），先给用户看页序与每页一句话主张。
3. 跑 `node scripts/build_html.mjs deck.json out/index.html`。
4. 跑 `python scripts/build_pptx.py deck.json out/主题.pptx`。
5. 跑 `node scripts/check.mjs out/index.html` 做静态检查。
6. 实机验收：
   - HTML：`agent-browser open file:///...` 后截图，或用浏览器全屏按 F 翻页，确认无溢出、无报错。
   - pptx：用 PowerShell COM 打开并导出 PDF，确认不弹修复、页数正确。
7. 交付时说明哪些页需要用户补真实数据或照片。

## deck.json 结构

```json
{
  "title": "主标题",
  "subtitle": "副标题",
  "presenter": "汇报人",
  "date": "2026-11-08",
  "theme": "claude-warm",
  "slides": [
    { "type": "cover", "kicker": "大创中期汇报", "title": "…", "subtitle": "…", "tags": ["…"] },
    { "type": "data", "title": "…", "note": "数据来源：…", "stats": [{"label":"…","value":38,"unit":"%"}],
      "chart": { "labels": ["Q1","Q2","Q3","Q4"], "values": [12,26,41,58], "unit": "%", "caption": "…" } },
    { "type": "points", "title": "…", "items": [{"title":"…","text":"…"}] },
    { "type": "exploded", "title": "…", "axis": "x", "caption": "…",
      "parts": [{"kind":"endcap","label":"端盖"},{"kind":"flange","label":"法兰"},
                {"kind":"gasket","label":"垫片"},{"kind":"bolt","label":"紧固螺栓"}] },
    { "type": "materials", "title": "…", "caption": "…",
      "cards": [{"kind":"brushed","name":"金属拉丝","code":"Brushed Metal","desc":"…"},
                {"kind":"anodized","name":"阳极氧化","code":"Anodized","desc":"…"},
                {"kind":"pcb","name":"PCB 走线","code":"PCB Trace","desc":"…"}] },
    { "type": "end", "title": "谢谢", "subtitle": "…" }
  ]
}
```

页面类型：`cover` 封面 / `statement` 大字观点页 / `data` 数据页（KPI + 柱状图）/ `points` 要点页 / `exploded` 爆炸视图 / `materials` 材质卡页 / `end` 结尾。

可选字段：`styleOverride`（页级覆盖风格）、`art`（整页图片，相对 deck.json 路径）、`artFit`（`cover` 默认 / `contain`，竖图用 contain）。

风格字段：推荐写 `"style": "keynote" | "academic" | "consulting" | "contest" | "minimal-art"`；不写则按 `meta` 自动决策。旧字段 `"theme": "claude-warm" | "tech-dark"` 继续兼容。

## 视觉硬规则

- 网格：左右安全边距 8%，标题区与内容区固定基线；全篇同一套间距。
- 配色：≤3 主色 + 中性色，且必须与主题相关，不用 Office 默认蓝。
- 字号：封面主标题 ≥54px（HTML）/ ≥40pt（pptx），内容页标题 ≥36px / ≥28pt，正文 ≥20px / ≥18pt。
- 留白：单页元素不超过 5 组；文字不超过 6 行。
- 禁用：Office 默认模板、艺术字、阴影叠阴影、每页塞满字、无意义特效。
- 单页动效 ≤3 类。

## 动效规则

HTML：标题上浮、卡片错峰入场、数字滚动计数、柱状按序生长、进度条随页推进。
pptx：Morph 平滑切换 + 分步出现（点击逐项）+ 缩放定位（用 Morph 的 byObject 实现跨页元素连续）。
动效只服务于信息节奏：先出现结论，再出现支撑数据。

## 风格系统（5 套赛级 + 2 套旧主题）

所有令牌写在 `build_html.mjs` 的 `STYLES` 与 `build_pptx.py` 的 `STYLES`，两处保持同名同值；页面级 `styleOverride` 只替换该页令牌。

| 风格 | 背景 | 文字/次级 | 强调 | 标题/正文字体 | 关键参数 | 适用 |
| --- | --- | --- | --- | --- | --- | --- |
| `keynote` | `#0B0B0C` | `#F5F5F7` / `#86868B` | `#2997FF` | 无衬线 / 无衬线 | fsHero 104 / fsTitle 46 / padX 110 / tracking -0.03 / lead 1.5 / motion 1.1s | 发布会、新品、创意展示 |
| `academic` | `#FFFFFF` | `#1B3A5C` / `#5D6B7A` | `#1B3A5C` | 宋体 SimSun / 微软雅黑 | fsHero 46 / fsTitle 28 / padX 88 / tracking -0.01 / motion 0.6s | 答辩、结题、实验报告 |
| `consulting` | `#F7F7F5` | `#16181D` / `#6A6E73` | `#B0432F` | 无衬线 / 无衬线 | fsHero 44 / fsTitle 24 / padX 64 / lead 1.55 / motion 0.55s | 调研、数据分析、复盘 |
| `contest` | `#FFFFFF` | `#111114` / `#6B6E75` | `#FF3D00` | 宋体 / 微软雅黑 | fsHero 88 / fsTitle 42 / fsKpi 76 / padX 104 / tracking -0.03 / motion 0.85s | 路演、挑战杯、互联网+ |
| `minimal-art` | `#F2EFE9` | `#1E1C18` / `#7A736A` | `#A65C3B` | 衬线（Instrument Serif→宋体）/ 微软雅黑 | fsHero 64 / fsTitle 34 / padX 96 / padY 56 / lead 1.75 / tracking -0.02 / motion 0.78s / stagger 100ms | 作品集、展示、低密度汇报 |
| `claude-warm`（旧） | `#FAF9F5` | `#1A1A18` / `#6B6862` | `#D97757` | 衬线 / 无衬线 | BASE 默认 | 兼容旧 deck.json |
| `tech-dark`（旧） | `#111315` | `#F2F3F2` / `#8A9095` | `#3FBDB2` | 衬线 / 无衬线 | BASE 默认 | 兼容旧 deck.json |

### 自动决策 `pickStyle`

优先级从高到低，HTML 与 pptx 同序实现：

1. `deck.style` 明确写风格名 → 强制使用；
2. 旧字段 `deck.theme`（`claude-warm` / `tech-dark`）→ 兼容使用；
3. **minimal-art 门槛**：`meta.purpose` 含「作品集/展示/汇报」+ 文本密度「低」+ 页数 ≤ 12 → `minimal-art`；
4. 关键词匹配：`academic`（答辩/结题/实验/论文/课程/汇报/大创）→ `contest`（路演/创业/挑战杯/互联网+/竞赛/大赛）→ `keynote`（发布/新品/产品/创意/demo/展示/亮相）→ `consulting`（数据分析/调研/复盘/评估/报告/研究）；
5. 无关键词时按特征打分（页数、文字密度、图表占比）；
6. 兜底 `contest`。

`meta` 建议写法：`{"purpose": "大创结题答辩", "audience": "评审专家组", "pageCount": 12, "chartRatio": 0.3, "textDensity": "中"}`。脚本会按实际 slides 重新计算页数与密度，`meta` 主要用于选风格。

### minimal-art 硬性规则

- 只用纸感底 `#F2EFE9`、墨色 `#1E1C18`、单一赭石强调 `#A65C3B`，不加大面积第二种彩色。
- 留白优先：单页元素 ≤ 4 组；装饰只用 1px 细线、细圆环、单色块，不用阴影、渐变、emoji、3D。
- 标题 ≥ 48pt 等效；字距 -0.02em；正文行距 1.6~1.8；正文 13px（HTML）。
- 动效：500~800ms 淡入 + 位移 ≤ 24px，`cubic-bezier(0.22,1,0.36,1)`，同层错峰 100ms。
- 美术图：封面 1920×1080、封底竖版 2480×3508（印刷比例 ~A4），四周留 5% 安全区；生成后 base64 内联，HTML 断网可开；pptx 用 `artFit` 定位（封面 cover、竖版封底 contain）。
- 参考实现：`Docs/_skill_test/minimal/`（美术图 + design-philosophy.md + 4 页样张）。

## 动效参数

**A. 爆炸视图（`exploded` 页）**
- 图层：`parts` 数组，每个零件独立 `<g class="part">`，按数组顺序编号 01…；
- 轴向：`axis: "x" | "y" | "d"`；位移步长 150px（y 轴 110px，斜 45° 为 120/-95px）；
- 时长：单件位移 1.5s，总时长随件数 1.2~1.8s；
- 错峰：每件 100ms（`--i * 100ms`）；标注延后 1.45s 起、每件 110ms；
- 缓动：`cubic-bezier(0.22, 1, 0.36, 1)`；
- 标注：引线 + 圆点 + 编号 + 名称，分离到位后淡入；
- 交互：进入页面 420ms 后自动分解；点「合拢」按钮或按 `R` 反向回位，可反复重播。

**B. 材质卡（`materials` 页）**
- 三种卡：`brushed`（拉丝）、`anodized`（阳极氧化）、`pcb`（PCB 走线），纹理为纯 CSS/内联 SVG，无外链；
- 入场：三卡错峰 120ms 上浮；
- 扫光：渐变条 1.05s 斜扫一次，延迟 `0.85s + i*120ms`，不循环；
- 切换：卡片「切换材质」按钮或点色块，两态交叉淡入 0.6s（拉丝↔镜面、哑光↔喷砂、铜箔↔沉金）；
- 放大：`局部放大` 把纹理层 `scale(1.55)`，0.9s 缓动，再点复位；
- 单页特效 ≤3 类：扫光、切换、放大，全部按序、不叠加循环动画。

## CSS 版 ↔ pptx 版的等价程度

| 能力 | HTML | pptx | 说明 |
| --- | --- | --- | --- |
| 页面切换 | 淡入 | Morph（`p15:morph`） | 等价 |
| 分步出现 | 错峰入场 | 点击逐项 | 顺序一致，节奏不同 |
| 数字滚动 / 柱状生长 | 有 | 无 | pptx 数据页为静态图表 |
| 爆炸分离 / 合拢 | 位移动画 + 标注淡入 | **不等价**：静态爆炸排布 + 分步出现 | 未注入路径动画，避免文件损坏；无反向合拢 |
| 材质扫光 / 双态切换 / 局部放大 | 有 | **不等价**：静态材质示意 | pptx 仅用形状与线条近似纹理，无动效 |

交付时必须在说明里点明上表后三行，不能对用户宣称两版动效一致。

## 3D 爆炸序列（外部素材）

若要把 CSS 示意换成真 3D 爆炸，需要三维组提供：**PNG 序列（带 alpha 透明通道）**，1920×1080，24 或 30 fps，单段 3~5s；或 **MOV/WebM（ProRes 4444 / VP9 alpha）**。HTML 版直接嵌入视频；pptx 版只能插视频文件（不保证跨机器播放），不能转成原生形状动画。

## 自检

- HTML：`check.mjs` 通过（无外链、无占位符残留）；浏览器全屏 16:9 无溢出；控制台无报错；离线可开。
- pptx：PowerPoint 打开无修复提示；页数与 HTML 一致；无文字溢出框；字体替换不乱版；动画顺序正确。
- 两版：文案、数字、页序逐条对齐。

## 文件位置

- 脚本：`scripts/build_html.mjs`、`scripts/build_pptx.py`、`scripts/check.mjs`
- 示例：`examples/deck.json`
- 输出目录：脚本示例用相对路径 `out/`（已被 `.gitignore` 忽略）；正式交付目录由用户指定
