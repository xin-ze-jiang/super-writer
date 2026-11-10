---
name: latex-paper
description: "LaTeX 论文排版：7 套现成模板（中文课程论文/实验报告/作业、数模国赛、IEEE、ACM、美赛），XeLaTeX 自动跑 bibtex/biber 出 PDF。用户要排版论文、编译 .tex、查 LaTeX 报错或改字号页边距时启用。"
---

# latex-paper · LaTeX 论文排版工作台

## 一、这个技能是什么

一套已经在本机装好、编译验证过的 LaTeX 排版底稿：7 套模板 + 一键编译脚本（XeLaTeX + 自动识别 bibtex/biber）+ 速查手册。用户给题目、正文、数据，就直接改模板、跑编译、交 PDF。

**启用**：中文课程论文、实验报告、平时作业、数学建模国赛（CUMCM）、IEEE / ACM 英文会议论文、MCM/ICM 美赛；任何"把内容排成论文/报告 PDF"的需求；LaTeX 报错排查；改字号、页边距、行距、字体、参考文献样式。

**不启用**：做 PPT（用 sj-ppt）、纯数据处理不出文档、Word/Markdown 排版。

## 二、目录结构（模板只有一份，不许另存副本）

```
<技能目录>\
├─ templates\<模板名>\      main.tex + refs.bib（7 套，唯一底稿）
├─ scripts\build.ps1        一键编译脚本
├─ scripts\parse_log.ps1    日志诊断解析（文件:行号: 说明）
├─ references\              模板选择、报错排查、中文排版、英文字体
└─ output\                  产物：<文件夹名>.pdf / <文件夹名>.log（首次运行自动创建）
```

`<技能目录>` 指本技能所在目录，安装后通常是 `~/.trae-cn/skills/latex-paper`（Windows 为 `%USERPROFILE%\.trae-cn\skills\latex-paper`）。

引擎：TeX Live 2026（full scheme），`xelatex` / `bibtex` / `biber` 必须在 PATH 中能被找到。

**文件缺失时**（用户删了、换机器）：
1. 先确认 `<技能目录>\templates` 和 `xelatex` 是否真的不可用，别凭猜测重装。
2. 只缺 `templates\` → 按 `references/templates.md` 末尾「模板重建规格」逐套重建：每套只需 1 个 `main.tex` + 1 个 `refs.bib`（模板名即目录名，入口文件必须叫 `main.tex`）。重建后跑 `build.ps1 -All` 自检，7 套全绿才算恢复。
3. 只缺 `build.ps1` → 按本文第五节流程重写：xelatex → bibtex/biber → xelatex ×2 → 复制到 `output\<文件夹名>.pdf` → 清中间文件。
4. 缺引擎 → 让用户安装 TeX Live（full scheme），不要用 MiKTeX 替代。
5. 不要在技能目录外再复制一份 `templates\`：底稿只有一份，以技能内 `templates\` 为准。

## 三、选哪套模板

| 场景 | 模板目录 | 文档类 / 格式 |
|---|---|---|
| 中文课程论文、结课小论文 | `cn-course-paper` | ctexart，小四宋体 1.5 倍行距，GB/T 7714（bibtex） |
| 中文实验报告、实验数据与分析 | `cn-lab-report` | ctexart，`\labinfo{课程}{日期}{姓名}{学号}`，section 为「一、二、」 |
| 通用课程作业、习题解答 | `cn-homework` | ctexart + biblatex(gb7714-2015) + **biber** |
| 全国大学生数学建模竞赛 | `cn-cumcm` | article + ctex，摘要页不编页码、正文从 1 起、题目三号黑体 |
| IEEE conference 英文论文 | `en-ieee` | IEEEtran[conference]，双栏，TeX Gyre Termes |
| ACM sigconf 英文论文 | `en-acm` | acmart[sigconf,nonacm] 双栏，CCS 概念 |
| MCM/ICM 美赛 | `en-mcm` | article 12pt + 1in 边距 + Summary Sheet + Times |

拿不准就问一句：中文还是英文、课程论文还是竞赛、学校/会议有没有指定模板。学校有硬性格式要求时，以用户给的为准改底稿副本。

## 四、标准工作流（按序，不跳步）

1. **复制模板到作业目录**（不要直接改底稿）
   ```powershell
   $Skill = Join-Path $HOME '.trae-cn\skills\latex-paper'
   $src   = Join-Path $Skill 'templates\cn-cumcm'
   $dst   = 'D:\作业\数模国赛_2026'          # 换成你自己的作业目录
   New-Item -ItemType Directory -Path $dst -Force | Out-Null
   Copy-Item "$src\*" $dst -Force
   ```
   `output\<文件夹名>.pdf` 里的「文件夹名」就是这里的 `数模国赛_2026`，所以作业目录名字取得有意义一点。

2. **只改两处**：`main.tex`（标题、作者、摘要、正文、公式、表格）和 `refs.bib`（文献）。模板已含占位标题、一节正文、一个公式、一张三线表、一条参考文献，直接替换即可。

3. **跑编译**
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Skill 'scripts\build.ps1') $dst
   ```
   成功：终端打印「[OK] 页数 N，耗时 …」+ PDF 绝对路径。
   失败：终端直接列出 log 里所有 `!` 开头的错误行和 `main.tex:行号`，log 已写到 `output\<文件夹名>.log`。加 `-Parse` 可拿到「main.tex:51: 未定义文献：xxx」这类能直接跳转的条目。

4. **产物**：`<技能目录>\output\<文件夹名>.pdf`（同名覆盖，只留最新一份），log 同名。交付时用 `computer://` 链接直接给用户这个 PDF。作业目录里会留一个 `main.pdf`（脚本只清中间文件、不删它），属正常，不要去删 `main.tex` 旁边的产物文件；以 `output\` 那份为准。

5. **自检后再交付**：页数合理、终端无 `!` 行、中文不方块、`\cite` 显示成数字而不是 `[?]`、公式编号连续、表格不超版心。有问题回改 `main.tex` 重跑，不要交付没编译过的源码。

## 五、脚本参数

先 `cd <技能目录>`，再执行（产物写到技能目录下的 `output\`）：

```powershell
.\scripts\build.ps1 cn-cumcm              # 按模板名（只在 templates 下找）
.\scripts\build.ps1 'D:\...\我的作业'      # 按目录路径（作业目录用这个）
.\scripts\build.ps1 -All                  # 依次编译 templates 下全部 7 套，出汇总表
.\scripts\build.ps1 cn-cumcm -KeepAux     # 保留 .aux/.log/.bcf 等中间文件，排错用
.\scripts\build.ps1 'D:\...\我的作业' -Parse           # 输出「文件:行号: 说明」结构化诊断
.\scripts\build.ps1 'D:\...\我的作业' -Watch           # 监听保存，自动重编译 + SumatraPDF 预览
.\scripts\build.ps1 'D:\...\我的作业' -Watch -NoViewer # 只监听重编译，不开窗口（agent 用）
.\scripts\parse_log.ps1 output\我的作业.log            # 单独解析已有日志
.\scripts\parse_log.ps1 output\我的作业.log -Json      # 输出 JSON，便于程序消费
```

脚本内部：`xelatex` → 有 `main.bcf` 跑 `biber main`、`main.aux` 含 `\bibdata` 跑 `bibtex main`、都没有则跳过 → `xelatex` ×2 → 复制 PDF/log 到 `output\` → 清中间文件。退出码 0 成功、1 失败。

**`-Parse` 诊断格式**：分「必须修」（编译错误、未定义引用、未定义文献）和「建议看」（Overfull/Underfull 溢出），每条都是 `文件:行号: 说明`。未定义引用/文献会给键名和页码，并回源码定位到实际使用的那一行；子文件里的问题也能定位到子文件。第 1 遍就失败时自动过滤引用类噪声（此时 `.aux` 尚未生成）。

**`-Watch` 监听**：保存 `.tex/.bib/.cls/.sty/.bst/图片` 后约 1 s 内自动重编译并刷新诊断；不加 `-NoViewer` 时尝试拉起 SumatraPDF（随 PDF 更新自动刷新），没装则提示跳过、不影响编译。`Ctrl+C` 结束。与 `-All` 互斥。

## 六、用户给题目和数据时的做法

- 用户给了题目/正文/实验数据/模型结果 → **直接改 `main.tex` 并编译**，不要再问"要不要帮你写"，也别等二次确认。
- 正文只写用户给的内容；数据一律用用户给的原始值，**不许自己生成或补全数据**（占位表格里写明"示例数据，请替换"）。
- 缺关键字段（学校格式要求、作者/学号/队号、参考文献是否必须真实可查）就在动手前一次问完，最多 4 个问题，用编号列。
- 改了字号、页边距、章节样式这类格式，交付时说明改了哪一行，方便用户回退。

## 七、references 文件地图

| 文件 | 什么时候读 |
|---|---|
| `references/templates.md` | 选模板、查目录约定与产物规则、提交前要替换哪些字段、**底稿丢了怎么重建** |
| `references/errors.md` | 编译报错、`[?]` 引用、字体找不到、环境/依赖检查 |
| `references/chinese-typesetting.md` | 改字号/页边距/行距/字体/编号样式、常用宏包、Windows 中文字体 |
| `references/english-fonts.md` | 英文模板字体（IEEE 的 Termes、ACM 的 Libertine、美赛的 Times） |

## 八、硬规则

1. 不改 `templates\` 里的底稿；所有内容改动都在作业目录的副本上做。
2. 中文必须 XeLaTeX，不许换 pdflatex；中文模板保持 `fontset=windows`。
3. 不编造数据、不编造参考文献（`refs.bib` 里的示例条目必须替换或删除）。
4. 不宣称"编译通过"除非本轮真的跑过脚本并看到 `[OK]`。
5. 交付必须给 PDF 路径，不能只给 `.tex` 源码。
