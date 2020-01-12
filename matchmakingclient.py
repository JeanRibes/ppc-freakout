import socket, struct
import sys

from array import array

from data import ClientMessage, TYPE_JOIN
from kbhit import KBHit

from matchmaking import list_servers, get_metadata


def server_chooser():
    print("Connexion au serveur maître...")
    servers = list_servers()

    if len(servers) == 0:
        return None

    print("Liste des serveurs :")
    for s in servers:
        print("[ ] " + str(s), end=" ", flush=True)
        try:
            metadata = get_metadata(s)
            print("{} connectés: {}".format(metadata[0], ", ".join(metadata[1])))
        except socket.timeout:
            print("Serveur injoignable")

    print("Faites votre choix avec les flèches haut-bas, validez avec droite")
    selected = 0
    kb = KBHit()

    def highlight(selected):
        n = 1 + len(servers) - selected
        print("\033[{}A\r[*]\033[{}B\r".format(str(n), str(n)), end='', flush=True)

    def revert(n):
        n = 1 + len(servers) - selected
        print("\033[{}A\r[ ]\033[{}B\r".format(str(n), str(n)), end='', flush=True)

    highlight(selected)
    while True:
        kc = kb.getarrow()
        revert(selected)
        # print('\r  ', end='',flush=True)
        if kc == 0:
            selected = (selected - 1) % len(servers)
        elif kc == 2:
            selected = (selected + 1) % len(servers)
        highlight(selected)
        if kc in [1, None]:
            break
    kb.set_normal_term()
    print("vous avez choisi ", end="")
    return servers[selected]


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        port = sys.argv[2]
        host = (ip, int(port))
    else:
        host = server_chooser()
        print()
        if host is None:
            host=(input('ip: '),int(input('port: ')))
    username=input("Choisissez un nom d'utilisateur: ")

    gamesock = socket.socket()
    gamesock.connect(host)

    gamesock.send(ClientMessage(type_message=TYPE_JOIN, payload=username).serialize())
