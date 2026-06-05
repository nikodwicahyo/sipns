#!/usr/bin/env bash
#
# build.sh — Build script SIPNS untuk Render.
# Dipanggil dari render.yaml -> buildCommand: "bash build.sh"
#
# Tahapan:
#   1) Update apt cache
#   2) Install system packages (WeasyPrint dependencies) dari Aptfile
#   3) Install Python dependencies dari requirements.txt
#
# Catatan:
#   - Pakai "bash build.sh" (bukan "./build.sh") agar tidak perlu chmod +x.
#   - libpango/libcairo/libffi WAJIB ada di runtime, kalau tidak
#     WeasyPrint akan raise OSError("cannot load library") saat generate PDF.
#
set -euo pipefail

echo "==> [1/3] apt-get update..."
apt-get update -qq

echo "==> [2/3] Install system packages (WeasyPrint)..."
# grep -v skip baris kosong & komentar; -x whole-line match.
PACKAGES=$(grep -vE '^\s*(#|$)' Aptfile | tr '\n' ' ')
apt-get install -y --no-install-recommends $PACKAGES
rm -rf /var/lib/apt/lists/*

echo "==> [3/3] Install Python dependencies..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

echo "==> Build complete. $(date -u)"
