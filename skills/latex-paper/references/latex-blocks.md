# 可选功能块（代码 / 算法 / 子图 / 长表 / 按节编号）

四套中文模板（cn-course-paper、cn-lab-report、cn-homework、cn-cumcm）默认只有正文、公式、三线表。下面五块按需复制到自己的作业副本里，**不要一次全开**，用不到就不加，编译更快、排版更干净。

每块都已在 TeX Live 2026 + XeLaTeX 下验证通过。

## 1. 代码块（listings）

导言区加：

```latex
\usepackage{listings}
\lstset{
  basicstyle   = \ttfamily\small,
  breaklines   = true,          % 长行自动折行
  frame        = single,
  numbers      = left,          % 左侧行号
  numberstyle  = \tiny,
  columns      = fullflexible,  % 避免中文/等宽字距被拉散
  keepspaces   = true,
  showstringspaces = false,
  tabsize      = 2
}
\renewcommand{\lstlistingname}{代码}   % 标题变成「代码 1」而不是 Listing 1
```

正文里两种写法：

```latex
% 写法 A：直接贴代码（短片段）
\begin{lstlisting}[language=Python,caption={核心迭代代码},label={lst:code}]
def f(x):
    return x ** 2   # 中文注释可以正常显示
\end{lstlisting}
% 引用：见代码~\ref{lst:code}

% 写法 B：引用外部源文件（长代码推荐，别把几百行贴进 .tex）
\lstinputlisting[language=C,caption={主程序},label={lst:main}]{code/main.c}
```

坑：代码里的中文注释要保证 `.tex` 是 UTF-8；`language=Python` 只影响关键字高亮，不加也能编译。

## 2. 算法伪代码（algorithm2e）

导言区加（**必须带 `ruled`**，否则标题跑到算法下方）：

```latex
\usepackage[ruled,linesnumbered]{algorithm2e}
\SetAlgorithmName{算法}{算法}{算法列表}
\SetKwInput{KwIn}{输入}
\SetKwInput{KwOut}{输出}
\SetKw{KwTo}{到}
```

正文里：

```latex
\begin{algorithm}[htbp]
  \caption{贪心分配算法}
  \KwIn{需求数组 $A$，长度 $n$}
  \KwOut{最大值 $m$}
  $m \leftarrow A_1$\;
  \For{$i \leftarrow 2$ \KwTo $n$}{
    \If{$A_i > m$}{$m \leftarrow A_i$\;}
  }
  \Return $m$\;
\end{algorithm}
```

坑：每行结尾的 `\;` 不能漏，漏了就不换行；`\For`、`\If` 必须用 algorithm2e 的写法，不能写 LaTeX 的 `\for`。

## 3. 子图（subcaption）

导言区加（`subcaption` 会自己加载 `caption`，不必重复加载）：

```latex
\usepackage{subcaption}
```

正文里：

```latex
\begin{figure}[htbp]
  \centering
  \begin{subfigure}{0.45\textwidth}
    \centering
    \includegraphics[width=\linewidth]{figs/a.pdf}
    \caption{原始信号}
    \label{fig:sub-a}
  \end{subfigure}\hfill
  \begin{subfigure}{0.45\textwidth}
    \centering
    \includegraphics[width=\linewidth]{figs/b.pdf}
    \caption{滤波后信号}
    \label{fig:sub-b}
  \end{subfigure}
  \caption{滤波前后对比}
  \label{fig:compare}
\end{figure}
```

两个子图宽度之和要小于 `\textwidth`（`0.45+0.45` 加 `\hfill` 刚好），别写 `0.5+0.5`，否则会溢出换行。想要中文括号编号「（a）」，加一行 `\renewcommand{\thesubfigure}{（\alph{subfigure}）}`（xeCJK 会在括号内侧留一点空隙，属正常）。

## 4. 跨页长表（longtable）

导言区加（长表**不能**放进 `table` 浮动体）：

```latex
\usepackage{longtable}
```

正文里：

```latex
\begin{longtable}{lcc}
  \caption{全部测量数据}\label{tab:all}\\
  \toprule
  序号 & 测量值 & 备注 \\
  \midrule
  \endfirsthead
  \multicolumn{3}{l}{续表~\thetable}\\
  \toprule
  序号 & 测量值 & 备注 \\
  \midrule
  \endhead
  \bottomrule
  \endfoot
  1 & 1.02 & 说明 \\
  2 & 2.05 & 说明 \\
  % ……更多行，自动跨页
\end{longtable}
```

`\endfirsthead` 之前是首页表头，`\endhead` 之前是后续页表头，`\endfoot` 之前是每页表尾。三段都要有，否则续页没有表头。

## 5. 图表公式按章/节编号

课程论文一般是全文连续编号（图 1、图 2），毕业论文和长报告才按章编号。

```latex
% 按节编号（ctexart 没有 chapter，用 section）：图 1.1、表 2.3、式 (3.2)
\numberwithin{figure}{section}
\numberwithin{table}{section}
\numberwithin{equation}{section}

% 按章编号（只对 ctexbook / cn-thesis 有意义）：图 1-1、表 2-1、式 (3-1)
\numberwithin{figure}{chapter}
\numberwithin{table}{chapter}
\numberwithin{equation}{chapter}
\renewcommand{\thefigure}{\thechapter-\arabic{figure}}
\renewcommand{\thetable}{\thechapter-\arabic{table}}
\renewcommand{\theequation}{\thechapter-\arabic{equation}}
```

`\numberwithin` 由 `amsmath` 提供，四套中文模板都已加载 `amsmath`，直接用即可。切换编号后记得重跑两遍编译，交叉引用才会更新。

## 6. 顺序与冲突

- 宏包加载顺序：`caption`（或 `subcaption`）放在 `hyperref` 之前；`algorithm2e` 放在 `hyperref` 之前。
- `subcaption` 与 `subfig`、`subfigure` 三个包**只能选一个**，同时加载必报错。
- `longtable` 不能包在 `table` 环境里，也不能用 `[htbp]` 浮动参数。
- 加了 `listings` 后如果正文里到处是 `\lstinline`，注意 `listings` 会改变 `\texttt` 的字距，介意的话改用 `\verb`。
