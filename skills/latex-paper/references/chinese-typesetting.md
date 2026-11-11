# 中文排版设置（字号 / 页边距 / 行距 / 字体）

## 1. 本机中文字体

| 字体 | fontspec 字体名 | 可用 |
|---|---|---|
| 宋体 | SimSun | 有 |
| 黑体 | SimHei | 有 |
| 楷体 | KaiTi | 有 |
| 仿宋 | FangSong | 有 |
| 微软雅黑 | Microsoft YaHei | 有 |

中文模板统一 `\documentclass[...,fontset=\swfontset]{ctexart}`，`\swfontset` 由 `main.tex` 开头的 `\IfFileExists` 检测决定：Windows 用 `windows`，macOS 用 `mac`，其他（Linux）用 `fandol`（TeX Live 自带，不用另装字体）。ctex 会自动指定：正文宋体、标题黑体、`\kaishu` 楷体、`\fangsong` 仿宋，不用手写字体文件路径。**中文必须 XeLaTeX。**

## 2. 改字号

| 想改什么 | 改哪里 | 写法 |
|---|---|---|
| 全局正文字号 | `\documentclass[...]` 选项 | `zihao=-4`（小四，默认）/ `zihao=5`（五号）/ `zihao=4`（四号） |
| 局部字号 | 正文里直接写 | `{\zihao{3}\heiti 三号黑体}` |
| 公式字号 | 公式环境内 | `\small`、`\footnotesize` 包住或写在环境内 |

中文字号对照：`\zihao{3}` 三号 16pt、`\zihao{4}` 四号 14pt、`\zihao{-4}` 小四 12pt、`\zihao{5}` 五号 10.5pt。

## 3. 改页边距 / 行距 / 缩进

| 想改什么 | 改哪里 | 写法 |
|---|---|---|
| 页边距 | 导言区 | `\geometry{top=2.54cm,bottom=2.54cm,left=3.17cm,right=3.17cm}` |
| 行距 | 导言区 | `\linespread{1.5}`（1.5 倍，模板默认）；单倍写 `1.0` |
| 段首缩进 | 导言区 | `\setlength{\parindent}{2em}` |
| 段间距 | 导言区 | `\setlength{\parskip}{0pt}` |
| 页眉页脚距离 | `geometry` 选项 | `\geometry{headsep=0.6cm,footskip=1.2cm}` |

注意 `\linespread` 要在 `\begin{document}` 之前；ctex 会自己处理中西文混排行距，一般不用再改 `\baselineskip`。

## 4. 改标题样式与编号

```latex
% 一级标题：四号黑体居中
\ctexset{
  section = {
    format     = \zihao{4}\heiti\centering,
    name       = {,、},            % 编号后加「、」
    number     = \chinese{section} % 一、二、三
  },
  subsection = {format = \zihao{-4}\heiti}
}
```

| 想改什么 | 写法 |
|---|---|
| 章节编号变汉字 | `number = \chinese{section}`，配 `name = {,、}` → 「一、」 |
| 标题字号字体 | `format = \zihao{4}\heiti` |
| 标题居中 | `format = \zihao{4}\heiti\centering` |
| 图表标题 | `\captionsetup{font=small,labelsep=quad}`（`caption` 宏包） |
| 不要页眉只要页码 | `\pagestyle{plain}` |
| 自定义页脚居中页码 | `\pagestyle{fancy}` + `\fancyfoot[C]{\thepage}` |
| 某页不要页码 | `\thispagestyle{empty}` |
| 某段重新从 1 编页 | `\pagenumbering{arabic}`（CUMCM 摘要页用 `\pagenumbering{gobble}` 关掉） |

## 5. 常用宏包

| 宏包 | 用途 | 备注 |
|---|---|---|
| `ctex` / `ctexart` | 中文排版 | 必须 XeLaTeX + 自动判断的 `fontset`（`windows` / `mac` / `fandol`） |
| `geometry` | 页边距 | 见上表 |
| `amsmath` / `amssymb` / `bm` | 公式 | `equation`、`align`、`cases`、`\bm{}` 粗体向量 |
| `booktabs` | 三线表 | `\toprule` `\midrule` `\bottomrule`，不要竖线 |
| `array` / `multirow` | 表格列格式与合并 | `\multirow{2}{*}{内容}` |
| `graphicx` | 插图 | `\includegraphics[width=0.8\textwidth]{fig.pdf}` |
| `caption` | 图表标题 | `\captionsetup{font=small,labelsep=quad}` |
| `enumitem` | 列表 | `\begin{enumerate}[label=（\arabic*）]` |
| `siunitx` | 单位 | `\SI{12}{\volt}`、`\si{\kilo\ohm}` |
| `fancyhdr` | 页眉页脚 | `\fancyfoot[C]{\thepage}` |
| `hyperref` | 超链接/书签 | 放最后加载，`[hidelinks]` 去红框 |
| `gbt7714` | 国标文献（bibtex） | `\bibliographystyle{gbt7714-numerical}` |
| `biblatex`+`style=gb7714-2015` | 国标文献（biber） | `backend=biber` + `\printbibliography` |

**进阶块**（代码块、算法伪代码、子图、跨页长表、图表按章/节编号）不要自己拼宏包，直接照抄 `references/latex-blocks.md` 里的导言区设置与正文写法。要点：

- 代码：`listings` + `\lstset{...}`，中文标题用 `\renewcommand{\lstlistingname}{代码}`。
- 算法：`algorithm2e[ruled,linesnumbered]` + `\SetAlgorithmName{算法}{算法}{算法列表}`。
- 子图：`subcaption`（与 `subfig`/`subfigure` 互斥），`subfigure` 宽 0.45 配 `\hfill`。
- 跨页长表：`longtable`，必须写 `\endfirsthead` / `\endhead` / `\endfoot` 三段，且不能放进 `table` 环境。
- 按章编号：`\counterwithin{figure}{chapter}` + `\renewcommand{\thefigure}{\thechapter-\arabic{figure}}`（表、公式同理）；按节编号用 `\numberwithin{figure}{section}`。
- 加载顺序：`caption`/`subcaption` 必须在 `hyperref` **之前**。

## 6. 中文文献两种写法（别混用）

```latex
% A. bibtex（cn-course-paper / cn-lab-report / cn-cumcm）
\usepackage{gbt7714}
\bibliographystyle{gbt7714-numerical}   % 顺序编码制；著者-出版年制写 gbt7714-author-year
\bibliography{refs}

% B. biber（cn-homework）
\usepackage[backend=biber,style=gb7714-2015]{biblatex}
\addbibresource{refs.bib}
\printbibliography[title={参考文献}]
```

同一份文档里不要既 `\bibliographystyle` 又 `\printbibliography`，会报 bbl 不是 biblatex 生成。

## 7. 中文常见坑

- 文件必须存 **UTF-8**，GBK 存的中文在 XeLaTeX 下直接乱码。
- 生僻字（人名、地名）可能缺字，编译日志出现 `Missing character`：换字体或改用图片。
- 中文标点用全角，`~` 写不换行空格，`\%` 转义百分号。
- 中英混排的数字、单位建议用半角，中间加空格更规范（`12 V`）。
