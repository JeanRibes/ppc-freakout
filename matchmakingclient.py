import socket,struct
from array import array

if __name__=='__main__':
    mms:socket.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    mms.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mms.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    mms.sendto(b'list', ('127.0.0.1', 5600))
    buf = mms.recv(1024)
    mms.close()

    length = struct.unpack('H', buf[:2])[0] # on lit les 4 premiers octets, longueur du payload
    data = list(struct.iter_unpack('5H', buf[2:]))
    servers = []
    for binsock in data:
        port = binsock[4]
        ip = ".".join(str(i) for i in binsock[:4])
        addr = (ip,port)
        print(addr)
        servers.append(addr)
    #print(array.frombytes(buf[4:]))


