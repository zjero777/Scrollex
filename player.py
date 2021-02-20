import pygame
from gameconst import *
from bullet import *
from utils import *

from os import path
img_dir = path.join(path.dirname(__file__), 'img')

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.player_img = pygame.image.load(path.join(img_dir, "ship-sprite-394x347-2.png")).convert()
        self.player_img = pygame.transform.scale(self.player_img, (50, 38))
        self.player_img.set_colorkey(GREEN)

        self.image = self.player_img
        self.rect = self.image.get_rect()
        self.radius = 20
        #pygame.draw.circle(self.player_img, RED, self.rect.center, self.radius, 1)
        

        self.rect.centerx = WIN_WIDTH / 2
        self.rect.bottom = WIN_HEIGHT - 10
        self.speedx = 0        

    def update(self):
        
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        self.rect.x += self.speedx
        if self.rect.right > WIN_WIDTH:
            self.rect.right = WIN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0      
        

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)