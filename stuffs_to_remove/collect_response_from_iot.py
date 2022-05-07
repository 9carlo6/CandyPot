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
from http.client import HTTPResponse
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


class FakeSocket():
    def __init__(self, response_bytes):
        self._file = BytesIO(response_bytes)
    def makefile(self, *args, **kwargs):
        return self._file

#headers = {'User-Agent': None, 'Host': None, 'Accept-Encoding': None, 'Accept': None, 'Connection': None}
#headers = b'GET http://5.188.210.101/echo.php HTTP/1.1\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36\r\nAccept: */*\r\nAccept-Encoding: gzip, deflate\r\nPragma: no-cache\r\nCache-control: no-cache\r\nCookie: cookie=ok\r\nReferer: https://www.google.com/\r\nHost: 5.188.210.101\r\nConnection: close\r\nContent-Length: 0\r\n\r\n'

#Bisogna implementare uno switch per scegliere tra i vari dispositivi
device = 'Huawei_router_addr'

device_ip_list = loadData(device + '.dat')

f = open(r'port_80_requests.csv', 'r', newline='\n')
reader = csv.reader(f)
#rimozione del primo elemento (header) dalla lista
port_80_requests_list = list(reader)
port_80_requests_list.pop(0)
f.close()

for i in device_ip_list:
    for r in port_80_requests_list:
        try:
            # r = requests.get('http://' + i, headers=headers, verify=False, timeout=2)
            #print(r[2].split("b'")[1].split("'")[0])
            #str_prova =  r[2].split("b'")[1].split("'")[0]
            #print(str_prova)
            #str_prova = str('GET /search?sourceid=chrome&ie=UTF-8&q=ergterst HTTP/1.1\r\nHost: www.google.com\r\nConnection: keep-alive\r\nAccept: application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5\r\nUser-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.45 Safari/534.13\r\nAccept-Encoding: gzip,deflate,sdch\r\nAvail-Dictionary: GeNLY2f-\r\nAccept-Language: en-US,en;q=0.8\r\n')

            #print("****PRIMA****")
            str_prova = r[2]
            #print(str_prova)

            if "HTTP" in str_prova:
                str_prova = r[2].split("HTTP")[0]
            #str_prova = re.split("http", str_prova, flags=re.IGNORECASE)
            if "GET" in str_prova:
                str_prova = str_prova.split("GET")[1]
            if "http" in str_prova:
                str_prova = str_prova.split("//")[1].split("/")[1]
            if "b'" in str_prova:
                str_prova = str_prova.split("b'")[1].split("'")[0]
            if "/" in str_prova:
                str_prova = str_prova.split("/")[1]

            #print("****DOPO****")
            #print(str_prova)
            #print()

            print("RICHIESTA:")
            print('http://' + str(i) + '/' + str_prova)
            response = None
            if "80" in str(i):
                response = requests.get('http://' + "34.198.69.116:80" , verify=False, timeout=2)
            print("RISPOSTA:")
            print(response.content)
            print(response)
            print(response.headers)
            if(response != None):
                print("ol")



            """
            http_response_bytes = str_prova.encode("utf-8")
            source = FakeSocket(http_response_bytes)
            response = HTTPResponse(source)
            response.begin()
            print("status:", response.status)
            # status: 200
            print("single header:", response.getheader('Content-Type'))
            # single header: text/xml; charset="utf-8"
            print("content:", response.read(len(str_prova)))
            # content: b'teststring'
            """

            """
            #print(str_prova)
            request = HTTPRequest(str_prova.encode)
            #print(request.error_code)  # None  (check this first)
            print(request.command)  # "GET"
            print(request.path)  # "/who/ken/trust.html"
            print(request.request_version)  # "HTTP/1.1"
            print(len(request.headers))  # 3
            print(request.headers.keys())  # ['Host', 'Accept-Charset', 'Accept']
            print(request.headers['host'])  # "cm.bell-labs.com"
            #print(request.error_code)  # 400
            #print(request.error_message)  # "Bad request syntax ('GET')"
            #print("RICHIESTA:")
            #response = requests.get('http://' + i , verify=False, timeout=2)
            #print(response.json())
            """
        except:
            print("Exception with IP:" + str(i) + " " + str(r[0]))

    print("----------------------------")
#storeData(device_ip_list, 'response_from_iot.dat')