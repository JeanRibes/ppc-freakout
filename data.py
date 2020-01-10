#!/usr/bin/env python3
import pickle

# messages serveur -> client
TYPE_BOARD_CHANGED = 1  # le message contient Board
TYPE_HAND_CHANGED = 2  # le message contient Hand
TYPE_TIMEOUT = 3  # le message contient Hand
TYPE_INFO = 4  # le serveur broadcaste une information textuelle ("jean a rejoint la partie"
TYPE_GAME_END = 8 # le message est le nom du joueur qui a gagné
# messages client -> serveur
TYPE_JOIN = 5  # le joueur donne son nom d'utilisateur
TYPE_READY = 6  # le joueur signal qu'il est prêt
TYPE_ACTION = 7  # une carte est jouée, sans garantie d'exécution

BROADCAST_TYPES = (TYPE_HAND_CHANGED, TYPE_INFO, TYPE_GAME_END)
UNICAST_TYPES = (TYPE_HAND_CHANGED, TYPE_TIMEOUT, TYPE_JOIN, TYPE_READY, TYPE_ACTION)
STRING_TYPES = (TYPE_JOIN, TYPE_INFO, TYPE_GAME_END)

class SerializableMixin:
    def serialize(self) -> str:
        return pickle.dumps(self)

    @staticmethod
    def deserialize(string):
        return pickle.loads(string)


class Card:
    value: int = 0
    color: bool = True
    """
    Red : color=True
    Blue: color=False
    """

    def __init__(self, color: bool = None, value: int = None, string=None):
        if string is None:
            assert value > 0, "la valeur doit être plus grande que 0"
            self.color = color
            self.value = value
        else:
            assert len(string) >= 2, "Mauvais format de carte: trop court"
            assert string[0] in ('R', 'B'), "Mauvais format: (R|B)[0-9]+"
            self.color = string[0] == 'R'  # prog stylée ...
            self.value = int(string[1:])

    @property
    def blue(self) -> bool:
        return not self.color

    @property
    def red(self) -> bool:
        return self.color

    def __eq__(a, b) -> bool:
        # type (a:Card, b:Card) -> bool
        return a.color == b.color and a.value == b.value

    def __ne__(a, b):
        # type (a:Card, b:Card) -> bool
        return a.color != b.color or a.value != b.value

    def __str__(self):
        return ("R" if self.color else "B") + str(self.value)

    def __gt__(a, b):
        return a.value > b.value


class List(list):
    def __init__(self, *args, **kwargs):
        if len(args) + len(kwargs) == 1:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(args)  # pour initialiser des listes en donnant les

    #            éléments en arguments
    def __str__(self):
        return ",".join([str(c) for c in self])

    def put(self, x):
        return self.append(x)


class Hand(List):
    pass


class Board(List):
    pass


class GameState(SerializableMixin):
    hand: Hand = []
    board: Board = None
    infos: str

    def __init__(self, board, hand=None, infos=None):
        self.hand = hand
        self.board = board
        self.infos = infos

    def __str__(self):
        if self.infos is None:
            return str(self.board) + " : " + str(self.hand)
        else:
            return self.infos


class Pile(List):
    pass


class Action:
    type_action: int = -1
    card: Card = None
    TYPE_MOVE = 2
    infos: str

    def __init__(self, type_action, card=None, infos=None):
        assert type_action in [self.TYPE_MOVE], "Type invalide"
        self.type_action = type_action
        self.infos = infos
        self.card = card

    def __str__(self):
        if self.infos is not None:
            return self.infos
        else:
            return str(self.card)


class Message(SerializableMixin):
    type_message: int = -1
    payload = None

    def __init__(self, type_message, payload):
        assert type_message in (
            TYPE_BOARD_CHANGED,
            TYPE_HAND_CHANGED,
            TYPE_TIMEOUT,
            TYPE_JOIN,
            TYPE_READY,
            TYPE_GAME_END,
            TYPE_INFO,
            TYPE_ACTION), "Message non valide"
        if type_message == TYPE_BOARD_CHANGED:
            assert type(payload) == Board
        if type_message in (TYPE_TIMEOUT, TYPE_HAND_CHANGED):
            assert type(payload) == Hand
        if type_message in STRING_TYPES:
            assert type(payload) == str
        if type_message == TYPE_READY:
            assert payload is None
        if type_message == TYPE_ACTION:
            assert type(payload) == Card

        self.payload = payload
        self.type_message = type_message

    def __str__(self):
        return self.type_message  # TODO: faire un truc beau

    # def check(self):
    #    if self.type_message in (TYPE_BOARD_CHANGED, TYPE_HAND_CHANGED, TYPE_TIMEOUT, TYPE_JOIN, TYPE_READY):
    #        if self.type_message == TYPE_BOARD_CHANGED:
    #            assert type(self.payload) == Board
    #        if self.type_message in (TYPE_TIMEOUT, TYPE_HAND_CHANGED):
    #            assert type(self.payload) == Hand
    #        if self.type_message == TYPE_JOIN:
    #            assert type(self.payload) == str
    #        if self.type_message == TYPE_READY:
    #            assert self.payload is None


class ClientMessage(Message):  # TODO: vérifier que c'est la bonne instance de Message
    pass


class ServerMessage(Message):
    pass

class Client(object):
    """
    Objet géré par le serveur
    """
    socket=None
    username=None
    uid=-1
    hand:Hand
    def __init__(self,socket,username,uid):
        self.socket=socket
        self.uid=uid
        self.username=username

    def send(self, message:Message):
        self.socket.send(message.serialize())
    def update_hand(self):
        self.send(ServerMessage(type_message=TYPE_HAND_CHANGED, payload=self.hand))