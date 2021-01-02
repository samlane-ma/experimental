#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango
import socket
import threading
import time
import queue


class FindMyPIClient:
    def __init__(self):
        self.ip_prefix = self._get_ip_prefix()
        self.max_processes = 255  # max number of threads to scan network
        self.timeout = 1          # how many seconds to wait for each ip

    def _get_ip_prefix(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0].split('.')
        except Exception:
            IP = ['127','0','0']
        finally:
            s.close()
        IP_prefix = "{}.{}.{}.".format(IP[0],IP[1],IP[2])
        return IP_prefix

    def _scan(self, ip_queue, results):
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        while True:
            ip = ip_queue.get()
            if ip is None:
                break
            try:
                sock.sendto("Are you a PI?".encode("utf-8"), (ip,8888))
                response = sock.recvfrom(4096)
                msgdata = response[0].decode("utf-8")
                sender=(response[1][0])
                msg = "{},{}".format(sender,msgdata)
                # if local machine is running on a PI with server active,
                # only don't add the localhost ip if there is a real IP 
                if sender == "127.0.0.1":
                    if self.ip_prefix == "127.0.0.":
                        results.put(msg)
                else:
                    results.put(msg)
            except (socket.timeout, OSError) as e:
                pass
        sock.close()

    def look_for_pi(self):
        self.ip_prefix = self._get_ip_prefix()
        ip_queue = queue.Queue()
        results = queue.Queue()
        pool = []
        threadcount = self.max_processes
        # if IP address is 127.0.0.1, just scan it, don't scan entire subnet
        if self.ip_prefix == '127.0.0.':
            threadcount = 1
            ip_queue.put('127.0.0.1')
        else:
            for i in range(1, 255):
                ip_queue.put(self.ip_prefix + '{0}'.format(i))
        for i in range(threadcount):
            t = threading.Thread(target=self._scan, args=(ip_queue,results), daemon=True)
            pool.append(t)
        for i in range(threadcount):
            ip_queue.put(None)
        for p in pool:
            p.start()
        for p in pool:
            p.join()
        return results

def search(pi_liststore,findmypi,freq):
    while True:
        pi_list = []
        found = findmypi.look_for_pi()
        while not found.empty():
            match = found.get().split(',')
            # if a machine answers twice (ie. if it's on wifi and ethernet)
            # only add the ip once (unlikely, but possible)
            if not match in pi_list:
                pi_list.append(match)
        GLib.idle_add(update_list,pi_liststore,pi_list)
        time.sleep(freq)

def update_list(pi_liststore,pi_list):
    to_remove = []
    # Search liststore, generate list of iterations to be removed
    # Also removes existing PIs from the list of PIs to add
    iter_child = pi_liststore.get_iter_first()
    tree_path = None
    while iter_child:
        in_list = False
        ip = pi_liststore.get_value(iter_child, 0)
        for pi in pi_list:
            if pi[0] == ip:
                in_list = True
                pi_list.remove(pi)
        if not in_list:
            to_remove.append(iter_child)
        iter_child = pi_liststore.iter_next(iter_child)

    for child in to_remove:
         pi_liststore.remove(child)

    # Adds missing PIs to liststore
    for pi in pi_list:
        pi_liststore.append(pi)
            
def on_refresh_clicked(button):
    pi_list = []
    found = findmypi.look_for_pi()
    while not found.empty():
        match = found.get().split(',')
        # if a machine answers twice (ie. if it's on wifi and ethernet)
        # only add the ip once (unlikely, but possible)
        if not match in pi_list:
            pi_list.append(match)
    GLib.idle_add(update_list,pi_liststore,pi_list)

def on_copyip_clicked(button):
    ip = get_value_at_col(pi_treeview,0)
    if ip != "":
        clipboard.set_text(ip,-1)

def get_value_at_col(tree,column):
    value = ""
    view_selection = tree.get_selection()
    (model,tree_iter) = view_selection.get_selected()
    if tree_iter != None:
        value = model.get_value(tree_iter,column)
    return value


def on_window_destroy(*args):
    Gtk.main_quit()

if __name__=="__main__":

    fields = ['IP','Host Name','Model']
    frequency = 30

    findmypi = FindMyPIClient()
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    window = Gtk.Window()
    window.set_title("Find My PI")
    vbox = Gtk.VBox()
    window.add(vbox)
    window.set_border_width(10)
    window.connect("destroy",on_window_destroy)

    pi_liststore = Gtk.ListStore(str, str, str)
    pi_treeview = Gtk.TreeView(model=pi_liststore)
    pi_treeview.set_size_request(290,150)
    for i, field in enumerate(fields):
        cell = Gtk.CellRendererText()
        if i == 0:
            cell.props.weight_set = True
            cell.props.weight = Pango.Weight.BOLD
        col = Gtk.TreeViewColumn(field, cell, text=i)
        col.set_sort_column_id(i)
        if i == 2:
            col.set_min_width(300)
        else:
            col.set_min_width(130)
        pi_treeview.append_column(col)
    vbox.add(pi_treeview)

    button_refresh = Gtk.Button(label="Refresh")
    button_refresh.connect("clicked",on_refresh_clicked)

    button_copy = Gtk.Button(label="Copy IP")
    button_copy.connect("clicked",on_copyip_clicked)

    bottom_grid = Gtk.Grid()
    bottom_grid.attach(button_refresh,0,0,1,1)
    bottom_grid.attach(button_copy,1,0,1,1)
    vbox.add(bottom_grid)

    window.show_all()

    thread = threading.Thread(target=search, args=(pi_liststore, findmypi, frequency),
                              daemon=True)
    thread.start()

    Gtk.main()
