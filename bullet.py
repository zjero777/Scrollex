import pygame
import random

from gameconst import *
from os import path
img_dir = path.join(path.dirname(__file__), 'img')


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        bullet_img = pygame.image.load(path.join(img_dir, "bullet.png")).convert_alpha()
        self.image = pygame.transform.scale(bullet_img, (10, 28))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # убить, если он заходит за верхнюю часть экрана
        if self.rect.bottom < 0:
            self.kill()