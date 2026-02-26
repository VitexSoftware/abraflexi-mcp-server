#!/bin/bash
# Build an AppImage for abraflexi-mcp-server
#
# Requirements: wget, uv (or pip)
# Downloads:    portable CPython, appimagetool
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="${PROJECT_DIR}/build/appimage"
APPDIR="${BUILD_DIR}/AbraFlexi-MCP-Server.AppDir"

PY_VERSION="3.12"
PY_FULL="3.12.9"
ARCH="$(uname -m)"

echo "==> Cleaning previous build"
rm -rf "${BUILD_DIR}"
mkdir -p "${APPDIR}/usr"

# --- Portable CPython ---
echo "==> Downloading portable CPython ${PY_FULL}"
PY_ARCHIVE="cpython-${PY_FULL}+20250205-${ARCH}-unknown-linux-gnu-install_only_stripped.tar.gz"
PY_URL="https://github.com/indygreg/python-build-standalone/releases/download/20250205/${PY_ARCHIVE}"

if [ ! -f "${BUILD_DIR}/${PY_ARCHIVE}" ]; then
    wget -q --show-progress -O "${BUILD_DIR}/${PY_ARCHIVE}" "${PY_URL}"
fi
tar -xf "${BUILD_DIR}/${PY_ARCHIVE}" -C "${APPDIR}/usr" --strip-components=1

# Trim unnecessary pieces to keep the image small
rm -rf "${APPDIR}/usr/share/man" \
       "${APPDIR}/usr/share/doc" \
       "${APPDIR}/usr/lib/python${PY_VERSION}/test" \
       "${APPDIR}/usr/lib/python${PY_VERSION}/tkinter" \
       "${APPDIR}/usr/lib/python${PY_VERSION}/idlelib" \
       "${APPDIR}/usr/lib/python${PY_VERSION}/turtledemo" \
       "${APPDIR}/usr/lib/python${PY_VERSION}/ensurepip"

# --- Install application ---
echo "==> Installing abraflexi-mcp-server + dependencies"
"${APPDIR}/usr/bin/python3" -m pip install --no-cache-dir --upgrade pip 2>/dev/null
"${APPDIR}/usr/bin/python3" -m pip install --no-cache-dir "${PROJECT_DIR}" 2>/dev/null

# --- AppDir metadata ---
echo "==> Setting up AppDir metadata"
cp "${SCRIPT_DIR}/AppRun" "${APPDIR}/AppRun"
chmod +x "${APPDIR}/AppRun"

cp "${SCRIPT_DIR}/abraflexi-mcp-server.desktop" "${APPDIR}/abraflexi-mcp-server.desktop"
cp "${SCRIPT_DIR}/abraflexi-mcp-server.svg"     "${APPDIR}/abraflexi-mcp-server.svg"

# Icon in hicolor tree (required by some desktop environments)
ICON_DIR="${APPDIR}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${ICON_DIR}"
cp "${SCRIPT_DIR}/abraflexi-mcp-server.svg" "${ICON_DIR}/"

# --- appimagetool ---
APPIMAGETOOL="${BUILD_DIR}/appimagetool"
if [ ! -x "${APPIMAGETOOL}" ]; then
    echo "==> Downloading appimagetool"
    wget -q --show-progress -O "${APPIMAGETOOL}" \
        "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-${ARCH}.AppImage"
    chmod +x "${APPIMAGETOOL}"
fi

# --- Build the AppImage ---
echo "==> Packaging AppImage"
APPIMAGE_NAME="AbraFlexi-MCP-Server-$(grep '__version__' "${PROJECT_DIR}/abraflexi_mcp_server/__init__.py" | cut -d'"' -f2)-${ARCH}.AppImage"
ARCH="${ARCH}" "${APPIMAGETOOL}" --no-appstream "${APPDIR}" "${BUILD_DIR}/${APPIMAGE_NAME}"

echo ""
echo "==> Done: ${BUILD_DIR}/${APPIMAGE_NAME}"
ls -lh "${BUILD_DIR}/${APPIMAGE_NAME}"
