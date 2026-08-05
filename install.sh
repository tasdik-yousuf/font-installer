#!/usr/bin/env bash
#
# install.sh — Install Bangla fonts from this repo onto a Linux system.
#
# Usage:
#   ./install.sh              # install for current user only (default, no sudo needed)
#   ./install.sh --system     # install system-wide for all users (requires sudo)
#   ./install.sh --list       # list the fonts that would be installed
#   ./install.sh --uninstall  # remove fonts installed by this script
#   ./install.sh -h | --help  # show help
#
# The script copies every .ttf/.otf file found in ./fonts into the
# appropriate fontconfig directory and rebuilds the font cache with fc-cache.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FONTS_SRC="${REPO_DIR}/fonts"
COLLECTION_NAME="bangla-fonts"

USER_FONT_DIR="${HOME}/.local/share/fonts/${COLLECTION_NAME}"
SYSTEM_FONT_DIR="/usr/share/fonts/truetype/${COLLECTION_NAME}"

MODE="user"
ACTION="install"

# ---------- helpers ----------

log()  { printf '\033[1;32m==>\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m==> warning:\033[0m %s\n' "$1" >&2; }
die()  { printf '\033[1;31m==> error:\033[0m %s\n' "$1" >&2; exit 1; }

usage() {
    sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
}

find_fonts() {
    # Prints matching font files, one per line. Empty output if none found.
    find "${FONTS_SRC}" -maxdepth 1 -type f \( -iname '*.ttf' -o -iname '*.otf' \) 2>/dev/null | sort
}

refresh_cache() {
    if command -v fc-cache >/dev/null 2>&1; then
        log "Refreshing font cache (fc-cache)..."
        fc-cache -f "$1" >/dev/null
    else
        warn "fc-cache not found; install fontconfig to refresh the font cache automatically."
        warn "You may need to log out/in or reboot for the fonts to be picked up."
    fi
}

# ---------- argument parsing ----------

while [[ $# -gt 0 ]]; do
    case "$1" in
        --system)
            MODE="system"
            shift
            ;;
        --user)
            MODE="user"
            shift
            ;;
        --list)
            ACTION="list"
            shift
            ;;
        --uninstall)
            ACTION="uninstall"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "Unknown option: $1 (see --help)"
            ;;
    esac
done

TARGET_DIR="${SYSTEM_FONT_DIR}"
[[ "${MODE}" == "user" ]] && TARGET_DIR="${USER_FONT_DIR}"

# ---------- actions ----------

if [[ "${ACTION}" == "list" ]]; then
    mapfile -t FONT_FILES < <(find_fonts)
    if [[ ${#FONT_FILES[@]} -eq 0 ]]; then
        warn "No .ttf/.otf files found in ${FONTS_SRC}"
        exit 0
    fi
    log "Found ${#FONT_FILES[@]} font file(s):"
    printf '  - %s\n' "${FONT_FILES[@]##*/}"
    exit 0
fi

if [[ "${ACTION}" == "uninstall" ]]; then
    for dir in "${USER_FONT_DIR}" "${SYSTEM_FONT_DIR}"; do
        if [[ -d "${dir}" ]]; then
            if [[ "${dir}" == "${SYSTEM_FONT_DIR}" && "${EUID}" -ne 0 ]]; then
                log "Removing ${dir} (needs sudo)..."
                sudo rm -rf "${dir}"
            else
                log "Removing ${dir}..."
                rm -rf "${dir}"
            fi
        fi
    done
    refresh_cache "${HOME}"
    log "Uninstall complete."
    exit 0
fi

# --- install ---

mapfile -t FONT_FILES < <(find_fonts)
if [[ ${#FONT_FILES[@]} -eq 0 ]]; then
    die "No .ttf/.otf files found in ${FONTS_SRC}. Add your font files there and re-run."
fi

log "Installing ${#FONT_FILES[@]} font file(s) to ${TARGET_DIR} (${MODE} install)"

if [[ "${MODE}" == "system" ]]; then
    if [[ "${EUID}" -ne 0 ]]; then
        log "System-wide install requires sudo, you may be prompted for your password."
        sudo mkdir -p "${TARGET_DIR}"
        sudo cp -f "${FONT_FILES[@]}" "${TARGET_DIR}/"
        sudo chmod 644 "${TARGET_DIR}"/*
    else
        mkdir -p "${TARGET_DIR}"
        cp -f "${FONT_FILES[@]}" "${TARGET_DIR}/"
        chmod 644 "${TARGET_DIR}"/*
    fi
else
    mkdir -p "${TARGET_DIR}"
    cp -f "${FONT_FILES[@]}" "${TARGET_DIR}/"
    chmod 644 "${TARGET_DIR}"/*
fi

refresh_cache "${HOME}"

log "Done. Installed fonts:"
printf '  - %s\n' "${FONT_FILES[@]##*/}"
log "Verify with: fc-list | grep -i bangla   (or search for a specific family name)"
