# Trae Skills 合集

三个自制的 Trae 技能，围绕「写论文 / 做 PPT / 写绘图提示词」三件日常事。每个技能都是自包含目录，复制过去就能用。

## 技能一览

| 技能 | 干什么 | 主要产物 |
|---|---|---|
| [latex-paper](skills/latex-paper/) | LaTeX 论文排版，7 套现成模板（中文课程论文、实验报告、作业、数模国赛、IEEE、ACM、美赛），一条命令跑完 XeLaTeX + bibtex/biber | PDF |
| [sj-ppt](skills/sj-ppt/) | 赛级 PPT 生产线，一份 `deck.json` 同时生成 HTML 演示版和可编辑 `.pptx` | 单文件 HTML + PPTX |
| [promptlab](skills/promptlab/) | 中文 AI 绘画提示词工坊，按七段式写提示词、用锚点保证系列图一致，自带自检脚本 | 提示词文本 + 设定卡 |

## 安装

把需要的技能目录整个复制到 Trae 的技能目录即可，不需要改配置：

```bash
# macOS / Linux
cp -r skills/latex-paper ~/.trae-cn/skills/

# Windows PowerShell
Copy-Item -Recurse skills\latex-paper "$HOME\.trae-cn\skills\"
```

技能在**新建对话**时扫描加载，装完开个新对话才生效。三个都装：

```bash
cp -r skills/latex-paper skills/sj-ppt skills/promptlab ~/.trae-cn/skills/
```

## 用法示例

**latex-paper**：把 `cn-cumcm` 模板复制到作业目录，改 `main.tex` 和 `refs.bib`，然后编译出 PDF。

```powershell
$Skill = Join-Path $HOME '.trae-cn\skills\latex-paper'
Copy-Item "$Skill\templates\cn-cumcm\*" 'D:\作业\数模国赛_2026' -Force
powershell -NoProfile -ExecutionPolicy Bypass -File "$Skill\scripts\build.ps1" 'D:\作业\数模国赛_2026'
```

**sj-ppt**：写好 `deck.json` 后生成两版。

```bash
node scripts/build_html.mjs deck.json out/index.html
python scripts/build_pptx.py deck.json out/deck.pptx
```

**promptlab**：跑一遍自检，按提示改到全部通过。

```bash
python scripts/check_prompt.py -p "你的提示词"
```

## 依赖

| 技能 | 依赖 |
|---|---|
| latex-paper | TeX Live 2026（full scheme），需要 `xelatex`、`bibtex`、`biber` 在 PATH 中；Windows PowerShell 5.1+ |
| sj-ppt | Node.js 18+（生成 HTML）；Python 3.8+，`python-pptx` 与 `lxml`（生成 PPTX） |
| promptlab | Python 3.8+，只用标准库，无需额外安装 |

`latex-paper` 的中文模板固定用 `xelatex`，不能换 `pdflatex`；模板按 `fontset=windows` 配置，非 Windows 系统需要把 `main.tex` 里的 `fontset=windows` 改成 `fontset=fandol` 或其他可用字体集。

## 目录结构

```
skills-repo/
├─ README.md
├─ LICENSE
├─ .gitignore
└─ skills/
   ├─ latex-paper/
   │  ├─ SKILL.md
   │  ├─ references/
   │  ├─ templates/        # 7 套模板，每套 main.tex + refs.bib
   │  └─ scripts/build.ps1
   ├─ sj-ppt/
   │  ├─ SKILL.md
   │  ├─ scripts/
   │  └─ examples/
   └─ promptlab/
      ├─ SKILL.md
      ├─ USAGE.md
      ├─ references/
      ├─ templates/
      ├─ scripts/check_prompt.py
      └─ examples/
```

编译产物（`output/`、`out/`、`*.pdf`、`*.aux`、`__pycache__/` 等）已写入 `.gitignore`，不会进仓库。

## 许可

MIT，见 [LICENSE](LICENSE)。
