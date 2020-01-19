#!/usr/bin/python3
import time
import typing
from queue import Queue

from data import *
from logic import *
from threading import Lock, Thread
from socket import socket, SOL_SOCKET, SO_REUSEADDR, SO_REUSEPORT, IPPROTO_UDP, AF_INET, SOCK_DGRAM, timeout
from data import *
from matchmaking import BroadcastGame


class NetworkingReceiver(Thread):
    """
    Se charge de récupérer les actions des clients et de les mettre dans une seule Queue
    """
    socket = None
    queue: Queue = None
    clients_map = None
    uid = None
    client = None  # le client géré par ce Thread

    running = True

    def __init__(self, socket, queue: Queue, clients: dict):
        self.uid = random() * 65553  # et pas dans les attributs sinon c'est toujour le même
        print("new NetworkReceiver: " + str(self.uid))
        self.queue = queue
        self.socket = socket
        self.clients_map = clients
        super().__init__()

    def run(self):
        while self.running:
            dyn_buf = self.socket.recv(4096)
            if len(dyn_buf) <= 0:
                self.running = False
                continue
            # print(dyn_buf)
            msg: ClientMessage = ClientMessage.deserialize(dyn_buf)
            print("action from {}: ".format(self.socket.getpeername()) + str(msg))
            self.queue.put((msg, self.uid))
            if msg.type_message == TYPE_JOIN:
                assert self.client == None, "client called JOIN twice !"
                print(msg.payload + " a rejoint la partie")
                self.client = Client(username=msg.payload, uid=self.uid, socket=self.socket)
                self.clients_map[self.uid] = self.client
            # self.queue.put((msg, self.uid))


class NetworkBroadcaster(Thread):
    """
    Se charge d'envoyer à tous les clients les modifications du plateau
    """
    queue: Queue = Queue()
    client_sockets: typing.List[socket] = []

    def __init__(self):
        super().__init__(daemon=True)

    def run(self) -> None:
        while True:
            to_broadcast: ServerMessage = self.queue.get(block=True)
            assert type(
                to_broadcast) == ServerMessage and to_broadcast.type_message in BROADCAST_TYPES, "mauvais type de message broadcast"
            for socket in self.client_sockets:
                socket.send(to_broadcast.serialize())
                # sock.setblocking(False) à voir si ça permet de faire recv() en bloquant


class ClientTimeout(Thread):
    client: Client
    needs_penalty: bool = None
    pile: Pile = None
    pileL: Lock = None

    def __init__(self, client, pile: Pile, pileL: Lock, *args, **kwargs):
        self.client = client
        self.needs_penalty = False
        self.pile = pile
        self.pileL = pileL
        super().__init__(daemon=True)

    def run(self) -> None:
        while len(pile) > 0:
            self.needs_penalty = True
            time.sleep(30)

            self.pileL.acquire()
            if self.needs_penalty and len(self.pile)>0:
                print("applying penalty to " + self.client.username)
                self.client.hand.put(
                    self.pile.pop()
                )
                self.client.send(ServerMessage(
                    type_message=TYPE_TIMEOUT,
                    payload=self.client.hand,
                    infos="Vous avez mis trop longtemps à vous décider"
                ))
                # self.client.update_hand(t_m=TYPE_TIMEOUT)
            self.pileL.release()

class Lobby(Thread):
    receive_queue: Queue
    broadcast_queue: Queue
    game_started = False
    clients_ready = None
    number_clients = None

    def __init__(self, rcv_q, brd_queue, n):
        self.receive_queue = rcv_q
        self.broadcast_queue = brd_queue
        self.number_clients = n
        self.clients_ready = 0
        super().__init__(daemon=True)

    def run(self) -> None:
        while not self.game_started:
            message, uid = self.receive_queue.get()
            print("lobby got "+str(message))
            if message.type_message == TYPE_JOIN:
                s = "{} a rejoint la partie !".format(message.payload)
                self.broadcast_queue.put(ServerMessage(type_message=TYPE_INFO, payload=s))
                print(s)
            elif message.type_message == TYPE_READY:
                print("1 ready")
                self.clients_ready += 1
                # if self.clients_ready == self.number_clients and self.clients_ready >= 1:
                #    self.game_started = True


if __name__ == '__main__':
    print("starting server", end='', flush=True)

    listener = socket()  # défaut: STREAM, IPv4
    # listener.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    # listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    port = 2000 + int(random()*5)
    print("on port " + str(port))
    listener.bind(("0.0.0.0", port))

    game_announcer = BroadcastGame(listener.getsockname())
    game_announcer.start()

    broadcaster = NetworkBroadcaster()
    broadcaster.start()
    broadcast_queue = broadcaster.queue
    receive_queue = Queue()
    number_clients = 0
    clients_map: typing.Dict[int, Client] = {}  # contient une map des clients avec leur uid et leur socket & username
    lobby = Lobby(rcv_q=receive_queue, brd_queue=broadcast_queue, n=number_clients)
    lobby.start()

    print("started lobby, awaiting clients")
    clients_list = []
    listener.settimeout(1)
    listener.listen(15)
    while number_clients < 1 or number_clients > lobby.clients_ready:
        print("{}/{} clients ready".format(lobby.clients_ready, number_clients))
        try:
            conn, address = listener.accept()
            broadcaster.client_sockets.append(
                conn)  # TODO: utiliser un Lock ici pour ne pas faire de problèmes entre Threads
            NetworkingReceiver(conn, receive_queue, clients=clients_map).start()
            number_clients += 1
        except timeout:
            continue
    print("game initializing")
    listener.settimeout(None)

    # ici, le jeu se crée , tout le monde a utilisé TYPE_READY
    game_announcer.run=False # on arrête le broadcast UDP

    cards_needed = number_clients * (5) + 5

    pile: Pile = Pile(
        shuffle(
            generate_pile(cards_needed, 10)
        )
    )

    board: Board = Board()
    first_card = pile.pop()
    board.put(first_card)

    boardL = Lock()
    pileL = Lock()

    # distribution des cartes
    print(clients_map)
    for _, client in clients_map.items():
        if len(pile) > 5:
            hand = Hand()
            pileL.acquire()
            for _ in range(5):
                hand.put(pile.pop())
            pileL.release()
            client.hand = hand
            client.update_hand()
            print(client.hand)

    # démarrage du jeu
    print("game starting")
    lobby.game_started=True
    broadcast_queue.put(ServerMessage(type_message=TYPE_BOARD_CHANGED, payload=board))
    for client in clients_map.values():
        tt = ClientTimeout(client, pile, pileL)
        tt.start()
        client.timeoutThread = tt

    # jeu
    while len(pile) > 0: #TODO: calculer le nombre de cartes restantes dans tout le jeu
        # réception du message
        data = receive_queue.get(block=True)
        message, uid = data
        print("processing message " + str(message))
        #flush(receive_queue)
        client = clients_map[uid]

        if message.type_message == TYPE_TIMEOUT:
            client.hand.put(pile.pop())
            client.update_hand(infos=str(len(pile)))
            continue

        assert message.type_message == TYPE_ACTION, "mauvais type d'action"
        assert type(message.payload) == Card
        card = message.payload
        # traitement
        boardL.acquire()
        if card in client.hand and is_valid(board, card):  # True = validate_move
            client.timeoutThread.needs_penalty = False
            client.hand.remove(card)
            board.put(card)  # TODO: utiliser boardL
            client.update_hand()
            broadcast_queue.put(ServerMessage(type_message=TYPE_BOARD_CHANGED, payload=board, infos="{} cartes restantes".format(len(pile))))
        else:
            pileL.acquire()  # nécessaire car Pile peut être modifiée par les ClientTimeout(Thread)
            client.hand.put(pile.pop())
            client.send(ServerMessage(type_message=TYPE_HAND_CHANGED, payload=client.hand,
                                      infos="Carte invalide, reste {}".format(len(pile))))  # on pénalise le joueur
            pileL.release()
        boardL.release()
    # le jeu est maintenant fini

    won_client: Client = None
    for client in clients_map.values():
        if len(client.hand) == 0 and won_client is None:
            won_client = client
            print(won_client.username + " a gagné !!")
        elif won_client is not None:
            print("erreur de logique: plusieurs client avaient des mains vides à la fin de la partie")
    if won_client is not None:
        broadcast_queue.put(ServerMessage(type_message=TYPE_GAME_END, payload="Vous avez gagné! "+won_client.username))
    else:
        broadcast_queue.put(ServerMessage(type_message=TYPE_GAME_END, payload="Tout le monde a perdu"))
