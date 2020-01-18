import random
import socket
import sys
from threading import Thread
import pygame

from data import *
from matchmaking import find_server


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


def afficher_message(screen, message, font):
    if message is not None:
        texte = font.render(message, True, (255, 255, 255))
        texte_rect = texte.get_rect()
        texte_rect.centerx = screen.get_width() // 2
        texte_rect.centery = screen.get_height() // 2
        screen.blit(texte, texte_rect)


def highlight(screen, y, x, selected_highlight):
    border = 4
    pygame.draw.rect(screen, (252, 232, 3) if selected_highlight else (255, 255, 255),
                     pygame.Rect(x - border, y - border, 40 + 2 * border, 60 + 2 * border))


class NetworkReceiver(Thread):
    hand = []
    board: Board = Board()
    message = None
    game_finished = False

    def __init__(self, conn):
        self.conn = conn
        super().__init__(daemon=True)

    def run(self) -> None:
        while True:
            buf = self.conn.recv(2048)
            data: ServerMessage = ServerMessage.deserialize(buf)
            self.message = data.infos
            print(data)  # affiche le type de message reçu
            if data.type_message in [TYPE_TIMEOUT, TYPE_HAND_CHANGED]:
                self.hand = [x.to_tuple() for x in data.payload]
            elif data.type_message == TYPE_BOARD_CHANGED:
                self.board = data.payload
            elif data.type_message in STRING_TYPES:
                self.message = data.payload
                print("--->" + data.payload)
            if data.type_message == TYPE_GAME_END:
                self.game_finished = True
                print("**************************= JEU FINI =*******************************")


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
    if len(hand) > 0:
        return (selected_index + i) % len(hand)
    else:
        return -1


screen = pygame.display.set_mode((1500, 500))
x0 = 10
y0 = 10
selected_index = 0
hy = y0
selected_highlight = False

if __name__ == '__main__':

    conn = socket.socket()
    conn.connect(find_server())
    server_data = NetworkReceiver(conn)
    username = "joueur sur gui" + str(random.random())
    server_data.message = username
    conn.send(ClientMessage(type_message=TYPE_JOIN, payload=username).serialize())
    server_data.start()
    pygame.init()
    pygame.display.set_caption(username)
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

        if selected_index >= len(server_data.hand) and selected_index > 0:
            selected_index -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    selected_highlight = True
                elif event.key == pygame.K_LEFT:
                    selected_index = (selected_index - 1) % len(server_data.hand)
                elif event.key == pygame.K_RIGHT:
                    selected_index = (selected_index + 1) % len(server_data.hand)
                elif event.key == pygame.K_q:
                    sys.exit(0)
                elif event.key == pygame.K_s:  # on lance le jeu
                    conn.send(ClientMessage(type_message=TYPE_READY).serialize())
                elif event.key == pygame.K_m:
                    server_data.message = None
                elif event.key == pygame.K_t:
                    conn.send(ClientMessage(type_message=TYPE_TIMEOUT).serialize())
            elif event.type == pygame.JOYHATMOTION:
                selected_index = move_selection(selected_index, event.value[0], server_data.hand)
                if event.value[1] != 0:
                    conn.send(ClientMessage(type_message=TYPE_TIMEOUT).serialize()) # boutons haut/bas du D-pad
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
                    if not selected_highlight and len(server_data.hand) > 0:
                        print("séléctionné carte {} index {}".format(server_data.hand[selected_index], selected_index))
                        selected_highlight = True
                elif event.button == 8:  # select
                    sys.exit(0)
                elif event.button == 0 and len(server_data.hand)>0:
                    server_data.hand[selected_index] = (
                        not server_data.hand[selected_index][0], server_data.hand[selected_index][1])
                elif event.button == 1 and len(server_data.hand)>0:
                    server_data.hand[selected_index] = (
                        server_data.hand[selected_index][0], server_data.hand[selected_index][1] + 1)
                elif event.button == 3 and len(server_data.hand)>0:
                    server_data.hand[selected_index] = (
                        server_data.hand[selected_index][0], server_data.hand[selected_index][1] - 1)
                if event.button == 9:
                    conn.send(ClientMessage(type_message=TYPE_READY).serialize())

        if selected_highlight and not server_data.game_finished and len(
                server_data.hand) > 0 and selected_index >= 0:  # une carte a été sélectionnée
            conn.send(ClientMessage(type_message=TYPE_ACTION,
                                    payload=Card.from_tuple(server_data.hand[selected_index])
                                    ).serialize())  # on envoie notre action au serveur
            print("sending action")
            selected_highlight = False

        if selected_index >= 0:
            highlight(screen, hy, x0 + 50 * selected_index, selected_highlight)
        dessiner_main(screen, y0, x0, server_data.hand, font)
        dessiner_board(screen, y0 + 90, x0, server_data.board, font)
        afficher_message(screen, server_data.message, font)

        pygame.display.update()
        pygame.display.flip()  # double-buffered
        clock.tick(60)  # on attent pour limiter les FPS à 30 (et pas 100000 et un jeu qui bouf 100% CPU)
        screen.fill((0, 100, 0))  # on reset pour la frame suivante

    print("fin ...")
