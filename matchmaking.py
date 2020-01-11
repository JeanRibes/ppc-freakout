import socket, struct
from threading import Thread
import typing

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

    # print(len(buf))
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


def metadata_to_bytes(metadata) -> bytes:
    length, usernames = metadata
    s = str(length) + ";,;" + ";,;".join(usernames)
    return s.encode('utf-8')


class MetadataServer(Thread):
    sock: socket.socket = None
    game_started = False
    # metadata: typing.Tuple[int, typing.List[str]]
    number_clients = 0
    clients_list: typing.List[str]

    def __init__(self, port, game_started, clients_list, number_clients=3):
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.port = port
        self.game_started = game_started
        self.clients_list = ['maurincomme', 'Zalgo']  # clients_list
        self.number_clients = number_clients
        super().__init__(daemon=True)

    def run(self) -> None:
        print("starting metadata server")
        self.sock.bind(('', self.port))
        while not self.game_started:
            request, client = self.sock.recvfrom(255)
            print(request, str(client))
            if request == b'can i haz metadata ?':
                self.sock.sendto(
                    metadata_to_bytes(
                        (self.number_clients, self.clients_list)
                    ), client)
            else: # le serveur de matchmaking demande si on attent toujours
                self.sock.sendto(b'im alive', client)


def bytes_to_metadata(binstr: bytes) -> typing.Tuple[int, typing.List[str]]:
    data = binstr.decode('utf-8').split(';,;')
    count = int(data[0])
    usernames = data[1:]
    return count, usernames


def get_metadata(host: typing.Tuple[str, int]) -> typing.Tuple[int, typing.List[str]]:
    mms: socket.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    mms.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mms.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    mms.sendto(b'can i haz metadata ?', host)
    mms.settimeout(5)
    res = mms.recv(1024)
    mms.close()
    return bytes_to_metadata(res)


if __name__ == '__main__':
    testmetadata = (2, ['Eric Maurincomme', 'ᛏᚺᛟᚱ ᛗᛃᛟᛚᚾᛇᚱ', "̘̰Z̭̙͈̺A̜̞̻͈̤͜L̞͇̙͍̜̦̠G͈̫̫͟O̲̰͡!̛̼̲̪̠̙̰̠"])
    assert bytes_to_metadata(metadata_to_bytes(testmetadata)) == testmetadata
