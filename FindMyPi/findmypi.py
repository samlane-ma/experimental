#!/usr/bin/env python3

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

if __name__=="__main__":

    headers = [['IP Address','Host Name','Model'],
               ['---------------','-------------------------',
                '------------------------------']]
    pi_list = []
    findmypi = FindMyPIClient()
    found = findmypi.look_for_pi()
    while not found.empty():
        match = found.get().split(',')
        if not match in pi_list:
            pi_list.append(match)
    print()
    for h in headers:
        print("{:<16}{:<26}{}".format(h[0],h[1],h[2]))
    for pi in pi_list:
        print("{:<16}{:<26}{}".format(pi[0],pi[1],pi[2]))
    print()


