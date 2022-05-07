import socket
import random
import pickle
import csv
import pandas as pd
from datetime import datetime
import requests
import sys
from data_handler import *

def deviceSelection(device):
    try:
        if 'Hikvision'.lower() == device.lower() or '1'.lower() == device.lower():
            device_ip_list = loadData('addresses/hikvision_camera_addr.dat')
        elif 'SonicWALL'.lower() == device.lower() or '2'.lower() == device.lower():
            device_ip_list = loadData('addresses/sonicWall_firewall_addr.dat')
        elif 'NETGEAR'.lower() == device.lower() or '3'.lower() == device.lower():
            device_ip_list = loadData('addresses/netgear_router_addr.dat')
        elif 'TR069'.lower() == device.lower() or '4'.lower() == device.lower():
            device_ip_list = loadData('addresses/TR069_protocolDevice_addr.dat')
        elif 'lighttpd'.lower() == device.lower() or '5'.lower() == device.lower():
            device_ip_list = loadData('addresses/lighttpd_protocolDevice_addr.dat')
        elif 'Huawei'.lower() == device.lower() or '6'.lower() == device.lower():
            device_ip_list = loadData('addresses/Huawei_router_addr.dat')
        elif 'kangle'.lower() == device.lower() or '7'.lower() == device.lower():
            device_ip_list = loadData('addresses/kangle_addr.dat')
        elif 'TP-LINK'.lower() == device.lower() or '8'.lower() == device.lower():
            device_ip_list = loadData('addresses/tplink_router_addr.dat')
        elif 'App-webs'.lower() == device.lower() or '9'.lower() == device.lower():
            device_ip_list = loadData('addresses/app_web_server_addr.dat')
        return device_ip_list
    except:
        print("\nException: The device does not exist")
        sys.exit(1)

def portSelection(port, device_ip_list):
    try:
        if '80' == port:
            scanSelectedPort(port, device_ip_list)
        elif '81' == port:
            scanSelectedPort(port, device_ip_list)
        elif '82' == port:
            scanSelectedPort(port, device_ip_list)
        elif '88' == port:
            scanSelectedPort(port, device_ip_list)
        elif '443' == port:
            scanSelectedPort(port, device_ip_list)
        elif '7547' == port:
            scanSelectedPort(port, device_ip_list)
        elif '8080' == port:
            scanSelectedPort(port, device_ip_list)
        elif '8081' == port:
            scanSelectedPort(port, device_ip_list)
        elif '9999' == port:
            scanSelectedPort(port, device_ip_list)
        elif 'all' == port:
            scanAllPort(device_ip_list)
    except:
        print("\nException: The port is invalid")
        sys.exit(1)

# Request Filter
def reqFilter(string):
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

# To start a scan for a specific port
def scanSelectedPort(port, device_ip_list):
    port_request_list = loadRequestList(port)
    for i in device_ip_list:
        for r in port_request_list:
            req_id = str(r[0])
            # If a scan has already been performed
            if not checkScan(str(i), req_id, port):
                try:
                    filtered_str = reqFilter(r[2])

                    response = requests.get('http://' + str(i) + '/' + filtered_str, verify=False, timeout=2)
                    print("Response Content:")
                    print(response.content)
                    print(response)

                    # If Response is empty
                    if response != None:
                        res_id = storeResponse(port, str(i), response.content)
                        storeScan(str(i), req_id, res_id, port, "True")

                except:
                    print("Exception with IP:" + str(i) + " " + str(r[0]))
                    storeScan(str(i), req_id, "Null", port, "False")

# To start a scan for all ports
def scanAllPort(device_ip_list):
    allowed_ports = ["80", "81", "82", "88", "443", "7547", "8080", "8081", "9999"]
    for p in allowed_ports:
        scanSelectedPort(p,device_ip_list)

def main():
    # Scelta di un dispositivo
    print("This script Sends all the requests stored in files port_*_requests.csv to all the IoT devices through their IP addresses stored in the files *_addr.dat.\n" +
        "All the responses received from the IoT devices are stored in the file port_*_response.csv.\n")
    print("Select an IoT Device:")
    print("1 -- Hikvision")
    print("2 -- SonicWALL")
    print("3 -- NETGEAR")
    print("4 -- TR069")
    print("5 -- lighttpd")
    print("6 -- Huawei")
    print("7 -- kangle")
    print("8 -- TP-LINK")
    print("9 -- App-webs")

    device = str(input("\nYour Choise: "))
    device_ip_list = deviceSelection(device)
    port = str(input("\nSelect a Port (digit all for select all the ports): "))
    portSelection(port, device_ip_list)

if __name__ == "__main__":
    main()