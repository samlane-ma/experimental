#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib

import socket
from select import select
import threading
import time

class FindMyPIServer:
    def __init__(self,port):
        self.port = port
        self.active = False
        self.lock = threading.Lock()
        self.model = self._get_model()
        self.ip = self.get_ip()
        GLib.timeout_add_seconds(10, self._watch_ip)

    def _get_model(self):
        model = "unknown"
        try:
            with open("/proc/cpuinfo") as cpufile: 
                cpuinfo = cpufile.readlines() 
                for line in cpuinfo: 
                    info = line.split(':')
                    if info[0].strip() == "Model":
                        model = info[1].strip()
                    elif info[0].strip() == "model name":
                        model = info[1].strip()
        except:
            pass
        return model

    def get_ip(self):
        # Return current IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def _watch_ip (self):
        # Watch to see if IP address changes, restart server if so
        # Slight delay before restarting for good meausre
        IP = self.get_ip()
        if IP != self.ip:
            print("IP Changed from {} to {}".format(self.ip,IP))
            self.ip = IP
            if self.active:
                self.toggle_server()
                time.sleep(2)
                self.toggle_server()
        return True

    def toggle_server(self):
        # If server inactive, start it, else stop it
        if not self.active:
            self.lock.acquire()
            self.ip = self.get_ip()
            self.hostname = socket.gethostname()
            self.lock.release()
            self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                self.udp.bind((self.ip,self.port))
            except OSError:
                print("Socket could not be opened")
                self.lock.acquire()
                self.run = False
                try:
                    self.udp.close()
                except:
                    pass
                self.lock.release()
            else:
                self.lock.acquire()
                self.input = [self.udp]
                self.run = True
                self.active = True
                self.lock.release()
                self.thread = threading.Thread(target=self.server_thread,
                                               args=(self.ip, self.hostname,
                                               self.model), daemon=True)
                self.thread.start()
                print("Server started")
        else:
            self.lock.acquire()
            self.run = False
            self.lock.release()
            print("stopping server")

    def update_label(self,label,data):
        if label != None:
            label.set_text(data)

    def server_thread(self,ip,host,model):
        while self.run:
            inputready,outputready,exceptready = select(self.input,[],[],1)
            for s in inputready:
                if s == self.udp:
                    data,addr = s.recvfrom(4096)
                    msg = data.decode("utf-8")
                    if msg == "Are you a PI?":
                        reply = "{},{},{}".format(ip, host, model)
                        sent = s.sendto(reply.encode(), addr)
                else:
                    print("unknown socket:")
        self.lock.acquire()
        self.udp.close()
        self.active = False
        self.lock.release()

    def get_status(self):
        return self.active

def change_button(button):
    # Re-enable button after a few seconds to prevent "button mashing"
    # Also make sure button text accurately reflects status
    if findmypiserver.get_status():
        print("Seems active")
        button.set_label("Stop Server")
    else:
        print("Seems stopped")
        button.set_label("Start Server")
    button.set_sensitive(True)

def on_button_clicked(button):
    # Disable button to prevent "button mashing"
    button.set_sensitive(False)
    findmypiserver.toggle_server()
    GLib.timeout_add_seconds(2,change_button,button)

def on_window_destroy(*args):
    Gtk.main_quit()

if __name__=="__main__":
    grid = Gtk.Grid()
    button = Gtk.Button()
    button.set_label("Start Server")
    label = Gtk.Label()
    label.set_text("Find My PI Server")
    window = Gtk.Window()
    window.add(grid)
    grid.attach(button,0,0,1,1)
    grid.attach(label,0,1,1,1)
    window.connect("destroy",on_window_destroy)
    window.show_all()
    findmypiserver = FindMyPIServer(8888)
    button.connect("clicked",on_button_clicked)
    on_button_clicked(button)
    Gtk.main()
