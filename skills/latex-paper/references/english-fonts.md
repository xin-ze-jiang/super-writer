# 英文模板字体

五套英文模板的字体已经配好，改之前先看这张表。

| 模板 | 正文 | 公式 | 说明 |
|---|---|---|---|
| en-journal-els | TeX Gyre Termes | TeX Gyre Termes Math | `elsarticle` 默认用 Computer Modern；要贴近 Elsevier 的 Times 风格必须手写 `\setmainfont` + `\setmathfont` |
| en-journal-ieee | TeX Gyre Termes | TeX Gyre Termes Math | 与 en-ieee 同：IEEEtran 在 XeLaTeX 下不会自动加载 Times，必须手写 |
| en-ieee | TeX Gyre Termes | TeX Gyre Termes Math | IEEEtran 面向 pdfLaTeX，在 XeLaTeX 下**不会**自动加载 Times；模板已手写 `\setmainfont` + `\setmathfont` |
| en-acm | Libertine（acmart 默认） | Libertine Math | acmart 自动选字体，**不要手改**，改了就与 ACM 模板不一致 |
| en-mcm | Times New Roman | TeX Gyre Termes Math | COMAP 要求 Times；系统没有 Times 时改成 `\setmainfont{TeX Gyre Termes}` |

## 对应的导言区写法

```latex
% en-ieee（IEEEtran + XeLaTeX）
\usepackage{cite}
\usepackage{amsmath}
\usepackage{fontspec}
\setmainfont{TeX Gyre Termes}          % Times 的度量兼容克隆
\usepackage{unicode-math}
\setmathfont{TeX Gyre Termes Math}
\usepackage{amsfonts}
```

```latex
% en-mcm（article + Times）
\usepackage{fontspec}
\setmainfont{Times New Roman}
\usepackage{amsmath}
\usepackage{unicode-math}
\setmathfont{TeX Gyre Termes Math}     % 不设的话公式是 Computer Modern，和 Times 正文明显不搭
```

```latex
% en-journal-els（elsarticle + XeLaTeX）
\usepackage{amsmath}
\usepackage{fontspec}
\setmainfont{TeX Gyre Termes}
\usepackage{unicode-math}
\setmathfont{TeX Gyre Termes Math}
```

acmart 不需要任何字体设置，`\documentclass[sigconf,...]{acmart}` 自动用 Libertine + Libertine Math。

## 换字体的规矩

1. 只改 `\setmainfont{字体名}` 一行，字体名必须是系统里真实存在的名字（Windows「字体设置」里看到的名字）。
2. 用了 `unicode-math` 后**不要**再 `\usepackage{amssymb}`，符号会冲突；`\mathbb`、`\mathcal` 由 unicode-math 提供。
3. 换正文不换公式会中西不搭，公式跟着改 `\setmathfont`。
4. 常用可选字体：`TeX Gyre Termes`（Times 风格）、`TeX Gyre Pagella`（Palatino 风格）、`TeX Gyre Heros`（Helvetica 风格）、`Latin Modern Roman`（LaTeX 默认）。

## 英文排版要点

- 双栏模板（IEEE / ACM）表格用 `[h]` 或 `[!t]` 要谨慎：`[!t]` 会把表推到第一栏顶部、跑到 Abstract 前面，模板里已改 `[h]`。
- 英文论文的摘要、关键词字段名各模板不同：IEEE 用 `abstract` + `IEEEkeywords`，ACM 用 `abstract` + `CCSXML/\ccsdesc` + `\keywords`，MCM 用 Summary Sheet 表格。
- 参考文献样式已经写死在各自模板里（`IEEEtran` / `ACM-Reference-Format` / `unsrt`），换样式会导致与会议要求不符。
