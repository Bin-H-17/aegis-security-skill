#!/usr/bin/env bash
# install_tools.sh — 跨平台安装 6 个安全 CLI 到 $SECURITY_TOOLS_HOME（默认 ~/security-tools）
# 用法： bash install_tools.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="${SECURITY_TOOLS_HOME:-$HOME/security-tools}"
mkdir -p "$TOOLS"
VENV="$TOOLS/venv"
if [ ! -d "$VENV" ]; then python3 -m venv "$VENV"; fi
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/pip" install -r "$HERE/requirements.txt"

OS="$(uname -s)"
if [ "$OS" = "Darwin" ]; then
  GLEAKS="gitleaks_8.30.1_darwin_arm64.tar.gz"; OSV="osv-scanner_2.4.0_macos_amd64.zip"
else
  GLEAKS="gitleaks_8.30.1_linux_x64.tar.gz"; OSV="osv-scanner_2.4.0_linux_amd64.zip"
fi

# gitleaks (tar.gz)
curl -sSL "https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/$GLEAKS" -o /tmp/g.tar.gz
( cd "$TOOLS" && tar xzf /tmp/g.tar.gz gitleaks 2>/dev/null || tar xzf /tmp/g.tar.gz )
# osv-scanner (zip)
curl -sSL "https://github.com/google/osv-scanner/releases/download/v2.4.0/$OSV" -o /tmp/o.zip
( cd /tmp && unzip -o o.zip >/dev/null && cp osv-scanner "$TOOLS/" )
echo "INSTALL_DONE tools=$TOOLS"
