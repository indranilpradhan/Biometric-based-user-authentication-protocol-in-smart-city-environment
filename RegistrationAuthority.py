import socket
import pickle
import time
import hashlib
import numpy as np

MKra = '123'
IDra = '456'
p = 5 #Prime order
IDsdj  = ''
TCsdj = ''
PIDapl = ''
PIDui = ''
TIDui = '789'
y = '5'

def createSocket():
    soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    return soc

def sendData(soc,data):
    try:
        data_byte =  pickle.dumps(data)
        soc.sendall(data_byte)
    except BaseException as e:
        print('Failed to send data')
        soc.close()

def recv(soc):
    received_data = b""
    while True:
        try:
            data = soc.recv(1024)
            received_data += data
            if data == b'':
                return None, 0

            else:
                if len(received_data) > 0:
                    try:
                        received_data = pickle.loads(received_data)
                        return received_data, 1
                    except BaseException as e:
                        print("Error Decoding the Client's Data: {msg}.\n".format(msg=e))
                        return None, 0
                else:
                    return None, 0

        except BaseException as e:
            print("Error Receiving Data from the Client: {msg}.\n".format(msg=e))
            return None, 0

def hashData(data):
    hashdata = hashlib.sha256(data.encode()).hexdigest()
    return hashdata

def calculateX(value):
    return hash(value)%256

#Generating a random bivariate polynomial
b = []
t = 2
def GenBivariatePolynomial():
    global b
    b = np.random.randint(0, p,[t+1, t+1])
    for i in range(t+1):
        for j in range(t+1):
            if i+j >= t:
                b[i][j] = 0

def bivariatePolynomial(x,y):
    x = calculateX(x)
    y = calculateX(y)
    poly = 0
    for u in range(t+1):
        for v in range(t+1):
            if u+v >= t:
                break
            poly += (b[u][v]*((x**u)*(y**v)%p))%p
    return str(poly)

def xor_two_str(a,b):
    xored = []
    max_len = max(len(a),len(b))
    a = a.zfill(max_len)
    b = b.zfill(max_len)
    for i in range(max_len):
        xored_value = chr(ord(a[i]) ^ ord(b[i]))
        xored.append(xored_value)
    return ''.join(xored)

def makeConnection(soc, port):
    try:
        soc.connect(("localhost", port))
    except BaseException as e:
        print("Error Connecting to the Server: {msg}".format(msg=e))
        soc.close()
        raise Exception('Socket Closed.')

def RegisterDevice():
    global MKra, IDsdj, TCsdj
    soc = createSocket()
    makeConnection(soc,10000)

    IDsdj = '123'
    MKsdj = '456'
    RTSsdj = time.time()

    data = IDsdj + MKsdj + str(RTSsdj) + MKra
    TCsdj = hashData(data)

    data = {'IDsdj':IDsdj,'TCsdj':TCsdj}
    sendData(soc,data)
    soc.close()

def RegisterAccessPoint():
    global MKra, y, IDsdj, TCsdj, PIDapl
    soc = createSocket()
    makeConnection(soc,10001)

    IDapl = '321'
    MKapl = '654'
    RTSapl = time.time()

    data = IDapl + MKapl + MKra + str(RTSapl)
    PIDapl = hashData(data)

    fl = bivariatePolynomial(PIDapl,y)

    data = {'PIDapl':PIDapl,'IDsdj':IDsdj,'TCsdj':TCsdj,'fl':fl}
    sendData(soc,data)
    soc.close()

def UserRegistration():
    global MKra, IDra, y, PIDapl, PIDui
    soc = createSocket()
    soc.bind(("localhost", 9999))
    soc.listen(1)
    connection, client_info = soc.accept()

    received_data, status = recv(connection)
    if status == 0:
        connection.close()
        raise Exception('No Data recieved')
    
    PIDui = received_data['PIDui']
    RPWuiGamma = received_data['RPWuiGamma']
    data = PIDui + MKra + IDra
    Aui = hashData(data)

    RTSui = str(time.time())
    data = MKra + RTSui + IDra
    hash_data = hashData(data)
    Bui = xor_two_str(hash_data,RPWuiGamma)

    fl = bivariatePolynomial(PIDui,y)

    PREPui = {'Aui':Aui, 'Bui':Bui, 'fl':fl,'PIDapl':PIDapl}
    sendData(connection, PREPui)
    connection.close()

def StoreInfoInAP():
    global TIDui, PIDui
    soc = createSocket()
    makeConnection(soc,10001)

    data = {'TIDui':TIDui,'PIDui':PIDui}
    sendData(soc,data)
    soc.close()

if __name__ == "__main__":
    GenBivariatePolynomial()
    RegisterDevice()
    RegisterAccessPoint()
    UserRegistration()
    StoreInfoInAP()
