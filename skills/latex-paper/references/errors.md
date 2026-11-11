# 报错速查与排错

## 1. 排错三步

1. **看终端**：`build.ps1` 失败时会直接把 log 里所有 `!` 开头的行和 `main.tex:行号` 打出来，先看第一条。
2. **看 log 文件**：`output\<文件夹名>.log`（脚本已把这次的 main.log 复制过去），搜第一个 `!`，它下面的 `l.行号` 就是出错位置。
3. **复现**：加 `-KeepAux` 重跑，保留 `.aux/.bcf/.blg`，多数"第二次编译才好"的问题靠这些中间文件判断。

## 2. 常见报错对照表

| 报错 | 原因 | 解决 |
|---|---|---|
| `! Undefined control sequence.` | 用了没加载的宏包，或命令拼错 | 看 `l.行号`；补 `\usepackage{...}` 或改拼写 |
| `! LaTeX Error: File 'xxx.sty' not found.` | 宏包没装 | `tlmgr install xxx`（full scheme 一般都有，先 `kpsewhich xxx.sty` 确认） |
| `! Package fontspec Error: The font "SimSun" cannot be found.` | 字体名写错或系统没装 | 模板已按平台自动选字体；仍报错就显式写 `fontset=fandol`（TeX Live 自带），英文换 TeX Gyre 系列 |
| `! Missing $ inserted.` | 数学符号写在文本模式 | 加 `$...$`；检查 `_`、`^`、`&` 误用 |
| `! LaTeX Error: Something's wrong--perhaps a missing \item.` | 列表环境缺 `\item` | 检查 `itemize` / `enumerate` |
| `! LaTeX Error: \begin{table} on input line N ended by \end{document}.` | 环境没闭合 | 补 `\end{table}` |
| `! Argument of \xxx has an extra }.` | 花括号不配对 | 数括号 / 用编辑器括号匹配 |
| `! Misplaced \omit.` | `\multicolumn` 前有别的 token（常见于 `\rule` 写在它前面） | 把 `\rule{0pt}{2.2em}` 挪进 `\multicolumn` 的参数里，保证 `\multicolumn` 是单元格第一个 token |
| `! Package biblatex Error: File 'main.bbl' not created by biblatex.` | 之前用 bibtex 编过，残留 bbl | 删 `main.bbl`、`main.aux` 后重编（`-KeepAux` 时最容易遇到） |
| `I found no \citation commands` | 正文没有 `\cite` | 至少引用一次，否则文献表为空 |
| `I didn't find a database entry for "xxx"` | bib key 拼错或条目没写 | 对齐 `refs.bib` 里的 key |
| `! Package inputenc Error: Unicode character` | 用 pdflatex 编了中文 | 换 xelatex（本工作台脚本已固定） |
| 中文变方块 / 乱码 | 字体缺字，或文件不是 UTF-8 | 文件存 UTF-8；模板已按平台自动选字体，仍缺字就显式 `fontset=fandol`；生僻字换字体 |
| `! Dimension too large.` | 图片尺寸或 tikz 坐标超限 | 缩小 `width=`，检查坐标 |
| 参考文献显示 `[?]` | 少跑一轮，或没跑 bibtex/biber | 用 `build.ps1` 重编（脚本已跑 3 遍） |
| `Package hyperref Warning: Token not allowed in a PDF string` | 标题里有公式/命令 | 加 `\texorpdfstring{公式}{文字}` |
| 编译很慢 / 卡住 | 字体缓存坏了，或某包在联网 | `fc-cache -fv`；用 `-interaction=nonstopmode` 看卡在哪一行 |
| 脚本报「找不到 xelatex」 | PATH 没生效（新装的 TeX Live） | 重开终端；或先执行 `$env:Path='D:\texlive\2026\bin\windows;'+$env:Path` |

## 3. 环境检查

```powershell
# 四个工具是否都在
xelatex --version
latexmk --version
bibtex --version
biber --version

# 版本参考（本机实测）
# XeTeX 3.141592653-2.6-0.999998 (TeX Live 2026)
# Latexmk 4.88
# BibTeX 0.99e
# biber 2.22

# 宏包/文档类在哪
kpsewhich IEEEtran.cls
kpsewhich acmart.cls
kpsewhich gbt7714.sty
kpsewhich ctexart.cls
```

## 4. 常用命令

```powershell
# 装缺失宏包（full scheme 基本不需要）
tlmgr install <包名>

# 更新索引
tlmgr update --self

# 手动单车编译（脚本之外排错用）
xelatex -interaction=nonstopmode -file-line-error main.tex
biber main    # 或 bibtex main
xelatex -interaction=nonstopmode -file-line-error main.tex
xelatex -interaction=nonstopmode -file-line-error main.tex

# 刷新字体缓存（换字体后中文不显示时）
fc-cache -fv
```

## 5. 判断"能不能交付"

- 终端最后有 `[OK] 页数 N`，退出码 0。
- 全文没有 `!` 错误行；`Missing character` 计数为 0（中文缺字会在这里暴露）。
- `\cite` 显示阿拉伯数字而不是 `[?]`。
- 页数与 `references/templates.md` 的预期一致（差 1–2 页属正常，差很多通常是表格/图溢出）。
