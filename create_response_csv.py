import pickle
from datetime import datetime
import csv

def storeData(obj, filename):
    pickleFile = open(filename, 'wb')
    pickle.dump(obj, pickleFile)
    pickleFile.close()

def loadData(filename):
    pickleFile = open(filename, 'rb')
    obj = pickle.load(pickleFile)
    pickleFile.close()
    return obj

port = int(input("Enter port:"))
#file_name = 'port_' + str(port) + '.dat'
#obj = loadData(file_name)


# open the file in the write mode
f = open('port_' + str(port) + '_response.csv', 'w', newline='')

# create the csv writer
writer = csv.writer(f)

row = ["ID", "ADDR", "HEADERS", "CONTENT", "STATUS_CODE", "REQ_TYPE", "VALUE", "TIME"]
writer.writerow(row)

file_name = 'response_from_iot.dat'
obj = loadData(file_name)


i=0
for value in list(obj.items()):
    address, response = value
    if(str(address.split(":")[1])==str(port)):
        i=i+1
        id = 'RES_' + str(i) + '_P' + str(port)

        # datetime object containing current date and time
        now = datetime.now()

        row = [id, address.split(":")[0], response.headers, response.content, response.status_code, response.request,now]

        # writer.writerow(header)
        writer.writerow(row)

# close the file
f.close()