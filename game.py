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
 
# Загрузка всей игровой графики
background = pygame.image.load(path.join(img_dir, 'bg1920.jpg')).convert()
background_rect = background.get_rect()

meteor_images = []
meteor_list = ["rock1.png",'rock2.png', 'rock3.png','rock4.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert_alpha())



random.seed()
for i in range(10):
    m = Mob(random.choice(meteor_images))
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

    collide = False
    hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
    if hits:
        runing = True
        collide = True

    hits = pygame.sprite.groupcollide(mobs, bullets, True, True, pygame.sprite.collide_circle)
    for hit in hits:
        m = Mob(random.choice(meteor_images))
        all_sprites.add(m)
        mobs.add(m)

    # Рендеринг
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    #draw_text(screen, f"{collide}", 15, player.rect.x, player.rect.y)
    
    # после отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()