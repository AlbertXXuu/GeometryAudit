param(
    [ValidateSet('View', 'Web', 'Reconstruct')][string]$Mode = 'Web',
    [string]$Run = 'run-02'
)
$ErrorActionPreference = 'Stop'
$experimentRoot = $PSScriptRoot
if ($Run -notmatch '^[a-zA-Z0-9_-]+$') { throw 'Run must be a simple directory name.' }
$recording = Join-Path $experimentRoot "$Run/scene.rrd"
$viewer = Join-Path $experimentRoot 'viewer/rerun.exe'
if ($Mode -eq 'View') {
    if (!(Test-Path -LiteralPath $recording)) { throw "Missing recording: $recording" }
    & $viewer $recording
    if ($LASTEXITCODE -ne 0) { throw "Viewer failed: $LASTEXITCODE" }
    return
}
if ($Mode -eq 'Web') {
    if (!(Test-Path -LiteralPath $recording)) { throw "Missing recording: $recording" }
    Write-Host 'Open http://127.0.0.1:9092/?url=rerun%2Bhttp%3A%2F%2F127.0.0.1%3A9878%2Fproxy ; Ctrl+C stops this local server.'
    & $viewer --serve-web --bind 127.0.0.1 --port 9878 --web-viewer-port 9092 $recording
    if ($LASTEXITCODE -ne 0) { throw "Web viewer failed: $LASTEXITCODE" }
    return
}

# Reuses the verified local CUDA torch installation; creates no shared packages.
$workspaceRoot = (Resolve-Path (Join-Path $experimentRoot '../../../..')).Path
$temporaryRoot = Join-Path $workspaceRoot '.workspace/tmp/geometry-audit'
$temporaryVenv = Join-Path $temporaryRoot ('replay-' + [guid]::NewGuid().ToString('N'))
try {
    python -c "import torch; assert torch.__version__ == '2.5.1+cu118'; assert torch.cuda.is_available()"
    if ($LASTEXITCODE -ne 0) { throw 'Expected CUDA torch 2.5.1+cu118 in base Python. See README.' }
    python -m venv --system-site-packages $temporaryVenv
    if ($LASTEXITCODE -ne 0) { throw 'Venv creation failed.' }
    $pythonExe = Join-Path $temporaryVenv 'Scripts/python.exe'
    & $pythonExe -m pip install --no-cache-dir -r (Join-Path $experimentRoot 'requirements-replay.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    & $pythonExe (Join-Path $experimentRoot 'verify_artifacts.py') --inputs-only
    if ($LASTEXITCODE -ne 0) { throw 'Input integrity check failed.' }
    & $pythonExe (Join-Path $experimentRoot 'run_baseline.py') --output $Run
    if ($LASTEXITCODE -ne 0) { throw 'Inference failed; inspect the new run result and traceback.' }
} finally {
    if (Test-Path -LiteralPath $temporaryVenv) {
        $resolved = (Resolve-Path -LiteralPath $temporaryVenv).Path
        $allowed = [IO.Path]::GetFullPath($temporaryRoot) + [IO.Path]::DirectorySeparatorChar
        if (!$resolved.StartsWith($allowed, [StringComparison]::OrdinalIgnoreCase)) { throw 'Cleanup path outside task temporary root.' }
        $links = Get-ChildItem -LiteralPath $resolved -Recurse -Force | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }
        if ($links) { throw 'Cleanup stopped: unexpected link inside temporary venv.' }
        $active = Get-Process python* -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path.StartsWith($resolved, [StringComparison]::OrdinalIgnoreCase) }
        if ($active) { throw 'Cleanup stopped: temporary Python process still running.' }
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}
