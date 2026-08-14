# install_tools.ps1 — Windows 安装 6 个安全 CLI 到 $SECURITY_TOOLS_HOME（默认 ~/security-tools）
# 用法（PowerShell）： .\install_tools.ps1
# 设计：本地离线、命令行调用不改上游；工具默认装 ~/security-tools。
$ErrorActionPreference = "Stop"

$TOOLS = $env:SECURITY_TOOLS_HOME
if (-not $TOOLS) { $TOOLS = Join-Path $HOME "security-tools" }
New-Item -ItemType Directory -Force -Path $TOOLS | Out-Null
$venv = Join-Path $TOOLS "venv"
if (-not (Test-Path $venv)) { python -m venv $venv }
$Scripts = Join-Path $venv "Scripts"
& "$Scripts\python.exe" -m pip install --upgrade pip
& "$Scripts\pip.exe" install -r "$PSScriptRoot\requirements.txt"

function Get-Bin($url, $name) {
  $zip = Join-Path $env:TEMP "dl_$name.zip"
  $dst = Join-Path $env:TEMP "binx_$name"
  Invoke-WebRequest -Uri $url -OutFile $zip
  Expand-Archive -Path $zip -DestinationPath $dst -Force
  Copy-Item -Path "$dst\*.exe" -Destination $TOOLS -Force
  Remove-Item $zip, $dst -Recurse -Force
  Write-Host "OK $name"
}

Get-Bin "https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_windows_x64.zip" "gitleaks"
Get-Bin "https://github.com/google/osv-scanner/releases/download/v2.4.0/osv-scanner_2.4.0_windows_amd64.zip" "osv-scanner"

Write-Host "INSTALL_DONE tools=$TOOLS"
