import zmq
import random
import sys
import time
from multiprocessing import Process,Value,Lock,Manager
import datetime
import time

class manager:
    def __init__(self):
        self.ips = []
        self.ids = []
        self.manage_ip = "127.0.0.1:"
        self.manage_port = "6000"
        self.max_id = 0
        self.update_port = "6001"

    def main(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://" + self.manage_ip + self.manage_port)
        while (True):
            ip = socket.recv_string()
            print ("Received ip: ", ip)
            
            new_id = -1
            for i in range(len(self.ips)):
                if ip == self.ips[i]:
                    new_id = self.ids[i]
                    break




            id_exists = True
            if new_id == -1:
                self.max_id += 1
                self.ips.append(ip)
                self.ids.append(self.max_id)
                new_id = self.max_id
                id_exists = False
            d = {
                "id": new_id,
                "ips": self.ips,
                "ids": self.ids
            }
            socket.send_pyobj(d)
            if not id_exists:
                d2 = {
                    "ip_added":ip,
                    "id_added":new_id
                }
                for i in range(len(self.ips)-1):
                    context2 = zmq.Context()
                    socket2 = context2.socket(zmq.PAIR)
                    socket2.connect("tcp://" + self.ips[i] + self.update_port)
                    socket2.send_pyobj(d2)
            






m = manager()
m.main()







