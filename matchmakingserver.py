import socket

if __name__=='__main__':
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT,1)
    sock.bind(())
    while True:
