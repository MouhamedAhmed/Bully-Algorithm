import json

ips = ["192.168.195.156","192.168.194.156","10.147.17.156","127.0.0.1"]
manager_ip = ["127.0.0.1"]
data = {"ips":ips,
        "manager_ip":manager_ip}

with open('ips.txt', 'w+') as outfile:
    json.dump(data, outfile)