from dataclasses import dataclass
import pygame
from ecs import Component

@dataclass
class Position(Component):
    x: float
    y: float

@dataclass
class Velocity(Component):
    dx: float = 0.0
    dy: float = 0.0

@dataclass
class Sprite(Component):
    image: pygame.Surface
    rect: pygame.Rect
    layer: int = 0

@dataclass
class PlayerInput(Component):
    pass # Tag component

@dataclass
class Player(Component):
    fire_rate: int = 250 # ms
    bullet_speed: float = -1.0
    bullet_damage: int = 1
    bullet_size: tuple = (10, 20)
    acceleration: float = 0.002
    friction: float = 0.98
    max_speed: float = 0.28
    shield: float = 30.0
    max_shield: float = 10.0
    hull: float = 50.0
    max_hull: float = 50.0
    shield_recharge_rate: float = 2.0 # points per second
    mass: float = 10.0 # Added mass for collision physics

@dataclass
class Mob(Component):
    type: str
    health: int = 1
    mass: float = 1.0

@dataclass
class Bullet(Component):
    damage: int = 1

@dataclass
class Collision(Component):
    radius: int

@dataclass
class Animation(Component):
    frames: list
    speed: float
    current_frame: int = 0
    last_update: int = 0

@dataclass
class Lifetime(Component):
    duration: int
    created_at: int

@dataclass
class GameState(Component):
    score: int = 0
    scrap: int = 0
    ore: int = 0
    xp: int = 0

@dataclass
class Rotation(Component):
    angle: float = 0.0
    speed: float = 0.0
    inertia: float = 1.0

@dataclass
class Loot(Component):
    type: str
    value: int

@dataclass
class Background(Component):
    pass # Tag component
