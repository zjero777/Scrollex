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
pygame.image.load = Mock(return_value=Mock(convert=Mock(), get_rect=Mock()))
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
from scrollex import Scrollex
from gameover import GameOver
from components import Mob, Player

# --- ECS Tests ---

class Position(Component):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Velocity(Component):
    def __init__(self, vx, vy):
        self.vx = vx
        self.vy = vy

class MovementSystem(System):
    def process(self):
        for entity_id, (pos, vel) in self.world.get_entities_with_components(Position, Velocity):
            pos.x += vel.vx
            pos.y += vel.vy

class RenderSystem(System):
    is_render_system = True
    def process(self):
        pass # Mock rendering

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
        self.world.process_update()
        self.assertEqual(pos.x, 1)
        self.assertEqual(pos.y, 1)

    def test_process_render_systems(self):
        render_system = RenderSystem()
        self.world.add_system(render_system)
        with patch.object(render_system, 'process') as mock_process:
            self.world.process_render()
            mock_process.assert_called_once()

    def test_process_update_does_not_call_render_system(self):
        render_system = RenderSystem()
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
        self.assertEqual(self.game.active, self.game)
        self.assertEqual(self.game.parent, self.game)

    def test_set_pause(self):
        self.game.SetPause()
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
        mock_child_game = Mock(spec=Game)
        mock_child_game.running = True
        mock_child_game.update = Mock()
        self.game.add(mock_child_game)
        self.game.update()
        mock_child_game.update.assert_called_once_with(self.game.dt)

    def test_draw_loop(self):
        mock_child_game = Mock(spec=Game)
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
    @patch('pygame.mouse.get_pressed', return_value=(0, 0, 0))
    @patch('pygame.key.get_pressed', return_value=[0]*300)
    @patch('pygame.transform.scale')
    @patch('scrollex.spritesheet')
    @patch('pygame.image.load')
    def test_play_lose_restart(self, mock_image_load, mock_spritesheet, mock_transform_scale, mock_key_get_pressed, mock_mouse_get_pressed):
        # Setup mocks
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_surface.get_rect.return_value = pygame.Rect(0, 0, 10, 10)
        mock_image_load.return_value = mock_surface
        mock_transform_scale.return_value = mock_surface
        mock_spritesheet_instance = mock_spritesheet.return_value
        mock_spritesheet_instance.images_slice.return_value = [mock_surface for _ in range(25)]

        # Initialize game
        mock_screen = Mock()
        game = Game(mock_screen)
        game.add(Main_menu(mock_screen))
        game.add(Scrollex(mock_screen))
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
            main_menu.update(16)
            mock_start.assert_called_with(Scrollex)

        # 2. Transition to Scrollex and simulate gameplay
        game.start(Scrollex)
        self.assertIsInstance(game.active, Scrollex)
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
            pygame.event.get.return_value = [mock_event]
            game_over_screen.update(16)
            mock_start.assert_called_with(Main_menu)

        # 6. Back to Main Menu
        game.start(Main_menu)
        self.assertIsInstance(game.active, Main_menu)


if __name__ == '__main__':
    unittest.main()