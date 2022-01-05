import pygame
import random


from gameconst import *

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, anim):
        pygame.sprite.Sprite.__init__(self)
        self.anim = anim
        self.frame = 0
        self.image = anim[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 30

    def update(self, dt):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.anim):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center