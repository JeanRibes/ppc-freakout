#!/usr/bin/env python3

from data import *
from random import random
from copy import deepcopy


def generate_pile_random(N=20, max_value=9):
    pile = Pile()
    for _ in range(N):
        value = int(random() * max_value) + 1
        color = random() > 0.5
        pile.append(Card(color, value))
    return pile


def generate_pile_fixed(max_value):
    pile = [Card(True, i) for i in range(1, max_value + 1)]
    pile.extend(
        [Card(False, i) for i in range(1, max_value + 1)]
    )
    return pile


def generate_pile(N, max_value):
    #return generate_pile_fixed(max_value)
    pile = generate_pile_random(N, max_value)
    pile.extend(
        generate_pile_fixed(max_value))  # toutes les cartes possibles plus un nombre de cartes alatoires
    return pile


def shuffle(pile):
    indexes = []
    inp = deepcopy(pile)
    for i, _ in enumerate(inp):
        indexes.append(i)
    out = []
    while len(inp) > 0:
        out.append(inp.pop(indexes[int(random() * len(inp))]))
    return out


def validate_move(card: Card, board: Card) -> bool:
    return (card.color != board.color and card.value == board.value) or \
           (card.color == board.color and abs(board.value - card.value) == 1)  # norme=1


def broadcast(queues, item):
    for q in queues:
        q.put(item, block=False)


def flush(queue):
    """
    merci StackOverflow
    :param queue:
    :return:
    """
    queue._wlock.acquire()
    while not queue.empty():
        queue.get()
    queue._wlock.release()


if __name__ == '__main__':
    cartes = generate_pile(5, 8)
    print(List(cartes))
    shuffled = List(shuffle(cartes))
    print(shuffled)
    for i in cartes:
        if i not in shuffled:
            print('erreur')