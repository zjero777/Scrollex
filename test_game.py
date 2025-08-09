import unittest
import pygame
from unittest.mock import Mock, patch, MagicMock

# Mock pygame for testing purposes
pygame.init = Mock()
pygame.display = Mock()
pygame.display.set_mode = Mock(return_value=Mock())
pygame.event = Mock()
pygame.event.get = Mock(return_value=[])
pygame.time = Mock()
pygame.time.Clock = Mock(return_value=Mock(tick=Mock(return_value=16))) # Simulate 60 FPS (1000ms/60 = 16.66ms)
pygame.mixer = Mock()
pygame.mixer.music = Mock()
pygame.image = Mock()
pygame.image.load = Mock(return_value=Mock(convert=Mock(), get_rect=Mock(), convert_alpha=Mock(return_value=Mock())))
pygame.font = Mock()
pygame.font.init = Mock()
pygame.font.Font = Mock(return_value=Mock())

# Mock pygame_gui before importing mainmenu
import sys
sys.modules['pygame_gui'] = MagicMock()
sys.modules['pygame_gui.elements'] = MagicMock()
sys.modules['pygame_gui.elements.UIButton'] = MagicMock()
sys.modules['pygame_gui.UIManager'] = MagicMock()

from ecs import World, Component, System
from game import Game
from mainmenu import Main_menu
from scrollex import ScrollexGame
from gameover import GameOver
from components import Mob, Player, Position, Velocity, Rotation, Lifetime, GameState, Bullet, Collision, Loot, PlayerInput, Sprite
from systems import MovementSystem, RotationSystem, PlayerControlSystem, CollisionSystem, LifetimeSystem, LootSystem, RenderSystem
from utils import Button, draw_text, WIN_WIDTH, WIN_HEIGHT, BLACK, WHITE, img_dir, path
from pausemenu import Pause_menu

# --- ECS Tests ---

class TestECS(unittest.TestCase):
    def setUp(self):
        self.world = World()

    def test_create_entity(self):
        entity_id = self.world.create_entity()
        self.assertIn(entity_id, self.world.entities)
        self.assertEqual(len(self.world.entities), 1)

    def test_create_entity_with_components(self):
        pos = Position(0, 0)
        entity_id = self.world.create_entity(pos)
        self.assertIn(entity_id, self.world.entities)
        self.assertIn(Position, self.world.entities[entity_id])
        self.assertEqual(self.world.get_component(entity_id, Position), pos)

    def test_remove_entity(self):
        entity_id = self.world.create_entity()
        self.world.remove_entity(entity_id)
        self.assertIn(entity_id, self.world.entities_to_remove)
        self.world.cleanup_entities()
        self.assertNotIn(entity_id, self.world.entities)

    def test_add_component(self):
        entity_id = self.world.create_entity()
        pos = Position(10, 20)
        self.world.add_component(entity_id, pos)
        self.assertIn(Position, self.world.entities[entity_id])
        self.assertEqual(self.world.get_component(entity_id, Position), pos)

    def test_remove_component(self):
        entity_id = self.world.create_entity()
        pos = Position(10, 20)
        self.world.add_component(entity_id, pos)
        self.world.remove_component(entity_id, Position)
        self.assertNotIn(Position, self.world.entities[entity_id])

    def test_get_component(self):
        entity_id = self.world.create_entity()
        pos = Position(10, 20)
        self.world.add_component(entity_id, pos)
        retrieved_pos = self.world.get_component(entity_id, Position)
        self.assertEqual(retrieved_pos.x, 10)
        self.assertEqual(retrieved_pos.y, 20)

    def test_get_entities_with_components(self):
        e1 = self.world.create_entity(Position(0,0), Velocity(1,1))
        e2 = self.world.create_entity(Position(10,10))
        e3 = self.world.create_entity(Position(20,20), Velocity(2,2))

        entities_with_pos_vel = list(self.world.get_entities_with_components(Position, Velocity))
        self.assertEqual(len(entities_with_pos_vel), 2)
        self.assertIn((e1, [self.world.get_component(e1, Position), self.world.get_component(e1, Velocity)]), entities_with_pos_vel)
        self.assertIn((e3, [self.world.get_component(e3, Position), self.world.get_component(e3, Velocity)]), entities_with_pos_vel)

    def test_add_system(self):
        system = MovementSystem()
        self.world.add_system(system)
        self.assertIn(system, self.world.systems)
        self.assertEqual(system.world, self.world)

    def test_process_update_systems(self):
        pos = Position(0, 0)
        vel = Velocity(1, 1)
        self.world.create_entity(pos, vel)
        movement_system = MovementSystem()
        self.world.add_system(movement_system)
        movement_system.process(1) # Directly call process
        self.assertEqual(pos.x, 1)
        self.assertEqual(pos.y, 1)

    def test_process_render_systems(self):
        render_system = RenderSystem(Mock())
        self.world.add_system(render_system)
        with patch.object(render_system, 'process') as mock_process:
            self.world.process_render()
            mock_process.assert_called_once()

    def test_process_update_does_not_call_render_system(self):
        render_system = RenderSystem(Mock())
        self.world.add_system(render_system)
        with patch.object(render_system, 'process') as mock_process:
            self.world.process_update()
            mock_process.assert_not_called()

# --- Game Tests ---

class TestGame(unittest.TestCase):
    def setUp(self):
        self.mock_screen = Mock()
        self.game = Game(self.mock_screen)

    def test_initialization(self):
        self.assertEqual(self.game.screen, self.mock_screen)
        self.assertTrue(self.game.running)
        self.assertFalse(self.game.setPause)
        self.assertIsNone(self.game.active)
        self.assertEqual(self.game.parent, self.game)

    def test_set_pause(self):
        self.game.SetPause(True)
        self.assertFalse(self.game.running)
        pygame.mixer.music.pause.assert_called_once()

    def test_add_entity(self):
        mock_entity = Mock()
        self.game.add(mock_entity)
        self.assertIn(mock_entity, self.game.entity)
        self.assertTrue(mock_entity.setPause)

    @patch('game.Game')
    def test_start_new_entity(self, MockGameClass):
        mock_new_game_state = MockGameClass.return_value
        mock_new_game_state.init = Mock()
        mock_new_game_state.GetPaused = Mock(return_value=False)

        self.game.start(MockGameClass) # Pass the mocked class

        self.assertEqual(self.game.active, mock_new_game_state)
        self.assertEqual(mock_new_game_state.parent, self.game)
        self.assertTrue(mock_new_game_state.running)
        mock_new_game_state.init.assert_called_once()

    def test_start_existing_entity(self):
        mock_existing_game_state = Mock(spec=Game)
        mock_existing_game_state.init = Mock()
        mock_existing_game_state.GetPaused = Mock(return_value=False)
        self.game.add(mock_existing_game_state)

        # Patch getEntity to return the existing mock
        with patch.object(self.game, 'getEntity', return_value=mock_existing_game_state):
            self.game.start(Mock()) # Pass any mock class, as getEntity is patched

        self.assertEqual(self.game.active, mock_existing_game_state)
        self.assertTrue(mock_existing_game_state.running)
        mock_existing_game_state.init.assert_called_once()

    def test_update_loop(self):
        mock_child_game = Mock()
        mock_child_game.running = True
        mock_child_game.update = Mock()
        self.game.add(mock_child_game)
        self.game.update()
        mock_child_game.update.assert_called_once_with(self.game.dt)

    def test_draw_loop(self):
        mock_child_game = Mock()
        mock_child_game.running = True
        mock_child_game.draw = Mock()
        self.game.add(mock_child_game)
        self.game.draw()
        mock_child_game.draw.assert_called_once()
        pygame.display.flip.assert_called_once()

# --- Main_menu Tests ---

class TestMainMenu(unittest.TestCase):
    def setUp(self):
        pygame.mixer.music.reset_mock()
        self.mock_screen = Mock()
        # Mock pygame_gui.UIManager constructor directly
        with patch('pygame_gui.UIManager') as MockUIManager:
            self.main_menu = Main_menu(self.mock_screen)
            self.main_menu.manager = MockUIManager.return_value
            # Mock the parent and its SetPause method
            self.main_menu.parent = Mock()
            self.main_menu.parent.SetPause = Mock()

    def test_initialization(self):
        self.assertIsNotNone(self.main_menu.background)
        self.assertIsNotNone(self.main_menu.background_rect)
        self.assertIsNotNone(self.main_menu.manager)
        self.assertIsNotNone(self.main_menu.start_button)
        self.assertIsNotNone(self.main_menu.quit_button)

    def test_init_music(self):
        self.main_menu.init()
        pygame.mixer.music.load.assert_called_once()
        pygame.mixer.music.set_volume.assert_called_once_with(0.12)
        pygame.mixer.music.play.assert_called_once_with(loops=-1, fade_ms=2000)

    def test_draw(self):
        self.main_menu.draw()
        self.mock_screen.blit.assert_called_once_with(self.main_menu.background, self.main_menu.background_rect)
        self.main_menu.manager.draw_ui.assert_called_once_with(self.mock_screen)

    def test_update_quit_event(self):
        mock_event = Mock()
        mock_event.type = pygame.QUIT
        pygame.event.get.return_value = [mock_event]

        self.main_menu.update(16) # dt value

        self.assertFalse(self.main_menu.running)
        self.main_menu.parent.SetPause.assert_called_once()
        self.main_menu.manager.process_events.assert_called_once_with(mock_event)
        self.main_menu.manager.update.assert_called_once_with(16)

    def test_update_start_button_event(self):
        mock_event = Mock()
        mock_event.type = pygame.USEREVENT
        mock_event.user_type = sys.modules['pygame_gui'].UI_BUTTON_PRESSED # Use mocked constant
        mock_event.ui_element = self.main_menu.start_button
        pygame.event.get.return_value = [mock_event]

        self.main_menu.update(16)

        self.main_menu.parent.start.assert_called_once()
        self.main_menu.manager.process_events.assert_called_once_with(mock_event)
        self.main_menu.manager.update.assert_called_once_with(16)

    def test_update_quit_button_event(self):
        mock_event = Mock()
        mock_event.type = pygame.USEREVENT
        mock_event.user_type = sys.modules['pygame_gui'].UI_BUTTON_PRESSED # Use mocked constant
        mock_event.ui_element = self.main_menu.quit_button
        pygame.event.get.return_value = [mock_event]

        self.main_menu.update(16)

        self.assertFalse(self.main_menu.running)
        self.main_menu.parent.SetPause.assert_called_once()
        self.main_menu.manager.process_events.assert_called_once_with(mock_event)
        self.main_menu.manager.update.assert_called_once_with(16)

class TestGameFlow(unittest.TestCase):
    @patch('pygame.Surface', return_value=Mock(convert_alpha=Mock(return_value=Mock()), get_rect=Mock()))
    @patch('pygame.mouse.get_pressed', return_value=(0, 0, 0))
    @patch('pygame.key.get_pressed', return_value=[0]*300)
    @patch('pygame.transform.scale')
    @patch('scrollex.spritesheet')
    @patch('pygame.image.load')
    @patch('pygame.draw.circle')
    def test_play_lose_restart(self, mock_draw_circle, mock_image_load, mock_spritesheet, mock_transform_scale, mock_key_get_pressed, mock_mouse_get_pressed, mock_surface):
        # Setup mocks
        mock_surface.get_rect.return_value = pygame.Rect(0, 0, 10, 10)
        mock_image_load.return_value = mock_surface
        mock_transform_scale.return_value = mock_surface
        mock_spritesheet_instance = mock_spritesheet.return_value
        mock_spritesheet_instance.images_slice.return_value = [mock_surface for _ in range(25)]

        # Initialize game
        mock_screen = Mock()
        game = Game(mock_screen)
        game.add(Main_menu(mock_screen))
        game.add(ScrollexGame(mock_screen))
        game.add(GameOver(mock_screen, score=0))

        # 1. Start the game from the main menu
        game.start(Main_menu)
        self.assertIsInstance(game.active, Main_menu)

        # Simulate clicking the start button
        main_menu = game.getEntity(Main_menu)
        with patch.object(main_menu.parent, 'start') as mock_start:
            mock_event = Mock()
            mock_event.type = pygame.USEREVENT
            mock_event.user_type = sys.modules['pygame_gui'].UI_BUTTON_PRESSED
            mock_event.ui_element = main_menu.start_button
            pygame.event.get.return_value = [mock_event]
            with patch('pygame.event.get', return_value=[mock_event]): # Local patch
                main_menu.update(16)
            mock_start.assert_called_with(ScrollexGame, new_game=True)

        # 2. Transition to Scrollex and simulate gameplay
        game.start(ScrollexGame)
        self.assertIsInstance(game.active, ScrollexGame)
        scrollex_game = game.active

        # Simulate destroying a few asteroids
        for _ in range(5):
            mobs_before = len(list(scrollex_game.world.get_entities_with_components(Mob)))
            scrollex_game.world.process_update(16) # Let mobs spawn
            mobs_after = len(list(scrollex_game.world.get_entities_with_components(Mob)))
            if mobs_after > mobs_before:
                mob_entity_id, _ = next(scrollex_game.world.get_entities_with_components(Mob))
                scrollex_game.world.remove_entity(mob_entity_id)
                scrollex_game.world.cleanup_entities()


        # 3. Simulate player death
        player_entity_id, _ = next(scrollex_game.world.get_entities_with_components(Player))
        scrollex_game.world.remove_entity(player_entity_id)
        scrollex_game.world.cleanup_entities()
        scrollex_game.update(16) # Update to trigger game over

        # 4. Transition to GameOver
        self.assertIsInstance(game.active, GameOver)

        # 5. Restart the game from the game over screen
        game_over_screen = game.active
        with patch.object(game_over_screen.parent, 'start') as mock_start:
            mock_event = Mock()
            mock_event.type = pygame.KEYUP
            mock_event.key = pygame.K_RETURN
            pygame.event.get.return_value = [mock_event]
            with patch('pygame.event.get', return_value=[mock_event]): # Local patch
                game_over_screen.update(16)
            mock_start.assert_called_with(Main_menu)

        # 6. Back to Main Menu
        game.start(Main_menu)
        self.assertIsInstance(game.active, Main_menu)


# --- Pause_menu Tests ---

class TestPauseMenu(unittest.TestCase):
    def setUp(self):
        self.mock_screen = Mock()
        with patch('pygame_gui.UIManager') as MockUIManager:
            self.pause_menu = Pause_menu(self.mock_screen)
            self.pause_menu.manager = MockUIManager.return_value
            self.pause_menu.parent = Mock()
            self.pause_menu.parent.getEntity.return_value = Mock(spec=ScrollexGame) # Mock ScrollexGame instance

    def test_initialization(self):
        self.assertFalse(self.pause_menu.running)
        self.assertIsNotNone(self.pause_menu.background)
        self.assertIsNotNone(self.pause_menu.background_rect)
        self.assertIsNotNone(self.pause_menu.manager)
        self.assertIsNotNone(self.pause_menu.resume_button)
        self.assertIsNotNone(self.pause_menu.quit_button)

    def test_draw(self):
        self.pause_menu.draw()
        self.pause_menu.manager.draw_ui.assert_called_once_with(self.mock_screen)

    def test_update_quit_event(self):
        mock_event = Mock()
        mock_event.type = pygame.QUIT
        pygame.event.get.return_value = [mock_event]

        self.pause_menu.update(16)

        self.assertFalse(self.pause_menu.running)
        self.assertFalse(self.pause_menu.parent.running)
        self.pause_menu.manager.process_events.assert_called_once_with(mock_event)
        self.pause_menu.manager.update.assert_called_once_with(16)

    def test_update_resume_button_event(self):
        mock_event = Mock()
        mock_event.type = pygame.USEREVENT
        mock_event.user_type = sys.modules['pygame_gui'].UI_BUTTON_PRESSED
        mock_event.ui_element = self.pause_menu.resume_button
        pygame.event.get.return_value = [mock_event]

        self.pause_menu.update(16)

        self.assertFalse(self.pause_menu.running)
        self.pause_menu.parent.getEntity.assert_called_once_with(ScrollexGame)
        self.assertEqual(self.pause_menu.parent.active, self.pause_menu.parent.getEntity.return_value)
        self.pause_menu.manager.process_events.assert_called_once_with(mock_event)
        self.pause_menu.manager.update.assert_called_once_with(16)

    def test_update_quit_main_menu_button_event(self):
        mock_event = Mock()
        mock_event.type = pygame.USEREVENT
        mock_event.user_type = sys.modules['pygame_gui'].UI_BUTTON_PRESSED
        mock_event.ui_element = self.pause_menu.quit_button
        pygame.event.get.return_value = [mock_event]

        self.pause_menu.update(16)

        self.assertFalse(self.pause_menu.running)
        self.pause_menu.parent.start.assert_called_once_with(Main_menu)
        self.pause_menu.manager.process_events.assert_called_once_with(mock_event)
        self.pause_menu.manager.update.assert_called_once_with(16)


# --- GameOver Tests ---

class TestGameOver(unittest.TestCase):
    def setUp(self):
        self.mock_screen = Mock()
        self.score = 123
        with patch('pygame_gui.UIManager') as MockUIManager:
            self.game_over = GameOver(self.mock_screen, self.score)
            self.game_over.manager = MockUIManager.return_value
            self.game_over.parent = Mock()

    def test_initialization(self):
        self.assertFalse(self.game_over.running)
        self.assertEqual(self.game_over.score, self.score)
        self.assertIsNotNone(self.game_over.background)
        self.assertIsNotNone(self.game_over.background_rect)
        self.assertIsNotNone(self.game_over.manager)
        self.assertIsNotNone(self.game_over.newgame_button)

    @patch('gameover.draw_text')
    def test_draw(self, mock_draw_text):
        self.game_over.draw()
        self.mock_screen.blit.assert_called_once_with(self.game_over.background, self.game_over.background_rect)
        mock_draw_text.assert_any_call(self.mock_screen, "GAME OVER", 64, WIN_WIDTH / 2, WIN_HEIGHT / 4)
        mock_draw_text.assert_any_call(self.mock_screen, f"Score: {self.score}", 22, WIN_WIDTH / 2, WIN_HEIGHT / 2)
        self.game_over.manager.draw_ui.assert_called_once_with(self.mock_screen)

    def test_update_quit_event(self):
        mock_event = Mock()
        mock_event.type = pygame.QUIT
        pygame.event.get.return_value = [mock_event]

        self.game_over.update(16)

        self.assertFalse(self.game_over.running)
        self.assertFalse(self.game_over.parent.running)
        self.game_over.manager.process_events.assert_called_once_with(mock_event)
        self.game_over.manager.update.assert_called_once_with(16)

    def test_update_key_return_event(self):
        mock_event = Mock()
        mock_event.type = pygame.KEYUP
        mock_event.key = pygame.K_RETURN
        pygame.event.get.return_value = [mock_event]

        self.game_over.update(16)

        self.assertFalse(self.game_over.running)
        self.game_over.parent.start.assert_called_once_with(Main_menu)
        self.game_over.manager.process_events.assert_called_once_with(mock_event)
        self.game_over.manager.update.assert_called_once_with(16)

    def test_update_new_game_button_event(self):
        mock_event = Mock()
        mock_event.type = pygame.USEREVENT
        mock_event.user_type = sys.modules['pygame_gui'].UI_BUTTON_PRESSED
        mock_event.ui_element = self.game_over.newgame_button
        pygame.event.get.return_value = [mock_event]

        self.game_over.update(16)

        self.assertFalse(self.game_over.running)
        self.game_over.parent.start.assert_called_once_with(Main_menu)
        self.game_over.manager.process_events.assert_called_once_with(mock_event)
        self.game_over.manager.update.assert_called_once_with(16)


# --- Systems Tests ---

class TestMovementSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.movement_system = MovementSystem()
        self.world.add_system(self.movement_system)

    def test_process_updates_position(self):
        pos = Position(0, 0)
        vel = Velocity(1, 2)
        self.world.create_entity(pos, vel)
        self.movement_system.process(1000) # dt = 1000ms
        self.assertEqual(pos.x, 1000)
        self.assertEqual(pos.y, 2000)

class TestRotationSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.rotation_system = RotationSystem()
        self.world.add_system(self.rotation_system)

    def test_process_updates_angle(self):
        rot = Rotation(angle=0, speed=0.1)
        self.world.create_entity(rot)
        self.rotation_system.process(1000) # dt = 1000ms
        self.assertEqual(rot.angle, 100.0)

    def test_process_angle_wraps_around(self):
        rot = Rotation(angle=350, speed=0.1)
        self.world.create_entity(rot)
        self.rotation_system.process(200) # dt = 200ms, 350 + 20 = 370, should be 10
        self.assertEqual(rot.angle, 10.0)

class TestPlayerControlSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.player_control_system = PlayerControlSystem()
        self.world.add_system(self.player_control_system)
        self.mock_get_pressed_keys = patch('pygame.key.get_pressed', return_value=[0]*300).start()
        self.mock_get_pressed_mouse = patch('pygame.mouse.get_pressed', return_value=(0, 0, 0)).start()
        self.addCleanup(patch.stopall)
        self.player_entity_id = self.world.create_entity(
            Position(WIN_WIDTH / 2, WIN_HEIGHT - 50),
            Velocity(),
            PlayerInput(),
            Player()
        )
        self.player_pos = self.world.get_component(self.player_entity_id, Position)
        self.player_vel = self.world.get_component(self.player_entity_id, Velocity)
        self.player_comp = self.world.get_component(self.player_entity_id, Player)

    def test_shield_recharge(self):
        self.player_comp.shield = 5.0
        self.player_comp.max_shield = 10.0
        self.player_comp.shield_recharge_rate = 1.0 # 1 point per second
        self.player_control_system.process(1000) # dt = 1000ms
        self.assertEqual(self.player_comp.shield, 6.0)

    def test_shield_does_not_exceed_max(self):
        self.player_comp.shield = 9.5
        self.player_comp.max_shield = 10.0
        self.player_comp.shield_recharge_rate = 1.0 # 1 point per second
        self.player_control_system.process(1000) # dt = 1000ms
        self.assertEqual(self.player_comp.shield, 10.0)

    def test_speed_clamping(self):
        self.player_vel.dx = 1.0
        self.player_vel.dy = 1.0
        self.player_comp.max_speed = 0.5
        self.player_control_system.process(16) # dt = 16ms
        speed = (self.player_vel.dx**2 + self.player_vel.dy**2)**0.5
        self.assertLessEqual(speed, self.player_comp.max_speed + 0.001) # Allow for float precision

class TestCollisionSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.mock_explosion_anim = {'sm': [Mock(), Mock()]}
        self.mock_expl_sounds = [Mock()]
        self.mock_meteor_images = [Mock()]
        self.mock_hit_sounds = [Mock()]
        self.collision_system = CollisionSystem(self.mock_explosion_anim, self.mock_expl_sounds, self.mock_meteor_images, self.mock_hit_sounds)
        self.world.add_system(self.collision_system)

    @patch('systems.CollisionSystem.create_explosion')
    @patch('systems.CollisionSystem.create_hit_particles')
    def test_bullet_mob_collision(self, mock_create_hit_particles, mock_create_explosion):
        mob_id = self.world.create_entity(Position(0, 0), Collision(10), Mob(type='small', health=1), Velocity(), Rotation())
        bullet_id = self.world.create_entity(Position(0, 0), Collision(5), Bullet(damage=1))

        print(f"Before process - Bullet {bullet_id} exists: {self.world.get_component(bullet_id, Bullet) is not None}")
        print(f"Before process - Mob {mob_id} exists: {self.world.get_component(mob_id, Mob) is not None}")

        self.collision_system.process(16)
        self.world.cleanup_entities()

        print(f"After cleanup - Bullet {bullet_id} exists: {self.world.get_component(bullet_id, Bullet) is not None}")
        print(f"After cleanup - Mob {mob_id} exists: {self.world.get_component(mob_id, Mob) is not None}")

        self.assertNotIn(bullet_id, self.world.entities) # Bullet removed
        self.assertNotIn(mob_id, self.world.entities) # Mob removed
        mock_create_explosion.assert_called_once() # Explosion created
        mock_create_hit_particles.assert_called_once() # Hit particles created

class TestLifetimeSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.lifetime_system = LifetimeSystem()
        self.world.add_system(self.lifetime_system)

    def test_entity_removed_after_lifetime(self):
        entity_id = self.world.create_entity(Lifetime(time_to_live=100))

        print(f"Before process - Entity {entity_id} exists: {self.world.get_component(entity_id, Lifetime) is not None}")

        self.lifetime_system.process(101) # Pass dt > time_to_live
        self.world.cleanup_entities()

        print(f"After cleanup - Entity {entity_id} exists: {self.world.get_component(entity_id, Lifetime) is not None}")

        self.assertNotIn(entity_id, self.world.entities) # Entity should be removed

class TestLootSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.loot_system = LootSystem()
        self.world.add_system(self.loot_system)
        self.player_id = self.world.create_entity(Position(0, 0), Collision(10), PlayerInput())
        self.game_state_id = self.world.create_entity(GameState(score=0))
        self.game_state = self.world.get_component(self.game_state_id, GameState)

    def test_score_updates_on_loot_collision(self):
        loot_id = self.world.create_entity(Position(0, 0), Collision(5), Loot(type='scrap', value=10))
        self.loot_system.process(16)
        self.world.cleanup_entities()
        self.assertEqual(self.game_state.score, 10)
        self.assertIsNone(self.world.get_component(loot_id, Loot)) # Loot removed


# --- Utils Tests ---

class TestButton(unittest.TestCase):
    def setUp(self):
        self.button = Button(x=0, y=0, width=100, height=50, text="Test Button")

    def test_handle_event_click(self):
        mock_event = Mock()
        mock_event.type = pygame.MOUSEBUTTONUP
        mock_event.button = 1
        mock_event.pos = (50, 25) # Inside button rect
        self.assertTrue(self.button.handle_event(mock_event))

    def test_handle_event_no_click(self):
        mock_event = Mock()
        mock_event.type = pygame.MOUSEBUTTONUP
        mock_event.button = 1
        mock_event.pos = (150, 25) # Outside button rect
        self.assertFalse(self.button.handle_event(mock_event))

    def test_handle_event_wrong_event_type(self):
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN # Not a mouse button up event
        self.assertFalse(self.button.handle_event(mock_event))


if __name__ == '__main__':
    unittest.main()