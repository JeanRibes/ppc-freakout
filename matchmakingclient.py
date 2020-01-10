import socket, struct
from array import array
from kbhit import KBHit

from matchmaking import list_servers

if __name__ == '__main__':
    servers = list_servers()
    for s in servers:
        print("[ ] " + str(s))
    selected = len(servers) - 1
    kb = KBHit()

    def highlight(selected):
        n=len(servers)-selected
        print("\033[{}A\r[*]\033[{}B".format(str(n),str(n)),end='', flush=True)
    def revert(n):
        n = len(servers) - selected
        print("\033[{}A\r[ ]\033[{}B".format(str(n),str(n)),end='', flush=True)

    highlight(selected)
    while True:
        kc = kb.getarrow()
        revert(selected)
        print('\r  ', end='',flush=True)
        if kc == 0:
            selected = (selected - 1) % len(servers)
            #print("\033[1A\r *", end='',flush=True)
        elif kc == 2:
            selected = (selected + 1) % len(servers)
            #print("\033[1B\r *", end='',flush=True)
        highlight(selected)
        if kc == 1:
            break
    print(servers[selected])
