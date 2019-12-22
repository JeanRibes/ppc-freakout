#!/usr/bin/python3
from data import *
from logic import *
from multiprocessing import Lock, Queue
from socket import socket
from threading import Thread
from data import *
class Networking(Thread):
    socket=None
    queue: Queue=None
    
    def __init__(self, socket, queue: Queue):
        self.queue = queue
        self.socket = socket
        super().__init__()
    
    def run(self):
        while True:
            dyn_buf = self.socket.recv(4096)
            action = Action.deserialize(dyn_buf)
            print(action)
            queue.put(action)





if __name__ == '__main__':
    print("starting server")
    pile: Pile = generate_pile(20)
    board: Card = pile.pop()

    boardL = Lock()
    pileL = Lock()
    listener = socket() # défaut: STREAM, IPv4
    listener.bind(("0.0.0.0", 1998))
    
    queue = Queue()
    while True:
        listener.listen(15)
        conn, address = listener.accept()
        hand = Hand()
        for _ in range(5):
            hand.put(pile.pop())
        conn.send(GameState(hand, board).serialize())
        Networking(conn, queue).start()

