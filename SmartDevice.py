import socket
import pickle
import time
import random
import hashlib
from base64 import b64encode, b64decode
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import sys

IDsdj = ''
TCsdj = ''
SKsdjui = ''

delta_t = 0.1

def recv(soc):
    received_data = b""
    while True:
        try:
            data = soc.recv(4096)
            received_data += data
            if data == b'':
                return None, 0

            else:
                if len(received_data) > 0:
                    try:
                        print('before loads')
                        received_data = pickle.loads(received_data)
                        print('after loads')
                        return received_data, 1
                    except BaseException as e:
                        print("Error Decoding the Client's Data: {msg}.\n".format(msg=e))
                        return None, 0
                else:
                    return None, 0

        except BaseException as e:
            print("Error Receiving Data from the Client: {msg}.\n".format(msg=e))
            return None, 0

def sendData(soc,data):
    try:
        data_byte =  pickle.dumps(data)
        soc.sendall(data_byte)
    except BaseException as e:
        print('Failed to send data')
        soc.close()

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

def RegisterDevice():
    global IDsdj, TCsdj
    soc = createSocket()
    soc.bind(("localhost", 10000))
    soc.listen(1)
    connection, client_info = soc.accept()

    received_data, status = recv(connection)
    if status == 0:
        connection.close()
        raise Exception('No Data recieved')
    IDsdj = received_data['IDsdj']
    TCsdj = received_data['TCsdj']
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

def decrypt(ct, iv, key):
    ct = b64decode(ct)
    iv = b64decode(iv)
    key = hashlib.sha256(key.encode('utf-8')).digest()[:256]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), 128)
    pt = pickle.loads(pt)
    return pt

def AuthenticateDevice():
    global TCsdj, IDsdj, SKsdjui

    soc = createSocket()
    soc.bind(("localhost", 10000))
    soc.listen(1)
    connection, client_info = soc.accept()

    received_data, status = recv(connection)
    if status == 0:
        connection.close()
        raise Exception('No Data recieved')

    TSapl = received_data['TSapl']
    TSaplstar = time.time()
    
    if abs(TSaplstar - TSapl) > delta_t:
        connection.close()
        raise Exception('Timed out')

    IDsdj = received_data['IDsdj']
    M2 = received_data['M2']
    M3 = received_data['M3']
    M4 = xor_two_str(M2, hashData(TCsdj + IDsdj + str(TSapl)))
    
    Rsdj = str(random.randint(10,100))
    TSsdj = time.time()

    M5 = hashData(IDsdj + TCsdj + Rsdj)
    SKsdjui = hashData(M4 + M5 + str(TSsdj))
    print('Session key ',SKsdjui)
    M6 = xor_two_str(M5, hashData(M4 + IDsdj + str(TSsdj)))

    SKVsdjui = hashData(SKsdjui + str(TSsdj))
    print('SKVsdjui ',SKVsdjui)
    M7 = xor_two_str(M3, hashData(M5 + str(TSsdj)))

    Msg3 = {'IDsdj':IDsdj, 'M6':M6, 'M7':M7, 'SKVsdjui':SKVsdjui, 'TSsdj':TSsdj}
    connection.close()

    soc = createSocket()
    makeConnection(soc,10002)
    sendData(soc,Msg3)
    soc.close()

def ReceiveFile():
    global SKsdjui
    
    soc = createSocket()
    soc.bind(("localhost", 10000))
    soc.listen(1)
    connection, client_info = soc.accept()

    received_data, status = recv(connection)
    if status == 0:
        connection.close()
        raise Exception('No Data recieved')

    file_name = received_data['filename']
    fp = open(file_name,'wb')
    while True:
        received_data, status = recv(connection)
        message = received_data['message']
        print(message)
        if message == 'END':
            print('Completed')
            connection.close()
            fp.close()
            break
        enc_data = received_data['cipher_text']
        iv = received_data['iv']
        # print('enc ',enc_data)
        # print('iv ',iv)
        plain_text = decrypt(enc_data,iv,SKsdjui)
        # print('plain text ',plain_text)
        fp.write(plain_text)
        data = {'sync':1}
        sendData(connection,data)
    fp.close()

if __name__ == '__main__':
    RegisterDevice()
    AuthenticateDevice()
    ReceiveFile()


