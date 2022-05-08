import socket
import random
import pickle
import csv
import pandas as pd
from datetime import datetime
import requests
import sys

# DATA HANDLE:
# 1 - PATH
# 2 - REQUESTS
# 3 - RESPONSES
# 4 - SESSIONS
# 5 - SCANS

RESPONSE_INITIAL_SCORE = 0.5
SESSION_DURATION = 80

def storeData(obj, filename):
    pickleFile = open(filename, 'wb')
    pickle.dump(obj, pickleFile)
    pickleFile.close()

def loadData(filename):
    pickleFile = open(filename, 'rb')
    obj = pickle.load(pickleFile)
    pickleFile.close()
    return obj

# 1 - PATH ----------------------------------------------------------------------------------
# Path Creation
def filePathCreation(port, type):
    try:
        if type == "req":
            path = "requests/port_" + str(port) + "_requests.csv"
        if type == "res":
            path = "responses/port_" + str(port) + "_responses.csv"
        if type == "ses":
            path = "sessions/port_" + str(port) + "_sessions.csv"
        return path
    except:
        print("Exception with path creation: port=" + str(port) + ", type=" + str(type))
        sys.exit(1)

# 2 - REQUESTS ------------------------------------------------------------------------------
# To load the request list
def loadRequestList(port):
    try:
        req_path = filePathCreation(str(port), "req")
        f = open(req_path, 'r', newline='\n')
        reader = csv.reader(f)
        res_lis = list(reader)
        res_lis.pop(0)
        f.close()
        return res_lis
    except:
        print("Exception with load request list: port=" + str(port))
        sys.exit(1)

# To store a request
def storeRequest(port, req_id, addr, value):
    try:
        req_path = filePathCreation(str(port), "req")
        f = open(req_path, 'a', newline='\n')
        writer = csv.writer(f)
        now = datetime.now()
        row = [req_id, addr, value, now]
        writer.writerow(row)
        f.close()
        return req_id
    except:
        print("Exception with store a request: port=" + str(port) + ", addr=" + str(addr))
        sys.exit(1)

def newRequestID(port):
    try:
        req_path = filePathCreation(str(port), "req")
        rows_number = len(pd.read_csv(req_path)) + 1
        req_id = 'REQ_' + str(rows_number) + '_P' + str(port)
        return req_id
    except:
        print("Exception with generate new request id: port=" + str(port))
        sys.exit(1)

# To check the existence of the current request in the requests list
def checkRequestExistence(port, addr, value):
    try:
        req_path = filePathCreation(str(port), "req")
        f = open(req_path, 'r', newline='\n')
        reader = csv.reader(f)
        request_list = list(reader)
        request_list.pop(0)
        f.close()
        check = False
        for r in request_list:
            if str(addr[0]) in r[1] and str(value) in r[2]:
                check = True
        return check
    except:
        print("Exception with check if request already existst: port=" + str(port) + ", addr=" + str(addr))
        sys.exit(1)

# 3 - RESPONSES -----------------------------------------------------------------------------
# To store a response
def storeResponse(port, addr, value):
    try:
        res_path = filePathCreation(str(port), "res")
        rows_number = len(pd.read_csv(res_path)) + 1
        f = open(res_path, 'a', newline='\n')
        writer = csv.writer(f)
        now = datetime.now()
        res_id = 'RES_' + str(rows_number) + '_P' + str(port)
        row = [res_id, addr, value, now, RESPONSE_INITIAL_SCORE]
        writer.writerow(row)
        f.close()
        return res_id
    except:
        print("Exception with store a response: port=" + str(port) + ", addr=" + str(addr))
        sys.exit(1)

# To load a response (body)
def loadResponse(port, res_id):
    try:
        res_path = filePathCreation(str(port), "res")
        f = open(res_path, 'r', newline='\n')
        reader = csv.reader(f)
        res_lis = list(reader)
        res_lis.pop(0)
        f.close()
        for r in res_lis:
            if str(r[0]) == str(res_id):
                return r[2]
        return None
    except:
        print("Exception with load a response: port=" + str(port) + ", res=" + str(res_id))
        sys.exit(1)

# To load a random response (id)
def loadRandomResponse(port):
    try:
        res_path = filePathCreation(str(port), "res")
        f = open(res_path, 'r', newline='\n')
        reader = csv.reader(f)
        res_lis = list(reader)
        res_lis.pop(0)
        res_id = random.choice(res_lis)
        f.close()
        return res_id
    except:
        print("Exception with load a random response: port=" + str(port))
        sys.exit(1)

# To check if responses list for this port is empty
def checkResponsesExistence(port):
    try:
        res_path = filePathCreation(str(port), "res")
        f = open(res_path, 'r', newline='\n')
        reader = csv.reader(f)
        res_lis = list(reader)
        f.close()
        if len(res_lis) < 2:
            return False
        else:
            return True
    except:
        print("Exception with check if responses list for this port is empty: port=" + str(port))
        sys.exit(1)

# To check the existence of the current value of response in the response list
def checkResponseValueExistence(port, value):
    try:
        res_path = filePathCreation(str(port), "res")
        f = open(res_path, 'r', newline='\n')
        reader = csv.reader(f)
        res_lis = list(reader)
        res_lis.pop(0)
        f.close()
        check = False
        res_id = None
        for r in res_lis:
            if str(value) == r[2]:
                res_id = r[0]
                check = True
                break
        return res_id, check
    except:
        print("Exception with check if the value of the response already existst: port=" + str(port))
        sys.exit(1)

# 4 - SESSIONS ------------------------------------------------------------------------------
# To store a session
def storeSession(ses_id, addr, req_id, res_id, port):
    try:
        ses_path = filePathCreation(str(port), "ses")
        rows_number = len(pd.read_csv(ses_path)) + 1
        f = open(ses_path, 'a', newline='\n')
        writer = csv.writer(f)
        now = datetime.now()
        if ses_id is not None:
            row = [ses_id, addr, req_id, res_id, now, "open", str(port)]
        else:
            row = ['S' + str(rows_number), addr, req_id, res_id, now, "open", str(port)]
        writer.writerow(row)
        f.close()
    except:
        print("Exception with store a session: port=" + str(port))
        sys.exit(1)

# To load the session list
def loadSessionList(port):
    try:
        ses_path = filePathCreation(str(port), "ses")
        f = open(ses_path, 'r', newline='\n')
        reader = csv.reader(f)
        ses_lis = list(reader)
        ses_lis.pop(0)
        f.close()
        return ses_lis
    except:
        print("Exception with load session list: port=" + str(port))
        sys.exit(1)

# To check the existence of the current attacker in the sessions list
def checkAttackerExistence(port, addr):
    try:
        ses_path = filePathCreation(str(port), "ses")
        f = open(ses_path, 'r', newline='\n')
        reader = csv.reader(f)
        session_list = list(reader)
        session_list.pop(0)
        f.close()
        check = False
        for s in session_list:
            if str(addr[0]) in s[1]:
                    check = True
        return check
    except:
        print("Exception with chek if attacker already exists: port=" + str(port) + ", addr=" + str(addr))
        sys.exit(1)

# To check if there is already a session open with a specific Attacker (if yes, return session id)
def checkOpenSession(port, addr):
    ses_path = filePathCreation(str(port), "ses")
    f = open(ses_path, 'r', newline='\n')
    reader = csv.reader(f)
    session_list = list(reader)
    session_list.pop(0)
    f.close()

    last_time = None
    ses_id = None
    # Backward scrolling of the list
    for s in reversed(session_list):
        if str(addr[0]) in str(s[1]):
            last_time = datetime.strptime(str(s[4]), '%Y-%m-%d %H:%M:%S.%f')
            ses_id = str(s[0])
            break

    check = False
    now = datetime.now()
    if last_time is not None and (now - last_time).total_seconds() >= SESSION_DURATION:
        print("Last session from this address was on: " + str(s[4]))
        ses_id = None
    elif last_time is not None and (now - last_time).total_seconds() < SESSION_DURATION:
        print("There is already a session with this address started "
              + str((now - last_time).total_seconds()) + " seconds ago")
        check = True
    else:
        print("This address has never started a session")

    return check, ses_id

# 5 - SCANS ---------------------------------------------------------------------------------
# Per store a scan
def storeScan(device, req, res, port, validity):
    try:
        rows_number = len(pd.read_csv('scans/iot_scanner_table.csv')) + 1
        f = open('scans/iot_scanner_table.csv', 'a', newline='\n')
        writer = csv.writer(f)
        now = datetime.now()
        scan_id = 'SCAN_' + str(rows_number)
        row = [scan_id, device, req, res, port, validity, now]
        writer.writerow(row)
        f.close()
        return scan_id
    except:
        print("Exception with store a scan: port=" + str(port) + ", device=" + str(device))
        sys.exit(1)

# To check if a scan already exists
def checkScan(device, req, port):
    try:
        f = open('scans/iot_scanner_table.csv', 'r', newline='\n')
        reader = csv.reader(f)
        scan_lis = list(reader)
        scan_lis.pop(0)
        f.close()
        check = False
        for s in scan_lis:
            if s[1] == device and s[2] == req and s[4] == port:
                check = True
        return check
    except:
        print("Exception with check if a scan exists: port=" + str(port) + ", device=" + str(device) + ", req=" + str(req))
        sys.exit(1)