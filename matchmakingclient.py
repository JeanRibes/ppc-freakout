import socket
from matchmaking import udp_announce_port

if __name__ == '__main__':
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # pour autoriser le boarast
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # pour éviter d'avoir l'erreur
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # de permission quand on ferme mal le jeu

    sock.bind(('',udp_announce_port)) # on veut tout recevoir

    sock.settimeout(5)
    try:
        msg, addr = sock.recvfrom(4096)
        print(f"{msg} reçu de {addr}")
    except socket.timeout:
        pass