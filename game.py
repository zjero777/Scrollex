# Pygame шаблон - скелет для нового проекта Pygame
import pygame
import random
from gameconst import *
from player import *
from utils import *

# создаем игру и окно
pygame.init()
pygame.mixer.init()  # для звука
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Scrollex")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group() 
player = Player()
all_sprites.add(player)

runing = True
while runing:
    # держим цикл на правильной скорости
    clock.tick(FPS)

    # Ввод процесса (события)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            runing = False

    # Обновление
    all_sprites.update()

    # Рендеринг
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_text(screen, "Test", 18, WIN_WIDTH / 2, 10)
    
    # после отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()