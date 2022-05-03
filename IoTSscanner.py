import socket
import random
import pickle
import csv
import pandas as pd
from datetime import datetime
import requests
from http.server import BaseHTTPRequestHandler
from io import BytesIO
import email
import pprint
from io import StringIO
import sys
import re

class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

def storeData(obj, filename):
    pickleFile = open(filename, 'wb')
    pickle.dump(obj, pickleFile)
    pickleFile.close()

def loadData(filename):
    pickleFile = open(filename, 'rb')
    obj = pickle.load(pickleFile)
    pickleFile.close()
    return obj

def loadRequestList(port):
    f = open(r'port_' + str(port) + '_requests.csv', 'r', newline='\n')
    reader = csv.reader(f)
    #rimozione del primo elemento (header) dalla lista
    res_lis = list(reader)
    res_lis.pop(0)
    f.close()
    return res_lis

def deviceSelection(device):
    try:
        if 'Hikvision'.lower() == device.lower():
            device_ip_list = loadData('hikvision_camera_addr.dat')
        elif 'SonicWALL'.lower() == device.lower():
            device_ip_list = loadData('sonicWall_firewall_addr.dat')
        elif 'NETGEAR'.lower() == device.lower():
            device_ip_list = loadData('netgear_router_addr.dat')
        elif 'TR069'.lower() == device.lower():
            device_ip_list = loadData('TR069_protocolDevice_addr.dat')
        elif 'lighttpd'.lower() == device.lower():
            device_ip_list = loadData('lighttpd_protocolDevice_addr.dat')
        elif 'Huawei'.lower() == device.lower():
            device_ip_list = loadData('Huawei_router_addr.dat')
        elif 'kangle'.lower() == device.lower():
            device_ip_list = loadData('kangle_addr.dat')
        elif 'TP-LINK'.lower() == device.lower():
            device_ip_list = loadData('tplink_router_addr.dat')
        elif 'App-webs'.lower() == device.lower():
            device_ip_list = loadData('app_web_server_addr.dat')
        return device_ip_list
    except:
        print("The device does not exist")
        sys.exit(1)

def portSelection(port):
    try:
        if '80' == port:
            port_request_list = loadRequestList(port)
        elif '81' == port:
            port_request_list = loadRequestList(port)
        elif '82' == port:
            port_request_list = loadRequestList(port)
        elif '88' == port:
            port_request_list = loadRequestList(port)
        elif '443' == port:
            port_request_list = loadRequestList(port)
        elif '7547' == port:
            port_request_list = loadRequestList(port)
        elif '8080' == port:
            port_request_list = loadRequestList(port)
        elif '8081' == port:
            port_request_list = loadRequestList(port)
        elif '9999' == port:
            port_request_list = loadRequestList(port)
        return port_request_list
    except:
        print("The port is invalid")
        sys.exit(1)

def httpFilter(string):
    filtered_str = string
    if "HTTP" in filtered_str:
        filtered_str = filtered_str.split("HTTP")[0]
    if "GET" in filtered_str:
        filtered_str = filtered_str.split("GET")[1]
    if "http" in filtered_str:
        filtered_str = filtered_str.split("//")[1].split("/")[1]
    if "b'" in filtered_str:
        filtered_str = filtered_str.split("b'")[1].split("'")[0]
    if "/" in filtered_str:
        filtered_str = filtered_str.split("/")[1]
    return filtered_str

# Per aggiungere la risposta al file relativo alla porta specifica
def addResponse(port, addr, value):
    rows_number = len(pd.read_csv('port_' + str(port) + '_response.csv')) + 1
    f = open(r'port_' + str(port) + '_response.csv', 'a', newline='\n')
    writer = csv.writer(f)
    now = datetime.now()
    res_id = 'RES_' + str(rows_number) + '_P' + str(port)
    row = [res_id, addr, value, now]
    writer.writerow(row)
    f.close()
    return res_id

# Per aggiungere una riga al file relativo alla scansione specifica
def addScan(device, req, res, port, validity):
    rows_number = len(pd.read_csv('IoTScannerTable.csv')) + 1
    f = open(r'IoTScannerTable.csv', 'a', newline='\n')
    writer = csv.writer(f)
    now = datetime.now()
    scan_id = 'SCAN_' + str(rows_number)
    row = [scan_id, device, req, res, port, validity, now]
    writer.writerow(row)
    f.close()
    return scan_id

def checkScan(device, req, port):
    f = open(r'IoTScannerTable.csv', 'r', newline='\n')
    reader = csv.reader(f)
    # rimozione del primo elemento (header) dalla lista
    scan_lis = list(reader)
    scan_lis.pop(0)
    f.close()
    check = False
    for s in scan_lis:
        if s[1] == device and s[2] == req and s[4] == port:
            check = True
    return check


def scanSelectedPort(port):
    port_request_list = portSelection(port)
    for i in device_ip_list:
        for r in port_request_list:
            req_id = str(r[0])
            # Se lo scan non è stato già effettuato
            if not checkScan(device, req_id, port):
                try:
                    filtered_str = httpFilter(r[2])

                    response = requests.get('http://' + str(i) + '/' + filtered_str, verify=False, timeout=2)
                    print("Response Content:")
                    print(response.content)
                    print(response)

                    # Se la risponsta non è vuota
                    if response != None:
                        res_id = addResponse(port, str(i), response.content)
                        addScan(device, req_id, res_id, port, "True")

                except:
                    print("Exception with IP:" + str(i) + " " + str(r[0]))
                    addScan(device, req_id, "Null", port, "False")

def scanAllPort():
    allowed_ports = ["80", "81", "82", "88", "443", "7547", "8080", "8081", "9999"]
    for p in allowed_ports:
        port_request_list = portSelection(str(p))
        for i in device_ip_list:
            for r in port_request_list:
                req_id = str(r[0])
                # Se lo scan non è stato già effettuato
                if not checkScan(device, req_id, port):
                    try:
                        filtered_str = httpFilter(r[2])

                        response = requests.get('http://' + str(i) + '/' + filtered_str, verify=False, timeout=2)
                        print("Response Content:")
                        print(response.content)
                        print(response)

                        # Se la risponsta non è vuota
                        if response != None:
                            res_id = addResponse(str(p), str(i), response.content)
                            addScan(device, req_id, res_id, str(p), "True")

                    except:
                        print("Exception with IP:" + str(i) + " " + str(r[0]))
                        addScan(device, req_id, "Null", str(p), "False")

# Scelta di un dispositivo
print("Select an IoT Device:")
print("--Hikvision")
print("--SonicWALL")
print("--NETGEAR")
print("--TR069")
print("--lighttpd")
print("--Huawei")
print("--kangle")
print("--TP-LINK")
print("--App-webs")

device = str(input("Your Choise:"))
device_ip_list = deviceSelection(device)

print()

# Scelta di una porta specifica
port = str(input("Select a Port (digit all for select all the ports):"))

if str(port) == 'all':
    scanAllPort()
else:
    scanSelectedPort(port)