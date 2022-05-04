import socket
import random
import pickle
import csv
import pandas as pd
from datetime import datetime

def storeData(obj, filename):
    pickleFile = open(filename, 'wb')
    pickle.dump(obj, pickleFile)
    pickleFile.close()

def loadData(filename):
    pickleFile = open(filename, 'rb')
    obj = pickle.load(pickleFile)
    pickleFile.close()
    return obj

# Per aggiungere la richiesta al file relativo alla porta specifica
def addRequest(port, addr, value):
    rows_number = len(pd.read_csv('port_' + str(port) + '_requests.csv')) + 1
    f = open(r'port_' + str(port) + '_requests.csv', 'a', newline='\n')
    writer = csv.writer(f)
    now = datetime.now()
    req_id = 'REQ_' + str(rows_number) + '_P' + str(port)
    row = [req_id, addr, value, now]
    writer.writerow(row)
    f.close()
    return req_id

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

# Per scegliere randomicamente la risposta da dare in caso di richiesta
def randomChoiseResponse(port):
    f = open(r'port_' + str(port) + '_response.csv', 'r', newline='\n')
    reader = csv.reader(f)
    #rimozione del primo elemento (header) dalla lista
    res_lis = list(reader)
    res_lis.pop(0)
    res_id = random.choice(res_lis)
    f.close()
    return res_id

# Per scegliere una risposta specifica
def selectResponse(res):
    f = open(r'port_' + str(port) + '_response.csv', 'r', newline='\n')
    reader = csv.reader(f)
    #rimozione del primo elemento (header) dalla lista
    res_lis = list(reader)
    res_lis.pop(0)

    for r in res_lis:
        if str(r[0]) == str(res):
            return r[2]

    return None

# Per aggiungere una sessione indicando la richiesta e risposta
def addSession(addr, req, res):
    rows_number = len(pd.read_csv('sessions.csv')) + 1
    f = open(r'sessions.csv', 'a', newline='\n')
    writer = csv.writer(f)
    now = datetime.now()
    row = ['S' + str(rows_number), addr, req, res, now]
    writer.writerow(row)
    f.close()

# Per controllare l'esistenza di almeno una risposta per la porta di interesse
def checkIfResponseExists(port):
    f = open(r'port_' + str(port) + '_response.csv', 'r', newline='\n')
    reader = csv.reader(f)
    #rimozione del primo elemento (header) dalla lista
    if len(list(reader)) < 2:
        return False
    else:
        return True

s = socket.socket()
host = socket.gethostname()
port = int(input("Enter port number:"))
s.bind(('', port))

# request_set = set()
request_set = loadData('port_' + str(port) + '.dat')

login_cgi = loadData('response_from_iot.dat')

s.listen(5)
print("Server started:")
random_response = True
try:
    while True:
        c, addr = s.accept()
        print('Got connection from', addr)
        msg_recived = c.recv(16384)
        # print(msg_recived)
        print('REQUEST:')
        print(repr(msg_recived))
        request_set.add(msg_recived)
        req = addRequest(port, addr, msg_recived)
        res = None

        # Per controllare se l'attaccante ha già effettuato una richiesta uguale
        # DA MODIFICARE (vengono utilizzate due funzioni, bisogna rendere il codice più pulito)
        already_answered = False
        if selectResponse(checkIfAttackerAlredyExists(addr, msg_recived)) is not None:
            already_answered = True

        response_exists = checkIfResponseExists(port)

        # Caso in cui si decide di dare una risposta scelta casualemente
        if random_response and response_exists and not already_answered:
            print('RESPONSE:')
            r = randomChoiseResponse(port)
            print(r)
            res = r[0]
            if "b'" in r[2]:
                filtered_response = r[2].split("b'")[1].split("'")[0]
                c.send(filtered_response.encode("utf-8"))
            else:
                c.send(r[2].encode("utf-8"))

        # Caso in cui l'attaccante ha già effettuato una richiesta uguale
        elif already_answered and response_exists:
            print('The Attacker already send the same request to us')
            print('RESPONSE:')
            r = selectResponse(checkIfAttackerAlredyExists(addr, msg_recived))
            res = checkIfAttackerAlredyExists(addr, msg_recived)
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

        addSession(addr, req, res)
        print('End of Connection')
        print()
        c.close()

except KeyboardInterrupt:
    print("Program interrupted, storing data and exiting.")

storeData(request_set, 'port_' + str(port) + '.dat')
