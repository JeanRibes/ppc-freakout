import socket
from typing import List, Tuple
from matchmaking import udp_port, list_to_bytes

if __name__ == '__main__':
    print("starting matchmaking server")
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(("0.0.0.0", udp_port))

    open_games: List[Tuple[str, int]] = []

    while True:
        data, addr = sock.recvfrom(255)
        print("{} : {}".format(str(addr), str(data)))
        if data == b"open":
            open_games.append(addr)
            print(open_games)
        elif data == b"close":
            open_games.remove(addr)
            print(open_games)
        else:
            print("else")
            sock.sendto(list_to_bytes(open_games), addr)
