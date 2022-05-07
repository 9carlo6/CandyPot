import csv
import pandas as pd
from datetime import datetime

from scapy.all import *



def test(pkt):
    #print(pkt)
    wrpcap("temp2.cap",pkt)
    b = raw(pkt)
    print(b)

print(rdpcap("temp2.cap"))

#sniff(filter="port 80", prn=test)

#p = sr1(IP(dst="www.google.com")/ICMP()/"XXXXXXXXXXX")
#p.show()

sniff(filter="port 80", prn=lambda x: x.sprintf("%IP.src%:%TCP.sport% -> %IP.dst%:%TCP.dport%  %2s,TCP.flags% : %TCP.payload%"))


"""
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
        if str(exp[1]) in requests_message:
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
        if len(session_list) == 1 and current_score <= 0.92:
            current_score = current_score + 0.08
        elif len(session_list) == 2 and current_score <= 0.97:
            current_score = current_score + 0.03
        elif len(session_list) == 3 and current_score <= 0.99:
            current_score = current_score + 0.01

        # Se è stato trovato del codice malevolo nella richiesta precedente allora si aumenta di + 0.2
        if check_exploit:
            current_score = current_score + 0.2
        print("Response " + str(last_response_id) + " new score: " + str(current_score))
    except:
        print("Exception with response: " + str(last_response_id))
    df.to_csv('port_' + str(port) + '_response.csv', index=False)

"""




"""
# open the file in the write mode
f = open('sessions.csv', 'w', newline='')

# create the csv writer
writer = csv.writer(f)

# write a row to the csv file
header = ['Session ID', 'Request ID', 'Response ID']
row = ['S1', 'req1', 'res1']
writer.writerow(header)
writer.writerow(row)

# close the file
f.close()
"""

"""
file = "port_8080_response.csv"
df = pd.read_csv(file)
df["SCORE"] = 0.5
df.to_csv(file, index=False)
"""

"""
file = "port_80_response.csv"
df = pd.read_csv(file)
print(df.loc[df["ID"] == "RES_3_P80", "SCORE"].values[0])
#print(df.loc[(df['STATUS'] == 'open') & (df['PORT'] == 80)])
#df.to_csv(file, index=False)
"""




