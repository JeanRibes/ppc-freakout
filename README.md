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

# Matchmaking
## Serveur maître
Il y a un serveur de coordination, le serveur maître.
Les serveurs de jeu s'y connectent et se déclarent ouverts puis fermés (quand la partie a commencé).
Le serveur maître interroge régulièrement les serveurs de jeu qui se sont présentés à lui pour voir s'ils sont toujours
en ligne.
## Clients
Les clients demandent au serveur maître la liste des serveurs de jeu, et ils tentent de se connecter à chaque serveur
pour récupérer des informations additionnelles comme le nombre de joueurs connectés et leurs pseudonymes.
## Communications
Toutes les communications de matchmaking sont en UDP, sur le même port que les communications TCP.
Cela permet au serveur maître de déduire l'adresse de jeu car c'est la même que celle utilisée pour l'annonce.

## Messages


 