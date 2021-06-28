# Pygame шаблон - скелет для нового проекта Pygame
# Alexandr Zhelanov https://soundcloud.com/alexandr-zhelanov

import pygame

import random


from gameconst import *
from player import *
from utils import *
from mob import *
from bullet import *
from explosion import *
 
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

expl_sounds = []
for snd in ['Explosion2.wav', 'Explosion4.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))

pygame.mixer.music.load(path.join(snd_dir, 'Flying me softly.mp3'))
pygame.mixer.music.set_volume(0.12)




meteor_images = []
meteor_list = ["rock1.png",'rock2.png', 'rock3.png','rock4.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert_alpha())

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []

ss_explosion = spritesheet(path.join(img_dir, "explosion_transparent.png"))
explosion = ss_explosion.images_slice(5,5)

for i in range(len(explosion)):
    explosion_anim['lg'].append(pygame.transform.scale(explosion[i], (128, 128)))
    explosion_anim['sm'].append(pygame.transform.scale(explosion[i], (64, 64)))

random.seed()
for i in range(10):
    m = Mob(random.choice(meteor_images))
    all_sprites.add(m)
    mobs.add(m)

pygame.mixer.music.play(loops=-1)
  
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

    collide = False
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        runing = True
        collide = True
        expl = Explosion(hit.rect.center, explosion_anim['sm'])
        all_sprites.add(expl)
        m = Mob(random.choice(meteor_images))
        all_sprites.add(m)
        mobs.add(m)



    hits = pygame.sprite.groupcollide(mobs, bullets, True, True, pygame.sprite.collide_circle)
    for hit in hits:
        random.choice(expl_sounds).play().set_volume(0.08)
        expl = Explosion(hit.rect.center, explosion_anim['lg'])
        all_sprites.add(expl)
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