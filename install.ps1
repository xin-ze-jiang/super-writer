<#
.SYNOPSIS
  super-writer：把技能安装到主流 AI 工具的配置目录。

.DESCRIPTION
  技能以目录形式分发，核心是目录根下的 SKILL.md。
  支持的工具（用户级）：
    trae     ~/.trae-cn/skills 或 ~/.trae/skills
    claude   ~/.claude/skills
    cursor   ~/.cursor/skills
    codex    ~/.agents/skills + 追加 ~/.codex/AGENTS.md
    cline    ~/.cline/skills
    gemini   ~/.gemini/skills
    copilot  ~/.copilot/skills
    windsurf ~/.codeium/windsurf/skills
    deepseek ~/.dsh/skills（DeepSeek Harness；也原生读 ~/.agents/skills）

.PARAMETER Target
  all | auto | claude | trae | cursor | codex | cline | gemini | copilot | windsurf | deepseek
  可写多个：-Target claude,cursor；默认 auto（只装检测到的工具）。

.EXAMPLE
  .\install.ps1
  .\install.ps1 -Target all
  .\install.ps1 -Target claude,cursor
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string[]]$Target = @('auto'),

    # 仓库根目录，默认取脚本所在目录
    [string]$Repo = '',

    # 覆盖用户主目录（一般不用，测试时避免污染真实配置）
    [string]$HomeDir = ''
)

$ErrorActionPreference = 'Stop'

$UserHome = if ($HomeDir) { $HomeDir } else { $HOME }
if (-not $UserHome) { $UserHome = $env:USERPROFILE }
$RepoRoot = if ($Repo) { (Resolve-Path $Repo).Path } else { Split-Path -Parent $PSCommandPath }
$SrcSkills = Join-Path $RepoRoot 'skills'

if (-not (Test-Path $SrcSkills)) {
    Write-Host "[错误] 找不到技能目录：$SrcSkills" -ForegroundColor Red
    exit 1
}

$Skills = @(Get-ChildItem -Path $SrcSkills -Directory | Sort-Object Name)
if ($Skills.Count -eq 0) {
    Write-Host "[错误] $SrcSkills 下没有技能目录" -ForegroundColor Red
    exit 1
}

# 每个技能一句话触发方式
$Triggers = @{
    'latex-paper' = '「把这份实验报告排成 PDF」或「用 latex-paper 编译这个 .tex」'
    'sj-ppt'      = '「用 sj-ppt 做一个 12 页答辩 PPT」'
    'promptlab'   = '「帮我写/改一条即梦提示词」'
}

# 目标工具：安装目录 + 用于 auto 检测的配置目录
$Specs = [ordered]@{}
$Specs['trae'] = @{
    Label  = 'Trae'
    Dir    = if (Test-Path (Join-Path $UserHome '.trae-cn')) { Join-Path $UserHome '.trae-cn\skills' } else { Join-Path $UserHome '.trae\skills' }
    Detect = @((Join-Path $UserHome '.trae-cn'), (Join-Path $UserHome '.trae'))
}
$Specs['claude'] = @{
    Label  = 'Claude Code'
    Dir    = Join-Path $UserHome '.claude\skills'
    Detect = @((Join-Path $UserHome '.claude'))
}
$Specs['cursor'] = @{
    Label  = 'Cursor'
    Dir    = Join-Path $UserHome '.cursor\skills'
    Detect = @((Join-Path $UserHome '.cursor'))
}
$Specs['codex'] = @{
    Label  = 'OpenAI Codex CLI'
    Dir    = Join-Path $UserHome '.agents\skills'
    Detect = @((Join-Path $UserHome '.codex'))
}
$Specs['cline'] = @{
    Label  = 'Cline'
    Dir    = Join-Path $UserHome '.cline\skills'
    Detect = @((Join-Path $UserHome '.cline'))
}
$Specs['gemini'] = @{
    Label  = 'Gemini CLI'
    Dir    = Join-Path $UserHome '.gemini\skills'
    Detect = @((Join-Path $UserHome '.gemini'))
}
$Specs['copilot'] = @{
    Label  = 'GitHub Copilot'
    Dir    = Join-Path $UserHome '.copilot\skills'
    Detect = @((Join-Path $UserHome '.copilot'))
}
$Specs['windsurf'] = @{
    Label  = 'Windsurf'
    Dir    = Join-Path $UserHome '.codeium\windsurf\skills'
    Detect = @((Join-Path $UserHome '.codeium\windsurf'))
}
$Specs['deepseek'] = @{
    Label  = 'DeepSeek Harness'
    Dir    = Join-Path $UserHome '.dsh\skills'
    Detect = @((Join-Path $UserHome '.dsh'))
}

function Install-Skills {
    param([string]$Name)

    $spec = $Specs[$Name]
    $dest = $spec.Dir
    New-Item -ItemType Directory -Path $dest -Force | Out-Null

    Write-Host ""
    Write-Host ("[{0}] {1}" -f $Name, $dest) -ForegroundColor Cyan
    foreach ($s in $Skills) {
        $to = Join-Path $dest $s.Name
        if (Test-Path $to) { Remove-Item $to -Recurse -Force }
        Copy-Item -Path $s.FullName -Destination $to -Recurse -Force
        # 本地产物 / 缓存不带走
        foreach ($junk in @('output', 'out', '__pycache__', '.venv')) {
            $j = Join-Path $to $junk
            if (Test-Path $j) { Remove-Item $j -Recurse -Force }
        }
        Write-Host ("  [OK] {0,-12} -> {1}" -f $s.Name, $to)
        if ($Triggers.ContainsKey($s.Name)) {
            Write-Host ("       触发：{0}" -f $Triggers[$s.Name]) -ForegroundColor DarkGray
        }
    }

    if ($Name -eq 'codex') {
        Update-CodexAgents
    }
}

function Update-CodexAgents {
    $adapter = Join-Path $RepoRoot 'adapters\codex\AGENTS.md'
    if (-not (Test-Path $adapter)) {
        Write-Host "  [跳过] 没有找到 adapters\codex\AGENTS.md，未追加全局指令" -ForegroundColor Yellow
        return
    }
    $agents = Join-Path $UserHome '.codex\AGENTS.md'
    New-Item -ItemType Directory -Path (Split-Path -Parent $agents) -Force | Out-Null

    $begin = '<!-- super-writer:begin -->'
    $end = '<!-- super-writer:end -->'
    $body = (Get-Content -Raw -Encoding UTF8 $adapter).TrimEnd()
    $block = "$begin`n$body`n$end"

    $existing = ''
    if (Test-Path $agents) {
        $existing = Get-Content -Raw -Encoding UTF8 $agents
        $pattern = '(?ms)^' + [regex]::Escape($begin) + '.*?^' + [regex]::Escape($end) + '\s*'
        $existing = [regex]::Replace($existing, $pattern, '')
    }
    $existing = $existing.TrimEnd()
    $out = if ($existing) { "$existing`n`n$block`n" } else { "$block`n" }
    Set-Content -Path $agents -Value $out -Encoding UTF8 -NoNewline
    Write-Host ("  [OK] AGENTS.md -> {0}" -f $agents)
}

# ---- 解析目标 ----
$want = @()
foreach ($t in $Target) {
    foreach ($x in ($t -split ',')) {
        $x = $x.Trim().ToLower()
        if ($x) { $want += $x }
    }
}
if ($want.Count -eq 0) { $want = @('auto') }

$names = @($Specs.Keys)
$selected = @()
$skipped = @()

if ($want -contains 'all') {
    $selected = $names
}
elseif ($want -contains 'auto') {
    foreach ($n in $names) {
        $hit = $false
        foreach ($d in $Specs[$n].Detect) { if (Test-Path $d) { $hit = $true } }
        if ($hit) { $selected += $n } else { $skipped += $n }
    }
}
else {
    foreach ($n in $want) {
        if ($names -contains $n) { $selected += $n }
        else { Write-Host "[忽略] 未知目标：$n（可用：all, auto, $($names -join ', ')）" -ForegroundColor Yellow }
    }
}

Write-Host "仓库：$RepoRoot"
Write-Host "技能：$((($Skills | ForEach-Object { $_.Name }) -join '、'))"
Write-Host "目标：$(if ($selected.Count) { $selected -join ', ' } else { '无' })"

if ($skipped.Count -gt 0) {
    Write-Host ""
    Write-Host ("[跳过] 未检测到：{0}" -f ($skipped -join ', ')) -ForegroundColor Yellow
    Write-Host "       需要全装请用：.\install.ps1 -Target all"
}

if ($selected.Count -eq 0) {
    Write-Host ""
    Write-Host "没有可安装的目标，未做任何修改。" -ForegroundColor Yellow
    exit 0
}

foreach ($n in $selected) {
    Install-Skills -Name $n
}

Write-Host ""
Write-Host "完成。技能在新对话/新会话中生效；重复执行会原地覆盖，不会产生重复目录。" -ForegroundColor Green
