# 模板选择与目录约定

## 1. 目录约定

```
<技能目录>\
├─ templates\                每套模板一个子目录，入口文件统一叫 main.tex，文献统一叫 refs.bib
│   ├─ cn-thesis\            中文本科毕业论文（ctexbook + bibtex + GB/T 7714）
│   ├─ cn-course-paper\      中文课程论文（ctexart + bibtex + GB/T 7714）
│   ├─ cn-lab-report\        中文实验报告（ctexart + bibtex + siunitx）
│   ├─ cn-homework\          通用课程作业（ctexart + biblatex + biber）
│   ├─ cn-cumcm\             全国大学生数学建模竞赛（ctexart，按 2023 修订规范手工实现）
│   ├─ en-journal-els\       Elsevier 期刊（elsarticle 单栏 preprint + 审稿行号）
│   ├─ en-journal-ieee\      IEEE 期刊（IEEEtran[journal] 双栏）
│   ├─ en-ieee\              IEEE conference（IEEEtran + TeX Gyre Termes）
│   ├─ en-acm\               ACM sigconf（acmart + Libertine）
│   └─ en-mcm\               MCM/ICM 美赛（article 12pt + Times + Summary Sheet）
├─ scripts\build.ps1         一键编译脚本
├─ references\               模板选择、报错、中文排版、英文字体
└─ output\                   产物：<文件夹名>.pdf / <文件夹名>.log（同名覆盖，只留最新一份）
```

改内容只需要动两处：`main.tex` 正文、`refs.bib` 文献。**`templates\` 是单一份底稿，作业一律复制出去改。**

## 2. 十套模板对照

| 模板 | 文档类 / 选项 | 版式要点 | 文献引擎 | 预期页数（占位内容） |
|---|---|---|---|---|
| cn-thesis | `ctexbook[UTF8,a4paper,zihao=-4,fontset=\swfontset,openany]` | 封面 + 中英摘要 + 目录 + 五章 + 参考文献 + 致谢 + 附录；封面不编号、摘要起罗马数字 I、正文阿拉伯数字从 1；图/表/公式按章编号（图 1-1） | bibtex + `gbt7714-numerical` | 13 |
| cn-course-paper | `ctexart[UTF8,a4paper,zihao=-4,fontset=\swfontset]` | A4，上下 2.54 / 左右 3.17 cm，小四宋体 1.5 倍行距，页码居中页脚 | bibtex + `gbt7714-numerical` | 2 |
| cn-lab-report | 同上 | 同上，`section` 编号为「一、二、」，`\labinfo{课程}{日期}{姓名}{学号}`，带 `siunitx` 单位 | bibtex + gbt7714 | 2 |
| cn-homework | 同上 | 同上，列表用 `enumitem` | **biber** + `biblatex[style=gb7714-2015]` | 2 |
| cn-cumcm | 同上 | 四边 2.5 cm；摘要页 `\pagenumbering{gobble}`，正文 `\pagenumbering{arabic}`；题目三号黑体、一级标题四号黑体居中 | bibtex + gbt7714 | 4 |
| en-journal-els | `elsarticle[preprint,review,12pt]` | A4 单栏 12pt；`frontmatter` 结构（title/author/affiliation/abstract/keyword）；`lineno` 正文行号；`\raggedbottom` | bibtex + `elsarticle-num` | 3 |
| en-journal-ieee | `IEEEtran[journal,10pt]` | 双栏 10pt；`\markboth` 页眉、`\thanks` 基金与单位、`IEEEkeywords`、`\appendices` 附录、作者简介留注释位 | bibtex + `IEEEtran` | 1 |
| en-ieee | `IEEEtran[conference]` | 双栏 10 pt，`\setmainfont{TeX Gyre Termes}` + `\setmathfont{TeX Gyre Termes Math}` | bibtex + `IEEEtran` | 1 |
| en-acm | `acmart[sigconf,nonacm]` | 双栏 9 pt，ACM 官方字体 Libertine，含 CCS 概念 | bibtex + `ACM-Reference-Format` | 1 |
| en-mcm | `article[12pt,letterpaper]` + `geometry[margin=1in]` | 全英文、单倍行距、1 in 边距；首页 Summary Sheet，25 页上限 | bibtex + `unsrt` | 4 |

需要代码块、算法伪代码、子图、跨页长表或图表按节编号时，看 `references/latex-blocks.md`，别自己拼宏包。

## 3. 选模板的判断顺序

1. 语种：中文 → cn-*；英文 → en-*
2. 用途：毕业论文 → cn-thesis；课程论文 → cn-course-paper；实验报告 → cn-lab-report；习题/作业 → cn-homework；数模国赛 → cn-cumcm；期刊投稿 → en-journal-els（Elsevier）/ en-journal-ieee（IEEE）；IEEE 会议 → en-ieee；ACM 投稿 → en-acm；美赛 → en-mcm
3. 学校/会议有硬性模板时，以对方要求为准，在副本上改，不动底稿。

## 4. 提交前必须替换的字段

**通用**

- [ ] 标题（`\title{}` 或标题区手写行）
- [ ] 作者、单位、邮箱、学号（IEEE 是 `\IEEEauthorblockA`，ACM 是 `\author` + `\affiliation`）
- [ ] 摘要里的占位句、关键词（`\keywords` / `IEEEkeywords`）
- [ ] 每个 `\section{}` 的标题与正文
- [ ] `refs.bib` 的示例文献（**务必删掉或替换**，别把占位文献投出去）
- [ ] 插图：模板无图，自己加 `\includegraphics[width=0.8\textwidth]{xxx.pdf}`
- [ ] 页眉页脚的课程名、队号、页码起始

**按模板**

| 模板 | 额外要改 |
|---|---|
| cn-thesis | 封面（学院/专业/班级/姓名/学号/指导教师/日期）、中英文摘要与关键词、各章标题、致谢、附录；图表按章编号不需要时删掉导言区 6 行 `\counterwithin`/`\thefigure` 重定义 |
| cn-course-paper | 摘要字数、页眉课程信息（如有） |
| cn-lab-report | `\labinfo{}` 四个参数、实验数据表数值（占位数据要换成真实测量值） |
| cn-cumcm | 摘要页（首页不编页码，正文从 1 起）、队号按当年规范、附录代码 |
| cn-homework | 班级、习题编号 |
| en-journal-els | `\journal{}` 期刊名、`\author`/`\affiliation`/`\cortext`、CRediT 与利益冲突声明、投稿系统要求的高亮（highlights）另附；交付排版稿时删 `\usepackage{lineno}` 与 `\linenumbers` |
| en-journal-ieee | `\markboth{}` 期刊名与卷期、`\thanks{}` 基金号与单位邮箱、`IEEEkeywords`、页数按目标 Transactions 限制、`\appendices` 按需保留 |
| en-ieee | `\IEEEauthorblockA` 单位与邮箱、`\IEEEkeywords` |
| en-acm | `\ccsdesc{}`、投稿时删 `nonacm` 并补 `\acmConference` / `\acmDOI` |
| en-mcm | Summary Sheet 的 Team Control Number、Problem Chosen（A–F）、Summary 正文 |

## 5. 格式依据与已知偏差

- **cn-cumcm**：组委会只发《论文格式规范》，**无官方 .cls**。本模板按 2023 修订版（2024–2025 沿用）手工实现：A4、四边 ≥2.5 cm、摘要页不编页码、正文阿拉伯数字从 1 起居中、题目三号黑体、一级标题四号黑体居中、正文小四宋体 1.5 倍行距、GB/T 7714 文献。偏差：未做官方「编号专用页/承诺书」版式（近年已不需要），行距取整与标题间距可能与官方 Word 版差 1–2 pt。
- **en-mcm**：COMAP 只提供 Word 版 Summary Sheet，无 .cls。首屏框线为手工绘制，与 Word 版线宽略有差异；12 pt、1 in 边距、25 页上限符合要求。
- **en-ieee**：IEEEtran 面向 pdfLaTeX，在 XeLaTeX 下不自动加载 Times，模板已手写 Termes；要求逐像素对齐官方时改用 pdflatex 编译（脚本固定 xelatex，需手动跑）。
- **en-acm**：`nonacm` 选项关闭了版权块与 DOI，属预览版；正式投稿要改成带 `\acmConference` 的完整配置。
- **cn-thesis**：ctexbook 下 `titlepage` 环境自带 `\newpage`，叠加 `\frontmatter` 的 `\clearpage` 会多出一张空白页，故封面改为 `\thispagestyle{empty}` + `center` 环境手写，再用 `\pagenumbering{Roman}` + `\setcounter{page}{0}` 实现「封面不计页码、摘要从 I 起、正文从 1 起」。参考文献的目录项必须挂在 natbib 的 `\bibsection` 里重定义，直接在 `\bibliography` 前写 `\cleardoublepage` + `\addcontentsline` 会多分一页并让目录页码错位。图表按章编号用 `\counterwithin` + `\thefigure` 六行实现，不需要时整段删掉即可回到全文连续编号。
- **en-journal-els**：`review` 选项只改行距，**不自动加行号**；需要行号必须 `\usepackage{lineno}` 并手动 `\linenumbers`，且 `\linenumbers` 要放在 `\end{frontmatter}` 之后，放前面会因标题区脚注触发 `Overfull \vbox`。另加 `\raggedbottom` 避免末页被拉满。
- **en-journal-ieee**：`IEEEtran[journal]` 在 XeLaTeX 下 `\IEEEPARstart` 会报 `Font ... not loadable`（下沉首字字体不可用），模板改用普通段首句；表格浮动用 `[h]`，用 `[t]` 会浮到 Abstract 上方。

## 6. 模板重建规格（底稿丢失时按此重建）

重建原则：每套目录下只需 `main.tex` + `refs.bib`；目录名 = 模板名；入口必须叫 `main.tex`（脚本按这个名字找）。每套都必须含：占位标题、作者、摘要/关键词、一节正文、一个公式（`equation`）、一张 `booktabs` 三线表、一条 `\cite` + 对应 bib 条目。重建后跑 `build.ps1 -All`，10 套全绿才算恢复。

`\swfontset` 由 `main.tex` 开头的 `\IfFileExists` 检测块决定：Windows→`windows`，macOS→`mac`，其他（Linux）→`fandol`（TeX Live 自带）。macOS / Linux 分支按 ctex 官方 fontset 名称写，未在 Windows 本机实测。

| 模板 | 骨架关键行 |
|---|---|
| cn-thesis | `\documentclass[UTF8,a4paper,zihao=-4,fontset=\swfontset,openany]{ctexbook}`；`geometry{top=2.54cm,bottom=2.54cm,left=3.0cm,right=3.0cm}`；`\linespread{1.5}`；封面用 `\thispagestyle{empty}`+`center`（**不要 `titlepage`**），后接 `\pagenumbering{Roman}`+`\setcounter{page}{0}`；`\renewcommand{\bibsection}{\chapter*{\bibname}\phantomsection\addcontentsline{toc}{chapter}{\bibname}}`；按章编号 6 行 `\counterwithin`+`\thefigure`；`\mainmatter` 起正文；`\appendix` 后 `\ctexset{chapter={name={附录,},number=\Alph{chapter}}}` |
| cn-course-paper | `\documentclass[UTF8,a4paper,zihao=-4,fontset=\swfontset]{ctexart}`；`geometry{top=2.54cm,bottom=2.54cm,left=3.17cm,right=3.17cm}`；`\linespread{1.5}`；`\pagestyle{plain}`；`\usepackage{gbt7714}`；`\bibliographystyle{gbt7714-numerical}` |
| cn-lab-report | 同上，另加 `siunitx`；`\newcommand{\labinfo}[4]{...}` 四参数表；`\ctexset{section={name={,、},number=\chinese{section},format=\zihao{4}\heiti}}` |
| cn-homework | 同上版式；`\usepackage[backend=biber,style=gb7714-2015]{biblatex}` + `\addbibresource{refs.bib}` + `\printbibliography[title={参考文献}]`；**不要** `\bibliographystyle` |
| cn-cumcm | `ctexart` 同上；`geometry{top=2.5cm,bottom=2.5cm,left=2.5cm,right=2.5cm}`；摘要页包 `\pagenumbering{gobble}` + `\thispagestyle{empty}`，`\newpage` 后 `\pagenumbering{arabic}`；`fancyhdr` 页脚居中页码；`\ctexset{section={format=\zihao{4}\heiti,format+={\centering}}}` 之类实现四号黑体居中 |
| en-journal-els | `\documentclass[preprint,review,12pt]{elsarticle}`；`fontspec`+`\setmainfont{TeX Gyre Termes}`；`\name`→`\title`/`\author[inst1]{...\corref{cor1}}`/`\cortext`/`\affiliation[instN]{organization=...,country=...}`/`abstract`/`keyword`；`\end{frontmatter}` **之后**才 `\linenumbers`（`lineno` 宏包）；`\raggedbottom`；`\bibliographystyle{elsarticle-num}` |
| en-journal-ieee | `\documentclass[journal,10pt]{IEEEtran}`；`\usepackage{cite}`；`fontspec`+Termes／`unicode-math`+Termes Math；三个 `\thanks{}`（收稿日期/基金/邮箱）；`\markboth{期刊名, Vol. 1, No. 1}{作者: 短标题}`；`IEEEkeywords`；**不用 `\IEEEPARstart`**（XeLaTeX 报字体不可用）；表格用 `[h]`；`\appendices`；`\bibliographystyle{IEEEtran}` |
| en-ieee | `\documentclass[conference]{IEEEtran}`；`\usepackage{cite}`；`fontspec` + `\setmainfont{TeX Gyre Termes}`；`unicode-math` + `\setmathfont{TeX Gyre Termes Math}`；`\bibliographystyle{IEEEtran}`；表格用 `[h]` 别用 `[!t]`（否则会浮到 Abstract 之前） |
| en-acm | `\documentclass[sigconf,nonacm]{acmart}`；`\settopmatter{printfolios=true,printacmref=false}`；`\begin{CCSXML}`+`\ccsdesc`；`\bibliographystyle{ACM-Reference-Format}`；字体不要手改（acmart 自动用 Libertine） |
| en-mcm | `\documentclass[12pt,letterpaper]{article}`；`\usepackage[margin=1in]{geometry}`；`fontspec` + `\setmainfont{Times New Roman}`；`unicode-math` + `\setmathfont{TeX Gyre Termes Math}`；首页 Summary Sheet 用 `tabular`（`\multicolumn` 必须是单元格第一个 token，`\rule` 要放进它的参数里）；`\bibliographystyle{unsrt}` |

`refs.bib` 最小可用条目（每套一份，改 key 和内容即可）：

```bibtex
@article{demo2026,
  author  = {Zhang, San and Li, Si},
  title   = {A Placeholder Reference for Template Testing},
  journal = {Journal of Placeholder Studies},
  year    = {2026},
  volume  = {1},
  number  = {1},
  pages   = {1--10}
}
```
