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

port = int(sys.argv[1])
#port = int(input("Enter port number:"))

#s = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_IP)
#s.bind((raw_input("[+] YOUR_INTERFACE : "),0))
#s.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
#s.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)
#s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
s = socket.socket()
#host = socket.gethostname()
s.bind(('', port))
s.listen(5)

request_set = loadData('port_dat/port_' + str(port) + '.dat')

print("Server started for port " + str(port) + ":")
random_response = True
try:
    while True:
        req_id = newRequestID(port)
        pcap_path = "/home/CandyPot/requests/port_" + str(port) + "_requests_pcap/" + req_id + ".pcap"
        p = sub.Popen(("sudo", "tcpdump", "port", str(port), "and", "(tcp[tcpflags] & tcp-push != 0)", "--print", "-Q", "in", "-w", pcap_path, "-Z", "root", "-c", "1"), stdout=sub.PIPE)
        # output = p.stdout.read()
        # print(output)

        c, addr = s.accept()
        print('Got connection from', addr)

        # Per capire se è stata avviata una nuova sessione con questo indirizzo
        check_session, ses_id = checkOpenSession(port, addr)

        #pkt = s.recvfrom(65565)
        #print(pkt)
        #print(pkt[1][0])

        msg_recived = c.recv(65565)
        print(msg_recived)
        print('REQUEST:')
        print(repr(msg_recived))

        request_set.add(msg_recived)

        # Per aggiungere la richiesta al dataset
        storeRequest(port, req_id, addr, msg_recived)
        res_id = None

        # Per aggiornare positivamente le risposte precedenti
        if check_session:
            positiveUpdateResponseScore(ses_id, req_id, port)

        # Per controllare se l'attaccante ha già effettuato una richiesta uguale
        # DA MODIFICARE (vengono utilizzate due funzioni, bisogna rendere il codice più pulito)
        #already_answered = False
        #if loadResponse(port, checkAttackerExistence(port, addr)) is not None:
        #    already_answered = True

        if checkAttackerExistence(port, addr):
            print("This Attacker already send us a request")

        # To check if responses list for this port is empty
        response_exists = checkResponsesExistence(port)

        # Caso in cui si decide di dare una risposta scelta casualemente
        if random_response and response_exists:
            print('RESPONSE:')
            r = loadRandomResponse(port)
            print(r)
            res_id = r[0]
            if "b'" in r[2]:
                filtered_response = r[2].split("b'")[1].split("'")[0]
                c.send(filtered_response.encode("utf-8"))
            else:
                c.send(r[2].encode("utf-8"))

        # Caso in cui l'attaccante ha già effettuato una richiesta uguale
        elif response_exists and not random_response:
            print('Not implemented')
        elif not response_exists:
            print('No answers have been collected yet')
            c.send(b'404')

        # Caso in cui si utilizza un approccio basato sul machine learning per scegliere la risposta
        # (Ancora da implementare)
        else:
            print('Thank you for connecting')
            c.send(b'Thank you for connecting')

        # Per aggiungere una nuova sessione o aggiornare una sessione esistente
        storeSession(ses_id, addr, req_id, res_id, port)
        print('End of Connection')
        print()
        c.close()

        negativeUpdateResponseScore(port)

except KeyboardInterrupt:
    print("Program interrupted, storing data and exiting.")

storeData(request_set, 'port_dat/port_' + str(port) + '.dat')
