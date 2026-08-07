#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
gui.py — drag-and-drop GUI front-end for install.sh

Lets you drag .ttf/.otf files onto a window (or browse for them),
then installs them with one click by copying them into fonts/ and
invoking install.sh — the same script and logic covered by tests/test.sh.

Requirements:
  Debian/Ubuntu: sudo apt install python3-gi gir1.2-gtk-3.0
  Arch Linux:    sudo pacman -S python-gobject gtk3

Usage:
  ./gui.py
"""
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib  # noqa: E402

import shutil
import subprocess
import sys
import threading
from pathlib import Path
from urllib.parse import unquote, urlparse

REPO_DIR = Path(__file__).resolve().parent
FONTS_DIR = REPO_DIR / "fonts"
INSTALL_SCRIPT = REPO_DIR / "install.sh"
VALID_EXTENSIONS = {".ttf", ".otf"}


class FontInstallerWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Linux Font Installer")
        self.set_default_size(480, 440)
        self.set_border_width(12)

        self.pending_files: dict[str, Path] = {}

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        header = Gtk.Label()
        header.set_markup("<b>Drag and drop .ttf / .otf files below</b>")
        header.set_halign(Gtk.Align.START)
        vbox.pack_start(header, False, False, 0)

        # --- drop zone ---
        self.drop_area = Gtk.EventBox()
        self.drop_area.set_size_request(-1, 100)
        drop_label = Gtk.Label(label="Drop font files here\n(or use Browse below)")
        drop_label.set_justify(Gtk.Justification.CENTER)
        self.drop_area.add(drop_label)
        frame = Gtk.Frame()
        frame.add(self.drop_area)
        vbox.pack_start(frame, False, False, 0)

        self.drop_area.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.drop_area.drag_dest_add_uri_targets()
        self.drop_area.connect("drag-data-received", self.on_drag_data_received)

        # --- browse fallback ---
        browse_btn = Gtk.Button(label="Browse for font files...")
        browse_btn.connect("clicked", self.on_browse_clicked)
        vbox.pack_start(browse_btn, False, False, 0)

        # --- selected files list ---
        list_label = Gtk.Label(label="Selected fonts:")
        list_label.set_halign(Gtk.Align.START)
        vbox.pack_start(list_label, False, False, 0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(120)
        self.listbox = Gtk.ListBox()
        scrolled.add(self.listbox)
        vbox.pack_start(scrolled, True, True, 0)

        # --- install scope ---
        scope_box = Gtk.Box(spacing=10)
        self.user_radio = Gtk.RadioButton.new_with_label_from_widget(
            None, "Install for me only"
        )
        self.system_radio = Gtk.RadioButton.new_with_label_from_widget(
            self.user_radio, "Install for all users (needs sudo)"
        )
        scope_box.pack_start(self.user_radio, False, False, 0)
        scope_box.pack_start(self.system_radio, False, False, 0)
        vbox.pack_start(scope_box, False, False, 0)

        # --- action buttons ---
        btn_box = Gtk.Box(spacing=10)
        self.install_btn = Gtk.Button(label="Install Fonts")
        self.install_btn.get_style_context().add_class("suggested-action")
        self.install_btn.connect("clicked", self.on_install_clicked)
        clear_btn = Gtk.Button(label="Clear")
        clear_btn.connect("clicked", self.on_clear_clicked)
        btn_box.pack_start(self.install_btn, True, True, 0)
        btn_box.pack_start(clear_btn, False, False, 0)
        vbox.pack_start(btn_box, False, False, 0)

        # --- status line ---
        self.status_label = Gtk.Label(label="")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_line_wrap(True)
        vbox.pack_start(self.status_label, False, False, 0)

        self.connect("destroy", Gtk.main_quit)

    # ---------- file handling ----------

    def add_file(self, path: Path) -> None:
        if path.suffix.lower() not in VALID_EXTENSIONS:
            return
        if str(path) in self.pending_files:
            return
        self.pending_files[str(path)] = path
        row = Gtk.ListBoxRow()
        row.add(Gtk.Label(label=path.name, xalign=0))
        self.listbox.add(row)
        self.listbox.show_all()
        self.status_label.set_text("")

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        uris = data.get_uris()
        added_any = False
        for uri in uris:
            parsed = urlparse(uri)
            if parsed.scheme == "file":
                self.add_file(Path(unquote(parsed.path)))
                added_any = True
        if uris and not added_any:
            self.status_label.set_markup(
                "<span foreground='red'>Only .ttf/.otf files are accepted.</span>"
            )
        drag_context.finish(True, False, time)

    def on_browse_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select font files",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_select_multiple(True)

        filt = Gtk.FileFilter()
        filt.set_name("Font files (*.ttf, *.otf)")
        filt.add_pattern("*.ttf")
        filt.add_pattern("*.otf")
        dialog.add_filter(filt)

        if dialog.run() == Gtk.ResponseType.OK:
            for filename in dialog.get_filenames():
                self.add_file(Path(filename))
        dialog.destroy()

    def on_clear_clicked(self, button):
        self.pending_files.clear()
        for row in self.listbox.get_children():
            self.listbox.remove(row)
        self.status_label.set_text("")

    # ---------- install ----------

    def on_install_clicked(self, button):
        if not self.pending_files:
            self.status_label.set_markup(
                "<span foreground='red'>No fonts selected.</span>"
            )
            return

        self.install_btn.set_sensitive(False)
        self.status_label.set_text("Copying fonts...")

        FONTS_DIR.mkdir(parents=True, exist_ok=True)
        for path in self.pending_files.values():
            try:
                shutil.copy2(path, FONTS_DIR / path.name)
            except OSError as e:
                self.status_label.set_markup(
                    f"<span foreground='red'>Failed to copy {GLib.markup_escape_text(path.name)}: "
                    f"{GLib.markup_escape_text(str(e))}</span>"
                )
                self.install_btn.set_sensitive(True)
                return

        scope_flag = "--system" if self.system_radio.get_active() else "--user"
        self.status_label.set_text("Installing...")
        threading.Thread(target=self.run_install, args=(scope_flag,), daemon=True).start()

    def run_install(self, scope_flag: str) -> None:
        try:
            if scope_flag == "--system" and shutil.which("pkexec"):
                # pkexec gives a graphical polkit password prompt instead of
                # blocking on a terminal sudo prompt the GUI has no way to show.
                cmd = ["pkexec", str(INSTALL_SCRIPT), "--system"]
            else:
                cmd = [str(INSTALL_SCRIPT), scope_flag]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            success = result.returncode == 0
            message = result.stdout if success else (result.stderr or result.stdout)
        except Exception as e:  # noqa: BLE001 - surface any failure to the user
            success = False
            message = str(e)

        GLib.idle_add(self.on_install_finished, success, message)

    def on_install_finished(self, success: bool, message: str):
        self.install_btn.set_sensitive(True)
        if success:
            self.status_label.set_markup(
                "<span foreground='green'>Installed successfully. "
                "Restart open apps to see the new fonts.</span>"
            )
        else:
            trimmed = GLib.markup_escape_text(message.strip()[:400])
            self.status_label.set_markup(
                f"<span foreground='red'>Install failed:\n{trimmed}</span>"
            )
        return False


def main() -> None:
    if not INSTALL_SCRIPT.exists():
        print(f"error: install.sh not found at {INSTALL_SCRIPT}", file=sys.stderr)
        sys.exit(1)
    win = FontInstallerWindow()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
