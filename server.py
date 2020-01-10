#!/usr/bin/python3
import time
import typing

from data import *
from logic import *
from threading import Lock, Thread
from multiprocessing import Queue
from socket import socket, SOL_SOCKET, SO_REUSEADDR, SO_REUSEPORT
from data import *


class NetworkingReceiver(Thread):
    """
    Se charge de récupérer les actions des clients et de les mettre dans une seule Queue
    """
    socket = None
    queue: Queue = None
    clients_map = None
    uid = random() * 65553
    client = None  # le client géré par ce Thread

    def __init__(self, socket, queue: Queue, clients: dict):
        self.queue = queue
        self.socket = socket
        self.clients_map = clients
        super().__init__()

    def run(self):
        while True:
            dyn_buf = self.socket.recv(4096)
            msg: ClientMessage = ClientMessage.deserialize(dyn_buf)
            print("action from {}: ".format(self.socket.getpeername()) + str(msg))
            if msg.type_message == TYPE_JOIN:
                assert self.client == None, "client called JOIN twice !"
                self.client = Client(username=msg.payload, uid=self.uid, socket=self.socket)
                self.clients_map[self.uid] = client
            self.queue.put((msg, self.uid))


class NetworkBroadcaster(Thread):
    """
    Se charge d'envoyer à tous les clients les modifications du plateau
    """
    queue: Queue = Queue()
    client_sockets: typing.List[socket] = None

    def __init__(self, chaussettes):
        self.sockets = chaussettes
        super().__init__(daemon=True)

    def run(self) -> None:
        while True:
            to_broadcast = self.queue.get(block=True)
            assert type(
                to_broadcast) == ServerMessage and to_broadcast.type_message in BROADCAST_TYPES, "mauvais type de message broadcast"
            for socket in self.sockets:
                socket.send(to_broadcast)
                # sock.setblocking(False) à voir si ça permet de faire recv() en bloquant


class ClientTimeout(Thread):
    client_socket: socket
    needs_penalty: bool = False

    def run(self) -> None:
        while True:
            self.needs_penalty = True
            time.sleep(15)
            if self.needs_penalty:
                self.client_socket.send(Action(type_action=Action.TYPE_TIMEOUT))


class BoardLogicProcessing(Thread):
    queue: Queue
    socket: socket = None
    hand: Hand = None
    boardL: Lock
    board: Card
    pileL: Lock
    pile: List

    def __init__(self, conn, queue, hand, board, boardL, pile, pileL):
        self.socket = conn
        self.queue = queue
        self.hand = hand
        self.board = board
        self.boardL = boardL
        self.pile = pile
        self.pileL = pileL
        super().__init__()

    def run(self):
        infos = None
        while len(self.pile) > 0:
            action = self.queue.get()
            print("queued" + str(action))
            infos = None
            if len(self.hand) == 0:
                infos = "you won"
            else:
                if action.type_action == Action.TYPE_TIMEOUT:
                    self.pileL.acquire()
                    self.hand.put(self.pile.pop())
                    self.pileL.release()
                elif action.type_action == Action.TYPE_MOVE:
                    #                print(abs(action.card.value-self.board.value))
                    if action.card in self.hand:
                        self.boardL.acquire()
                        if validate_move(action.card, self.board):
                            self.hand.remove(action.card)
                            self.board = action.card
                            self.boardL.release()
                        else:
                            self.boardL.release()
                            self.pileL.acquire()
                            self.hand.put(self.pile.pop())  # penalty
                            self.pileL.release()
            self.socket.send(GameState(self.hand, self.board, infos).serialize())
            flush(self.queue)
        self.socket.send(GameState(self.hand, self.board, "game ended").serialize())
        self.queue.close()


class Lobby(Thread):
    receive_queue: Queue
    broadcast_queue: Queue
    game_started = False
    clients_ready = 0
    number_clients = None

    def __init__(self, rcv_q, brd_queue, n):
        self.receive_queue = rcv_q
        self.broadcast_queue = brd_queue
        self.number_clients = n
        super().__init__(daemon=True)

    def run(self) -> None:
        while not self.game_started:
            message: ClientMessage = self.receive_queue.get()
            if message.type_message == TYPE_JOIN:
                s = "{} a rejoint la partie !".format(message.payload)
                self.broadcast_queue.put(ServerMessage(type_message=TYPE_INFO, payload=s))
                print(s)
            elif message.type_message == TYPE_READY:
                self.clients_ready += 1
                if self.clients_ready == self.number_clients and self.clients_ready >= 2:
                    self.game_started = True


if __name__ == '__main__':
    print("starting server")

    listener = socket()  # défaut: STREAM, IPv4
    listener.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    listener.bind(("0.0.0.0", 1993))

    client_sockets = []  # pour broadcast
    nb = NetworkBroadcaster(client_sockets)
    broadcast_queue = nb.queue
    receive_queue = Queue()
    number_clients = 0
    clients_map: typing.Dict[int, Client] = {}  # contient une map des clients avec leur uid et leur socket & username
    lobby = Lobby(rcv_q=receive_queue, brd_queue=broadcast_queue, n=number_clients)
    lobby.start()
    game_started = lobby.game_started

    print("started lobby, awaiting clients")
    while not game_started:
        listener.listen(15)
        conn, address = listener.accept()
        client_sockets.append(conn)
        NetworkingReceiver(conn, receive_queue, clients=clients_map).start()
        number_clients += 1
    del lobby
    print("game starting")
    # ici, le jeu se lance
    cards_needed = number_clients * (5) + 5

    pile: Pile = Pile(
        shuffle(
            generate_pile(cards_needed, 10)
        )
    )
    board: Board = Board([pile.pop()])

    boardL = Lock()
    pileL = Lock()

    # distribution des cartes
    for _, client in clients_map:
        if len(pile) > 5:
            hand = Hand()
            pileL.acquire()
            for _ in range(5):
                hand.put(pile.pop())
            pileL.release()
            client.hand = hand

    # jeu
    while len(pile) > 0:
        # réception du message
        message, uid = receive_queue.get()
        flush(receive_queue)

        client = clients_map[uid]
        card = message.payload

        assert message.type_message == TYPE_ACTION, "mauvais type d'action"
        assert type(card) == Card
        # traitement
        if card in client.hand:
            if True:  # validate_move(card, board):
                client.hand.remove(card)
        client.update_hand()
    # le jeu est maintenant fini

    won_client: Client = None
    for _, client in clients_map:
        if len(client.hand) == 0 and won_client is None:
            won_client = client
            print(won_client.username+" a gagné !!")
        elif won_client is not None:
            print("erreur de logique: plusieurs client avaient des mains vides à la fin de la partie")
    broadcast_queue.put(ServerMessage(type_message=TYPE_GAME_END, payload=won_client.username))
