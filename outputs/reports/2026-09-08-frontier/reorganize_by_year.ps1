param([switch]$Apply)

$ErrorActionPreference = 'Stop'

# Derive vault root from script location: .../outputs/reports/2026-09-08-frontier -> up 3 levels.
$root = $PSScriptRoot
$root = Split-Path -Parent $root   # -> reports
$root = Split-Path -Parent $root   # -> outputs
$root = Split-Path -Parent $root   # -> vault root

$sourceDirs = @('wiki_array\sources', 'wiki\sources')
foreach ($d in $sourceDirs) {
  if (-not (Test-Path -LiteralPath (Join-Path $root $d))) {
    Write-Host ("FATAL: missing dir " + (Join-Path $root $d))
    exit 1
  }
}

$moves = New-Object System.Collections.ArrayList

foreach ($d in $sourceDirs) {
  $base = Join-Path $root $d
  Get-ChildItem -LiteralPath $base -Filter '*.md' | ForEach-Object {
    $fn = $_.Name
    $stem = [System.IO.Path]::GetFileNameWithoutExtension($fn)
    if ($stem -match '(\d{4})$') {
      [void]$moves.Add(@{ Kind = $d; Year = $Matches[1]; Name = $fn })
    } else {
      Write-Host ("SKIP no-year: " + $d + "\" + $fn)
    }
  }
}

$litFn = 'Conv-TasNet - Surpassing Ideal TF Masking 2019.md'
if (Test-Path -LiteralPath (Join-Path $root ("literature\" + $litFn))) {
  [void]$moves.Add(@{ Kind = 'literature'; Year = '2019'; Name = $litFn })
}

Write-Host ("=== MOVE PLAN (" + $moves.Count + " files) ===")
$yearCounts = @{}
foreach ($m in $moves) {
  if ($m.Kind -eq 'literature') { $tgt = "wiki\sources\" + $m.Year }
  else { $tgt = $m.Kind + "\" + $m.Year }
  Write-Host ("  " + $m.Kind + " -> " + $tgt + "\" + $m.Name)
  if ($yearCounts.ContainsKey($m.Year)) { $yearCounts[$m.Year] = $yearCounts[$m.Year] + 1 }
  else { $yearCounts[$m.Year] = 1 }
}
$yc = ($yearCounts.GetEnumerator() | Sort-Object Name | ForEach-Object { ($_.Key + ":" + $_.Value) }) -join ', '
Write-Host ("year counts: " + $yc)
Write-Host ""

if (-not $Apply) {
  Write-Host "[DRY RUN] no changes. Re-run with -Apply to execute."
  return
}

# ---- execute moves ----
foreach ($m in $moves) {
  if ($m.Kind -eq 'literature') {
    $src = Join-Path $root ("literature\" + $m.Name)
    $dstDir = Join-Path $root ("wiki\sources\" + $m.Year)
  } else {
    $src = Join-Path $root ($m.Kind + "\" + $m.Name)
    $dstDir = Join-Path $root ($m.Kind + "\" + $m.Year)
  }
  New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
  Move-Item -LiteralPath $src -Destination (Join-Path $dstDir $m.Name)
}
Write-Host ("[APPLIED] moved " + $moves.Count + " files")

# ---- link rewrite: [[.../sources/Name]] -> [[Name]] ----
$re = [regex]'\[\[(?:[^\]|]*?/)?(?:wiki_array|wiki)/sources/([^\]|]+)(\|[^\]]*)?\]\]'
$enc = New-Object System.Text.UTF8Encoding($false)
$total = 0

Get-ChildItem -LiteralPath $root -Recurse -Filter '*.md' | Where-Object {
  ($_.FullName -notmatch '\\raw\\') -and
  ($_.FullName -notmatch '\\.obsidian\\') -and
  ($_.FullName -notmatch '\\.git\\')
} | ForEach-Object {
  $p = $_.FullName
  $txt = [System.IO.File]::ReadAllText($p)
  $new = $re.Replace($txt, '[[$1$2]]')
  if ($new -ne $txt) {
    [System.IO.File]::WriteAllText($p, $new, $enc)
    $c = $re.Matches($txt).Count
    $total += $c
    Write-Host ("  " + $p.Substring($root.Length + 1) + ": " + $c)
  }
}
Write-Host ("[APPLIED] link rewrites: " + $total + " occurrences")