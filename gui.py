import socket
import sys
from threading import Thread, Event

import pygame
import pygameMenu

from data import *
from matchmaking import FindGame


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
    game_ready=False

    def __init__(self, conn: socket.socket):
        self.conn = conn
        super().__init__(daemon=True)

    def run(self) -> None:
        while not self.game_finished or True:
            buf = self.conn.recv(2048)
            data: ServerMessage = ServerMessage.deserialize(buf)
            self.message = data.infos
            print(data)  # affiche le type de message reçu
            if data.type_message in [TYPE_TIMEOUT, TYPE_HAND_CHANGED]:
                self.hand = [x.to_tuple() for x in data.payload]
            elif data.type_message == TYPE_BOARD_CHANGED:
                self.board = data.payload
                if not self.game_ready:
                    print("debut jeu")
                self.game_ready = True
            elif data.type_message in STRING_TYPES:
                self.message = data.payload
                print("--->" + data.payload)
            if data.type_message == TYPE_GAME_END:
                print("**************************= JEU FINI =*******************************")
                self.game_finished = True
                self.message = data.payload
                # self.conn.close()

    def send(self, message: ClientMessage):
        if not self.game_finished:
            # self.conn.setblocking(False)
            self.conn.send(message.serialize())


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
police = "Noto Sans"
menu_running = True
if __name__ == '__main__':
    server_finder = FindGame(daemon=True)
    server_finder.start()
    pygame.init()  # initialisation des ressources
    pygame.display.set_caption("PPC Freak Out!")
    font = pygame.font.SysFont(police, 20, 5)
    clock = pygame.time.Clock()  # intialisation du timer FPS


    def bg_func():
        screen.fill((128, 0, 128))


    # setup du menu
    main = pygameMenu.Menu(screen, 1000, 500, police, "Freak Out !", True, bgfun=bg_func, menu_height=400,
                           menu_width=900)
    main._onclose = main.disable
    main.add_text_input(title="nom d'utilisateur: ", textinput_id='username', default="", input_underline='_',
                        maxchar=15, align=pygameMenu.locals.ALIGN_LEFT)
    main.add_selector("Joystick", values=[('On', 0), ('Off', 1)], selector_id='joystick', default=1)
    main.add_option('Jouer', main.disable)
    main.add_option('Quitter', pygameMenu.events.EXIT)

    main.mainloop()  # 1er affichage du menu
    main.disable(closelocked=True)
    username = main.get_input_data()['username']
    joystick = main.get_input_data()['joystick'][0] == 'On'
    print(f"joystick : {joystick}, username={username}, input_date: {main.get_input_data()}")
    try:
        if len(sys.argv) > 2:
            if sys.argv[1] == "-j":
                joystick = True
        if joystick:
            j = pygame.joystick.Joystick(0)
            j.init()
    except:
        j = None
    # configuration du jeu finie

    # démarrage du réseau
    screen.fill((102, 102, 153))
    afficher_message(screen, "Connexion au serveur de jeu", font)
    pygame.display.update()
    pygame.display.flip()
    conn = socket.socket()
    server_finder.join()  # attend le timeout de l'écoute du broadcast

    conn.connect(server_finder.found_server)  # écoute le broadast local pour découvrir le serveur
    server_data = NetworkReceiver(conn)  # initialisation de la connexion au serveur de jeu
    server_data.message = username
    conn.send(ClientMessage(type_message=TYPE_JOIN, payload=username).serialize())
    #
    # lobby: attente des autres joueurs
    start_menu = pygameMenu.TextMenu(screen, 700, 400, police, "Lobby", bgfun=bg_func)


    def im_ready():
        print('sending ready')
        start_menu.disable(closelocked=True)
        conn.send(ClientMessage(type_message=TYPE_READY).serialize())



    start_menu.add_option("Demarrer", im_ready)
    start_menu.add_option('Quitter', pygameMenu.events.EXIT)

    # pendant l'attente on initialise le menu 'ESC' du jeu
    game_menu = pygameMenu.Menu(screen, 800, 400, police, "Freak Out !", True, bgfun=bg_func, menu_height=300,
                                menu_width=700)
    game_menu._onclose = game_menu.disable
    game_menu.add_option('Quitter', pygameMenu.events.EXIT)
    game_menu.add_option('Retour au jeu', game_menu.disable)
    game_menu.disable()

    server_data.start()
    start_menu.mainloop()

    screen.fill((153, 102, 0))
    afficher_message(screen, "Attente des autres joueurs", font)
    pygame.display.update()
    pygame.display.flip()
    print("starting game")

    #server_data.game_ready_event.wait()

    while not server_data.game_ready:
        events=pygame.event.get()
        game_menu.mainloop(events)
        screen.fill((153, 102, 0))
        afficher_message(screen, "Attente des autres joueurs", font)
        clock.tick(60)
        pygame.display.update()
        pygame.display.flip()
        if server_data.game_ready:
            print('start game')

    while True:  # on quitte avec le menu

        if selected_index >= len(server_data.hand):
            selected_index -= 1

        events = pygame.event.get()
        game_menu.mainloop(events)  # pour que le menu puisse s'afficher si on appuie sur ESC
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()
                if y >= 10 and y <= 70:
                    clicked_index= (x-10)//50
                    #print(f"calc:{clicked_index} index: {selected_index}")
                    if clicked_index < len(server_data.hand):
                        selected_index = clicked_index
                #print(f"x={x} y={y}")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    selected_highlight = True
                elif event.key == pygame.K_ESCAPE:
                    game_menu.enable()
                elif event.key == pygame.K_LEFT:
                    selected_index = move_selection(selected_index, -1, server_data.hand)
                elif event.key == pygame.K_RIGHT:
                    selected_index = move_selection(selected_index, +1, server_data.hand)
                elif event.key == pygame.K_q:
                    sys.exit(0)
                elif event.key == pygame.K_s:  # on lance le jeu
                    server_data.send(ClientMessage(type_message=TYPE_READY))
                elif event.key == pygame.K_m:
                    server_data.message = None
            elif event.type == pygame.JOYHATMOTION:
                selected_index = move_selection(selected_index, event.value[0], server_data.hand)
            elif event.type == pygame.JOYAXISMOTION:
                # print("j{} h{} v{}".format(event.joy, event.axis, event.value))
                selected_index = move_selection(selected_index, int(event.value), server_data.hand)
                break  # je voulais avoir moins d'auto-repeat mais en fait ça marche pas
            elif event.type == pygame.JOYBUTTONDOWN:
                # print("j{} b{}".format(event.joy, event.button))
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
                elif event.button == 0 and len(server_data.hand) > 0:
                    server_data.hand[selected_index] = (
                        not server_data.hand[selected_index][0], server_data.hand[selected_index][1])
                elif event.button == 1 and len(server_data.hand) > 0:
                    server_data.hand[selected_index] = (
                        server_data.hand[selected_index][0], server_data.hand[selected_index][1] + 1)
                elif event.button == 3 and len(server_data.hand) > 0:
                    server_data.hand[selected_index] = (
                        server_data.hand[selected_index][0], server_data.hand[selected_index][1] - 1)

        if selected_highlight and not server_data.game_finished and len( # action 'asynchrone'
                server_data.hand) > 0 and selected_index >= 0:  # une carte a été sélectionnée
            server_data.send(ClientMessage(
                type_message=TYPE_ACTION,
                payload=Card.from_tuple(server_data.hand[selected_index])
            ))  # on envoie notre action au serveur
            print("sending action")
            selected_highlight = False

        if selected_index >= 0 and not server_data.game_finished:
            highlight(screen, hy, x0 + 50 * selected_index, selected_highlight)
        dessiner_main(screen, y0, x0, server_data.hand, font)
        dessiner_board(screen, y0 + 90, x0, server_data.board, font)
        afficher_message(screen, server_data.message, font)

        pygame.display.update()
        pygame.display.flip()  # double-buffered
        clock.tick(60)  # on attent pour limiter les FPS à 30 (et pas 100000 et un jeu qui bouf 100% CPU)
        screen.fill((0, 100, 0))  # on reset pour la frame suivante
