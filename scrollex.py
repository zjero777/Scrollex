import pygame
import random
from os import path
from ecs import World
from components import *
from systems import (
    MovementSystem, RenderSystem, PlayerControlSystem, 
    CollisionSystem, AnimationSystem, LifetimeSystem, 
    BoundarySystem, MobSpawningSystem, LootSystem, UISystem, RotationSystem,
    BackgroundSystem
)
from gameconst import *
from utils import *
from game import Game

class ScrollexGame(Game):
    def __init__(self, screen):
        super().__init__(screen)
        self.world = World()

    def init(self):
        self.load_assets()
        self.create_player()
        self.create_game_state()
        self.setup_systems()
        self.create_background()

    def load_assets(self):
        self.bg_images = [
            pygame.image.load(path.join(img_dir, f'bg{i}.png')).convert() for i in range(1, 5)
        ]
        self.bg_images.append(pygame.image.load(path.join(img_dir, 'bg5.jpg')).convert())
        self.meteor_images = [
            pygame.image.load(path.join(img_dir, f'rock{i}.png')).convert_alpha() for i in range(1, 5)
        ]
        self.expl_sounds = [
            pygame.mixer.Sound(path.join(snd_dir, f'explosion{i}.wav')) for i in range(2, 5, 2)
        ]
        self.hit_sounds = [
            pygame.mixer.Sound(path.join(snd_dir, 'gluhoy-udar.mp3'))
        ]
        self.explosion_anim = load_explosion_animation()

    def setup_systems(self):
        self.world.add_system(MovementSystem())
        self.world.add_system(RotationSystem())
        self.world.add_system(BackgroundSystem())
        self.world.add_system(PlayerControlSystem())
        self.world.add_system(CollisionSystem(self.explosion_anim, self.expl_sounds, self.meteor_images, self.hit_sounds))
        self.world.add_system(AnimationSystem())
        self.world.add_system(LifetimeSystem())
        self.world.add_system(BoundarySystem())
        self.world.add_system(MobSpawningSystem(self.meteor_images))
        self.world.add_system(LootSystem())
        self.world.add_system(RenderSystem(self.screen)) # RenderSystem before UISystem
        self.world.add_system(UISystem(self.screen)) # UISystem should be last for rendering on top

    def create_background(self):
        # Static background
        bg_choice = self.bg_images[0] # Use the first image as static
        bg_image = pygame.transform.scale(bg_choice, (WIN_WIDTH, WIN_HEIGHT))
        self.world.create_entity(
            Position(WIN_WIDTH / 2, WIN_HEIGHT / 2),
            Sprite(bg_image, bg_image.get_rect(), layer=0)
        )

        # Slow stars
        slow_stars = create_starfield(WIN_WIDTH, WIN_HEIGHT, 200, (100, 100, 100), (0.5, 1.5))
        for i in range(2):
            self.world.create_entity(
                Position(WIN_WIDTH / 2, i * WIN_HEIGHT - WIN_HEIGHT / 2),
                Velocity(dy=0.02),
                Sprite(slow_stars, slow_stars.get_rect(), layer=1),
                Background()
            )

        # Fast stars
        fast_stars = create_starfield(WIN_WIDTH, WIN_HEIGHT, 50, (200, 200, 200), (1, 2))
        for i in range(2):
            self.world.create_entity(
                Position(WIN_WIDTH / 2, i * WIN_HEIGHT - WIN_HEIGHT / 2),
                Velocity(dy=0.05),
                Sprite(fast_stars, fast_stars.get_rect(), layer=2),
                Background()
            )

    def create_player(self):
        player_img = pygame.image.load(path.join(img_dir, "jet.png")).convert_alpha()
        player_img = pygame.transform.scale(player_img, (50, 70))
        self.world.create_entity(
            Position(WIN_WIDTH / 2, WIN_HEIGHT - 50),
            Velocity(),
            Sprite(player_img, player_img.get_rect(), layer=4),
            PlayerInput(),
            Player(),
            Collision(25)
        )

    def create_game_state(self):
        self.world.create_entity(GameState())

    

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.parent.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from pausemenu import Pause_menu
                    self.parent.start(Pause_menu)

    def update(self, dt):
        self.events()
        self.world.process_update(dt)
        self.check_player_death()
        

    def draw(self):
        self.screen.fill(BLACK)
        self.world.process_render()

    def check_player_death(self):
        if not any(self.world.get_entities_with_components(PlayerInput)):
            self.running = False