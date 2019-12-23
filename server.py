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
            print("action from {}: ".format(self.socket.getpeername()) + str(action))
            queue.put(action)

class BoardLogicProcessing(Thread):
    queue: Queue
    socket: socket=None
    hand: Hand=None
    boardL: Lock
    board: Card
    pileL: Lock
    pile: List

    def __init__(self, conn, queue, hand, board, boardL, pile, pileL):
        self.socket = conn
        self.queue = queue
        self.hand = hand
        self.board = board
        self.boardL = boardL
        self.pile = pile
        self.pileL = pileL
        super().__init__()
    def run(self):
        infos=None
        while len(self.pile)>0:
            action = self.queue.get()
            print("queued"+str(action))
            infos=None
            if len(self.hand)==0:
                infos="you won"
            else:
                if action.type_action == Action.TYPE_TIMEOUT:
                    self.pileL.acquire()
                    self.hand.put(self.pile.pop())
                    self.pileL.release()
                elif action.type_action == Action.TYPE_MOVE:
    #                print(abs(action.card.value-self.board.value))
                    if action.card in self.hand:
                        self.boardL.acquire()
                        if validate_move(action.card, self.board):
                            self.hand.remove(action.card)
                            self.board = action.card
                            self.boardL.release()
                        else:
                            self.boardL.release()
                            self.pileL.acquire()
                            self.hand.put(self.pile.pop()) #penalty
                            self.pileL.release()
            self.socket.send(GameState(self.hand,self.board, infos).serialize())
            flush(self.queue)
        self.socket.send(GameState(self.hand,self.board, "game ended").serialize())
        self.queue.close()


if __name__ == '__main__':
    print("starting server")
    pile: Pile = Pile(shuffle(4*generate_pile(20, 3)))
    board: Card = pile.pop()

    boardL = Lock()
    pileL = Lock()
    listener = socket() # défaut: STREAM, IPv4
    listener.bind(("0.0.0.0", 1993))
    
    queues=[] #pour broadcast

    while len(pile)>5:
        listener.listen(15)
        conn, address = listener.accept()
        if len(pile)>5:
            hand = Hand()
            pileL.acquire()
            for _ in range(5):
                hand.put(pile.pop())
            pileL.release()
            conn.send(GameState(hand, board).serialize())
            queue = Queue()
            queues.append(queue)
            Networking(conn, queue).start()
            BoardLogicProcessing(conn, queue, hand, board, boardL, pile,
                             pileL).start()
