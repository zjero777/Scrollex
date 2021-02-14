# Pygame шаблон - скелет для нового проекта Pygame
import pygame
import random

from gameconst import *
from player import *
from utils import *
from mob import *
from bullet import *

# создаем игру и окно
pygame.init()
pygame.mixer.init()  # для звука
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption( "Scrollex")
clock = pygame.time.Clock()
player = Player()
all_sprites.add(player)

random.seed()
for i in range(20):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


runing = True
while runing:
    # держим цикл на правильной скорости
    clock.tick(FPS)

    # Ввод процесса (события)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            runing = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Обновление
    all_sprites.update()

    hits = pygame.sprite.spritecollide(player, mobs, False)
    if hits:
        runing = False

    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

    # Рендеринг
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_text(screen, "Test", 18, WIN_WIDTH / 2, 10)
    
    # после отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()