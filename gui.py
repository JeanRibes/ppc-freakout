import sys

import pygame


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


list_cartes = [
    (True, 4),
    (False, 5),
    (True, 5),
    (False, 9),
    (True, 1), (False, 2), (False, 3)
]
map_cartes = [
    [(True, 4), (True, 4), (True, 4), (True, 4)],
    [(True, 5), (True, 5), (True, 5), (True, 5)],
    [(False, 5), (False, 5), (False, 5), ],
    [(False, 9), (False, 9), (False, 9), (False, 9), ],
    [(True, 1), (True, 1), (True, 1)],
]


def dessiner_board(screen, x0, y0, board, font):
    x = x0
    y = y0
    for cartes in map_cartes:
        for couleur, chiffre in cartes:
            dessiner_carte(screen, couleur, chiffre, font, x, y)
            x += 70
        y += 50
        x = x0


def highlight(screen, y, x, selected_highlight):
    border = 4
    pygame.draw.rect(screen, (252, 232, 3) if selected_highlight else (255, 255, 255),
                     pygame.Rect(x - border, y - border, 40 + 2 * border, 60 + 2 * border))


def move_selection(selected_index, i):
    return (selected_index + i) % len(list_cartes)

chance = False

screen = pygame.display.set_mode((1500, 500))
x0 = 10
y0 = 10
selected_index = 0
hy = y0
selected_highlight = False

if __name__ == '__main__':
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

    while not done:
        if selected_highlight:  # une carte a été sélectionnée
            list_cartes.pop(selected_index)
            selected_highlight = False
            if selected_index > len(list_cartes) - 1:
                selected_index -= 1
        if len(list_cartes) == 0:
            break

        highlight(screen, hy, x0 + 50 * selected_index, selected_highlight)
        dessiner_main(screen, y0, x0, list_cartes, font)
        dessiner_board(screen, y0 + 90, x0, map_cartes, font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("buzz")
                    selected_highlight = not selected_highlight
                elif event.key == pygame.K_LEFT:
                    selected_index = (selected_index - 1) % len(list_cartes)
                elif event.key == pygame.K_RIGHT:
                    selected_index = (selected_index + 1) % len(list_cartes)
            elif event.type == pygame.JOYHATMOTION:
                selected_index = move_selection(selected_index, event.value[0])
                selected_index = move_selection(selected_index, event.value[1])
            elif event.type == pygame.JOYAXISMOTION:
                print("axis")
                print("j{} h{} v{}".format(event.joy, event.axis, event.value))
                selected_index=move_selection(selected_index, int(event.value))
                break # je voulais avoir moins d'auto-repeat mais en fait ça marche pas
                #selected_index = move_selection(selected_index, int(event.value)*int(abs(event.value)>0.5)*int(chance))
            elif event.type == pygame.JOYBUTTONDOWN:
                print("j{} b{}".format(event.joy, event.button))
                if event.button == 5:
                    selected_index = move_selection(selected_index, 1)
                elif event.button == 4:
                    selected_index = move_selection(selected_index, -1)
                elif event.button == 2 or event.button == 7:
                    if not selected_highlight:
                        print("séléctionné carte {} index {}".format(list_cartes[selected_index], selected_index))
                    selected_highlight = not selected_highlight
                elif event.button == 8:  # select
                    list_cartes.clear()
                elif event.button == 0:
                    list_cartes[selected_index] = (not list_cartes[selected_index][0], list_cartes[selected_index][1])
                elif event.button == 1:
                    list_cartes[selected_index] = (list_cartes[selected_index][0], list_cartes[selected_index][1] + 1)
                elif event.button == 3:
                    list_cartes[selected_index] = (list_cartes[selected_index][0], list_cartes[selected_index][1] - 1)
                if event.button == 9:
                    list_cartes.append((True,5))

        pygame.display.update()
        pygame.display.flip()  # double-buffered
        clock.tick(30)  # on attent pour limiter les FPS à 60 (et pas 100000 et un jeu qui bouf 100% CPU)
        screen.fill((0, 100, 0))  # on reset pour la frame suivante

    print("fin ...")
