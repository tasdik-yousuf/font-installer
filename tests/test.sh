#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# tests/test.sh — automated test suite for install.sh
#
# Runs install.sh inside an isolated sandbox (a temp HOME + a temp copy of
# the script and fonts/ dir), so it never touches your real
# ~/.local/share/fonts or the repo's own fonts/ folder.
#
# Usage: ./tests/test.sh

set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "${WORKDIR}"' EXIT

PASS=0
FAIL=0

ok()      { printf '  \033[1;32mPASS\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
bad()     { printf '  \033[1;31mFAIL\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }
skip()    { printf '  \033[1;33mSKIP\033[0m %s\n' "$1"; }
section() { printf '\n\033[1;34m== %s ==\033[0m\n' "$1"; }

# ---------- isolated sandbox ----------
export HOME="${WORKDIR}/home"
mkdir -p "${HOME}"

SANDBOX="${WORKDIR}/repo"
mkdir -p "${SANDBOX}/fonts"
cp "${REPO_DIR}/install.sh" "${SANDBOX}/install.sh"
chmod +x "${SANDBOX}/install.sh"
cd "${SANDBOX}"

INSTALLED_DIR="${HOME}/.local/share/fonts/custom-fonts"

make_dummy_font() {
    # Content doesn't matter here — these tests exercise file discovery,
    # copy, cache-refresh, and cleanup logic, not real glyph rendering.
    printf 'placeholder font content for test discovery' > "fonts/$1"
}

# ---------- shellcheck (static analysis) ----------
section "shellcheck"
if command -v shellcheck >/dev/null 2>&1; then
    if shellcheck "${REPO_DIR}/install.sh" >/tmp/shellcheck.out 2>&1; then
        ok "shellcheck clean"
    else
        bad "shellcheck reported issues (see /tmp/shellcheck.out)"
        cat /tmp/shellcheck.out
    fi
else
    skip "shellcheck not installed"
fi

# ---------- --help ----------
section "--help"
if ./install.sh --help | grep -qi "Usage:"; then
    ok "help text prints"
else
    bad "help text missing or broken"
fi

# ---------- empty fonts/ folder ----------
section "empty fonts/ folder should fail cleanly"
if ./install.sh >/tmp/empty_install.out 2>&1; then
    bad "install succeeded on empty fonts/ (it should have refused)"
else
    if grep -qi "no .ttf" /tmp/empty_install.out; then
        ok "clear error message on empty fonts/"
    else
        bad "failed, but without a clear error message"
    fi
fi

section "--list with no fonts present"
if ./install.sh --list 2>&1 | grep -qi "no .ttf"; then
    ok "--list warns when no fonts are present"
else
    bad "--list did not warn on empty fonts/"
fi

# ---------- --list with fonts present ----------
section "--list with fonts present"
make_dummy_font "Test-Regular.ttf"
make_dummy_font "Test-Bold.ttf"
LIST_OUT="$(./install.sh --list)"
if echo "${LIST_OUT}" | grep -q "Test-Regular.ttf" && echo "${LIST_OUT}" | grep -q "Test-Bold.ttf"; then
    ok "--list detects all font files in fonts/"
else
    bad "--list missed one or more font files"
fi

# ---------- user install ----------
section "user install (--user)"
if ./install.sh --user >/tmp/install.out 2>&1; then
    if [[ -f "${INSTALLED_DIR}/Test-Regular.ttf" && -f "${INSTALLED_DIR}/Test-Bold.ttf" ]]; then
        ok "user install copies all fonts to ~/.local/share/fonts/custom-fonts"
    else
        bad "user install ran but expected files are missing"
    fi
else
    bad "user install exited non-zero"
    cat /tmp/install.out
fi

# ---------- idempotency ----------
section "idempotency (installing twice)"
if ./install.sh --user >/tmp/install2.out 2>&1; then
    COUNT=$(find "${INSTALLED_DIR}" -type f | wc -l)
    if [[ "${COUNT}" -eq 2 ]]; then
        ok "re-running install does not duplicate files (still 2)"
    else
        bad "unexpected file count after second install: ${COUNT} (expected 2)"
    fi
else
    bad "second install run failed"
fi

# ---------- uninstall ----------
section "uninstall"
if ./install.sh --uninstall >/tmp/uninstall.out 2>&1; then
    if [[ ! -d "${INSTALLED_DIR}" ]]; then
        ok "uninstall removes the installed fonts directory"
    else
        bad "uninstall ran but left files behind"
    fi
else
    bad "uninstall exited non-zero"
fi

section "uninstall when nothing is installed (should not crash)"
if ./install.sh --uninstall >/tmp/uninstall2.out 2>&1; then
    ok "uninstall is safe to run when nothing is installed"
else
    bad "uninstall crashed with nothing installed"
fi

# ---------- unknown flag ----------
section "unknown flag is rejected"
if ./install.sh --bogus-flag >/tmp/unknown.out 2>&1; then
    bad "unknown flag was silently accepted (should error)"
else
    ok "unknown flag rejected with an error"
fi

# ---------- summary ----------
printf '\n\033[1;36m%s passed, %s failed\033[0m\n' "${PASS}" "${FAIL}"
[[ "${FAIL}" -eq 0 ]]
