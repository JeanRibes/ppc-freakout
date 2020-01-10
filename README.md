# ppc-freakout

PPC project

c'est le serveur qui doit faire le timeout, pas le client

en fait on ne pose pas la carte SUR la précédente mais à côté
donc la stratégie n'est pas de bloquer l'autre (on ne peut pas), mais de réfléchir le plus vite possible

## design: 
* une seule Queue client -> serveur
* un moyen de broadcast serveur -> clients