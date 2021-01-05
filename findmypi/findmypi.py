#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from findmypiclient import FindMyPITreeView, FindMyPIClient
import sys

def print_list(pi_search):
    print('\nPIs found by mac address:')
    print('IP Address       Mac Address        Presumed Model')
    print('---------------  -----------------  -------------------------')
    for pi in pi_search.get_list_from_mac():
        print('{:<15}  {}  {}'.format(pi[0],pi[1],pi[2]))
    print('\nPIs found by UDP server:')
    print('IP Address       Host Name          Reported Model')
    print('---------------  -----------------  -------------------------')
    for pi in pi_search.get_list_from_server():
        print('{:<15}  {:<17}  {}'.format(pi[0],pi[1],pi[2]))
    print()

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

    if len(sys.argv) > 1:
        if sys.argv[1] == 'mac':
            method = 'mac'
        elif sys.argv[1] == 'server':
            method = 'server'
        elif sys.argv[1] == 'list':
            pi_search = FindMyPIClient()
            print_list(pi_search)
            exit(0)
        else:
            print('Starting in server mode')
            method = 'server'
    else:
        print('Starting in server mode')
        method = 'server'

    pi_treeview = FindMyPITreeView(method=method,frequency=15)
    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.add(pi_treeview)
    window = Gtk.Window()
    window.set_size_request(580,200)
    window.set_title("Find My PI")
    window.set_border_width(3)
    window.connect("destroy",on_window_destroy)

    bottom_grid = Gtk.Grid()
    button_refresh = Gtk.Button(label="Refresh")
    button_refresh.connect("clicked",on_refresh_clicked,pi_treeview)
    bottom_grid.attach(button_refresh,0,0,1,1)
    button_copy = Gtk.Button(label="Copy IP")
    button_copy.connect("clicked",on_copyip_clicked,pi_treeview)
    bottom_grid.attach(button_copy,1,0,1,1)

    vbox = Gtk.VBox()

    vbox.pack_start(scrolled_window, True, True, 3)
    vbox.pack_start(bottom_grid, False, False, 0)

    window.add(vbox)
    window.show_all()

    Gtk.main()
