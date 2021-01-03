#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango
import socket
import threading
import time
import queue

class FindMyPIClient:

    def __init__(self, port):
        self.ip_prefix = self._get_ip_prefix()
        self.max_threads = 255  # max number of threads to scan network
        self.timeout = 1        # how many seconds to wait for each ip
        self.port = port

    def _get_ip_prefix(self):
        # Gets the client's IP prefix
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
        # Scans an IP from the queue and checks if it is a PI
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        while True:
            ip = ip_queue.get()
            if ip is None:
                break
            try:
                sock.sendto("Are you a PI?".encode("utf-8"), (ip,self.port))
                response = sock.recvfrom(4096)
                msgdata = response[0].decode("utf-8")
                sender=(response[1][0])
                msg = "{},{}".format(sender,msgdata)
                # If local machine is running on a PI with server active,
                # don't add the localhost ip if there is a real IP also.
                if sender == "127.0.0.1":
                    if self.ip_prefix == "127.0.0.":
                        # If you are not connected to a network and you are
                        # scanning your own IP (why?), it's ok to add it
                        results.put(msg)
                    else:
                       # If 127.0.0.1 returns a result but have a real network
                       # IP also, do nothing for 127.0.0.1
                       pass
                else:
                    results.put(msg)
            except (socket.timeout, OSError) as e:
                pass
        sock.close()

    def get_list(self):
        # Starts 'max_threads' number of threads to search for PIs
        self.ip_prefix = self._get_ip_prefix()
        ip_queue = queue.Queue()
        results = queue.Queue()
        pool = []
        threadcount = self.max_threads
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
        pi_list = []
        while not results.empty():
            match = results.get().split(',')
            # if a machine answers twice (ie. if it's on wifi and ethernet)
            # only add the ip once (unlikely, but possible)
            if not match in pi_list:
                pi_list.append(match)
        return pi_list


class FindMyPITreeView (Gtk.TreeView):
    # Gtk.Treeview that contains a list of discovered PIs, and coninually
    # updates the list, and allows manual updating of list.
    def __init__(self, port, frequency=30):
        super().__init__()

        self.port = port
        self.findpi = FindMyPIClient(self.port)
        self.pi_liststore = Gtk.ListStore(str, str, str)
        self.set_model(self.pi_liststore)
        self.set_size_request(290,150)
        self.fields = ['IP','Host Name','Model']
        self.frequency = frequency

        for i, field in enumerate(self.fields):
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
            self.append_column(col)

        self.thread = threading.Thread(target=self._search, daemon=True)
        self.thread.start()

    def _search(self):
        # Thread that automatically refreshes the list
        while True:
            self.refresh_list()
            time.sleep(self.frequency)

    def _update_list(self,pi_list):
        to_remove = []
        # Search liststore, generate list of iterations to be removed
        # Also removes existing PIs from the list of PIs to add
        iter_child = self.pi_liststore.get_iter_first()
        tree_path = None
        while iter_child:
            in_list = False
            ip = self.pi_liststore.get_value(iter_child, 0)
            for pi in pi_list:
                if pi[0] == ip:
                    in_list = True
                    pi_list.remove(pi)
            if not in_list:
                to_remove.append(iter_child)
            iter_child = self.pi_liststore.iter_next(iter_child)
        for child in to_remove:
             self.pi_liststore.remove(child)
        # Adds missing PIs to liststore
        for pi in pi_list:
            self.pi_liststore.append(pi)

    def get_list(self):
        # Returns list of connected PIs using FindMyPIClient
        return self.findpi.get_list()

    def refresh_list(self):
        # Refresh the treeview.  Can be called manually
        pi_list = self.findpi.get_list()
        GLib.idle_add(self._update_list,pi_list)

    def get_value_at_col(self,column):
        # Returns the value of the specified column currently selected row
        value = ""
        view_selection = self.get_selection()
        (model,tree_iter) = view_selection.get_selected()
        if tree_iter != None:
            value = model.get_value(tree_iter,column)
        return value

