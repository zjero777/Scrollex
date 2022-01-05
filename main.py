# Alexandr Zhelanov https://soundcloud.com/alexandr-zhelanov
import pygame

from game import *
from mainmenu import *
from pausemenu import *
from scrollex import *


# создаем игру и окно
pygame.init()
pygame.mixer.init()  # для звука
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Scrollex")

game = Game(screen)

game.add(Main_menu(screen))
game.add(Scrollex(screen))
game.add(Pause_menu(screen))

game.start(Main_menu)


while game.runing:
    game.update()
    game.draw()
pygame.quit()
exit(0)
