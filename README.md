# Linux Font Installer

A font installer for Linux — drag-and-drop GUI or one-line CLI — that installs a collection of TrueType/OpenType fonts for the current user or system-wide, using standard [fontconfig](https://www.freedesktop.org/wiki/Software/fontconfig/) conventions.

[![CI](https://github.com/tasdik-yousuf/font-installer/actions/workflows/ci.yml/badge.svg)](https://github.com/tasdik-yousuf/font-installer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## What it does

- Copies every `.ttf` / `.otf` file in `fonts/` into:
  - `~/.local/share/fonts/custom-fonts` (default, per-user, no root needed), or
  - `/usr/share/fonts/truetype/custom-fonts` (with `--system`, available to all users)
- Runs `fc-cache -f` to rebuild the font cache so apps pick up the fonts immediately
- Works on any distro with `bash` + `fontconfig` (Ubuntu/Debian, Fedora, Arch, etc.)
- Works with **any** font collection — this isn't tied to a specific language or script. Drop in whatever `.ttf`/`.otf` files you have.
- Ships with **no fonts included** — this is just the installer. You bring your own `.ttf`/`.otf` files, either by dragging them into the GUI or dropping them into `fonts/` for the CLI.

## Requirements

- **CLI (`install.sh`)**: just `bash` + [fontconfig](https://www.freedesktop.org/wiki/Software/fontconfig/) — both are already present on virtually every Linux desktop. No Python, no pip, nothing else to install.
- **GUI (`gui.py`)**: additionally needs GTK3 + PyGObject. Install these through your distro's package manager (recommended — see below), or via `requirements.txt` with pip if you'd rather use a virtualenv.

```bash
# Debian/Ubuntu
sudo apt install python3-gi gir1.2-gtk-3.0

# Arch Linux
sudo pacman -S python-gobject gtk3
```

If you'd rather use pip (e.g. inside a virtualenv), see [`requirements.txt`](./requirements.txt) — note it needs system GTK dev headers to build and is not the recommended path on Linux; the apt/pacman install above is simpler and avoids that entirely.

## Quick start

```bash
git clone https://github.com/tasdik-yousuf/font-installer.git
cd font-installer
```

Add your own `.ttf`/`.otf` files into the `fonts/` folder (created automatically the first time you run `install.sh` or `gui.py` — see [Adding your own fonts](#adding-your-own-fonts) below), then:

```bash
./install.sh
```

That's it — the fonts are installed for your user account. Verify with:

```bash
fc-list | grep -i "<font family name>"
```

## GUI

Prefer clicking over typing? There's a drag-and-drop desktop app too.

**Run it:**
```bash
./gui.py
```

Drag `.ttf`/`.otf` files onto the window (or click **Browse**), choose *just for me* or *all users*, and click **Install Fonts**. It's just a thin front-end — under the hood it copies your dropped files into `fonts/` and calls `install.sh`, the same script and logic covered by the test suite below.

Want it in your applications menu instead of the terminal? Edit the `Exec=` line in [`font-installer.desktop`](./font-installer.desktop) to point at your clone's absolute path, then copy it to `~/.local/share/applications/`.

## Usage (CLI)

```
./install.sh              # install for current user only (default, no sudo needed)
./install.sh --system     # install system-wide for all users (requires sudo)
./install.sh --list       # list the fonts that would be installed
./install.sh --uninstall  # remove fonts installed by this script
./install.sh -h|--help    # show help
```

## Adding your own fonts

`fonts/` is not tracked in git — it's a plain drop folder, created automatically the first time you run `install.sh` or `gui.py`. Drop any `.ttf` or `.otf` files into it (via the GUI's drag-and-drop, or manually) and re-run `./install.sh`. The script picks up every font file in that directory — no code changes needed.

## Testing

The repo includes an automated test suite that runs `install.sh` in an isolated sandbox — a temp `$HOME` and a temp copy of the script — so it never touches your real fonts or `~/.local/share/fonts`. It covers `--list`, `--help`, a real install, re-running install (idempotency), `--uninstall`, uninstalling when nothing's installed, an empty `fonts/` folder, and an unknown flag.

```bash
./tests/test.sh
```

This also runs automatically on every push/PR via GitHub Actions (see the CI badge above), alongside a [ShellCheck](https://www.shellcheck.net/) lint pass.

Note the test suite only exercises the script's *logic* (file discovery, copying, cleanup) using placeholder files — it can't verify that a real font's glyphs render correctly. For that, install a real font and check it visually in an app (LibreOffice, GIMP, etc.).

The GUI has its own headless smoke test (requires `python3-gi`, `gir1.2-gtk-3.0`, and `xvfb`), covering window construction, file staging/rejection/dedup, clearing, and a full install cycle:

```bash
xvfb-run -a python3 tests/test_gui.py
```

This also runs in CI as a separate job.

## Repository layout

```
font-installer/
├── tests/
│   ├── test.sh              # automated test suite for install.sh (safe, isolated sandbox)
│   └── test_gui.py          # headless smoke test for the GUI (safe, isolated sandbox)
├── install.sh                # install / uninstall / list
├── gui.py                     # drag-and-drop GTK front-end for install.sh
├── font-installer.desktop     # optional applications-menu launcher
├── requirements.txt            # optional pip deps for gui.py (see Requirements above)
├── LICENSE
└── README.md

fonts/                          # NOT tracked in git — created automatically, drop your fonts here
```

## License

This project is licensed under the [MIT License](./LICENSE) — see the LICENSE file for the full text. In short: you're free to use, copy, modify, merge, publish, distribute, sublicense, and sell copies, as long as the copyright notice and license text are included in copies or substantial portions of the software.

The MIT License applies to the code in this repository (`install.sh`, `gui.py`, `tests/`, and supporting tooling). **Font files you place in `fonts/` are not covered by this project's license** — each font family carries whatever license its original designer/foundry chose (e.g. SIL Open Font License, Apache 2.0, a proprietary EULA, etc.). If you're distributing your own fonts alongside this installer, keep track of each font's name, source, and license separately, and only include fonts you have the right to redistribute.

## Troubleshooting

- **Fonts don't show up in an app after installing**: some apps (especially Electron/GTK apps and browsers) cache their own font list — restart the app, or log out/in.
- **`fc-cache: command not found`**: install fontconfig, e.g. `sudo apt install fontconfig` on Debian/Ubuntu.
- **Permission denied on `--system`**: the script uses `sudo` automatically when needed; make sure your user has sudo rights.
- **GUI won't launch / `ModuleNotFoundError: No module named 'gi'`**: install the GTK bindings listed under [Requirements](#requirements) for your distro.
- **GUI's "all users" install doesn't prompt for a password**: it uses `pkexec` for a graphical prompt if available, falling back to a plain `sudo` call (which needs a terminal) otherwise. If neither is available or configured, run `./install.sh --system` directly in a terminal instead.

