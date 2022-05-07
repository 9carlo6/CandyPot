import socket
import random
import pickle
import csv
import pandas as pd
from datetime import datetime
import sys
import time
from IoTLearner import negativeUpdateResponseScore, positiveUpdateResponseScore

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
    f.close()

    for r in res_lis:
        if str(r[0]) == str(res):
            return r[2]

    return None

# Per aggiungere una sessione indicando la richiesta e risposta
def addSession(ses_id, addr, req_id, res_id, port):
    rows_number = len(pd.read_csv('sessions.csv')) + 1
    f = open(r'sessions.csv', 'a', newline='\n')
    writer = csv.writer(f)
    now = datetime.now()
    if ses_id is not None:
        row = [ses_id, addr, req_id, res_id, now, "open", str(port)]
    else:
        row = ['S' + str(rows_number), addr, req_id, res_id, now, "open", str(port)]
    writer.writerow(row)
    f.close()

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

s = socket.socket()
host = socket.gethostname()
s.bind(('', port))
s.listen(5)

request_set = loadData('port_' + str(port) + '.dat')
login_cgi = loadData('response_from_iot.dat')

print("Server started for port " + str(port) + ":")
random_response = True
try:
    while True:
        c, addr = s.accept()
        print('Got connection from', addr)

        # Per capire se è stata avviata una nuova sessione con questo indirizzo
        check_session, ses_id = checkIfNewSession(addr)

        msg_recived = c.recv(20000)
        print('REQUEST:')
        print(repr(msg_recived))
        request_set.add(msg_recived)
        # Per aggiungere la richiesta al dataset (ritorna l'id della richiesta)
        req_id = addRequest(port, addr, msg_recived)
        res_id = None

        # Per aggiornare positivamente le risposte precedenti
        if not check_session:
            positiveUpdateResponseScore(ses_id, req_id, port)

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
            r = selectResponse(checkIfAttackerAlredyExists(addr, msg_recived))
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
        addSession(ses_id, addr, req_id, res_id, port)
        print('End of Connection')
        print()
        c.close()

        negativeUpdateResponseScore(port)

except KeyboardInterrupt:
    print("Program interrupted, storing data and exiting.")

storeData(request_set, 'port_' + str(port) + '.dat')
