#!/usr/bin/env python3

from data import *
from random import random
from copy import deepcopy
def generate_pile(N= 20, max_value=9):
    pile = Pile()
    for _ in range(N):
        value = int(random()*max_value) + 1
        color = random() > 0.5
        pile.append(Card(color, value))
    return pile
def shuffle(pile):
    indexes = []
    inp = deepcopy(pile)
    for i, _ in enumerate(inp):
        indexes.append(i)
    out = []
    while len(inp)>0:
        out.append(inp.pop(indexes[int(random()*len(inp))]))
    return out

if __name__ == '__main__':
    cartes = generate_pile(5)
    print(List(cartes))
    shuffled = List(shuffle(cartes))
    print(shuffled)
    for i in cartes:
        if i not in shuffled:
            print('erreur')
