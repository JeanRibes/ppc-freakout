#!/usr/bin/env python3
from random import random
from threading import Thread
from socket import socket
import sys

import typing

from data import *
from logic import validate_move
import time


class IdiotieAutomatique(Thread):
    conn: socket
    hand: typing.List[Card] = None
    board: Board = None
    game_started = False

    def __init__(self, socket):
        self.conn = socket
        super().__init__()

    def run(self):
        last_info = None
        while last_info is None:
            data = self.conn.recv(4096)
            if len(data) > 1:
                msg: ServerMessage = ServerMessage.deserialize(data)
                if msg.type_message in HAND_TYPES:
                    self.hand = msg.payload
                if msg.type_message is TYPE_BOARD_CHANGED:
                    self.board = msg.payload
                    self.game_started = True
                if msg.type_message in STRING_TYPES:
                    print(msg.payload)
                if self.game_started:
                    self.play()

    def send(self, card: Card):
        print("{} -> ".format(str(card)))
        self.conn.send(ClientMessage(type_message=TYPE_ACTION, payload=card).serialize())

    def play(self):
        """
        Essaie de jouer une carte de la main
        :return:
        """
        for board_card in self.board:
            for hand_card in self.hand:
                if hand_card // board_card:
                    self.send(hand_card)
                    return


if __name__ == '__main__':
    print("Starting client")
    conn = socket()
    conn.connect(("0.0.0.0", 1993))
    conn.send(ClientMessage(type_message=TYPE_JOIN,
                            payload="IdiotieAutomatique-{}".format(str(int(random() * 100)))).serialize())
    time.sleep(5)
    conn.send(ClientMessage(type_message=TYPE_READY).serialize())
    IdiotieAutomatique(conn).start()
