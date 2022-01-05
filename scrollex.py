import pygame

from game import Game
from explosion import *
from gameconst import *
from mob import Mob
from pausemenu import Pause_menu
from player import Player
from utils import *


class Scrollex(Game):
    def __init__(self, screen):
        super().__init__(screen)
        self.player = Player()
        all_sprites.add(self.player)
        self.background = pygame.image.load(
            path.join(img_dir, 'bg1920.jpg')).convert()
        self.background_rect = self.background.get_rect()
        self.expl_sounds = []
        for snd in ['Explosion4.wav', 'Explosion2.wav']:
            self.expl_sounds.append(
                pygame.mixer.Sound(path.join(snd_dir, snd)))

        self.meteor_images = []
        meteor_list = ["rock1.png", 'rock2.png', 'rock3.png', 'rock4.png']
        for img in meteor_list:
            self.meteor_images.append(pygame.image.load(
                path.join(img_dir, img)).convert_alpha())

        self.explosion_anim = {}
        self.explosion_anim['lg'] = []
        self.explosion_anim['sm'] = []

        ss_explosion = spritesheet(
            path.join(img_dir, "explosion_transparent.png"))
        explosion = ss_explosion.images_slice(5, 5)

        for i in range(len(explosion)):
            self.explosion_anim['lg'].append(
                pygame.transform.scale(explosion[i], (128, 128)))
            self.explosion_anim['sm'].append(
                pygame.transform.scale(explosion[i], (64, 64)))


        random.seed()
        for i in range(10):
            m = Mob(random.choice(self.meteor_images))
            all_sprites.add(m)
            mobs.add(m)

    def init(self):
        if not self.load_music:
            pygame.mixer.music.load(path.join(snd_dir, 'Deep Space Destructors - From The Ashes.mp3'))
            pygame.mixer.music.set_volume(0.12)
            pygame.mixer.music.play(loops=-1, fade_ms=2000)
            self.load_music = True
        else:
            pygame.mixer.music.unpause()
                    
    def draw(self):
        # self.screen.fill(BLACK)
        self.screen.blit(self.background, self.background_rect)
        all_sprites.draw(self.screen)

    def update(self, dt):
        # self.clock.tick(FPS)
        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_ESCAPE]:
            self.parent.start(Pause_menu)

        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                self.runing = False
                self.parent.SetPause()

        # Обновление
        all_sprites.update(dt)

        collide = False
        hits = pygame.sprite.spritecollide(
            self.player, mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            runing = True
            collide = True
            expl = Explosion(hit.rect.center, self.explosion_anim['sm'])
            all_sprites.add(expl)
            m = Mob(random.choice(self.meteor_images))
            all_sprites.add(m)
            mobs.add(m)

        hits = pygame.sprite.groupcollide(
            mobs, bullets, True, True, pygame.sprite.collide_circle)
        for hit in hits:
            random.choice(self.expl_sounds).play().set_volume(0.08)
            expl = Explosion(hit.rect.center, self.explosion_anim['lg'])
            all_sprites.add(expl)
            m = Mob(random.choice(self.meteor_images))
            all_sprites.add(m)
            mobs.add(m)
