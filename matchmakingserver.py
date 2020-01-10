import socket
import struct
from typing import List, Tuple, Dict

from array import array


def ipv4_to_int(ip: str) -> List[int]:
    return [int(x) for x in ip.split('.')]


def socket_to_bytes(ip, port)->bytes:
    # array.array('H',[*ipv4_to_int(ip),port]).tobytes()
    return struct.pack("!4BH", *ipv4_to_int(ip), port)  # 4B : l'adresse IP (signed char) H: le port

def list_to_bytes(addr_list):
    blist=[]
    for ip,port in addr_list:
        blist.extend(ipv4_to_int(ip))
        blist.append(port)
    buf = array('H',blist)
    length = struct.pack('H', len(buf))
    return length+buf

if __name__ == '__main__':
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(("0.0.0.0", 5600))

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
