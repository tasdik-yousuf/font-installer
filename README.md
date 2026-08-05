# Bangla Fonts Installer

A tiny, dependency-free shell script to install a collection of Bangla (Bengali) TrueType/OpenType fonts on Linux — for the current user or system-wide — using standard [fontconfig](https://www.freedesktop.org/wiki/Software/fontconfig/) conventions.

[![CI](https://github.com/USERNAME/bangla-fonts-installer/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/bangla-fonts-installer/actions/workflows/ci.yml)

## What it does

- Copies every `.ttf` / `.otf` file in [`fonts/`](./fonts) into:
  - `~/.local/share/fonts/bangla-fonts` (default, per-user, no root needed), or
  - `/usr/share/fonts/truetype/bangla-fonts` (with `--system`, available to all users)
- Runs `fc-cache -f` to rebuild the font cache so apps pick up the fonts immediately
- Works on any distro with `bash` + `fontconfig` (Ubuntu/Debian, Fedora, Arch, etc.)

## Quick start

```bash
git clone https://github.com/USERNAME/bangla-fonts-installer.git
cd bangla-fonts-installer
./install.sh
```

That's it — the fonts are installed for your user account. Verify with:

```bash
fc-list | grep -i bangla
```

or search for a specific family name, e.g. `fc-list | grep -i "kalpurush"`.

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

Note the test suite only exercises the script's *logic* (file discovery, copying, cleanup) using placeholder files — it can't verify that a real font's glyphs render correctly. For that, install a real font and check it visually in an app (LibreOffice, GIMP, etc.), and see [Quick start](#quick-start) for manual/Docker testing options.

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

## Font licensing

The **installer script** in this repo is MIT licensed (see [LICENSE](./LICENSE)). The **font files themselves** may be under separate licenses set by their original designers/foundries (e.g. SIL Open Font License). If you're distributing this repo publicly, add a `fonts/LICENSES.md` noting the license and source of each font family you include, and only include fonts you have the right to redistribute.

## Troubleshooting

- **Fonts don't show up in an app after installing**: some apps (especially Electron/GTK apps and browsers) cache their own font list — restart the app, or log out/in.
- **`fc-cache: command not found`**: install fontconfig, e.g. `sudo apt install fontconfig` on Debian/Ubuntu.
- **Permission denied on `--system`**: the script uses `sudo` automatically when needed; make sure your user has sudo rights.

## License

MIT — see [LICENSE](./LICENSE).
