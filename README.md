# ppc-freakout

PPC project

c'est le serveur qui doit faire le timeout, pas le client

en fait on ne pose pas la carte SUR la précédente mais à côté
donc la stratégie n'est pas de bloquer l'autre (on ne peut pas), mais de réfléchir le plus vite possible

## design: 
* une seule Queue client -> serveur
* un moyen de broadcast serveur -> clients

# idées prof
* utiliser le multiprocessing manager (multiprocessing en réseau, serveur RPC)
* il y a un threadtimer qui existe pour remplacer mon
* vérifier que les objets partagés n'ont pas de problmes de synchro;
faire les locks au cas où
* utiliser ``struct`` au lieu de ``pickle``

* pour faire de la concurrence ultime, il faudrait que certaines cartes empêchent
l'adversaire de placer certaines cartes
# implem prof
il a un mode où le joueur prend la main avec un buzzer et il a 3s pour jouer

# idées
* si on a deux exemplaires de cartes, ces deux sont enlevées