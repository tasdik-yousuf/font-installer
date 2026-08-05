# fonts/

Put your `.ttf` / `.otf` font files directly in this folder (no subfolders — the installer only scans the top level).

After adding files, run from the repo root:

```bash
./install.sh --list     # sanity check they're picked up
./install.sh            # install
```

## Licensing note

This project's [MIT License](../LICENSE) covers the installer script only — not the fonts themselves. If you plan to push this repo publicly with real font files included, create a `fonts/LICENSES.md` here listing, for each font family:

- Font name
- Source / foundry (e.g. Google Fonts, a type foundry, SIL)
- License (e.g. SIL Open Font License 1.1)
- Link to the original license text

Only include fonts you have the right to redistribute.
