#!/usr/bin/env python3

import socket
import threading
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

if __name__=="__main__":
    findmypi = FindMyPIClient()
    found = findmypi.look_for_pi()
    print("{0:<18} {1:<16} {2}".format("IP Address","Host Name","Model"))
    while not found.empty():
        match = found.get().split(',')
        print("{0:<18} {1:<16} {2}".format(match[0],match[1],match[2]))
