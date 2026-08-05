# fonts/

Put your `.ttf` / `.otf` Bangla font files directly in this folder (no subfolders — the installer only scans the top level).

After adding files, run from the repo root:

```bash
./install.sh --list     # sanity check they're picked up
./install.sh            # install
```

## fonts/LICENSES.md

If you plan to push this repo publicly, create a `LICENSES.md` here listing, for each font family:

- Font name
- Source / foundry (e.g. Google Fonts, Omicron Lab, SIL)
- License (e.g. SIL Open Font License 1.1)
- Link to the original license text

This keeps redistribution clean and gives credit to the original type designers.
