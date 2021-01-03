#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from findmypiclient import FindMyPITreeView

def on_refresh_clicked(button,fpi):
    fpi.refresh_list()

def on_copyip_clicked(button,fpi):
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    ip = fpi.get_value_at_col(0)
    if ip != "":
        clipboard.set_text(ip,-1)

def on_window_destroy(*args):
    Gtk.main_quit()

if __name__=="__main__":

    pi_treeview = FindMyPITreeView(8888)
    window = Gtk.Window()
    window.set_title("Find My PI")
    window.set_border_width(10)
    window.connect("destroy",on_window_destroy)

    bottom_grid = Gtk.Grid()
    button_refresh = Gtk.Button(label="Refresh")
    button_refresh.connect("clicked",on_refresh_clicked,pi_treeview)
    bottom_grid.attach(button_refresh,0,0,1,1)
    button_copy = Gtk.Button(label="Copy IP")
    button_copy.connect("clicked",on_copyip_clicked,pi_treeview)
    bottom_grid.attach(button_copy,1,0,1,1)

    vbox = Gtk.VBox()

    vbox.add(pi_treeview)
    vbox.add(bottom_grid)

    window.add(vbox)
    window.show_all()

    Gtk.main()
