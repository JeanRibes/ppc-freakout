import socket
import time
from threading import Timer, Thread
from typing import List, Tuple
from matchmaking import udp_port, list_to_bytes

if __name__ == '__main__':
    print("starting matchmaking server")
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(("0.0.0.0", udp_port))

    open_games: List[Tuple[str, int]] = []
    last_seen = {}


    def check_gameservers():
        while True:
            time.sleep(5)
            for host in open_games:
                if last_seen[host] > 2:
                    print(str(host)+" a été rejeté pour inactivité")
                    open_games.remove(host)
                else:
                    sock.sendto(b'R U alive ?', host)
                    last_seen[host] += 1
    Thread(target=check_gameservers, daemon=True).start()
    while True:
        data, addr = sock.recvfrom(255)
        print("{} : {}".format(str(addr), str(data)))
        if data == b"open":
            open_games.append(addr)
            last_seen[addr] = 0
            print(open_games)
        elif data == b"close":
            try:
                open_games.remove(addr)
            except ValueError:
                print(str(addr) + " n'a pas pu être enlevé")

            print(open_games)
        elif data == b'im alive':
            last_seen[addr] = 0
            #print("{} poked".format(addr))
        elif data == b'list':
            print("sending list to" + str(addr))
            sock.sendto(list_to_bytes(open_games), addr)
