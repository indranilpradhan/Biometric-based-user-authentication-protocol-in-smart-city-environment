import socket
import pickle
import time
import hashlib
import numpy as np

IDsdj = ''
TCsdj = ''
PIDapl = ''
fl = []
TIDui = '789'
PIDui = ''
delta_t = 5
p = 5
b = []
t = 2
dic = {}

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

def createSocket():
    soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    return soc

def makeConnection(soc, port):
    try:
        soc.connect(("localhost", port))
    except BaseException as e:
        print("Error Connecting to the Server: {msg}".format(msg=e))
        soc.close()
        raise Exception('Socket Closed.')

def sendData(soc,data):
    try:
        data_byte =  pickle.dumps(data)
        soc.sendall(data_byte)
    except BaseException as e:
        print('Failed to send data')
        soc.close()

def RegisterAccessPoint():
    global IDsdj, TCsdj, fl, PIDapl
    soc= createSocket()
    soc.bind(("localhost", 10001))
    soc.listen(1)
    connection, client_info = soc.accept()

    received_data, status = recv(connection)
    if status == 0:
        connection.close()
        raise Exception('No Data recieved')

    IDsdj = received_data['IDsdj']
    TCsdj = received_data['TCsdj']
    PIDapl = received_data['PIDapl']
    fl = received_data['fl']
    connection.close()

def StoreInfoInAPfromRA():
    global TIDui, PIDui
    soc = createSocket()
    soc.bind(("localhost", 10001))
    soc.listen(1)
    connection, client_info = soc.accept()

    received_data, status = recv(connection)
    if status == 0:
        connection.close()
        raise Exception('No Data recieved')
    TIDui = received_data['TIDui']
    PIDui = received_data['PIDui']
    dic[TIDui] = PIDui
    connection.close()

def hashData(data):
    hashdata = hashlib.sha256(data.encode()).hexdigest()
    return hashdata

def xor_two_str(a,b):
    xored = []
    max_len = max(len(a),len(b))
    a = a.zfill(max_len)
    b = b.zfill(max_len)
    for i in range(max_len):
        xored_value = chr(ord(a[i]) ^ ord(b[i]))
        xored.append(xored_value)
    return ''.join(xored)

def getRandomId():
    return str(int(time.time())%1024)

def calculateX(value):
    sum = 0
    for i in value:
        sum += ord(i)
    a= sum%256
    return a

def GenBivariatePolynomial():
    global b
    b = b = [[1,2,3],[1,2,3],[1,2,3]]
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

def Authentication():
    global IDsdj, PIDapl, TCsdj, dic

    soc = createSocket()
    soc.bind(("localhost", 10001))
    soc.listen(1)
    connection, client_info = soc.accept()

    received_data, status = recv(connection)
    if status == 0:
        connection.close()
        raise Exception('No Data recieved')

    TSui = received_data['TSui']

    cur_time = time.time()
    if cur_time - TSui > delta_t:
        connection.close()
        raise Exception('Timed Out')
    connection.close()
    TIDui = received_data['TIDui']
    PIDui = dic[TIDui]
    
    fl = bivariatePolynomial(PIDui,PIDapl)

    Zui = received_data['Zui']
    Yui = received_data['Yui']
    IDsdj = received_data['IDsdj']

    Zui_ = hashData(TIDui + Yui + fl + IDsdj + str(TSui))
    if Zui_ != Zui:
        connection.close()
        raise Exception('Hash values are different at Access point')

    M1 = xor_two_str(Yui, hashData(fl + str(TSui)))
    TSapl = time.time()
    M2 = xor_two_str(hashData(M1 + PIDui + PIDapl), hashData(TCsdj + IDsdj + str(TSapl)))
    TIDui_new = getRandomId()
    M3 =  xor_two_str(TIDui_new, hashData(TIDui + PIDui + PIDapl + fl))
    Msg2 = {'IDsdj':IDsdj, 'M2':M2, 'M3':M3 , 'TSapl':TSapl}

    soc = createSocket()
    makeConnection(soc,10000)
    sendData(soc,Msg2)
    soc.close()


if __name__ == '__main__':
    GenBivariatePolynomial()
    RegisterAccessPoint()
    StoreInfoInAPfromRA()
    Authentication()