#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
tests/test_gui.py — headless smoke test for gui.py

Requires a display (run under `xvfb-run` in CI / headless environments):
    xvfb-run -a python3 tests/test_gui.py

Exercises: window construction, drag/drop-equivalent file staging,
non-font files being rejected, and a full install cycle (copy into a
throwaway fonts/ dir + invoke install.sh) with a fake $HOME so it never
touches your real fonts.
"""
import os
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("GDK_BACKEND", "x11")

REPO_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_DIR))

import gi  # noqa: E402

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # noqa: E402

PASS = 0
FAIL = 0


def ok(msg: str) -> None:
    global PASS
    print(f"  PASS {msg}")
    PASS += 1


def bad(msg: str) -> None:
    global FAIL
    print(f"  FAIL {msg}")
    FAIL += 1


def main() -> int:
    # Isolate from the real filesystem: fake $HOME, and point gui.py's
    # module-level FONTS_DIR/INSTALL_SCRIPT at a throwaway sandbox copy.
    import shutil

    workdir = Path(tempfile.mkdtemp())
    fake_home = workdir / "home"
    fake_home.mkdir()
    os.environ["HOME"] = str(fake_home)

    sandbox = workdir / "repo"
    sandbox.mkdir()
    shutil.copy2(REPO_DIR / "install.sh", sandbox / "install.sh")
    (sandbox / "install.sh").chmod(0o755)

    import gui as gui_module

    gui_module.REPO_DIR = sandbox
    gui_module.FONTS_DIR = sandbox / "fonts"
    gui_module.INSTALL_SCRIPT = sandbox / "install.sh"

    print("== window construction ==")
    win = gui_module.FontInstallerWindow()
    win.show_all()
    if win.get_title() == "Linux Font Installer":
        ok("window constructs with correct title")
    else:
        bad(f"unexpected title: {win.get_title()}")

    print("== file staging ==")
    font_file = workdir / "Test-Regular.ttf"
    font_file.write_bytes(b"placeholder font bytes for test")
    win.add_file(font_file)
    if len(win.pending_files) == 1:
        ok("valid .ttf file is staged")
    else:
        bad(f"expected 1 staged file, got {len(win.pending_files)}")

    not_a_font = workdir / "not_a_font.txt"
    not_a_font.write_text("hello")
    win.add_file(not_a_font)
    if len(win.pending_files) == 1:
        ok("non-font file is rejected (still 1 staged)")
    else:
        bad(f"non-font file was incorrectly staged: {len(win.pending_files)} total")

    dup = workdir / "Test-Regular.ttf"
    win.add_file(dup)
    if len(win.pending_files) == 1:
        ok("duplicate file is not double-staged")
    else:
        bad("duplicate file was staged twice")

    print("== clear ==")
    win.on_clear_clicked(None)
    if len(win.pending_files) == 0:
        ok("clear empties the staged file list")
    else:
        bad("clear did not empty the staged file list")

    print("== full install cycle ==")
    win.add_file(font_file)
    win.user_radio.set_active(True)
    win.on_install_clicked(None)

    deadline = time.time() + 15
    ctx = GLib.MainContext.default()
    while time.time() < deadline:
        while ctx.pending():
            ctx.iteration(False)
        status = win.status_label.get_text()
        if "Installed successfully" in status or "failed" in status.lower():
            break
        time.sleep(0.1)

    installed_dir = fake_home / ".local" / "share" / "fonts" / "custom-fonts"
    if (installed_dir / "Test-Regular.ttf").exists():
        ok("install cycle copies font into the fake user fonts dir")
    else:
        bad(f"expected font not found at {installed_dir}; status was: {win.status_label.get_text()}")

    win.destroy()
    shutil.rmtree(workdir, ignore_errors=True)

    print(f"\n{PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
