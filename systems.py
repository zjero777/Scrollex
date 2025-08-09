import pygame
import random
from os import path
from ecs import System
from components import *
from gameconst import *
from utils import *

class MovementSystem(System):
    def process(self, dt):
        for entity_id, (position, velocity) in self.world.get_entities_with_components(Position, Velocity):
            position.x += velocity.dx * dt
            position.y += velocity.dy * dt

class RotationSystem(System):
    def process(self, dt):
        for entity_id, (rotation,) in self.world.get_entities_with_components(Rotation):
            rotation.angle = (rotation.angle + rotation.speed * dt) % 360

class BackgroundSystem(System):
    def process(self, dt):
        bg_entities = list(self.world.get_entities_with_components(Position, Sprite, Background))
        if not bg_entities:
            return

        # # Assuming all bg tiles have the same height
        # bg_height = bg_entities[0][1][1].image.get_height()
        # num_tiles = len(bg_entities)
        
        # for entity_id, (position, sprite, _) in bg_entities:
        #     if position.y > WIN_HEIGHT + bg_height / 2:
        #         position.y -= num_tiles * bg_height

class RenderSystem(System):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        self.is_render_system = True

    def process(self):
        entities_to_render = []
        for entity_id, (position, sprite) in self.world.get_entities_with_components(Position, Sprite):
            entities_to_render.append((sprite.layer, position, sprite, self.world.get_component(entity_id, Rotation)))

        entities_to_render.sort(key=lambda e: e[0])

        for layer, position, sprite, rotation in entities_to_render:
            if rotation:
                rotated_image = pygame.transform.rotate(sprite.image, rotation.angle)
                rect = rotated_image.get_rect(center=(position.x, position.y))
                self.screen.blit(rotated_image, rect)
            else:
                sprite.rect.center = (position.x, position.y)
                self.screen.blit(sprite.image, sprite.rect)

class PlayerControlSystem(System):
    def process(self, dt):
        keystate = pygame.key.get_pressed()
        mousestate = pygame.mouse.get_pressed()

        for entity_id, (position, velocity, player_input, player) in self.world.get_entities_with_components(Position, Velocity, PlayerInput, Player):
            # Apply friction
            velocity.dx *= player.friction
            velocity.dy *= player.friction

            # Apply acceleration
            if keystate[pygame.K_a]:
                velocity.dx -= player.acceleration * dt
            if keystate[pygame.K_d]:
                velocity.dx += player.acceleration * dt
            if keystate[pygame.K_w]:
                velocity.dy -= player.acceleration * dt
            if keystate[pygame.K_s]:
                velocity.dy += player.acceleration * dt

            # Clamp speed to max_speed
            speed = (velocity.dx**2 + velocity.dy**2)**0.5
            if speed > player.max_speed:
                velocity.dx = (velocity.dx / speed) * player.max_speed
                velocity.dy = (velocity.dy / speed) * player.max_speed

            # Boundary checking
            if position.x > WIN_WIDTH - 25:
                position.x = WIN_WIDTH - 25
                velocity.dx = 0
            if position.x < 25:
                position.x = 25
                velocity.dx = 0
            if position.y > WIN_HEIGHT - 25:
                position.y = WIN_HEIGHT - 25
                velocity.dy = 0
            if position.y < 25:
                position.y = 25
                velocity.dy = 0

            # Shield recharge
            if player.shield < player.max_shield:
                player.shield += player.shield_recharge_rate * (dt / 1000.0)
                if player.shield > player.max_shield:
                    player.shield = player.max_shield

            if mousestate[0]:
                self.shoot(position.x, position.y, player)

    def shoot(self, x, y, player):
        now = pygame.time.get_ticks()
        # Simple cooldown
        if now - getattr(self, 'last_shot', 0) > player.fire_rate:
            self.last_shot = now
            bullet_img = pygame.image.load(path.join(img_dir, "bullet.png")).convert_alpha()
            bullet_img = pygame.transform.scale(bullet_img, player.bullet_size)
            self.world.create_entity(
                Position(x, y),
                Velocity(dy=player.bullet_speed),
                Sprite(bullet_img, bullet_img.get_rect(), layer=5),
                Bullet(damage=player.bullet_damage),
                Collision(5)
            )

class CollisionSystem(System):
    def __init__(self, explosion_anim, expl_sounds, meteor_images, hit_sounds):
        super().__init__()
        self.explosion_anim = explosion_anim
        self.expl_sounds = expl_sounds
        self.meteor_images = meteor_images
        self.hit_sounds = hit_sounds
        self.loot_sprites = {
            "scrap": pygame.Surface((15, 15)),
            "ore": pygame.Surface((15, 15)),
            "xp": pygame.Surface((15, 15)),
        }
        self.loot_sprites["scrap"].fill((128, 128, 128))
        self.loot_sprites["ore"].fill((255, 165, 0))
        self.loot_sprites["xp"].fill((0, 0, 255))
        self.mob_types = {
            'small': {'size': (30, 30), 'score': 20, 'health': 1},
            'medium': {'size': (60, 60), 'score': 10, 'health': 3},
            'large': {'size': (100, 100), 'score': 5, 'health': 5}
        }

    def process(self, dt):
        # A more specific collision detection
        mobs = list(self.world.get_entities_with_components(Position, Collision, Mob, Velocity, Rotation))
        bullets = list(self.world.get_entities_with_components(Position, Collision, Bullet))
        players = list(self.world.get_entities_with_components(Position, Collision, PlayerInput))

        # Check for collisions between bullets and mobs
        for bullet_id, (b_pos, b_col, bullet) in bullets:
            for mob_id, (m_pos, m_col, mob, _, __) in mobs:
                dist_sq = (b_pos.x - m_pos.x)**2 + (b_pos.y - m_pos.y)**2
                if dist_sq < (b_col.radius + m_col.radius)**2:
                    self.world.remove_entity(bullet_id)
                    mob.health -= bullet.damage
                    channel = random.choice(self.hit_sounds).play()
                    if channel:
                        channel.set_volume(0.1)
                    self.create_hit_particles(b_pos)
                    if mob.health <= 0:
                        if mob.type in ['large', 'medium'] and random.random() < 0.3:
                            num_small_mobs = random.randint(2, 4)
                            for _ in range(num_small_mobs):
                                new_mob_type = 'small' if mob.type == 'medium' else 'medium'
                                self.create_mob(new_mob_type, m_pos)

                        self.world.remove_entity(mob_id)
                        explosion_size = 'lg' if mob.type == 'large' else 'sm'
                        self.create_explosion(m_pos, explosion_size)
                        self.create_loot(m_pos)

        # Check for collisions between players and mobs
        for player_id, (p_pos, p_col, _) in players:
            player = self.world.get_component(player_id, Player)
            player_velocity = self.world.get_component(player_id, Velocity)
            if not player or not player_velocity:
                continue

            for mob_id, (m_pos, m_col, mob, m_vel, __) in mobs:
                # Check if mob still exists
                if self.world.get_component(mob_id, Mob):
                    dist_sq = (p_pos.x - m_pos.x)**2 + (p_pos.y - m_pos.y)**2
                    if dist_sq < (p_col.radius + m_col.radius)**2:
                        # Damage calculation for player
                        mob_damage_to_player = mob.health # Mob damage to player is its health
                        
                        if player.shield > 0:
                            player.shield -= mob_damage_to_player
                            if player.shield < 0:
                                player.hull += player.shield # shield is negative, so this subtracts
                                player.shield = 0
                        else:
                            player.hull -= mob_damage_to_player

                        if player.hull <= 0:
                            self.world.remove_entity(player_id)
                            self.create_explosion(p_pos, 'lg') # bigger explosion for player

                        # Collision resolution (similar to mob-mob collision)
                        if dist_sq == 0:
                            continue

                        dx = p_pos.x - m_pos.x
                        dy = p_pos.y - m_pos.y
                        dist = (dist_sq)**0.5

                        # Normalize the collision vector
                        nx = dx / dist
                        ny = dy / dist

                        # Relative velocity
                        rvx = player_velocity.dx - m_vel.dx
                        rvy = player_velocity.dy - m_vel.dy

                        # Velocity along the normal
                        vel_along_normal = rvx * nx + rvy * ny

                        # Do not resolve if velocities are separating
                        if vel_along_normal > 0:
                            continue
                        
                        # Coefficient of restitution (e.g., 0.8 for a somewhat bouncy collision)
                        e = 0.8

                        # Calculate impulse scalar
                        impulse_scalar = -(1 + e) * vel_along_normal
                        impulse_scalar /= (1 / player.mass) + (1 / mob.mass)

                        # Apply impulse
                        impulse_x = impulse_scalar * nx
                        impulse_y = impulse_scalar * ny
                        
                        player_velocity.dx += impulse_x / player.mass
                        player_velocity.dy += impulse_y / player.mass
                        m_vel.dx -= impulse_x / mob.mass
                        m_vel.dy -= impulse_y / mob.mass

                        # Damage calculation for mob based on impulse and player mass
                        player_collision_damage_factor = 0.1 # Adjust this value for desired damage
                        mob.health -= abs(impulse_scalar) * player_collision_damage_factor
                        
                        if mob.health <= 0:
                            self.world.remove_entity(mob_id)
                            self.create_explosion(m_pos, 'sm')
                            self.create_loot(m_pos)

        # Check for collisions between mobs
        for i in range(len(mobs)):
            for j in range(i + 1, len(mobs)):
                mob1_id, (pos1, col1, mob1, vel1, rot1) = mobs[i]
                mob2_id, (pos2, col2, mob2, vel2, rot2) = mobs[j]

                dist_sq = (pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2
                if dist_sq < (col1.radius + col2.radius)**2:
                    # Collision detected, now handle the bounce
                    dx = pos1.x - pos2.x
                    dy = pos1.y - pos2.y
                    dist = (dist_sq)**0.5
                    
                    if dist == 0:
                        continue

                    # Normalize the collision vector
                    nx = dx / dist
                    ny = dy / dist

                    # Relative velocity
                    rvx = vel1.dx - vel2.dx
                    rvy = vel1.dy - vel2.dy

                    # Velocity along the normal
                    vel_along_normal = rvx * nx + rvy * ny

                    # Do not resolve if velocities are separating
                    if vel_along_normal > 0:
                        continue
                    
                    # Coefficient of restitution (e.g., 0.8 for a somewhat bouncy collision)
                    e = 0.8

                    # Calculate impulse scalar
                    impulse_scalar = -(1 + e) * vel_along_normal
                    impulse_scalar /= (1 / mob1.mass) + (1 / mob2.mass)

                    # Apply impulse
                    impulse_x = impulse_scalar * nx
                    impulse_y = impulse_scalar * ny
                    vel1.dx += impulse_x / mob1.mass
                    vel1.dy += impulse_y / mob1.mass
                    vel2.dx -= impulse_x / mob2.mass
                    vel2.dy -= impulse_y / mob2.mass

                    # Angular impulse
                    # For simplicity, we'll just apply a fraction of the impulse as torque
                    # A more accurate model would involve cross products
                    rot1.speed += (impulse_x * ny - impulse_y * nx) / rot1.inertia
                    rot2.speed -= (impulse_x * ny - impulse_y * nx) / rot2.inertia

    def create_explosion(self, position, size):
        channel = random.choice(self.expl_sounds).play()
        if channel:
            channel.set_volume(0.08)
        anim = self.explosion_anim[size]
        self.world.create_entity(
            Position(position.x, position.y),
            Sprite(anim[0], anim[0].get_rect(), layer=3),
            Animation(frames=anim, speed=50),
            Lifetime(duration=len(anim) * 50, created_at=pygame.time.get_ticks())
        )

    def create_loot(self, position):
        loot_type = random.choice(["scrap", "ore", "xp"])
        loot_value = {"scrap": 5, "ore": 10, "xp": 20}[loot_type]
        loot_sprite = self.loot_sprites[loot_type]
        self.world.create_entity(
            Position(position.x, position.y),
            Velocity(dx=random.uniform(-0.1, 0.1), dy=random.uniform(-0.1, 0.1)),
            Sprite(loot_sprite, loot_sprite.get_rect(), layer=3),
            Loot(type=loot_type, value=loot_value),
            Collision(10)
        )

    def create_mob(self, mob_type, position):
        mob_info = self.mob_types[mob_type]
        mob_img = random.choice(self.meteor_images)
        mob_img = pygame.transform.scale(mob_img, mob_info['size'])
        
        mass = (mob_info['size'][0] * mob_info['size'][1]) / 100.0
        radius = int(mob_img.get_rect().width * .85 / 2)
        inertia = 0.5 * mass * radius**2

        self.world.create_entity(
            Position(position.x, position.y),
            Velocity(dx=random.uniform(-0.2, 0.2), dy=random.uniform(-0.2, 0.2)),
            Sprite(mob_img, mob_img.get_rect(), layer=3),
            Mob(type=mob_type, health=mob_info['health'], mass=mass),
            Collision(radius),
            Rotation(speed=random.uniform(-0.1, 0.1), inertia=inertia)
        )

    def create_hit_particles(self, position):
        particle_count = random.randint(3, 7)
        for _ in range(particle_count):
            particle_surface = pygame.Surface((3, 3))
            particle_surface.fill((128, 128, 128))
            self.world.create_entity(
                Position(position.x, position.y),
                Velocity(dx=random.uniform(-0.3, 0.3), dy=random.uniform(-0.3, 0.3)),
                Sprite(particle_surface, particle_surface.get_rect(), layer=3),
                Lifetime(duration=random.randint(100, 300), created_at=pygame.time.get_ticks())
            )

class AnimationSystem(System):
    def process(self, dt):
        for entity_id, (sprite, animation) in self.world.get_entities_with_components(Sprite, Animation):
            now = pygame.time.get_ticks()
            if now - animation.last_update > animation.speed:
                animation.last_update = now
                animation.current_frame = (animation.current_frame + 1) % len(animation.frames)
                sprite.image = animation.frames[animation.current_frame]

class LifetimeSystem(System):
    def process(self, dt):
        for entity_id, (lifetime,) in self.world.get_entities_with_components(Lifetime):
            if pygame.time.get_ticks() - lifetime.created_at > lifetime.duration:
                self.world.remove_entity(entity_id)

class BoundarySystem(System):
    def process(self, dt):
        for entity_id, (position,) in self.world.get_entities_with_components(Position):
            # Check for mobs and bullets going off-screen
            is_mob = self.world.get_component(entity_id, Mob)
            is_bullet = self.world.get_component(entity_id, Bullet)

            if is_mob:
                if position.y > WIN_HEIGHT + 20 or position.x < -25 or position.x > WIN_WIDTH + 20:
                    self.world.remove_entity(entity_id)
            elif is_bullet:
                if position.y < -10:
                    self.world.remove_entity(entity_id)

class MobSpawningSystem(System):
    def __init__(self, meteor_images):
        super().__init__()
        self.meteor_images = meteor_images
        self.min_mobs = 10
        self.mob_types = {
            'small': {'size': (30, 30), 'score': 20, 'health': 1},
            'medium': {'size': (60, 60), 'score': 10, 'health': 3},
            'large': {'size': (100, 100), 'score': 5, 'health': 5}
        }

    def process(self, dt):
        mob_count = len(list(self.world.get_entities_with_components(Mob)))
        if mob_count < self.min_mobs:
            for _ in range(self.min_mobs - mob_count):
                self.create_mob()

    def create_mob(self, mob_type=None, position=None):
        if mob_type is None:
            mob_type = random.choice(list(self.mob_types.keys()))
        mob_info = self.mob_types[mob_type]
        mob_img = random.choice(self.meteor_images)
        mob_img = pygame.transform.scale(mob_img, mob_info['size'])
        
        mass = (mob_info['size'][0] * mob_info['size'][1]) / 100.0
        radius = int(mob_img.get_rect().width * .85 / 2)
        inertia = 0.5 * mass * radius**2

        if position is None:
            position = Position(random.randrange(WIN_WIDTH - mob_info['size'][0]), random.randrange(-100, -40))

        self.world.create_entity(
            position,
            Velocity(dx=random.randrange(-2, 2) / 20, dy=random.randrange(1, 6) / 20),
            Sprite(mob_img, mob_img.get_rect(), layer=3),
            Mob(type=mob_type, health=mob_info['health'], mass=mass),
            Collision(radius),
            Rotation(speed=random.randrange(-2, 3) / 10.0, inertia=inertia)
        )

class LootSystem(System):
    def process(self, dt):
        players = list(self.world.get_entities_with_components(Position, Collision, PlayerInput))
        loots = list(self.world.get_entities_with_components(Position, Collision, Loot))

        for player_id, (p_pos, p_col, _) in players:
            for loot_id, (l_pos, l_col, loot) in loots:
                dist_sq = (p_pos.x - l_pos.x)**2 + (p_pos.y - l_pos.y)**2
                if dist_sq < (p_col.radius + l_col.radius)**2:
                    self.world.remove_entity(loot_id)
                    for _, (game_state,) in self.world.get_entities_with_components(GameState):
                        game_state.score += loot.value
                        if loot.type == "scrap":
                            game_state.scrap += 1
                        elif loot.type == "ore":
                            game_state.ore += 1
                        elif loot.type == "xp":
                            game_state.xp += 1

class UISystem(System):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.is_render_system = True

    def process(self):
        for _, (game_state,) in self.world.get_entities_with_components(GameState):
            score_text = self.font.render(f"Score: {game_state.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))

            scrap_text = self.font.render(f"Scrap: {game_state.scrap}", True, (128, 128, 128))
            self.screen.blit(scrap_text, (10, 50))

            ore_text = self.font.render(f"Ore: {game_state.ore}", True, (255, 165, 0))
            self.screen.blit(ore_text, (10, 90))

            xp_text = self.font.render(f"XP: {game_state.xp}", True, (0, 0, 255))
            self.screen.blit(xp_text, (10, 130))

        player_entities = list(self.world.get_entities_with_components(Player))
        if player_entities:
            player_id, (player,) = player_entities[0]
            
            # Shield bar
            if player.shield > 0:
                shield_pct = player.shield / player.max_shield
                shield_bar_length = 100
                shield_bar_height = 10
                shield_bar_x = 10
                shield_bar_y = WIN_HEIGHT - 35
                fill = shield_pct * shield_bar_length
                outline_rect = pygame.Rect(shield_bar_x, shield_bar_y, shield_bar_length, shield_bar_height)
                fill_rect = pygame.Rect(shield_bar_x, shield_bar_y, fill, shield_bar_height)
                pygame.draw.rect(self.screen, (0, 128, 255), fill_rect)
                pygame.draw.rect(self.screen, (255, 255, 255), outline_rect, 2)

            # Hull bar
            if player.hull > 0:
                hull_pct = player.hull / player.max_hull
                hull_bar_length = 100
                hull_bar_height = 10
                hull_bar_x = 10
                hull_bar_y = WIN_HEIGHT - 20
                fill = hull_pct * hull_bar_length
                outline_rect = pygame.Rect(hull_bar_x, hull_bar_y, hull_bar_length, hull_bar_height)
                fill_rect = pygame.Rect(hull_bar_x, hull_bar_y, fill, hull_bar_height)
                pygame.draw.rect(self.screen, (0, 255, 0), fill_rect)
                pygame.draw.rect(self.screen, (255, 255, 255), outline_rect, 2)