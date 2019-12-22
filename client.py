#!/usr/bin/env python3
from threading import Thread
from socket import socket
import sys
from data import *

class Display(Thread):
    conn: socket
    hand: Hand
    board: Card
    def __init__(self, socket):
        self.conn = socket
        super().__init__()
    def run(self):
        while True:
            data = self.conn.recv(4096)
            if len(data)>1: 
                state = GameState.deserialize(data)
                self.board=state.board
                self.hand=state.hand
                print(state)
                print(":>")

class Input(Thread):
    conn: socket
    def __init__(self, socket):
        self.conn = socket
        super().__init__()
    def run(self):
        while True:
            choice = input()
            action = Action(type_action=Action.TYPE_MOVE,
                            card=Card(string=choice))
#            self.conn.send(bytes(choice, "ascii")) # pas besoin d'UTF-8
            self.conn.send(action.serialize()) # pas besoin d'UTF-8

if __name__ == '__main__':
    print("Starting client")
    conn = socket()
    conn.connect(("0.0.0.0", 1998))
    Input(conn).start()
    Display(conn).start()
