import csv
import pandas as pd
from datetime import datetime
from data_handler import *
import subprocess as sub
import time

NEGATIVE_RESPONSE_SCORE = 0.2
EXPLOIT_DETECTED_SCORE = 0.5
SESSION_TIME = 180
FIRST_RESPONSE_SCORE = 0.08
SECOND_RESPONSE_SCORE = 0.03
THIRD_RESPONSE_SCORE = 0.01
SCORE_LIMIT = 1

# Negative update
def negativeUpdateResponseScore(port):
    session_list = loadSessionList(port)

    # Select all session id of the session still open to validate
    open_sessions_to_validate = []
    session_id_list_to_validate = []
    long_sessions_list = []
    now = datetime.now()
    for s in session_list:
        if str(s[5]) == "open":
            last_time = datetime.strptime(str(s[4]), '%Y-%m-%d %H:%M:%S.%f')
            if (now - last_time).total_seconds() >= SESSION_TIME:
                open_sessions_to_validate.append(s)
                session_id_list_to_validate.append(str(s[0]))
                if session_id_list_to_validate.count(str(s[0]))>1:
                    long_sessions_list.append(str(s[0]))

    # Select all session id of the session that have only one exchange of messages
    short_sessions_list = set(session_id_list_to_validate)
    for s in set(long_sessions_list):
        short_sessions_list.remove(s)
   
    # Select all response ids to be negatively updated
    negative_response_list = []
    for s in session_list:
        if str(s[0]) in short_sessions_list:
            negative_response_list.append(str(s[3]))

    # Negative responses update
    res_path = filePathCreation(str(port), "res")
    df = pd.read_csv(res_path)
    for nr in set(negative_response_list):
        try:
            # print(df.loc[df["ID"] == str(nr), "SCORE"])
            current_score = df.loc[df["ID"] == nr, "SCORE"].values[0]
            print("Response " + str(nr) + " current score: " + str(current_score))
            current_score = float(current_score)
            if (current_score - NEGATIVE_RESPONSE_SCORE) <= 0.0:
                current_score = 0.0
            else:
                current_score = current_score - NEGATIVE_RESPONSE_SCORE
            df.loc[df["ID"] == nr, "SCORE"] = current_score
            print("Response " + str(nr) + " new score: " + str(current_score))

        except:
            print("Exception with response: " + str(nr))
            #df.loc[df["ID"] == nr, "SCORE"] = 0.5
    df.to_csv(res_path, index=False)

    # Close open sessions that have been checked
    ses_path = filePathCreation(str(port), "ses")
    df = pd.read_csv(ses_path)
    for s in set(session_id_list_to_validate):
        df.loc[df["SessionID"] == s, "STATUS"] = "closed"
        df.loc[df["SessionID"] == s, "PORT"] = str(int(port))

    for s in session_list:
        if str(s[6]) == str(port):
            df.loc[df["SessionID"] == str(s[0]), "PORT"] = str(int(port))
    df.to_csv(ses_path, index=False)

# Snort alerts check
def checkSnortAlerts(port, req_id):
    time.sleep(1)
    snort_conf_path = ("/etc/snort/snort.conf")
    pcap_path = ("/home/CandyPot/requests/port_" + str(port) + "_requests_pcap/" + str(req_id) + ".pcap")
    p = sub.Popen(("sudo", "snort", "-c", str(snort_conf_path), "-A", "console", "-q", "-r", str(pcap_path)),
                  stdout=sub.PIPE)
    alert_check = False
    for alert in p.stdout:
        alert_check = True
        print("**************** Alert Found *********************")
    return alert_check

# Altrernative alerts check
def checkTextAlerts(request_message):
    f = open(r'exploit_code.csv', 'r', newline='\n')
    reader = csv.reader(f)
    exploit_list = list(reader)
    exploit_list.pop(0)
    f.close()

    check_exploit = False
    for exp in exploit_list:
        if str(exp[1]) in request_message:
            check_exploit = True

    return check_exploit

# Positive update
def positiveUpdateResponseScore(ses_id, req_id, port):
    session_list = loadSessionList(port)

    response_session_list = []
    for s in session_list:
        if str(s[0]) == ses_id:
            response_session_list.append(str(s[3]))

    # To get the last response of the current session
    last_response_id = response_session_list[-1]

    # Based on the request received, a score is assigned to the response
    # 1 - Check for malicious code in the request
    # 2 - A score is assigned based on the order of the response in the session

    # 1 --------------------------------------------------------------
    requests_list = loadRequestList(port)

    request_message = ""
    for r in requests_list:
        if str(r[0]) == req_id:
            request_message = str(r[2])

    # Check if there is something malicious in the request
    check_exploit = checkTextAlerts(request_message)

    # Check Snort Alert in pcap file
    alert_check = checkSnortAlerts(port, req_id)

    # 2 --------------------------------------------------------------
    res_path = filePathCreation(str(port), "res")
    df = pd.read_csv(res_path)
    try:
        changes_check = False
        current_score = df.loc[df["ID"] == str(last_response_id), "SCORE"].values[0]
        current_score = float(current_score)
        initial_score = current_score
        if len(response_session_list) == 1 and current_score <= SCORE_LIMIT - FIRST_RESPONSE_SCORE:
            current_score = current_score + FIRST_RESPONSE_SCORE
            changes_check = True
        elif len(response_session_list) == 2 and current_score <= SCORE_LIMIT - SECOND_RESPONSE_SCORE:
            current_score = current_score + SECOND_RESPONSE_SCORE
            changes_check = True
        elif len(response_session_list) == 3 and current_score <= SCORE_LIMIT - THIRD_RESPONSE_SCORE:
            current_score = current_score + THIRD_RESPONSE_SCORE
            changes_check = True

        # If malicious code was found in the previous request then its score is increased
        if check_exploit or alert_check:
            current_score = current_score + EXPLOIT_DETECTED_SCORE
            changes_check = True

        df.loc[df["ID"] == str(last_response_id), "SCORE"] = current_score

        if changes_check:
            print('----------Positive score update - port ' + str(port) + '----------')
            print("Response " + str(last_response_id) + " current score: " + str(initial_score))
            print("Response " + str(last_response_id) + " new score: " + str(current_score))
            print('----------End of positive score update - port ' + str(port) + '----------')
    except:
        print("Exception with response: " + str(last_response_id))
    df.to_csv(res_path, index=False)
