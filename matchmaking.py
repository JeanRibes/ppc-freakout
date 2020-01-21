import socket, struct
from threading import Thread
import typing
import time

from array import array

udp_announce_port = 5688
server_ip = "vps.ribes.ovh"


def ipv4_to_ints(ip: str) -> typing.List[int]:
    return [int(x) for x in ip.split('.')]


def socket_to_bytes(ip, port) -> bytes:
    # array.array('H',[*ipv4_to_int(ip),port]).tobytes()
    return struct.pack("!4BH", *ipv4_to_ints(ip), port)  # 4B : l'adresse IP (signed char) H: le port


def bytes_to_socket(bin: bytes) -> typing.Tuple[str, int]:
    data = struct.unpack("!4BH", bin)
    ip = ".".join((str(i) for i in data[:4]))
    port = data[4]
    return (ip, port)


class BroadcastGame(Thread):
    run = True

    def __init__(self, tcp_addr=('127.0.0.1', 1976)):
        self.tcp_addr = tcp_addr
        super().__init__(daemon=True)

    def run(self) -> None:
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # pour autoriser le boarast
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # pour éviter d'avoir l'erreur
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # de permission quand on ferme mal le jeu
        while self.run:
            sock.sendto(socket_to_bytes(*self.tcp_addr), ('255.255.255.255', udp_announce_port))
            time.sleep(1)


def find_server():
    print("Recherche de serveurs de jeu")
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # pour autoriser le boarast
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # pour éviter d'avoir l'erreur
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # de permission quand on ferme mal le jeu

    sock.bind(('', udp_announce_port))  # on veut tout recevoir

    sock.settimeout(10)
    try:
        msg, addr = sock.recvfrom(4096)
        game_addr = bytes_to_socket(msg)
        print(f"{game_addr} reçu de {addr}")
        print("Jeu trouvé, connexion...")
        return game_addr
    except socket.timeout:
        print("Aucun serveur trouvé !")
        print("Essai de l'adresse par défaut")
        return ('127.0.0.1', 1976)

class FindGame(Thread):
    def run(self) -> None:
        self.found_server = find_server()

if __name__ == '__main__':
    BroadcastGame().start()
    FindGame().start()
