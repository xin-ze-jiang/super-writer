<#
.SYNOPSIS
    LaTeX 模板一键编译脚本（XeLaTeX + 自动识别 BibTeX / Biber）

.DESCRIPTION
    流程： xelatex -> bibtex/biber -> xelatex -> xelatex -> 清理中间文件 -> 复制 PDF 到 output
    输出策略： output\<模板名>.pdf / .log 每次同名覆盖，只保留最新一份；
              编译失败时不覆盖旧 PDF，但会把这次的 main.log 写到 output\<模板名>.log 供排错。
    失败时打印 .log 中含 "!" 的错误行；成功时输出 PDF 路径与页数。

.EXAMPLE
    .\build.ps1 cn-cumcm
    编译 templates\cn-cumcm

.EXAMPLE
    .\build.ps1 .\templates\en-ieee -KeepAux
    按目录路径编译，并保留 .aux/.log 等中间文件

.EXAMPLE
    .\build.ps1 -All
    依次编译全部模板并输出汇总表
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Target,

    [switch]$All,

    [switch]$KeepAux
)

$ErrorActionPreference = 'Stop'

$Root    = Split-Path -Parent $PSScriptRoot
$TplRoot = Join-Path $Root 'templates'
$OutRoot = Join-Path $Root 'output'

$CleanPatterns = @(
    'main.aux', 'main.log', 'main.out', 'main.toc', 'main.lof', 'main.lot',
    'main.bcf', 'main.blg', 'main.bbl', 'main.run.xml', 'main.spl', 'main.brf',
    'main.fls', 'main.fdb_latexmk', 'main.synctex.gz', 'main.idx', 'main.ilg',
    'main.ind', 'main.glo', 'main.gls', 'main.xdv', 'main.dvi'
)

function Write-Step {
    param([string]$Text)
    Write-Host ("  {0}" -f $Text) -ForegroundColor DarkGray
}

# 从日志中提取错误信息
function Get-LogErrors {
    param([string]$LogPath)

    if (-not (Test-Path $LogPath)) { return @('（未生成 main.log）') }

    $lines  = Get-Content -LiteralPath $LogPath -Encoding UTF8
    $result = New-Object System.Collections.Generic.List[string]

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ($line -match '^!') {
            $result.Add($line.Trim())
            if ($i + 1 -lt $lines.Count -and $lines[$i + 1].Trim() -ne '') {
                $result.Add('    ' + $lines[$i + 1].Trim())
            }
        }
        elseif ($line -match '^.+\.(tex|sty|cls|bib):\d+:') {
            $result.Add($line.Trim())
        }
    }

    if ($result.Count -eq 0) {
        $result.Add('（日志中没有以 ! 开头的错误行，请查看 main.log 末尾）')
    }
    return $result.ToArray()
}

# 失败时把这次编译的日志写到 output，便于事后排错
function Publish-FailureLog {
    param(
        [string]$LogPath,
        [string]$Name
    )

    if (Test-Path -LiteralPath $LogPath) {
        Copy-Item -LiteralPath $LogPath -Destination (Join-Path $OutRoot ('{0}.log' -f $Name)) -Force
    }
}

function Invoke-Tool {
    param(
        [string]$Exe,
        [string[]]$Arguments,
        [string]$WorkDir
    )

    Push-Location -LiteralPath $WorkDir
    try {
        $null = & $Exe @Arguments 2>&1
        return $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
}

function Compile-Template {
    param([string]$Dir)

    $name = Split-Path -Leaf $Dir
    $result = [pscustomobject]@{
        Name    = $name
        Ok      = $false
        Pages   = 0
        Seconds = 0.0
        Pdf     = ''
        Engine  = '-'
        Message = ''
    }

    Write-Host ""
    Write-Host ("=== {0} ===" -f $name) -ForegroundColor Cyan

    $main = Join-Path $Dir 'main.tex'
    if (-not (Test-Path -LiteralPath $main)) {
        $result.Message = '缺少 main.tex'
        Write-Host $result.Message -ForegroundColor Red
        return $result
    }

    $log     = Join-Path $Dir 'main.log'
    $pdf     = Join-Path $Dir 'main.pdf'
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    if (Test-Path -LiteralPath $pdf) { Remove-Item -LiteralPath $pdf -Force }
    if (Test-Path -LiteralPath $log) { Remove-Item -LiteralPath $log -Force }

    $xeArgs = @('-interaction=nonstopmode', '-file-line-error', '-halt-on-error', 'main.tex')

    # ---------- 第 1 遍 ----------
    Write-Step '[1] xelatex  pass 1'
    $code = Invoke-Tool -Exe 'xelatex' -Arguments $xeArgs -WorkDir $Dir
    if ($code -ne 0) {
        $stopwatch.Stop()
        $result.Seconds = [math]::Round($stopwatch.Elapsed.TotalSeconds, 1)
        $result.Message = 'xelatex 第 1 遍失败'
        Publish-FailureLog -LogPath $log -Name $name
        Write-Host "  编译失败（exit=$code），错误行：" -ForegroundColor Red
        Get-LogErrors -LogPath $log | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        return $result
    }

    # ---------- 参考文献：自动识别 biber / bibtex ----------
    $bcf     = Join-Path $Dir 'main.bcf'
    $aux     = Join-Path $Dir 'main.aux'
    $bibTool = $null

    if (Test-Path -LiteralPath $bcf) {
        $bibTool = 'biber'
    }
    elseif (Test-Path -LiteralPath $aux) {
        $auxText = Get-Content -LiteralPath $aux -Raw -Encoding UTF8
        if ($auxText -match '\\bibdata') { $bibTool = 'bibtex' }
    }

    if ($bibTool) {
        $result.Engine = $bibTool
        Write-Step ("[2] {0} main" -f $bibTool)
        $bibCode = Invoke-Tool -Exe $bibTool -Arguments @('main') -WorkDir $Dir
        if ($bibCode -ne 0) {
            Write-Host ("  {0} 警告：退出码 {1}，请检查 .blg 文件" -f $bibTool, $bibCode) -ForegroundColor Yellow
        }
    }
    else {
        Write-Step '[2] 跳过参考文献（未发现 \bibdata 或 .bcf）'
    }

    # ---------- 第 2、3 遍 ----------
    $step = 3
    foreach ($pass in 2, 3) {
        Write-Step ("[{0}] xelatex  pass {1}" -f $step, $pass)
        $step++
        $code = Invoke-Tool -Exe 'xelatex' -Arguments $xeArgs -WorkDir $Dir
        if ($code -ne 0) {
            $stopwatch.Stop()
            $result.Seconds = [math]::Round($stopwatch.Elapsed.TotalSeconds, 1)
            $result.Message = ("xelatex 第 {0} 遍失败" -f $pass)
            Publish-FailureLog -LogPath $log -Name $name
            Write-Host ("  编译失败（exit={0}），错误行：" -f $code) -ForegroundColor Red
            Get-LogErrors -LogPath $log | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
            return $result
        }
    }

    $stopwatch.Stop()
    $result.Seconds = [math]::Round($stopwatch.Elapsed.TotalSeconds, 1)

    # ---------- 页数 ----------
    $logText = Get-Content -LiteralPath $log -Raw -Encoding UTF8
    if ($logText -match 'Output written on .*?\((\d+)\s+pages?') {
        $result.Pages = [int]$Matches[1]
    }

    # ---------- 复制到 output（同名覆盖，只留最新一份） ----------
    $outPdf = Join-Path $OutRoot ('{0}.pdf' -f $name)
    $outLog = Join-Path $OutRoot ('{0}.log' -f $name)
    Copy-Item -LiteralPath $pdf -Destination $outPdf -Force
    Copy-Item -LiteralPath $log -Destination $outLog -Force
    $result.Pdf = $outPdf
    $result.Ok  = $true
    $result.Message = '成功'

    Write-Host ("  [OK] 页数 {0}，耗时 {1} s" -f $result.Pages, $result.Seconds) -ForegroundColor Green
    Write-Host ("  PDF : {0}" -f $outPdf) -ForegroundColor Green

    # ---------- 清理 ----------
    if (-not $KeepAux) {
        foreach ($f in $CleanPatterns) {
            $p = Join-Path $Dir $f
            if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Force }
        }
        Write-Step '已清理中间文件（-KeepAux 可保留）'
    }

    return $result
}

# ======================= 主流程 =======================
foreach ($tool in 'xelatex', 'bibtex', 'biber') {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "找不到 $tool，请确认 TeX Live 已安装且 PATH 已生效（可重开终端再试）"
    }
}

if (-not (Test-Path -LiteralPath $OutRoot)) {
    $null = New-Item -ItemType Directory -Path $OutRoot -Force
}

$targets = @()

if ($All) {
    $targets = Get-ChildItem -LiteralPath $TplRoot -Directory | Sort-Object Name | ForEach-Object { $_.FullName }
}
elseif ($Target) {
    if (Test-Path -LiteralPath $Target -PathType Container) {
        $targets = @((Resolve-Path -LiteralPath $Target).Path)
    }
    else {
        $candidate = Join-Path $TplRoot $Target
        if (Test-Path -LiteralPath $candidate -PathType Container) {
            $targets = @($candidate)
        }
        else {
            throw "找不到模板：$Target（可用的模板见 templates 目录）"
        }
    }
}
else {
    Write-Host '用法： .\build.ps1 <模板名|目录路径> [-KeepAux]' -ForegroundColor Yellow
    Write-Host '       .\build.ps1 -All' -ForegroundColor Yellow
    exit 1
}

$results = @()
$total   = [System.Diagnostics.Stopwatch]::StartNew()

foreach ($dir in $targets) {
    $results += Compile-Template -Dir $dir
}

$total.Stop()

# ======================= 汇总 =======================
if ($results.Count -gt 1) {
    $okCount  = @($results | Where-Object { $_.Ok }).Count
    $badCount = @($results | Where-Object { -not $_.Ok }).Count

    Write-Host ''
    Write-Host '================ 编译汇总 ================' -ForegroundColor Cyan
    Write-Host ('{0,-18} {1,-6} {2,4} {3,9} {4}' -f '模板', '结果', '页数', '耗时(s)', '文献')
    Write-Host ('-' * 58)
    foreach ($r in $results) {
        $state = if ($r.Ok) { '成功' } else { '失败' }
        $line  = '{0,-18} {1,-6} {2,4} {3,9} {4}' -f $r.Name, $state, $r.Pages, $r.Seconds, $r.Engine
        if ($r.Ok) { Write-Host $line } else { Write-Host $line -ForegroundColor Red }
    }
    Write-Host ('-' * 58)
    Write-Host ("总计：{0} 套，成功 {1} 套，失败 {2} 套，用时 {3:N1} s" -f `
        $results.Count, $okCount, $badCount, $total.Elapsed.TotalSeconds) -ForegroundColor Cyan
}

$failed = @($results | Where-Object { -not $_.Ok })
if ($failed.Count -gt 0) { exit 1 }
exit 0
