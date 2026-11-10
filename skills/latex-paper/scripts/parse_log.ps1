<#
.SYNOPSIS
    解析 LaTeX 编译日志，输出「文件:行号: 说明」结构化诊断。

.DESCRIPTION
    配合 build.ps1 的 -file-line-error 使用。把日志内容分成：
      - 必须修：编译错误、未定义引用/文献
      - 建议看：Overfull / Underfull 排版溢出
    三轮编译产生的重复条目会自动去重。既可作为库被 build.ps1 dot-source，
    也可单独当命令行工具用。

.EXAMPLE
    .\parse_log.ps1 .\main.log

.EXAMPLE
    .\parse_log.ps1 .\main.log -Json
    输出 JSON，便于其他程序或 agent 直接消费。
#>
param(
    [Parameter(Position = 0)]
    [string]$LogPath,

    [switch]$Json
)

function Resolve-DiagPath {
    param(
        [string]$Path,
        [string]$BaseDir
    )

    if (-not $Path) { return '' }

    $p = $Path -replace '/', '\'
    $p = $p -replace '^\.\\', ''

    if (-not $BaseDir) { return $p }

    $base = $BaseDir.TrimEnd('\') + '\'
    if ($p.StartsWith($base, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $p.Substring($base.Length)
    }
    return $p
}

# 日志没给文件名时，回源码反查 ref/cite 键的使用位置
function Find-UsageLocation {
    param(
        [string]$Key,
        [string]$Kind,
        [string]$BaseDir
    )

    if (-not $Key -or -not $BaseDir) { return $null }

    $k = [regex]::Escape($Key)
    $pattern = if ($Kind -eq 'cite') {
        '\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{[^}]*' + $k + '[^}]*\}'
    }
    else {
        '\\(?:ref|eqref|autoref|pageref|nameref|cref|Cref)\*?\{' + $k + '\}'
    }

    $files = Get-ChildItem -LiteralPath $BaseDir -Recurse -File -Filter '*.tex' -ErrorAction SilentlyContinue
    foreach ($f in $files) {
        $idx = 0
        foreach ($src in (Get-Content -LiteralPath $f.FullName -Encoding UTF8)) {
            $idx++
            if ($src -match $pattern) {
                return [pscustomobject]@{
                    File = Resolve-DiagPath -Path $f.FullName -BaseDir $BaseDir
                    Line = $idx
                }
            }
        }
    }
    return $null
}

function Get-LatexDiagnostics {
    param(
        [string]$Path,
        [string]$BaseDir
    )

    $items = New-Object System.Collections.Generic.List[object]
    if (-not (Test-Path -LiteralPath $Path)) { return $items.ToArray() }
    if (-not $BaseDir) { $BaseDir = Split-Path -Parent $Path }

    $lines   = @(Get-Content -LiteralPath $Path -Encoding UTF8)
    $seen    = @{}
    $curFile = ''
    $curLine = 0
    $defaultTex = 'main.tex'

    function Add-Diag {
        param(
            [string]$Level,
            [string]$Kind,
            [string]$File,
            [int]$Line,
            [string]$Message
        )

        $key = '{0}|{1}|{2}|{3}|{4}' -f $Level, $Kind, $File, $Line, $Message
        if ($seen.ContainsKey($key)) { return }
        $seen[$key] = $true
        $items.Add([pscustomobject]@{
            Level   = $Level
            Kind    = $Kind
            File    = $File
            Line    = $Line
            Message = $Message
        })
    }

    foreach ($raw in $lines) {
        $line = $raw.TrimEnd()

        # -file-line-error 产出：./main.tex:12: 错误信息
        if ($line -match '^(?<f>[^:]+\.(?:tex|sty|cls|bib|def|cfg)):(?<n>\d+):\s*(?<m>.+)$') {
            $file = Resolve-DiagPath -Path $Matches['f'] -BaseDir $BaseDir
            $num  = [int]$Matches['n']
            $msg  = $Matches['m'].Trim().TrimEnd('.')
            $curFile = $file
            $curLine = $num

            if ($msg -match '^(LaTeX|Package\s+\S+|Class\s+\S+)\s+Warning') {
                Add-Diag -Level 'info' -Kind 'warning' -File $file -Line $num -Message $msg
            }
            else {
                Add-Diag -Level 'must' -Kind 'error' -File $file -Line $num -Message $msg
            }
            continue
        }

        # 传统 ! 开头错误，沿用上一条定位
        if ($line -match '^!\s*(?<m>.+)') {
            Add-Diag -Level 'must' -Kind 'error' -File $curFile -Line $curLine -Message ($Matches['m'].Trim().TrimEnd('.'))
            continue
        }

        # 未定义引用（LaTeX / Package natbib 等都可能报）
        if ($line -match '(?:LaTeX|Package\s+\S+|Class\s+\S+)\s+Warning:\s+Reference\s+`(?<k>[^'']+)''\s+on\s+page\s+(?<p>\d+)\s+undefined') {
            $key  = $Matches['k']
            $page = $Matches['p']
            $file = if ($curFile) { $curFile } else { $defaultTex }
            $num  = $curLine
            $hit  = Find-UsageLocation -Key $key -Kind 'ref' -BaseDir $BaseDir
            if ($hit) { $file = $hit.File; $num = $hit.Line }
            Add-Diag -Level 'must' -Kind 'ref' -File $file -Line $num `
                -Message ('未定义引用：{0}（第 {1} 页）' -f $key, $page)
            continue
        }

        # 未定义文献
        if ($line -match '(?:LaTeX|Package\s+\S+|Class\s+\S+)\s+Warning:\s+Citation\s+`(?<k>[^'']+)''\s+on\s+page\s+(?<p>\d+)\s+undefined') {
            $key  = $Matches['k']
            $page = $Matches['p']
            $file = if ($curFile) { $curFile } else { $defaultTex }
            $num  = $curLine
            $hit  = Find-UsageLocation -Key $key -Kind 'cite' -BaseDir $BaseDir
            if ($hit) { $file = $hit.File; $num = $hit.Line }
            Add-Diag -Level 'must' -Kind 'cite' -File $file -Line $num `
                -Message ('未定义文献：{0}（第 {1} 页）' -f $key, $page)
            continue
        }

        # 排版溢出
        if ($line -match '^(?<t>Overfull|Underfull)\s+\\(?<b>[hv])box') {
            $type = $Matches['t']
            $box  = $Matches['b']
            $num  = 0
            if ($line -match '(?:at lines?|detected at line)\s+(?<n>\d+)') { $num = [int]$Matches['n'] }

            if ($line -match '\((?<a>-?[\d.]+)pt too (?:wide|high)\)') {
                $msg = $type + ' \' + $box + 'box 超出 ' + $Matches['a'] + 'pt'
            }
            else {
                $msg = $type + ' \' + $box + 'box 排版过松'
            }
            Add-Diag -Level 'info' -Kind 'box' -File $curFile -Line $num -Message $msg
            continue
        }
    }

    return @($items | Sort-Object `
        @{ Expression = { if ($_.Level -eq 'must') { 0 } else { 1 } } }, Kind, File, Line)
}

function Format-LatexDiagnostics {
    param([object[]]$Diagnostics)

    $out  = New-Object System.Collections.Generic.List[string]
    $list = @($Diagnostics)

    if ($list.Count -eq 0) {
        $out.Add('诊断：未发现错误、未定义引用或排版溢出')
        return $out.ToArray()
    }

    $must = @($list | Where-Object { $_.Level -eq 'must' })
    $info = @($list | Where-Object { $_.Level -ne 'must' })

    if ($must.Count -gt 0) {
        $out.Add(('必须修（{0}）' -f $must.Count))
        foreach ($d in $must) {
            $loc = if ($d.Line -gt 0) { '{0}:{1}' -f $d.File, $d.Line }
                   elseif ($d.File) { $d.File }
                   else { '(位置未知)' }
            $out.Add(('  {0}: {1}' -f $loc, $d.Message))
        }
    }

    if ($info.Count -gt 0) {
        $out.Add(('建议看（{0}）' -f $info.Count))
        foreach ($d in $info) {
            $loc = if ($d.Line -gt 0) { '{0}:{1}' -f $d.File, $d.Line }
                   elseif ($d.File) { $d.File }
                   else { '(位置未知)' }
            $out.Add(('  {0}: {1}' -f $loc, $d.Message))
        }
    }

    return $out.ToArray()
}

# 作为命令行工具直接调用时才输出；被 build.ps1 dot-source 时 $LogPath 为空，静默
if ($LogPath) {
    if (Test-Path -LiteralPath $LogPath) {
        $full = (Resolve-Path -LiteralPath $LogPath).Path
        $diag = @(Get-LatexDiagnostics -Path $full -BaseDir (Split-Path -Parent $full))

        if ($Json) {
            $diag | ConvertTo-Json -Depth 3
        }
        else {
            Format-LatexDiagnostics -Diagnostics $diag | ForEach-Object { Write-Output $_ }
        }
    }
    else {
        Write-Output ('找不到日志文件：{0}' -f $LogPath)
        exit 2
    }
}
