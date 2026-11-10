# Trae Skills 合集

三个自制的 Trae 技能，围绕「写论文 / 做 PPT / 写绘图提示词」三件日常事。每个技能都是自包含目录，装进 Trae 的技能目录就能用。

## 1. 仓库是什么

| 技能 | 干什么 | 依赖 | 产物形式 |
|---|---|---|---|
| [latex-paper](skills/latex-paper/) | LaTeX 论文排版。10 套现成模板：中文课程论文、实验报告、作业、数模国赛、本科毕业论文、IEEE/ACM 会议、美赛、Elsevier 期刊、IEEE 期刊；一条命令跑完 XeLaTeX + bibtex/biber | TeX Live（`xelatex`/`bibtex`/`biber` 在 PATH）、PowerShell 5.1+ | PDF（+ 编译日志 `.log`） |
| [sj-ppt](skills/sj-ppt/) | 赛级 PPT 生产线。一份 `deck.json` 同时生成单文件 HTML 演示版和可编辑 `.pptx` | Node.js 18+；生成 pptx 另需 Python 3.8+ 与 `python-pptx`、`lxml` | `out/index.html` + `out/*.pptx` |
| [promptlab](skills/promptlab/) | 中文 AI 绘画提示词工坊。七段式写提示词、用锚点保证系列图一致，自带自检脚本 | Python 3.8+（只用标准库） | 提示词文本 + 设定卡（对话内交付） |

三个技能互不依赖，可以只装其中一个。

## 2. 安装

技能目录位置：Trae 国内版是 `~/.trae-cn/skills/`（Windows 为 `%USERPROFILE%\.trae-cn\skills\`），国际版是 `~/.trae/skills/`。下面命令按国内版写。

### 方式 A：git clone（推荐，方便更新）

```bash
git clone https://github.com/xin-ze-jiang/super-writer.git
cd super-writer
```

克隆下来只是仓库，还要按方式 C 把技能目录复制进 Trae 的技能目录。

### 方式 B：下载 ZIP 解压

在仓库页面点 `Code` → `Download ZIP`，解压到一个固定目录（比如 `D:\tools\super-writer`）。之后同样按方式 C 复制。

### 方式 C：复制技能目录（真正的安装动作）

单个技能：

```powershell
# Windows PowerShell
Copy-Item -Recurse .\skills\latex-paper "$HOME\.trae-cn\skills\"
```

```bash
# macOS / Linux
mkdir -p ~/.trae-cn/skills
cp -R skills/latex-paper ~/.trae-cn/skills/
```

三个都装：

```powershell
# Windows
New-Item -ItemType Directory -Force "$HOME\.trae-cn\skills" | Out-Null
'latex-paper','sj-ppt','promptlab' | ForEach-Object {
  Copy-Item -Recurse ".\skills\$_" "$HOME\.trae-cn\skills\" -Force
}
```

```bash
# macOS / Linux
mkdir -p ~/.trae-cn/skills
cp -R skills/latex-paper skills/sj-ppt skills/promptlab ~/.trae-cn/skills/
```

装完检查一下（`SKILL.md` 必须直接在技能目录根下，不能多套一层）：

```powershell
Get-ChildItem "$HOME\.trae-cn\skills\latex-paper"
# 期望看到：SKILL.md  templates  scripts  references
```

技能在**新建对话**时扫描加载，装完需要开个新对话才生效。

## 3. 怎么被触发

### 自动命中

技能靠 `SKILL.md` 的 `description` 匹配，用日常说法说话就行：

| 你会怎么说 | 命中的技能 |
|---|---|
| 把实验报告排成 PDF / 帮我排一篇课程论文 / 这份 LaTeX 报 Undefined control sequence / 页边距改成 2.5 cm / 毕业论文模板 | latex-paper |
| 做个 4 页汇报 PPT / 大创答辩 PPT / 要能动又有 pptx 版本 / 这组数据做成柱状图页 | sj-ppt |
| 帮我改这段提示词 / 写个即梦提示词 / 角色三视图要长得一样 / 绘本分镜 | promptlab |

### 手动指定

在对话里直接输入斜杠命令，强制走对应技能：

```
/latex-paper
/sj-ppt
/promptlab
```

## 4. 每个技能怎么用

### 4.1 latex-paper

**能做什么**：选题材 → 复制模板 → 改 `main.tex` 和 `refs.bib` → 一键编译出 PDF；顺带排查 LaTeX 报错、改字号/页边距/行距/参考文献样式。

**最小可用命令**（`$Skill` 指技能安装目录）：

```powershell
$Skill = Join-Path $HOME '.trae-cn\skills\latex-paper'

# 1) 自检：编译全部 10 套模板，看谁报错
powershell -NoProfile -ExecutionPolicy Bypass -File "$Skill\scripts\build.ps1" -All -Parse

# 2) 编译某一套模板
powershell -NoProfile -ExecutionPolicy Bypass -File "$Skill\scripts\build.ps1" cn-cumcm -Parse

# 3) 编译自己的作业目录（目录里要有 main.tex 和 refs.bib）
powershell -NoProfile -ExecutionPolicy Bypass -File "$Skill\scripts\build.ps1" 'D:\作业\数模国赛_2026' -Parse
```

**产物**：`$Skill\output\<文件夹名>.pdf`，同时留一份 `<文件夹名>.log`。传目录时「文件夹名」就是你的作业目录名，所以目录名起得有意义一点（`数模国赛_2026` 而不是 `新建文件夹`）。`-KeepAux` 可保留中间文件，`-Parse` 把日志里的报错翻成「文件:行号: 说明」。

**需要你提供**：题材（中文/英文、课程论文/竞赛/毕业论文/投稿）、学校或会议的格式要求（有就发，没有用模板默认）、正文与数据、参考文献条目。

### 4.2 sj-ppt

**能做什么**：把内容写进一个 `deck.json`，生成两版交付：单文件 HTML（可直接全屏演示、带动效）和可编辑 `.pptx`（老师能打开改）。内置 5 套赛级风格和静态检查脚本。

**最小可用命令**（在技能目录下执行）：

```powershell
cd "$HOME\.trae-cn\skills\sj-ppt"

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

### 4.3 promptlab

**能做什么**：按「主体 → 动作与构图 → 镜头 → 光线 → 材质风格 → 氛围 → 画幅」七段式写中文提示词，先定一致性锚点（角色卡/世界卡），再逐页只改变化部分；自带自检脚本查空话、维度冲突、画幅缺失。

**最小可用命令**：

```powershell
cd "$HOME\.trae-cn\skills\promptlab"

# 直接查一段提示词
python scripts/check_prompt.py -p "黄昏的旧书店，木质书架，暖黄灯光，胶片质感，画幅 3:4"

# 从文件读、批量读（每行一条）、指定语言
python scripts/check_prompt.py -f prompt.txt
python scripts/check_prompt.py -b batch.txt
python scripts/check_prompt.py --lang zh < prompt.txt
```

**产物**：提示词文本、角色设定卡、世界设定卡、分镜表，直接在对话里交付，不写文件；自检结果打印在终端（`可提交` / 需要改的具体问题）。

**需要你提供**：画幅（竖版 3:4 / 方图 1:1 / 横版 16:9）、目标工具（默认即梦）、数量（单图 / 系列几张 / 绘本几页），以及主体是谁、在做什么。

## 5. 依赖与安装

| 依赖 | 版本 | 用在哪 | 缺了会怎样 |
|---|---|---|---|
| TeX Live | 2026 full scheme | latex-paper | 编译直接失败：`xelatex: 无法将...识别为 cmdlet`。装完整版，别用 MiKTeX 替代 |
| `xelatex` / `bibtex` / `biber` 在 PATH | 随 TeX Live | latex-paper | 装了 TeX Live 但没进 PATH 同样报找不到命令（Windows 默认路径形如 `D:\texlive\2026\bin\windows`） |
| PowerShell | 5.1+ | latex-paper 的 `build.ps1` | 脚本跑不起来。macOS/Linux 需装 `pwsh`，或改用第 6 节的手动编译命令 |
| Node.js | 18+ | sj-ppt 生成 HTML | `node: command not found`；`build_html.mjs` 用 ESM，低于 18 会报语法错 |
| Python | 3.8+ | sj-ppt 生成 pptx；promptlab 自检 | 脚本无法启动 |
| `python-pptx`、`lxml` | 最新 | sj-ppt 生成 pptx | `ModuleNotFoundError: No module named 'pptx'`。pip 装即可 |

PATH 临时补法（不想改系统环境变量时，当前窗口有效）：

```powershell
$env:PATH = 'D:\texlive\2026\bin\windows;' + $env:PATH
```

## 6. 不用技能也能用

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

sj-ppt 的两个脚本也是普通命令行程序，`node scripts/build_html.mjs 你的deck.json 输出.html` 即可，不必经过对话。promptlab 的 `check_prompt.py` 同样可以单独跑。

## 7. 更新方式

技能不会被自动同步，更新要手动做两步：

```powershell
# 1) 拉最新代码
cd D:\tools\super-writer
git pull

# 2) 重新覆盖复制一次（Windows 用 robocopy，/E 表示含子目录，会覆盖旧文件）
robocopy .\skills\latex-paper "$HOME\.trae-cn\skills\latex-paper" /E
robocopy .\skills\sj-ppt      "$HOME\.trae-cn\skills\sj-ppt"      /E
robocopy .\skills\promptlab   "$HOME\.trae-cn\skills\promptlab"   /E
```

```bash
# macOS / Linux
cd ~/tools/super-writer && git pull
cp -Rf skills/latex-paper skills/sj-ppt skills/promptlab ~/.trae-cn/skills/
```

复制完开新对话生效。注意 `cp -R` 不会删掉旧版本里已删除的文件，要彻底干净就先删技能目录再复制。

## 8. 常见坑

| 现象 | 原因 | 处理 |
|---|---|---|
| 技能装了但完全不生效 | 多套了一层目录，比如 `skills/latex-paper/latex-paper/SKILL.md` | `SKILL.md` 必须在技能目录根；目录名要与 `SKILL.md` 里的 `name` 一致（`latex-paper` / `sj-ppt` / `promptlab`） |
| `xelatex: 无法将...识别为 cmdlet` | TeX Live 的 bin 目录没进 PATH | 用第 5 节的 `$env:PATH` 临时补，或把 `D:\texlive\2026\bin\windows` 加进系统环境变量 |
| 编译报 `Font "SimSun" not found` 之类 | 模板用 `fontset=windows`，非 Windows 没这些字体 | 把 `main.tex` 里 `fontset=windows` 改成 `fontset=fandol`，或装对应中文字体 |
| 中文全是乱码或 `Missing character` | `.tex` 存成了 GBK | 统一存 UTF-8（无 BOM）；`.ps1` 脚本相反，要 UTF-8 **带 BOM** |
| 参考文献显示 `[?]` | 没跑 bibtex/biber，或 `refs.bib` 里没有对应 key | 按第 6 节顺序跑四遍；检查 `\cite{}` 的 key 与 bib 条目一致 |
| `build.ps1` 报脚本无法加载 | 执行策略限制 | 调用时带 `-ExecutionPolicy Bypass`，或 `Set-ExecutionPolicy -Scope Process Bypass` |
| `deck.json` 读取报 JSON 解析错误 | 文件带 BOM 或被存成 GBK | 用 UTF-8（推荐无 BOM）保存；改完 JSON 要重跑两个脚本，别手改 HTML/PPTX |
| pptx 打开提示「需要修复」 | 未按流程生成，或手动改过 pptx | 只改 `deck.json` 再重新生成 |
| 页数/交叉引用不对 | XeLaTeX 只跑了一遍 | 至少 `xelatex` 跑两遍（脚本已自动跑三遍） |

## 9. 目录结构

```
skills-repo/
├─ README.md
├─ LICENSE
├─ .gitignore
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
   └─ promptlab/
      ├─ SKILL.md
      ├─ USAGE.md
      ├─ references/          # 电影感、一致性、方法、动效、视觉词库
      ├─ templates/           # 角色 / 场景 / 绘本 / 3D 四类设定卡
      ├─ scripts/check_prompt.py
      └─ examples/
```

编译与生成产物（`output/`、`out/`、`*.pdf`、`*.aux`、`__pycache__/` 等）已写入 `.gitignore`，不会进仓库。

## 10. 许可

MIT，见 [LICENSE](LICENSE)。
