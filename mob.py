import pygame
import random

from gameconst import *

class Mob(pygame.sprite.Sprite):
    def __init__(self, img):
        pygame.sprite.Sprite.__init__(self)
        self.mob_img = img
        self.mob_img = pygame.transform.scale(self.mob_img, (80, 80))

        self.image = self.mob_img 
        self.rect = self.image.get_rect()

        self.radius = int(self.rect.width * .85 / 2)
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

        self.rect.x = random.randrange(WIN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        self.rotate()
        if self.rect.top > WIN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIN_WIDTH + 20:
            self.rect.x = random.randrange(WIN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-3, 3)
    
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.mob_img, self.rot)
            self.rect = self.image.get_rect()
            #pygame.draw.rect(self.image, WHITE, self.rect, 1)
            #pygame.draw.circle(self.image, RED, self.rect.center, self.radius, 1)
            self.rect.center = old_center
            
            
            
