$ErrorActionPreference = 'Stop'
$recording = Join-Path $PSScriptRoot 'run-518/scene.rrd'
$layout = Join-Path $PSScriptRoot 'run-518/viewer.rbl'
$viewer = Join-Path $PSScriptRoot '../round1/viewer/rerun.exe'
foreach ($file in @($recording, $layout, $viewer)) {
    if (!(Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing replay dependency: $file" }
}
Write-Host 'Open http://127.0.0.1:9092/?url=rerun%2Bhttp%3A%2F%2F127.0.0.1%3A9878%2Fproxy'
Write-Host 'Four frozen TUM views; drag the 3D pane to orbit. Ctrl+C stops the local server.'
& $viewer --serve-web --bind 127.0.0.1 --port 9878 --web-viewer-port 9092 $recording $layout
if ($LASTEXITCODE -ne 0) { throw "Replay viewer exited with code $LASTEXITCODE" }
