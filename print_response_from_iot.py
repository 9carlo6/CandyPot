import pickle
import requests

def storeData(obj, filename):
    pickleFile = open(filename, 'wb')
    pickle.dump(obj, pickleFile)
    pickleFile.close()

def loadData(filename):
    pickleFile = open(filename, 'rb')
    obj = pickle.load(pickleFile)
    pickleFile.close()
    return obj

#port = int(input("Enter port:"))
file_name = 'response_from_iot.dat'
obj = loadData(file_name)
#print(obj)
for value in list(obj.items()):
    address, response = value
    print(address)
    print(response.headers)
    print(response.content)
    print(response.status_code)
    print(response.request)
    print(response.url)
    #print(value)
    print(address.split(":")[1])
    print()
