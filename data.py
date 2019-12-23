#!/usr/bin/env python3
import pickle

class Card:
    value: int=0
    color: bool=True
    """
    Red : color=True
    Blue: color=False
    """

    def __init__(self, color:bool=None, value:int=None, string=None):
        if string is None:
            assert value > 0, "la valeur doit être plus grande que 0"
            self.color=color
            self.value=value
        else:
            assert len(string)>=2, "Mauvais format de carte: trop court"
            assert string[0] in ('R', 'B'), "Mauvais format: (R|B)[0-9]+"
            self.color = string[0] == 'R' #prog stylée ...
            self.value=int(string[1:])

    @property
    def blue(self)->bool:
        return not self.color
    @property
    def red()->bool:
        return self.color
    def __eq__(a, b)->bool:
        # type (a:Card, b:Card) -> bool
        return a.color == b.color and a.value == b.value
    def __ne__(a,b):
        # type (a:Card, b:Card) -> bool
        return a.color != b.color or a.value != b.value
    def __str__(self):
        return ("R" if self.color else "B")+str(self.value)
    def __gt__(a, b):
        return a.value > b.value

class List(list):
    def __init__(self, *args, **kwargs):
        if len(args)+len(kwargs)==1:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(args) # pour initialiser des listes en donnant les
#            éléments en arguments
    def __str__(self):
        return ",".join([str(c) for c in self])
    def put(self, x):
        return self.append(x)
class Hand(List):
    pass
class GameState:
    hand: Hand = []
    board: Card = None
    infos: str
    def __init__(self, hand, board, infos=None):
        self.hand=hand
        self.board=board
        self.infos=infos
    def __str__(self):
        if self.infos is None:
            return str(self.board)+" : "+str(self.hand)
        else: return self.infos
    def serialize(self)->str:
        return pickle.dumps(self)
    @staticmethod
    def deserialize(string):
        return pickle.loads(string)

class Pile(List):
    pass

class Action:
    type_action: int=-1
    card: Card=None
    TYPE_TIMEOUT=1
    TYPE_MOVE=2
    infos: str
    def __init__(self, type_action, card=None, infos=None):
        assert type_action in [self.TYPE_TIMEOUT, self.TYPE_MOVE], "Type invalide"
        self.type_action = type_action
        self.infos=infos
        self.card=card
    def serialize(self)->str:
        return pickle.dumps(self)
    @staticmethod
    def deserialize(string):
        return pickle.loads(string)
    def __str__(self):
        if self.type_action == self.TYPE_TIMEOUT:
            return "timeout"
        elif self.infos is not None:
            return self.infos
        else:
            return str(self.card)

if __name__ == '__main__':
    card1 = Card(string="B12")
    card2 = Card(color=True, value=13)
    card3 = Card(string=str(card1))
    print(card1)
    print(card2)
    h = Hand(card1, card2, card3)
    print(h)
    print(GameState(h, card3))
