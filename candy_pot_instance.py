import socket
import random
import pickle
import csv
import pandas as pd
from datetime import datetime
import sys
import time
from iot_learner import *
from data_handler import *
import subprocess as sub
import struct
from threading import Thread

def randomResponse(port, socket):
    print('RESPONSE:')
    r = loadRandomResponse(port)
    print(str(r[0]) + ": " + str(r[2]))
    res_id = r[0]
    if "b'" in r[2]:
        filtered_response = r[2].split("b'")[1].split("'")[0]
        socket.send(filtered_response.encode("utf-8"))
    else:
        socket.send(r[2].encode("utf-8"))
    return res_id

def portSelection(port):
    try:
        if '80' == port:
            createCandyPot(port)
        elif '81' == port:
            createCandyPot(port)
        elif '82' == port:
            createCandyPot(port)
        elif '88' == port:
            createCandyPot(port)
        elif '443' == port:
            createCandyPot(port)
        elif '7547' == port:
            createCandyPot(port)
        elif '8080' == port:
            createCandyPot(port)
        elif '8081' == port:
            createCandyPot(port)
        elif '9999' == port:
            createCandyPot(port)
        elif 'all' == port:
            createAllCandyPot()
    except:
        print("\nException: The port is invalid")
        sys.exit(1)

def createCandyPot(port):
    try:
        s = socket.socket()
        s.bind(('', int(port)))
        s.listen(5)
        request_set = loadData('port_dat/port_' + str(port) + '.dat')
        print("Server started for port " + str(port))
        random_response = True
        try:
            while True:
                req_id = newRequestID(port)
                pcap_path = "/home/CandyPot/requests/port_" + str(port) + "_requests_pcap/" + req_id + ".pcap"
                p = sub.Popen((
                              "sudo", "tcpdump", "port", str(port), "and", "(tcp[tcpflags] & tcp-push != 0)", "--print",
                              "-Q", "in", "-w", pcap_path, "-Z", "root", "-c", "1"), stdout=sub.PIPE)
                # p = sub.Popen(("sudo", "tcpdump", "port", str(port), "and", "(tcp[tcpflags] & tcp-push != 0)", "-Q", "in", "-w", pcap_path, "-Z", "root", "-c", "1"))

                c, addr = s.accept()
                print('\n----------Got connection from' + addr + "----------")

                # To find out if a new session has been started with this address
                check_session, ses_id = checkOpenSession(port, addr)

                # To collect de request and print it
                msg_recived = c.recv(65565)
                # print(msg_recived)
                print('REQUEST:')
                print(repr(msg_recived))

                request_set.add(msg_recived)

                # To add the request to the dataset
                storeRequest(port, req_id, addr, msg_recived)
                res_id = None

                # To positively update previous answers
                if check_session:
                    positiveUpdateResponseScore(ses_id, req_id, port)

                # To check if the attacker is already in the dataset of this port
                if checkAttackerExistence(port, addr):
                    print("This Attacker already send us a request")

                # To check if responses list for this port is empty
                response_exists = checkResponsesExistence(port)

                # Random response
                if random_response and response_exists:
                    res_id = randomResponse(port, c)
                # If the attacker has already made an equal request
                elif response_exists and not random_response:
                    print('Not implemented')
                elif not response_exists:
                    print('No answers have been collected yet')
                    c.send(b'404')
                # Q-Learning approach
                else:
                    print('Thank you for connecting')
                    c.send(b'Thank you for connecting')

                # To add a new session or update an existing session
                storeSession(ses_id, addr, req_id, res_id, port)
                print('----------End of Connection----------')
                print()
                c.close()

                # To negatively update previous answers
                negativeUpdateResponseScore(port)
        except KeyboardInterrupt:
            print("Program interrupted, storing data and exiting.")

        storeData(request_set, 'port_dat/port_' + str(port) + '.dat')
    except:
        print("CandyPot error at port " + str(port))
        createCandyPot(port)

def createAllCandyPot():
    allowed_ports = ["80", "81", "82", "88", "443", "7547", "8080", "8081", "9999"]
    for p in allowed_ports:
        t = Thread(target=createCandyPot, args=(p,))
        t.start()

def main():
    port = str(input("Select a Port (digit all for select all the ports): "))
    portSelection(str(port))

if __name__ == "__main__":
    main()