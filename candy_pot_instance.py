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
import struct
from Pcap import *

# Per controllare l'esistenza dell'attaccante corrente nella lista delle sessioni
# In caso positivo ritorna la richiesta effettuata dall'attaccante
def checkIfAttackerAlredyExists(addr, value):
    f = open(r'sessions.csv', 'r', newline='\n')
    reader = csv.reader(f)
    # rimozione del primo elemento (header) dalla lista
    session_list = list(reader)
    session_list.pop(0)
    f.close()

    for s in session_list:
        if str(addr[0]) in s[1]:
            if checkIfRequestFromAttackerAlreadyExists(addr, value) is not None:
                return s[3]
    return None

# Per controllare l'esistenza della richiesta corrente nella lista delle richieste
# In caso affermativo ritorna l'id della richiesta
def checkIfRequestFromAttackerAlreadyExists(addr, value):
    f = open(r'port_' + str(port) + '_requests.csv', 'r', newline='\n')
    reader = csv.reader(f)
    # rimozione del primo elemento (header) dalla lista
    request_list = list(reader)
    request_list.pop(0)
    f.close()
    req = None
    for r in request_list:
        if str(addr[0]) in r[1] and str(value) in r[2]:
            req = r[0]
    return req

# Per controllare l'esistenza di almeno una risposta per la porta di interesse
def checkIfResponseExists(port):
    f = open(r'port_' + str(port) + '_response.csv', 'r', newline='\n')
    reader = csv.reader(f)
    res_lis = list(reader)
    f.close()
    #rimozione del primo elemento (header) dalla lista
    if len(res_lis) < 2:
        return False
    else:
        return True

# Per controllare c'è bisogno di avviare una nuova sessione
# Se la sessione è già avviata ritorna il numero di sessione
def checkIfNewSession(addr):
    f = open(r'sessions.csv', 'r', newline='\n')
    reader = csv.reader(f)
    session_list = list(reader)
    session_list.pop(0)
    f.close()

    last_time = None
    ses_id = None
    # Controllo temporale
    # Si parte dalla fine della lista delle sessioni per cercare l'ultima richiesta fatta dall'attaccante
    for s in reversed(session_list):
        if str(addr[0]) in str(s[1]):
            last_time = datetime.strptime(str(s[4]), '%Y-%m-%d %H:%M:%S.%f')
            ses_id = str(s[0])
            break

    check = True
    now = datetime.now()
    if (now - last_time).total_seconds() >= 80:
        print("Last session from this address was on: " + str(s[4]))
        ses_id = None
    elif (now - last_time).total_seconds() < 80:
        print("There is already a session with this address started "
              + str((now - last_time).total_seconds()) + " seconds ago")
        check = False
    else:
        print("This address has never started a session")

    return check, ses_id

# Per aggiornare lo score relativo alle risposte
"""
def updateResponseScore(port):
    session_file = 'sessions.csv'
    sf = pd.read_csv(file)
    sf["SessionID"]

    response_file = ('port_' + str(port) + '_response.csv')

    return None
"""


#port = int(sys.argv[1])
port = int(input("Enter port number:"))


s = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_IP)
#s.bind((raw_input("[+] YOUR_INTERFACE : "),0))
s.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
s.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)
#s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
#s = socket.socket()
#host = socket.gethostname()
s.bind(('', port))
#s.listen(5)

request_set = loadData('port_' + str(port) + '.dat')
login_cgi = loadData('response_from_iot.dat')

print("Server started for port " + str(port) + ":")
random_response = True
try:
    while True:
        #c, addr = s.accept()
        #print('Got connection from', addr)

        # Per capire se è stata avviata una nuova sessione con questo indirizzo
        #check_session, ses_id = checkIfNewSession(addr)

        # Create Object
        p = Pcap('temp.pcap')
        pkt = s.recvfrom(65565)
        print(pkt)
        print(pkt[1][0])
        p.write(pkt[0])
        # flush data
        p.pcap_file.flush()
        # close file
        p.close()

        msg_recived = s.recv(20000)
        print(msg_recived)
        break
        print('REQUEST:')
        print(repr(msg_recived))
        request_set.add(msg_recived)
        # Per aggiungere la richiesta al dataset (ritorna l'id della richiesta)
        req_id = storeRequest(port, addr, msg_recived)
        res_id = None

        # Per aggiornare positivamente le risposte precedenti
        if not check_session:
            positiveUpdateResponseScore(ses_id, req_id, port)

        # Per controllare se l'attaccante ha già effettuato una richiesta uguale
        # DA MODIFICARE (vengono utilizzate due funzioni, bisogna rendere il codice più pulito)
        already_answered = False
        if loadResponse(port, checkIfAttackerAlredyExists(addr, msg_recived)) is not None:
            already_answered = True

        response_exists = checkIfResponseExists(port)

        # Caso in cui si decide di dare una risposta scelta casualemente
        if random_response and response_exists and not already_answered:
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
        elif already_answered and response_exists:
            print('The Attacker already send the same request to us')
            print('RESPONSE:')
            r = loadResponse(port, checkIfAttackerAlredyExists(addr, msg_recived))
            res_id = checkIfAttackerAlredyExists(addr, msg_recived)
            print(r)
            if "b'" in r:
                filtered_response = r.split("b'")[1].split("'")[0]
                c.send(filtered_response.encode("utf-8"))
            else:
                c.send(r.encode("utf-8"))
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

storeData(request_set, 'port_' + str(port) + '.dat')
