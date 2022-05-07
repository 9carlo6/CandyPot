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
file_name = 'port_' + str(port) + '.dat'
obj = loadData(file_name)


# open the file in the write mode
f = open('port_' + str(port) + '_requests.csv', 'w', newline='')

# create the csv writer
writer = csv.writer(f)

row = ["ID", "ADDR", "VALUE", "TIME"]
writer.writerow(row)

i=0
for value in obj:
    i=i+1
    id = 'REQ_' + str(i) + '_P' + str(port)
    #value = bytes(s, 'utf-8') + value
    print(value)
    #print(value.decode())
    print()

    # datetime object containing current date and time
    now = datetime.now()

    row = [id, None, value, now]

    # writer.writerow(header)
    writer.writerow(row)

# close the file
f.close()