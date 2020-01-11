import socket, struct
from array import array
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
    print("vous avez choisi ", end="")
    return servers[selected]


if __name__ == '__main__':
    print(server_chooser())
