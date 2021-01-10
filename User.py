import socket
import pickle
from fuzzy_extractor import FuzzyExtractor
import random
import json
import hashlib
import pickle
from base64 import b64encode, b64decode
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import numpy as np
import time
import sys

IDui = '123'
PWui = '456'
BIOui = 'AABBCCDDEEFFGGHH'
SIGMAui = ''
SIGMAui_ = ''
TAUui = ''
PIDui = ''
RPWui = ''
fl = ''
Cui = ''
TIDui = '789'
PIDapl = ''
I = None
ct = ''
iv = ''
alpha = ''
beta = ''
gamma = ''
delta_t = 5
Aui = ''
SKVuisdj = ''
b = []
t = 2
p = 5
IDsdj = '123'
PWui_ = ''
BSTARui = ''
Xui = ''
rui = ''
RPWui_ = ''
SKuisdj = ''

extractor = FuzzyExtractor(16, 8)

def createSocket():
    soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    return soc

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

def sendData(soc,data):
    try:
        data_byte =  pickle.dumps(data)
        soc.sendall(data_byte)
    except BaseException as e:
        print('Failed to send data')
        soc.close()

def sendEncData(soc,data):
    try:
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
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

def makeConnection(soc, port):
    try:
        soc.connect(("localhost", port))
    except BaseException as e:
        print("Error Connecting to the Server: {msg}".format(msg=e))
        soc.close()
        raise Exception('Socket Closed.')

def calculateX(value):
    sum = 0
    for i in value:
        sum += ord(i)
    a = sum%256
    return a

def encrypt(data, key):
    data_byte = pickle.dumps(data)
    key = hashlib.sha256(key.encode('utf-8')).digest()[:256]
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data_byte, 128))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    return ct, iv

def decrypt(ct, iv, key):
    ct = b64decode(ct)
    iv = b64decode(iv)
    key = hashlib.sha256(key.encode('utf-8')).digest()[:256]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), 128)
    pt = pickle.loads(pt)
    return pt

def UserRegistration():
    global BSTARui, alpha, beta, gamma, IDui, PWui, RPWui, BIOui, extractor, SIGMAui, TAUui, fl, Cui, PIDapl, I, ct, iv, Aui, PIDui
    soc = createSocket()
    makeConnection(soc, 9999)

    SIGMAui, TAUui = extractor.generate(BIOui)

    alpha = str(random.randint(10,100))
    beta = str(random.randint(10,100))
    gamma = str(random.randint(10,100))

    data = IDui + alpha
    PIDui = hashData(data)

    data = PWui + SIGMAui.decode('ISO-8859-1').strip() + beta
    RPWui = hashData(data)
    # print('RPWui ',RPWui)

    RPWuiGamma = xor_two_str(RPWui, gamma)
    PREQui = {'PIDui': PIDui, 'RPWuiGamma':RPWuiGamma}
    sendData(soc,PREQui)

    recieved_data, status = recv(soc)
    if status == 0:
        soc.close()
        raise Exception('No Data recieved')

    Bui = recieved_data['Bui']
    fl = recieved_data['fl']
    Aui = recieved_data['Aui']
    PIDapl = recieved_data['PIDapl']
    BSTARui = xor_two_str(Bui,gamma)

    I = {'Aui':Aui,'BSTARui':BSTARui,'beta':beta,'PIDui':PIDui,'PIDapl':PIDapl}
    data = IDui + SIGMAui.decode('ISO-8859-1').strip() + PWui
    Kui = hashData(data)
    ct, iv = encrypt(I,Kui)
    
    data = Aui + SIGMAui.decode('ISO-8859-1').strip() + beta
    Cui = hashData(data)
    soc.close()

def Login():
    global alpha, beta, gamma, TAUui, extractor, I, ct, iv, Cui, beta, PWui_, SIGMAui_

    IDui = input("Enter ID")
    PWui_ = input("Enter Password")
    BIOui_ = input("Enter Biometric")

    try:
        SIGMAui_ = extractor.reproduce(BIOui_,TAUui)
        data = IDui + SIGMAui_.decode('ISO-8859-1').strip() + PWui_
        Kui_ = hashData(data)
        I_ = decrypt(ct, iv, Kui_)
        if I != I_:
            raise Exception('Wrong Credentials')

        Aui_ = I['Aui']
        data = Aui_+ SIGMAui_.decode('ISO-8859-1').strip() + beta
        Cui_ = hashData(data)
        if Cui != Cui_:
            raise Exception('Wrong Credentials')
        else:
            print('Authenticated')
    except Exception as e:
        raise Exception('Wrong Credentials')

def GenBivariatePolynomial():
    global b
    b = [[1,2,3],[1,2,3],[1,2,3]]
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

def BuildSessionKey():
    global delta_t, RWUu_, Xui, Aui, PIDui, PIDapl, SKVuisdj, b, TIDui, rui, RPWui_, SKuisdj

    soc = createSocket()
    soc.bind(("localhost", 10002))
    soc.listen(1)
    connection, client_info = soc.accept()

    received_data, status = recv(connection)
    if status == 0:
        connection.close()
        raise Exception('No Data recieved')

    TSstartsdj = time.time()
    TSsdj = received_data['TSsdj']
    M6 = received_data['M6']
    IDsdj = received_data['IDsdj']
    SKVsdjui = received_data['SKVsdjui']
    M7 = received_data['M7']

    if TSstartsdj - TSsdj > delta_t:
        connection.close()
        raise Exception('Timeout')

    data = Aui + Xui + RPWui_ + rui
    hashdata = hashData(data)

    data = hashdata + PIDui + PIDapl
    M8 = hashData(data)
    data = M8 + IDsdj + str(TSsdj)
    hashdata = hashData(data)

    M9 = xor_two_str(M6,hashdata)

    data = M8 + M9 + str(TSsdj)
    SKuisdj = hashData(data)
    print('session key ',SKuisdj)
    data = SKuisdj + str(TSsdj)
    SKVuisdj = hashData(data)
    print('SKVuisdj ',SKVuisdj)

    if SKVsdjui != SKVuisdj:
        connection.close()
        raise Exception('Key Mismtach')

    data1 = M9 + str(TSsdj)
    hashdata1 = hashData(data1)

    fl = bivariatePolynomial(PIDui, PIDapl)
    data2 = TIDui + PIDui + PIDapl + fl
    hashdata2 = hashData(data2)

    temp_xor = xor_two_str(M7,hashdata1)
    TIDuinew = xor_two_str(temp_xor,hashdata2)

    TIDui = TIDuinew

def Msg1():
    global IDsdj, Yui, Zui, TSui, PWui_, SIGMAui_, BSTARui, Aui, PIDui, PIDapl, Xui, rui, RPWui_

    soc = createSocket()
    makeConnection(soc,10001)

    TSui=time.time()
    rui=str(random.randint(10, 100))

    data = PWui_ + SIGMAui_.decode('ISO-8859-1').strip() + beta
    RPWui_ = hashData(data)
    Xui =  xor_two_str(BSTARui, RPWui_)

    data = Aui + Xui + RPWui_ + rui
    Yuipart1 = hashData(data)

    fl = bivariatePolynomial(PIDui,PIDapl)
    data= fl + str(TSui)
    Yuipart2 = hashData(data)
    Yui = xor_two_str(Yuipart1, Yuipart2)

    data = TIDui + Yui + fl + IDsdj + str(TSui)

    Zui = hashData(data)
    data = {'TIDui':TIDui,'IDsdj':IDsdj,'Yui':Yui,'Zui':Zui,'TSui':TSui}

    sendData(soc,data)
    soc.close()

def TransferFile():
    global SKuisdj

    src = input('Enter File Name')

    soc = createSocket()
    makeConnection(soc,10000)

    data = {'filename':src}
    sendEncData(soc,data)

    fp = open(src,'rb')
    while True:
        data = fp.read(512)
        if not data:
            # print('here')
            data = {'message':'END'}
            sendEncData(soc,data)
            soc.close()
            fp.close()
            break
        cipher_text, iv = encrypt(data,SKuisdj)
        # print('enc ',cipher_text)
        # print('iv ',iv)
        # print('data ',data)
        data = {'message':'DATA','cipher_text':cipher_text,'iv':iv}
        sendEncData(soc,data)
        rec, st = recv(soc)
    fp.close()

if __name__ == '__main__':
    GenBivariatePolynomial()
    UserRegistration()
    Login()
    Msg1()
    BuildSessionKey()
    TransferFile()
