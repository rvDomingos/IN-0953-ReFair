# Download GloVe 6B 100d vectors required by REFAIR.py.
# Windows PowerShell version.
# Usage: powershell -ExecutionPolicy Bypass -File scripts\download_glove.ps1

$ErrorActionPreference = "Stop"

$Here = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Root = Resolve-Path (Join-Path $Here "..")

$GloveUrl = "https://nlp.stanford.edu/data/glove.6B.zip"
$TargetFiles = @(
    Join-Path $Root "models\glove.6B.100d.txt"
    Join-Path $Root "ReFair-App\refair-server\models\glove.6B.100d.txt"
)

$NeedDownload = $false
foreach ($f in $TargetFiles) {
    if (-not (Test-Path $f)) {
        $NeedDownload = $true
        break
    }
}

if (-not $NeedDownload) {
    Write-Host "GloVe already present in both target locations. Nothing to do."
    exit 0
}

$TmpDir = New-Item -ItemType Directory -Path ([System.IO.Path]::GetTempPath()) -Name ("glove_" + [Guid]::NewGuid())
try {
    $Zip = Join-Path $TmpDir.FullName "glove.6B.zip"
    Write-Host "Downloading GloVe 6B from $GloveUrl (~822 MB compressed) ..."
    Invoke-WebRequest -Uri $GloveUrl -OutFile $Zip -UseBasicParsing

    Write-Host "Extracting glove.6B.100d.txt ..."
    Expand-Archive -Path $Zip -DestinationPath $TmpDir.FullName -Force
    $Extracted = Join-Path $TmpDir.FullName "glove.6B.100d.txt"

    foreach ($f in $TargetFiles) {
        $Dir = Split-Path -Parent $f
        if (-not (Test-Path $Dir)) {
            New-Item -ItemType Directory -Path $Dir | Out-Null
        }
        Copy-Item -Path $Extracted -Destination $f -Force
        Write-Host "Wrote $f"
    }

    Write-Host "Done."
}
finally {
    Remove-Item -Recurse -Force $TmpDir.FullName
}
