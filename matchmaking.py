import socket, struct
from threading import Thread
import typing
import time

from array import array

udp_announce_port = 5688
server_ip = "vps.ribes.ovh"

class BroadcastGame(Thread):
    message = b'0 joueurs'
    run=True
    def run(self) -> None:
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # pour autoriser le boarast
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # pour éviter d'avoir l'erreur
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # de permission quand on ferme mal le jeu
        while self.run:
            sock.sendto(self.message, ('255.255.255.255', udp_announce_port))
            time.sleep(3)

    def setmessage(self, msg:str):
        self.message = msg.encode('utf-8')


if __name__ == '__main__':
    BroadcastGame().start()