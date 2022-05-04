import csv
import pandas as pd
from datetime import datetime

def negativeUpdateResponseScore(port):
    f = open(r'sessions.csv', 'r', newline='\n')
    reader = csv.reader(f)
    session_list = list(reader)
    session_list.pop(0)
    f.close()

    # seleziona l'id delle sessioni ancora aperte relative alla specifica porta
    open_sessions_to_validate = []
    checked_session_list = []
    long_sessions_list = []
    now = datetime.now()
    for s in session_list:
        if str(s[6]) == str(port) and str(s[5]) == "open":
            last_time = datetime.strptime(str(s[4]), '%Y-%m-%d %H:%M:%S.%f')
            if (now - last_time).total_seconds() >= 180:
                open_sessions_to_validate.append(s)
                if str(s[0]) in checked_session_list:
                    long_sessions_list.append(str(s[0]))
                checked_session_list.append(str(s[0]))

    # seleziona l'id delle sessioni che hanno un solo scambio di messaggi
    short_sessions_list = set(checked_session_list)
    for s in set(long_sessions_list):
        short_sessions_list.remove(s)


    # seleziona l'id delle risposte alle quali bisogna ridurre lo score
    negative_response_list = []
    for s in session_list:
        if str(s[0]) in short_sessions_list:
            negative_response_list.append(str(s[3]))

    # Riduce lo score delle risposte selezionate
    df = pd.read_csv('port_' + str(port) + '_response.csv')
    for nr in set(negative_response_list):
        try:
            # print(df.loc[df["ID"] == str(nr), "SCORE"])
            current_score = df.loc[df["ID"] == nr, "SCORE"].values[0]
            print("Response " + str(nr) + " current score: " + str(current_score))
            current_score = float(current_score)
            if (current_score - 0.2) <= 0.0:
                current_score = 0.0
            else:
                current_score = current_score - 0.2
            df.loc[df["ID"] == nr, "SCORE"] = current_score
            print("Response " + str(nr) + " new score: " + str(current_score))

        except:
            print("Exception with response: " + str(nr))
            #df.loc[df["ID"] == nr, "SCORE"] = 0.5
    df.to_csv('port_' + str(port) + '_response.csv', index=False)


    # Chiudere le sessioni aperte che sono state controllate
    df = pd.read_csv('sessions.csv')
    for s in set(checked_session_list):
        df.loc[df["SessionID"] == s, "STATUS"] = "closed"
        df.loc[df["SessionID"] == s, "PORT"] = str(int(port))

    for s in session_list:
        if str(s[6]) == str(port):
            df.loc[df["SessionID"] == str(s[0]), "PORT"] = str(int(port))
    df.to_csv('sessions.csv', index=False)


def positiveUpdateResponseScore(ses_id, req_id, port):
    f = open(r'sessions.csv', 'r', newline='\n')
    reader = csv.reader(f)
    session_list = list(reader)
    session_list.pop(0)
    f.close()

    response_session_list = []
    for s in session_list:
        if str(s[0]) == ses_id:
            response_session_list.append(str(s[3]))

    # Per prendere l'ultima risposta della sessione corrente
    last_response_id = response_session_list[-1]

    # In base alla richiesta arrivata si assegna uno score alla risposta
    # Bisogna controllare se nella richiesta c'è del codice malevolo
    f = open(r'port_' + str(port) + '_requests.csv', 'r', newline='\n')
    reader = csv.reader(f)
    requests_list = list(reader)
    requests_list.pop(0)
    f.close()

    request_message = ""
    for r in requests_list:
        if str(r[0]) == req_id:
            request_message = str(r[2])

    f = open(r'exploit_code.csv', 'r', newline='\n')
    reader = csv.reader(f)
    exploit_list = list(reader)
    exploit_list.pop(0)
    f.close()

    check_exploit = False
    for exp in exploit_list:
        if str(exp[1]) in request_message:
            check_exploit = True

    # In base all'ordine della risposta nella sessione si assegna uno score
    # Prima risposta della sessione + 0.08
    # Seconda risposta della sessione + 0.03
    # Terza risposta della sessione + 0.01
    df = pd.read_csv('port_' + str(port) + '_response.csv')
    try:
        current_score = df.loc[df["ID"] == str(last_response_id), "SCORE"].values[0]
        current_score = float(current_score)
        print("Response " + str(last_response_id) + " current score: " + str(current_score))
        if len(response_session_list) == 1 and current_score <= 0.92:
            current_score = current_score + 0.08
        elif len(response_session_list) == 2 and current_score <= 0.97:
            current_score = current_score + 0.03
        elif len(response_session_list) == 3 and current_score <= 0.99:
            current_score = current_score + 0.01

        # Se è stato trovato del codice malevolo nella richiesta precedente allora si aumenta di + 0.2
        if check_exploit:
            current_score = current_score + 0.2
        print("Response " + str(last_response_id) + " new score: " + str(current_score))
    except:
        print("Exception with response: " + str(last_response_id))
    df.to_csv('port_' + str(port) + '_response.csv', index=False)