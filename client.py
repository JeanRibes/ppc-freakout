#!/usr/bin/env python3
import sys
import time
from threading import Thread

from data import *
from matchmaking import find_server
import socket

class NetworkReceiver(Thread):
    hand = []
    board: Board = Board()
    message = None
    game_finished = False
    game_ready=False

    def __init__(self, conn: socket.socket):
        self.conn = conn
        super().__init__()

    def run(self) -> None:
        while not self.game_finished:
            buf = self.conn.recv(2048)
            data: ServerMessage = ServerMessage.deserialize(buf)
            self.message = data.infos
            #print(data, file=sys.stderr)  # affiche le type de message reçu
            if data.type_message in [TYPE_TIMEOUT, TYPE_HAND_CHANGED]:
                self.hand = data.payload
                print(self.hand)
            elif data.type_message == TYPE_BOARD_CHANGED:
                self.board = data.payload
                self.print_board()
                self.game_ready = True
            elif data.type_message in STRING_TYPES:
                print(self.message)
                print("--->" + data.payload)
            if data.type_message == TYPE_GAME_END:
                print("**************************= JEU FINI =*******************************")
                self.game_finished = True
                print(data.payload)
    def send(self, message:ClientMessage):
        self.conn.send(message.serialize())
    def print_board(server_data):
        print(", ".join([str(card) for card in server_data.board.keys() if len(server_data.board[card]) > 0]))

if __name__ == '__main__':
    conn = socket.socket()
    conn.connect(find_server())
    server_data = NetworkReceiver(conn=conn)
    server_data.start()

    server_data.send(ClientMessage(type_message=TYPE_JOIN, payload=input('votre pseudo: ')))
    input('Appuyez sur ENTER pour démarrer la partie')
    server_data.send(ClientMessage(type_message=TYPE_READY, payload=None))
    while not server_data.game_ready:
        time.sleep(2)

    while not server_data.game_finished:
        index_c = input()
        server_data.send(ClientMessage(type_message=TYPE_ACTION, payload=server_data.hand[int(index_c)]))
