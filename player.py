import pygame
from gameconst import *
from bullet import *
from utils import *



class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.player_img = pygame.image.load(path.join(img_dir, "jet.png")).convert_alpha()
        self.player_img = pygame.transform.scale(self.player_img, (50, 70))

        self.image = self.player_img
        self.rect = self.image.get_rect()
        self.radius = 20
        #pygame.draw.circle(self.player_img, RED, self.rect.center, self.radius, 1)
        

        self.rect.centerx = WIN_WIDTH / 2
        self.rect.bottom = WIN_HEIGHT - 10
        self.speedx = 0        

        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()

        # Загрузка мелодий игры
        self.shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'Laser_Shoot43.wav'))

    def update(self, dt):
        #time_factor = self.dt*FPS        
        
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        mousestate = pygame.mouse.get_pressed()
        if keystate[pygame.K_a]:
            self.speedx = -0.8
        if keystate[pygame.K_d]:
            self.speedx = 0.8
        if mousestate[0]:
            self.shoot()
        self.rect.x += self.speedx*dt
        if self.rect.right > WIN_WIDTH:
            self.rect.right = WIN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0      
        

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            self.shoot_sound.play().set_volume(0.04)