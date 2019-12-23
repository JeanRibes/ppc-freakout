#!/usr/bin/env python3
from threading import Thread
from socket import socket
import sys
from data import *
from logic import validate_move
import time
class AutomaticPlayer(Thread):
    conn: socket
    def __init__(self, socket):
        self.conn = socket
        super().__init__()
    def run(self):
        last_info=None
        while last_info is None:
            data = self.conn.recv(4096)
            if len(data)>1: 
                state = GameState.deserialize(data)
                last_info = state.infos
                print("game state: "+str(state))
                to_play=Action(Action.TYPE_TIMEOUT, None)
                for card in state.hand:
                    if validate_move(card, state.board):
                        to_play = Action(type_action=Action.TYPE_MOVE, card=card)
                        break
                if to_play.type_action == Action.TYPE_TIMEOUT:
                    print("will play: timeout")
                else:
                    print("will play: {}".format(to_play.card))
                self.conn.send(to_play.serialize())
            time.sleep(0.01)


if __name__ == '__main__':
    print("Starting client")
    conn = socket()
    conn.connect(("0.0.0.0", 1993))
    AutomaticPlayer(conn).start()
