#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango
import socket
import threading
import time
import queue

class FindMyPIClient:
    def __init__(self):
        self.ip_prefix = self._get_ip_prefix()
        self.max_processes = 255
        self.timeout = 1

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
                msg = sock.recvfrom(4096)[0].decode("utf-8")
                results.put(msg)
            except (socket.timeout, OSError) as e:
                pass
        sock.close()

    def look_for_pi(self):
        self.ip_prefix = self._get_ip_prefix()
        ip_queue = queue.Queue()
        results = queue.Queue()
        pool = []
        for i in range(self.max_processes):
            t = threading.Thread(target=self._scan, args=(ip_queue,results), daemon=True)
            pool.append(t)
        for i in range(1, 255):
            ip_queue.put(self.ip_prefix + '{0}'.format(i))
        for p in pool:
            ip_queue.put(None)
        for p in pool:
            p.start()
        for p in pool:
            p.join()
        return results

def search(listmodel,findmypi,freq):
    while True:
        pi_list = []
        found = findmypi.look_for_pi()
        while not found.empty():
            match = found.get().split(',')
            pi_list.append(match)
        GLib.idle_add(update_list,listmodel,pi_list)
        time.sleep(freq)

def update_list(listmodel,pi_list):
    listmodel.clear()
    for i in range(len(pi_list)):
        listmodel.append(pi_list[i])

def on_window_destroy(*args):
    Gtk.main_quit()

if __name__=="__main__":

    fields = ['IP','Host Name','Model']
    frequency = 30

    findmypi = FindMyPIClient()

    window = Gtk.Window()
    window.set_default_size(250, 100)
    window.set_border_width(10)
    window.connect("destroy",on_window_destroy)
    listmodel = Gtk.ListStore(str, str, str)
    listmodel.append(["Searching","",""])
    view = Gtk.TreeView(model=listmodel)
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
        view.append_column(col)
    window.add(view)
    window.show_all()

    thread = threading.Thread(target=search, args=(listmodel, findmypi, frequency),
                              daemon=True)
    thread.start()

    Gtk.main()
