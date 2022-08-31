#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import apthelper

buttons = []
spinner = Gtk.Spinner()
status_label = Gtk.Label(label="")

def enable_buttons():
    for button in buttons:
        button.set_sensitive(True)
    spinner.stop()
    status_label.set_text("")


def on_button_clicked(button, apt, method, entry):
    button.set_sensitive(False)
    spinner.start()
    status_label.set_text("Please wait...")
    items = entry.get_text().replace(' ','').split(',')
    if method == "install":
        apt.set_packages(install=items)
    elif method == "remove":
        apt.set_packages(remove=items)
    elif method == "purge":
        apt.set_packages(purge=items)
    apt.run_apt(run_success=enable_buttons, run_failure=enable_buttons)



def on_runall_clicked (button, apt, install, remove, purge):
    for button in buttons:
        button.set_sensitive(False)
    spinner.start()
    status_label.set_text("Please wait...")
    apt.set_packages(install = install.get_text().replace(' ','').split(','),
                     remove = remove.get_text().replace(' ','').split(','),
                     purge = purge.get_text().replace(' ','').split(','))
    apt.run_apt(run_success=enable_buttons, run_failure=enable_buttons)


if __name__ == "__main__":

    apt = apthelper.AptHelper()

    window = Gtk.Window()

    grid = Gtk.Grid()
    window.add(grid)

    # If we want the dialog box to prevent the app from being used while running
    # apt.modal = True
    # apt.window = window

    entry_install = Gtk.Entry()
    button_install = Gtk.Button(label="Install")
    entry_remove = Gtk.Entry()
    button_remove = Gtk.Button(label="Remove")
    entry_purge = Gtk.Entry()
    button_purge = Gtk.Button(label="Purge")
    status_label = Gtk.Label(label="")

    button_runall = Gtk.Button(label="Process all")

    buttons.append(button_install)
    buttons.append(button_remove)
    buttons.append(button_purge)
    buttons.append(button_runall)

    grid.attach(entry_install,0,0,2,1)
    grid.attach(button_install,2,0,1,1)
    grid.attach(entry_remove,0,1,2,1)
    grid.attach(button_remove,2,1,1,1)
    grid.attach(entry_purge,0,2,2,1)
    grid.attach(button_purge,2,2,1,1)

    grid.attach(button_runall, 1,3,1,1)

    grid.attach(status_label,0,4,2,1)
    grid.attach(spinner,2,4,1,1)

    window.connect("destroy", Gtk.main_quit)
    button_install.connect("clicked", on_button_clicked, apt, "install", entry_install)
    button_remove.connect("clicked", on_button_clicked, apt, "remove", entry_remove)
    button_purge.connect("clicked", on_button_clicked, apt, "purge", entry_purge)
    button_runall.connect("clicked", on_runall_clicked, apt, entry_install, entry_remove, entry_purge)

    window.show_all()
    Gtk.main()
