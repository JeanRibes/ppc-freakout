import random
import socket
import sys
from threading import Thread
import pygame

from data import *


def dessiner_carte(screen, couleur, chiffre, font, y, x):
    if couleur:
        rgb = (0, 0, 255)
    else:
        rgb = (255, 0, 0)
    card_rect = pygame.Rect(x, y, 40, 60)
    pygame.draw.rect(screen, rgb, card_rect)
    text = font.render(("R" if not couleur else "B") + str(chiffre), True, (255, 255, 255))
    textrect: pygame.rect.RectType = text.get_rect()
    textrect.centerx = card_rect.centerx
    textrect.centery = card_rect.centery
    screen.blit(text, textrect)


def dessiner_main(screen, x0, y0, cartes, font):
    x = x0
    y = y0
    for couleur, chiffre in cartes:
        dessiner_carte(screen, couleur, chiffre, font, y, x)
        x += 50


def highlight(screen, y, x, selected_highlight):
    border = 4
    pygame.draw.rect(screen, (252, 232, 3) if selected_highlight else (255, 255, 255),
                     pygame.Rect(x - border, y - border, 40 + 2 * border, 60 + 2 * border))


class NetworkReceiver(Thread):
    hand = []
    board: Board = Board()

    def __init__(self, conn):
        super().__init__(daemon=True)

    def run(self) -> None:
        while True:
            buf = conn.recv(2048)
            data: Message = ServerMessage.deserialize(buf)
            print(data)
            if data.type_message == TYPE_HAND_CHANGED:
                print(data.payload)
                self.hand = [x.to_tuple() for x in data.payload]
            elif data.type_message == TYPE_BOARD_CHANGED:
                self.board = data.payload
                print(self.board)


# board = [[(True, 4), (True, 4), (True, 4), (True, 4)],[(True, 5), (True, 5), (True, 5), (True, 5)],[(False, 5), (False, 5), (False, 5), ],[(False, 9), (False, 9), (False, 9), (False, 9), ],[(True, 1), (True, 1), (True, 1)],]


def dessiner_board(screen, x0, y0, board, font):
    x = x0
    y = y0
    for cartes in board.values():
        for carte in cartes:
            dessiner_carte(screen, carte.color, carte.value, font, x, y)
            x += 70
        y += 50
        x = x0


def move_selection(selected_index, i, hand):
    return (selected_index + i) % len(hand)


screen = pygame.display.set_mode((1500, 500))
x0 = 10
y0 = 10
selected_index = 0
hy = y0
selected_highlight = False

if __name__ == '__main__':

    conn = socket.socket()
    conn.connect(("127.0.0.1", 1996))
    conn.send(ClientMessage(type_message=TYPE_JOIN, payload="joueur sur gui" + str(random.random())).serialize())
    conn.send(ClientMessage(type_message=TYPE_READY).serialize())
    server_data = NetworkReceiver(conn)
    server_data.start()
    pygame.init()
    font = pygame.font.SysFont("Noto Sans", 20, 5)
    # font = pygame.font.SysFont(None, 20)
    done = False
    clock = pygame.time.Clock()  # intialisation du timer FPS

    try:
        assert sys.argv[1] == "-j"
        j = pygame.joystick.Joystick(0)
        j.init()
    except:
        pass
    # while len(server_data.hand)==0:
    # clock.tick(1)
    while not done:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("buzz")
                    selected_highlight = True
                elif event.key == pygame.K_LEFT:
                    selected_index = (selected_index - 1) % len(server_data.hand)
                elif event.key == pygame.K_RIGHT:
                    selected_index = (selected_index + 1) % len(server_data.hand)
                elif event.key == pygame.K_q:
                    sys.exit(0)
            elif event.type == pygame.JOYHATMOTION:
                selected_index = move_selection(selected_index, event.value[0], server_data.hand)
                selected_index = move_selection(selected_index, event.value[1], server_data.hand)
            elif event.type == pygame.JOYAXISMOTION:
                print("axis")
                print("j{} h{} v{}".format(event.joy, event.axis, event.value))
                selected_index = move_selection(selected_index, int(event.value), server_data.hand)
                break  # je voulais avoir moins d'auto-repeat mais en fait ça marche pas
                # selected_index = move_selection(selected_index, int(event.value)*int(abs(event.value)>0.5)*int(chance))
            elif event.type == pygame.JOYBUTTONDOWN:
                print("j{} b{}".format(event.joy, event.button))
                if event.button == 5:
                    selected_index = move_selection(selected_index, 1, server_data.hand)
                elif event.button == 4:
                    selected_index = move_selection(selected_index, -1, server_data.hand)
                elif event.button == 2 or event.button == 7:
                    if not selected_highlight:
                        print("séléctionné carte {} index {}".format(server_data.hand[selected_index], selected_index))
                        selected_highlight = True
                elif event.button == 8:  # select
                    sys.exit(0)
                elif event.button == 0:
                    server_data.hand[selected_index] = (
                    not server_data.hand[selected_index][0], server_data.hand[selected_index][1])
                elif event.button == 1:
                    server_data.hand[selected_index] = (
                    server_data.hand[selected_index][0], server_data.hand[selected_index][1] + 1)
                elif event.button == 3:
                    server_data.hand[selected_index] = (
                    server_data.hand[selected_index][0], server_data.hand[selected_index][1] - 1)
                if event.button == 9:
                    server_data.hand.append((True, 5))

        highlight(screen, hy, x0 + 50 * selected_index, selected_highlight)
        dessiner_main(screen, y0, x0, server_data.hand, font)
        dessiner_board(screen, y0 + 90, x0, server_data.board, font)

        if selected_highlight:  # une carte a été sélectionnée
            # list_cartes.pop(selected_index)
            conn.send(ClientMessage(type_message=TYPE_ACTION,
                                    payload=Card.from_tuple(server_data.hand[selected_index])
                                    ).serialize())  # on envoie notre action au serveur
            selected_highlight = False
            if selected_index > len(server_data.hand) - 1:
                selected_index -= 1
            continue

        pygame.display.update()
        pygame.display.flip()  # double-buffered
        clock.tick(30)  # on attent pour limiter les FPS à 30 (et pas 100000 et un jeu qui bouf 100% CPU)
        screen.fill((0, 100, 0))  # on reset pour la frame suivante

    print("fin ...")
