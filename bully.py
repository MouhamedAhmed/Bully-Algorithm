import zmq
import random
import sys
import time
from multiprocessing import Process,Value,Lock,Manager
import datetime
import time
import json


class process:
    def __init__(self,ip,id,ips,ids):
        self.ips_to_send_ok_on = Manager().list()
        
        self.ips = ips
        self.ids = ids
        self.own_ip = ip
        self.own_id = id

        self.election_port = "5200"


        self.ok_port = "5300"
        self.update_port = "6001"
        self.lead_port = "5400"
        self.lead_ip = Manager().dict({
            "ip":""
        })

        self.last_ok_time =  Manager().dict({"date":datetime.datetime.now()})

    def send_election (self):
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        
        while True:
            for i in range(len(self.ips)):
                if (self.ips[i] != self.own_ip) and (self.ids[i] > self.own_id):
                    socket.connect("tcp://" + self.ips[i] + self.election_port)
                    socket.send_string(self.own_ip)
           

    def recv_election (self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.bind ("tcp://" + self.own_ip + self.election_port)
        socket.subscribe("")

        while True:
            ip_sent_election = socket.recv_string()
            self.ips_to_send_ok_on.append(ip_sent_election)

    def send_ok (self):
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        while True:
            if len(self.ips_to_send_ok_on) != 0:
                socket.connect("tcp://" + self.ips_to_send_ok_on[0] + self.ok_port)
                socket.send_string(self.own_ip)
                del(self.ips_to_send_ok_on[0])
                # time.sleep(0.001)


    def recv_ok (self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.bind ("tcp://" + self.own_ip + self.ok_port)
        socket.subscribe("")
        while True:
            ip_sent_ok = socket.recv_string()
            self.last_ok_time["date"] = datetime.datetime.now()

    def I_am_a_leader (self):
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        t = datetime.datetime.now()
        while True:
            if (datetime.datetime.now() - self.last_ok_time["date"]).total_seconds() > 1:
                self.lead_ip["ip"] = self.own_ip
                for i in self.ips:
                    socket.connect("tcp://" + i + self.lead_port)
                    socket.send_string(self.own_ip)

                time.sleep(0.01)


    def recv_leader (self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.bind ("tcp://" + self.own_ip + self.lead_port)
        socket.subscribe("")

        t = datetime.datetime.now()

        while True:
            self.lead_ip["ip"] = socket.recv_string()
            

    def recv_updates(self):
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.bind("tcp://" + self.own_ip + self.update_port)
        while(True):
            d = socket.recv_pyobj()
            # print(d)
            self.ids.append(d["id_added"])
            self.ips.append(d["ip_added"])
            # print(self.ids)
            # print(self.ips)

    def print_leader(self):
        while True:
            time.sleep(1)
            print("leader_ip",self.lead_ip["ip"][:-1])
            # print("my id:",self.own_id)



    def main (self):
        send_election_process = Process(target = self.send_election)
        send_election_process.start()

        recv_election_process = Process(target = self.recv_election)
        recv_election_process.start()

        send_ok_process = Process(target = self.send_ok)
        send_ok_process.start()

        recv_ok_process = Process(target = self.recv_ok)
        recv_ok_process.start()

        I_am_a_leader_process = Process(target = self.I_am_a_leader)
        I_am_a_leader_process.start()

        recv_leader_process = Process(target = self.recv_leader)
        recv_leader_process.start()

        recv_updates_process = Process(target = self.recv_updates)
        recv_updates_process.start()


        print_leader_process = Process(target = self.print_leader)
        print_leader_process.start()


        send_election_process.join()
        recv_election_process.join()
        send_ok_process.join()
        recv_ok_process.join()
        I_am_a_leader_process.join()
        recv_leader_process.join()
        recv_updates_process.join()
        print_leader_process.join()





def send_to_manager(ip,manager_ip,manager_port):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect ("tcp://" + manager_ip + manager_port)
    socket.send_string(ip)
    return socket.recv_pyobj()



with open('ips.txt') as json_file:
    data = json.load(json_file)
code = int(input("Enter your device number from 1 to "+str(len(data["ips"]))+" : "))-1
ip = data["ips"][code]+":"

manager_ip = data["manager_ip"][0]+":"
manager_port = "6000"
d = send_to_manager(ip,manager_ip,manager_port)
my_id = d["id"]
current_ids = Manager().list(d["ids"])
current_ips = Manager().list(d["ips"])


    

p1 = process(ip,my_id,current_ips,current_ids)

process_1 = Process(target =  p1.main)

process_1.start()

process_1.join()


