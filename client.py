#!/usr/bin/env python3
from threading import Thread
from socket import socket
import sys
from data import *

class Display(Thread):
    conn: socket
    state: GameState = None
    def __init__(self, socket):
        self.conn = socket
        super().__init__()
    def run(self):
        while True:
            data = self.conn.recv(4096)
            if len(data)>1: 
                state = GameState.deserialize(data)
                self.state=state
                print("game state: "+str(state))
                print("\n:>", end=" ")

class Input(Thread):
    conn: socket
    def __init__(self, socket):
        self.conn = socket
        super().__init__()
    def run(self):
        while True:
            choice = input()
            try:
                action = Action(type_action=Action.TYPE_MOVE,
                            card=Card(string=choice))
                self.conn.send(action.serialize()) # pas besoin d'UTF-8
            except AssertionError as e:
                print("Erreur: "+e.args[0])
                continue

if __name__ == '__main__':
    print("Starting client")
    conn = socket()
    conn.connect(("0.0.0.0", 1994))
    Input(conn).start()
    Display(conn).start()
