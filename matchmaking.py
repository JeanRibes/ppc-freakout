import socket, struct

from array import array

udp_port = 1352
server_ip = "127.0.0.1"


def ipv4_from_ints(ints):
    return ".".join(str(i) for i in ints)


def socket_from_ints(ints):
    return (
        ipv4_from_ints(ints[:4]),
        ints[4]
    )


def list_servers():
    mms: socket.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    mms.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mms.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    mms.sendto(b'list', (server_ip, udp_port))
    buf = mms.recv(1024)
    mms.close()

    #print(len(buf))
    data = list(struct.iter_unpack('5H', buf))
    servers = []
    for intsock in data:
        servers.append(socket_from_ints(intsock))
    return servers

def signal_matchmaking(state: bytes, local_port):
    mms: socket.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    mms.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mms.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    mms.bind(("0.0.0.0", local_port))
    mms.sendto(state, (server_ip, udp_port))
    mms.close()

def ipv4_to_int(ip: str):
    return [int(x) for x in ip.split('.')]


def socket_to_bytes(ip, port) -> bytes:
    # array.array('H',[*ipv4_to_int(ip),port]).tobytes()
    return struct.pack("!4BH", *ipv4_to_int(ip), port)  # 4B : l'adresse IP (signed char) H: le port


def list_to_bytes(addr_list):
    blist = []
    for ip, port in addr_list:
        blist.extend(ipv4_to_int(ip))
        blist.append(port)
    buf = array('H', blist)
    return buf
