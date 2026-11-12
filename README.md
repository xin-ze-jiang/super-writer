# super-writer

给主流 AI 编程工具用的一组技能：LaTeX 论文排版、赛级 PPT 生成、中文 AI 绘画提示词、坐标纸出图。每个技能都是自包含目录，复制进去就能用。

宣传页（GitHub Pages）：<https://xin-ze-jiang.github.io/super-writer/>

## 1. 仓库是什么

| 技能 | 干什么 | 依赖 | 产物形式 |
|---|---|---|---|
| [latex-paper](skills/latex-paper/) | LaTeX 论文排版。10 套现成模板：中文课程论文、实验报告、作业、数模国赛、本科毕业论文、IEEE/ACM 会议、美赛、Elsevier 期刊、IEEE 期刊；一条命令跑完 XeLaTeX + bibtex/biber | TeX Live（`xelatex`/`bibtex`/`biber` 在 PATH）、PowerShell 5.1+ | PDF（+ 编译日志 `.log`） |
| [sj-ppt](skills/sj-ppt/) | 赛级 PPT 生产线。一份 `deck.json` 同时生成单文件 HTML 演示版和可编辑 `.pptx` | Node.js 18+；生成 pptx 另需 Python 3.8+ 与 `python-pptx`、`lxml` | `out/index.html` + `out/*.pptx` |
| [promptlab](skills/promptlab/) | 中文 AI 绘画提示词工坊。七段式写提示词、用锚点保证系列图一致，自带自检脚本 | Python 3.8+（只用标准库） | 提示词文本 + 设定卡（对话内交付） |
| [coordinate-plot](skills/coordinate-plot/) | 坐标纸出图。把实验数据画成 1mm 真实毫米格的曲线图，供打印后手绘；支持折线/平滑/线性拟合/散点、上下 1~2 子图、黑白打印 | Python 3.8+、`matplotlib` | 300dpi PNG |

四个技能互不依赖，可以只装其中一个。

## 2. 安装

技能目录位置：Claude Code 是 `~/.claude/skills/`（Windows 为 `%USERPROFILE%\.claude\skills\`）。下面命令按 Claude Code 写；Cursor、Cline、Gemini CLI、Copilot、Windsurf、Codex、DeepSeek、Trae 的路径见第 3 节对照表，把目录换掉即可。

### 方式 A：git clone（推荐，方便更新）

```bash
git clone https://github.com/xin-ze-jiang/super-writer.git
cd super-writer
```

克隆下来只是仓库，还要按方式 C 把技能目录复制进 AI 工具的技能目录。

### 方式 B：下载 ZIP 解压

在仓库页面点 `Code` → `Download ZIP`，解压到一个固定目录（比如 `D:\tools\super-writer`）。之后同样按方式 C 复制。

### 方式 C：复制技能目录（真正的安装动作）

单个技能：

```powershell
# Windows PowerShell
Copy-Item -Recurse .\skills\latex-paper "$HOME\.claude\skills\"
```

```bash
# macOS / Linux
mkdir -p ~/.claude/skills
cp -R skills/latex-paper ~/.claude/skills/
```

四个都装：

```powershell
# Windows
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
'latex-paper','sj-ppt','promptlab','coordinate-plot' | ForEach-Object {
  Copy-Item -Recurse ".\skills\$_" "$HOME\.claude\skills\" -Force
}
```

```bash
# macOS / Linux
mkdir -p ~/.claude/skills
cp -R skills/latex-paper skills/sj-ppt skills/promptlab skills/coordinate-plot ~/.claude/skills/
```

装完检查一下（`SKILL.md` 必须直接在技能目录根下，不能多套一层）：

```powershell
Get-ChildItem "$HOME\.claude\skills\latex-paper"
# 期望看到：SKILL.md  templates  scripts  references
```

技能在**新建对话**时扫描加载，装完需要开个新对话才生效。

## 3. 跨工具安装（Claude Code / Cursor / Codex / Cline / Gemini / Copilot / Windsurf / DeepSeek）

super-writer 的技能就是标准 `SKILL.md` 目录：Claude Code、DeepSeek Harness、Trae、Cursor、Cline、Gemini CLI、GitHub Copilot、Windsurf 都能直接读，安装动作就是把整个技能目录复制到对应位置（`scripts/`、`templates/`、`references/` 一起带走）。OpenAI Codex CLI 以 `AGENTS.md` 为主，脚本会额外追加索引并把技能放到 `~/.agents/skills/`（多工具共用目录）。DeepSeek Harness 与 Codex 共用 `~/.agents/skills/`，装一份即可，脚本会自动去重。

一条命令装完：

```powershell
# Windows（在仓库根目录执行）
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Target auto
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Target all
```

```bash
# macOS / Linux
./install.sh --target auto          # 只装本机检测到的工具
./install.sh --target all           # 全装，缺目录就创建
./install.sh --target claude,cursor # 指定多个
```

`-Target` / `--target` 取值：`all`、`auto`（默认）、`claude`、`trae`、`cursor`、`codex`、`cline`、`gemini`、`copilot`、`windsurf`、`deepseek`。`auto` 按配置目录是否存在判断，会打印装到哪、跳过哪些；重复执行原地覆盖，不产生重复目录；`output/`、`out/`、`__pycache__/` 等本地产物不会被复制。

| 工具 | 安装路径（用户级） | 方式 | 脚本还是手动 |
|---|---|---|---|
| Trae | `~/.trae-cn/skills/<技能名>/`（国际版 `~/.trae/skills/`） | 复制整个技能目录 | 脚本 |
| Claude Code | `~/.claude/skills/<技能名>/` | 复制整个技能目录 | 脚本 |
| Cursor | `~/.cursor/skills/<技能名>/` | 复制整个技能目录 | 脚本 |
| Codex CLI | `~/.agents/skills/<技能名>/` + 追加 `~/.codex/AGENTS.md` | 复制目录 + 单文件索引 | 脚本 |
| Cline | `~/.cline/skills/<技能名>/` | 复制整个技能目录 | 脚本 |
| Gemini CLI | `~/.gemini/skills/<技能名>/` | 复制整个技能目录 | 脚本 |
| GitHub Copilot | `~/.copilot/skills/<技能名>/` | 复制整个技能目录 | 脚本 |
| Windsurf | `~/.codeium/windsurf/skills/<技能名>/` | 复制整个技能目录 | 脚本 |
| DeepSeek Harness | `~/.agents/skills/<技能名>/`（与 Codex 共用，装一份即可） | 复制整个技能目录 | 脚本 |

项目级（只对当前仓库生效）需要手动放单文件规则，文件在 `adapters/`：

| 工具 | 放哪 | 文件 |
|---|---|---|
| Cursor Rules | `.cursor/rules/` | `adapters/cursor/super-writer.mdc`（必须是 `.mdc`） |
| Codex / 通用 | 项目根 `AGENTS.md` | `adapters/codex/AGENTS.md`（Cline / Copilot / Windsurf / Gemini 也读） |
| Cline Rules | `.clinerules/` 或 `.cline/rules/` | `adapters/cline/super-writer.md` |
| Gemini CLI | 项目根 `GEMINI.md` | `adapters/gemini/GEMINI.md` |
| GitHub Copilot | `.github/copilot-instructions.md`、`.github/instructions/` | `adapters/copilot/` 下两个位置各放对应文件 |
| Windsurf | `.windsurf/rules/` | `adapters/windsurf/rules-snippet.md` |

`adapters/` 里的内容不是第二份正文，而是从 `skills/*/SKILL.md` 提取「何时用 / 关键命令 / 产物」生成的索引。改完技能后刷新：

```bash
python scripts/gen-adapters.py           # 重新生成 adapters/
python scripts/gen-adapters.py --check   # 只检查是否过期
```

各工具路径、frontmatter 要求与查证来源见 [docs/cross-tool-support.md](docs/cross-tool-support.md)（查证日期 2026-11-10）。

## 4. 怎么被触发

### 自动命中

技能靠 `SKILL.md` 的 `description` 匹配，用日常说法说话就行：

| 你会怎么说 | 命中的技能 |
|---|---|
| 把实验报告排成 PDF / 帮我排一篇课程论文 / 这份 LaTeX 报 Undefined control sequence / 页边距改成 2.5 cm / 毕业论文模板 | latex-paper |
| 做个 4 页汇报 PPT / 大创答辩 PPT / 要能动又有 pptx 版本 / 这组数据做成柱状图页 | sj-ppt |
| 帮我改这段提示词 / 写个即梦提示词 / 角色三视图要长得一样 / 绘本分镜 | promptlab |
| 这组数据画成坐标纸 / 毫米方格图打印出来手绘 / 实验数据出图要能照着描 | coordinate-plot |

### 手动指定

在对话里直接输入斜杠命令，强制走对应技能：

```
/latex-paper
/sj-ppt
/promptlab
/coordinate-plot
```

## 5. 每个技能怎么用

### 5.1 latex-paper

**能做什么**：选题材 → 复制模板 → 改 `main.tex` 和 `refs.bib` → 一键编译出 PDF；顺带排查 LaTeX 报错、改字号/页边距/行距/参考文献样式。

**最小可用命令**（`$Skill` 指技能安装目录）：

```powershell
$Skill = Join-Path $HOME '.claude\skills\latex-paper'

# 1) 自检：编译全部 10 套模板，看谁报错
powershell -NoProfile -ExecutionPolicy Bypass -File "$Skill\scripts\build.ps1" -All -Parse

# 2) 编译某一套模板
powershell -NoProfile -ExecutionPolicy Bypass -File "$Skill\scripts\build.ps1" cn-cumcm -Parse

# 3) 编译自己的作业目录（目录里要有 main.tex 和 refs.bib）
powershell -NoProfile -ExecutionPolicy Bypass -File "$Skill\scripts\build.ps1" 'D:\作业\数模国赛_2026' -Parse
```

**产物**：`$Skill\output\<文件夹名>.pdf`，同时留一份 `<文件夹名>.log`。传目录时「文件夹名」就是你的作业目录名，所以目录名起得有意义一点（`数模国赛_2026` 而不是 `新建文件夹`）。`-KeepAux` 可保留中间文件，`-Parse` 把日志里的报错翻成「文件:行号: 说明」。

**需要你提供**：题材（中文/英文、课程论文/竞赛/毕业论文/投稿）、学校或会议的格式要求（有就发，没有用模板默认）、正文与数据、参考文献条目。

### 5.2 sj-ppt

**能做什么**：把内容写进一个 `deck.json`，生成两版交付：单文件 HTML（可直接全屏演示、带动效）和可编辑 `.pptx`（老师能打开改）。内置 5 套赛级风格和静态检查脚本。

**最小可用命令**（在技能目录下执行）：

```powershell
cd "$HOME\.claude\skills\sj-ppt"

# 生成 HTML（先用自带的示例 deck.json 试跑）
node scripts/build_html.mjs examples/deck.json out/index.html

# 生成 PPTX
python scripts/build_pptx.py examples/deck.json out/deck.pptx

# 静态检查：溢出、缺字段、字号过小等
node scripts/check.mjs out/index.html
```

生成 pptx 前装依赖：

```bash
pip install python-pptx lxml
```

**产物**：`out/index.html`、`out/deck.pptx`（都在技能目录的 `out/` 下，也可以把输出路径指到你自己的目录）。

**需要你提供**：场合、页数、汇报时长、有没有学校模板或校徽、风格取向；以及每页的真实数据和文案（缺的页脚本会用占位，交付时会标出来）。

### 5.3 promptlab

**能做什么**：按「主体 → 动作与构图 → 镜头 → 光线 → 材质风格 → 氛围 → 画幅」七段式写中文提示词，先定一致性锚点（角色卡/世界卡），再逐页只改变化部分；自带自检脚本查空话、维度冲突、画幅缺失。

**最小可用命令**：

```powershell
cd "$HOME\.claude\skills\promptlab"

# 直接查一段提示词
python scripts/check_prompt.py -p "黄昏的旧书店，木质书架，暖黄灯光，胶片质感，画幅 3:4"

# 从文件读、批量读（每行一条）、指定语言
python scripts/check_prompt.py -f prompt.txt
python scripts/check_prompt.py -b batch.txt
python scripts/check_prompt.py --lang zh < prompt.txt
```

**产物**：提示词文本、角色设定卡、世界设定卡、分镜表，直接在对话里交付，不写文件；自检结果打印在终端（`可提交` / 需要改的具体问题）。

**需要你提供**：画幅（竖版 3:4 / 方图 1:1 / 横版 16:9）、目标工具（默认即梦）、数量（单图 / 系列几张 / 绘本几页），以及主体是谁、在做什么。

### 5.4 coordinate-plot

**能做什么**：把实验数据画成物理尺寸真实的毫米方格纸图（1mm 细格 / 5mm 中格 / 10mm 粗格），打印后照着数格子往纸质坐标纸上抄。四种画法：折线直连 / 平滑曲线 / 线性拟合（标斜率、截距、R²）/ 只画散点；支持上下 1~2 个子图、多列叠画、中文轴标签与单位、黑白打印优先，默认 300dpi PNG。

**最小可用命令**（`$Skill` 指技能安装目录）：

```bash
cd "$HOME/.claude/skills/coordinate-plot"
python scripts/plot.py --csv examples/demo_spring.csv --x 0 --y 1 --mode fit --out 弹簧.png
```

Windows 也可以直接双击 `examples\run_example.bat`，示例图输出到 `output\`。macOS / Linux 没有 `.bat`，跑上面的 `python` 命令即可。

**产物**：PNG（省略 `--out` 时落在 CSV 同目录）。

**需要你提供**：数据文件、x/y 各是哪一列、要不要拟合线、几个子图、坐标轴范围与每大格代表多少、轴标签（含单位）。

## 6. 依赖与安装

| 依赖 | 版本 | 用在哪 | 缺了会怎样 |
|---|---|---|---|
| TeX Live | 2026 full scheme | latex-paper | 编译直接失败：`xelatex: 无法将...识别为 cmdlet`。装完整版，别用 MiKTeX 替代 |
| `xelatex` / `bibtex` / `biber` 在 PATH | 随 TeX Live | latex-paper | 装了 TeX Live 但没进 PATH 同样报找不到命令（Windows 默认路径形如 `D:\texlive\2026\bin\windows`） |
| PowerShell | 5.1+ | latex-paper 的 `build.ps1` | 脚本跑不起来。macOS/Linux 需装 `pwsh`，或改用第 7 节的手动编译命令 |
| Node.js | 18+ | sj-ppt 生成 HTML | `node: command not found`；`build_html.mjs` 用 ESM，低于 18 会报语法错 |
| Python | 3.8+ | sj-ppt 生成 pptx；promptlab 自检；coordinate-plot 出图 | 脚本无法启动 |
| `python-pptx`、`lxml` | 最新 | sj-ppt 生成 pptx | `ModuleNotFoundError: No module named 'pptx'`。pip 装即可 |
| `matplotlib` | 3.5+ | coordinate-plot 出图 | `ModuleNotFoundError: No module named 'matplotlib'`；`pip install matplotlib` 即可，中文缺字会变方块并打印 `[warn]` |

PATH 临时补法（不想改系统环境变量时，当前窗口有效）：

```powershell
$env:PATH = 'D:\texlive\2026\bin\windows;' + $env:PATH
```

## 7. 不用技能也能用

模板就是普通 `.tex` 文件，不装技能、不经过 AI 也能编译：

```powershell
# 把模板复制到自己的工作目录
Copy-Item -Recurse .\skills\latex-paper\templates\cn-course-paper 'D:\论文\课程论文' -Force

# 在模板目录里手动跑四遍（XeLaTeX 需要两遍以上才收敛交叉引用）
cd 'D:\论文\课程论文'
xelatex main.tex
bibtex main        # cn-homework 用 biber main
xelatex main.tex
xelatex main.tex
```

`main.pdf` 就是成品。目录里还需要有 `refs.bib`，缺了参考文献会显示 `[?]`。

sj-ppt 的两个脚本也是普通命令行程序，`node scripts/build_html.mjs 你的deck.json 输出.html` 即可，不必经过对话。promptlab 的 `check_prompt.py`、coordinate-plot 的 `scripts/plot.py` 同样可以单独跑。

## 8. 更新方式

技能不会被自动同步，更新要手动做两步：

```powershell
# 1) 拉最新代码
cd D:\tools\super-writer
git pull

# 2) 重新覆盖复制一次（Windows 用 robocopy，/E 表示含子目录，会覆盖旧文件）
robocopy .\skills\latex-paper     "$HOME\.claude\skills\latex-paper"     /E
robocopy .\skills\sj-ppt          "$HOME\.claude\skills\sj-ppt"          /E
robocopy .\skills\promptlab       "$HOME\.claude\skills\promptlab"       /E
robocopy .\skills\coordinate-plot "$HOME\.claude\skills\coordinate-plot" /E
```

```bash
# macOS / Linux
cd ~/tools/super-writer && git pull
cp -Rf skills/latex-paper skills/sj-ppt skills/promptlab skills/coordinate-plot ~/.claude/skills/
```

复制完开新对话生效。注意 `cp -R` 不会删掉旧版本里已删除的文件，要彻底干净就先删技能目录再复制。

## 9. 常见坑

| 现象 | 原因 | 处理 |
|---|---|---|
| 技能装了但完全不生效 | 多套了一层目录，比如 `skills/latex-paper/latex-paper/SKILL.md` | `SKILL.md` 必须在技能目录根；目录名要与 `SKILL.md` 里的 `name` 一致（`latex-paper` / `sj-ppt` / `promptlab` / `coordinate-plot`） |
| `xelatex: 无法将...识别为 cmdlet` | TeX Live 的 bin 目录没进 PATH | 用第 5 节的 `$env:PATH` 临时补，或把 `D:\texlive\2026\bin\windows` 加进系统环境变量 |
| 编译报 `Font "SimSun" not found` 之类 | 模板字体集已按平台自动判断（Windows→`windows`，macOS→`mac`，其他→`fandol`），正常不会出现 | 已自动判断，无需手动改；若仍报错，多半是系统缺字体或自己改过 `main.tex` 开头的检测块，可显式写 `fontset=fandol`（TeX Live 自带） |
| 中文全是乱码或 `Missing character` | `.tex` 存成了 GBK | 统一存 UTF-8（无 BOM）；`.ps1` 脚本相反，要 UTF-8 **带 BOM** |
| 参考文献显示 `[?]` | 没跑 bibtex/biber，或 `refs.bib` 里没有对应 key | 按第 6 节顺序跑四遍；检查 `\cite{}` 的 key 与 bib 条目一致 |
| `build.ps1` 报脚本无法加载 | 执行策略限制 | 调用时带 `-ExecutionPolicy Bypass`，或 `Set-ExecutionPolicy -Scope Process Bypass` |
| `deck.json` 读取报 JSON 解析错误 | 文件带 BOM 或被存成 GBK | 用 UTF-8（推荐无 BOM）保存；改完 JSON 要重跑两个脚本，别手改 HTML/PPTX |
| pptx 打开提示「需要修复」 | 未按流程生成，或手动改过 pptx | 只改 `deck.json` 再重新生成 |
| 页数/交叉引用不对 | XeLaTeX 只跑了一遍 | 至少 `xelatex` 跑两遍（脚本已自动跑三遍） |

## 10. 目录结构

```
super-writer/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ install.ps1                 # Windows 一键安装
├─ install.sh                  # macOS / Linux 一键安装
├─ adapters/                   # 由 SKILL.md 生成的各工具规则文件（勿手改）
│  ├─ cursor/super-writer.mdc
│  ├─ codex/AGENTS.md
│  ├─ cline/super-writer.md
│  ├─ gemini/GEMINI.md
│  ├─ copilot/copilot-instructions.md + instructions/
│  └─ windsurf/rules-snippet.md
├─ docs/cross-tool-support.md  # 各工具路径与格式核实结论（2026-11-10）
├─ scripts/gen-adapters.py     # 从 SKILL.md 刷新 adapters/
└─ skills/
   ├─ latex-paper/
   │  ├─ SKILL.md
   │  ├─ references/          # 模板选择、报错排查、中文排版、英文字体、进阶块
   │  ├─ templates/           # 10 套模板，每套 main.tex + refs.bib
   │  └─ scripts/             # build.ps1、parse_log.ps1
   ├─ sj-ppt/
   │  ├─ SKILL.md
   │  ├─ scripts/             # build_html.mjs、build_pptx.py、check.mjs
   │  └─ examples/            # deck.json 示例
   ├─ promptlab/
   │  ├─ SKILL.md
   │  ├─ USAGE.md
   │  ├─ references/          # 电影感、一致性、方法、动效、视觉词库
   │  ├─ templates/           # 角色 / 场景 / 绘本 / 3D 四类设定卡
   │  ├─ scripts/check_prompt.py
   │  └─ examples/
   └─ coordinate-plot/
      ├─ SKILL.md
      ├─ scripts/plot.py      # 出图主程序（matplotlib）
      └─ examples/            # demo_spring.csv、demo_rtd.csv、run_example.bat（Windows）
```

编译与生成产物（`output/`、`out/`、`*.pdf`、`*.aux`、`__pycache__/` 等）已写入 `.gitignore`，不会进仓库。

## 11. 许可

MIT，见 [LICENSE](LICENSE)。
