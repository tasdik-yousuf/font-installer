# Linux Font Installer

A tiny, dependency-free shell script to install a collection of TrueType/OpenType fonts on Linux — for the current user or system-wide — using standard [fontconfig](https://www.freedesktop.org/wiki/Software/fontconfig/) conventions.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## What it does

- Copies every `.ttf` / `.otf` file in [`fonts/`](./fonts) into:
  - `~/.local/share/fonts/custom-fonts` (default, per-user, no root needed), or
  - `/usr/share/fonts/truetype/custom-fonts` (with `--system`, available to all users)
- Runs `fc-cache -f` to rebuild the font cache so apps pick up the fonts immediately
- Works on any distro with `bash` + `fontconfig` (Ubuntu/Debian, Fedora, Arch, etc.)
- Works with **any** font collection — this isn't tied to a specific language or script. Drop in whatever `.ttf`/`.otf` files you have.

## Quick start

```bash
git clone https://github.com/tasdik-yousuf/bangla-fonts-installer.git
cd bangla-fonts-installer
./install.sh
```

That's it — the fonts are installed for your user account. Verify with:

```bash
fc-list | grep -i "<font family name>"
```

## Usage

```
./install.sh              # install for current user only (default, no sudo needed)
./install.sh --system     # install system-wide for all users (requires sudo)
./install.sh --list       # list the fonts that would be installed
./install.sh --uninstall  # remove fonts installed by this script
./install.sh -h|--help    # show help
```

## Adding your own fonts

Drop any `.ttf` or `.otf` files into [`fonts/`](./fonts) and re-run `./install.sh`. The script picks up every font file in that directory — no code changes needed.

## Testing

The repo includes an automated test suite that runs `install.sh` in an isolated sandbox — a temp `$HOME` and a temp copy of the script — so it never touches your real fonts or `~/.local/share/fonts`. It covers `--list`, `--help`, a real install, re-running install (idempotency), `--uninstall`, uninstalling when nothing's installed, an empty `fonts/` folder, and an unknown flag.

```bash
./tests/test.sh
```

This also runs automatically on every push/PR via GitHub Actions (see the CI badge above), alongside a [ShellCheck](https://www.shellcheck.net/) lint pass.

Note the test suite only exercises the script's *logic* (file discovery, copying, cleanup) using placeholder files — it can't verify that a real font's glyphs render correctly. For that, install a real font and check it visually in an app (LibreOffice, GIMP, etc.).

## Repository layout

```
bangla-fonts-installer/
├── fonts/          # put your .ttf/.otf files here
├── tests/
│   └── test.sh     # automated test suite (safe, isolated sandbox)
├── install.sh      # install / uninstall / list
├── LICENSE
└── README.md
```

## License

This project is licensed under the [MIT License](./LICENSE) — see the LICENSE file for the full text. In short: you're free to use, copy, modify, merge, publish, distribute, sublicense, and sell copies, as long as the copyright notice and license text are included in copies or substantial portions of the software.

The MIT License applies to the code in this repository (`install.sh`, `tests/test.sh`, and supporting tooling). **Font files you place in `fonts/` are not covered by this project's license** — each font family carries whatever license its original designer/foundry chose (e.g. SIL Open Font License, Apache 2.0, a proprietary EULA, etc.). If you're distributing this repo publicly with actual font files included, add a `fonts/LICENSES.md` listing each font's name, source, and license, and only include fonts you have the right to redistribute.

## Troubleshooting

- **Fonts don't show up in an app after installing**: some apps (especially Electron/GTK apps and browsers) cache their own font list — restart the app, or log out/in.
- **`fc-cache: command not found`**: install fontconfig, e.g. `sudo apt install fontconfig` on Debian/Ubuntu.
- **Permission denied on `--system`**: the script uses `sudo` automatically when needed; make sure your user has sudo rights.
