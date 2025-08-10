import pygame
import pygame_gui
from game import Game
from utils import draw_text, WIN_WIDTH, WIN_HEIGHT, BLACK, Button, img_dir, path, snd_dir


class GameOver(Game):
    def __init__(self, screen, score):
        super().__init__(screen)
        self.running = False
        self.score = score
        self.background = pygame.image.load(
            path.join(img_dir, 'bg1920.jpg')).convert()
        self.background_rect = self.background.get_rect()
        self.manager = pygame_gui.UIManager((WIN_WIDTH, WIN_HEIGHT))
        self.newgame_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIN_WIDTH / 2-100, WIN_HEIGHT * 3 / 4), (200, 80)),
                                                          text='New Game',
                                                          manager=self.manager)
        
    def init(self):
        pygame.mixer.music.load(path.join(snd_dir, 'Deep Space Destructors - From The Ashes.mp3'))
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(loops=-1, fade_ms=1000)

    def draw(self):
        self.screen.blit(self.background, self.background_rect)

        draw_text(self.screen, "GAME OVER", 64, WIN_WIDTH / 2, WIN_HEIGHT / 4)
        draw_text(self.screen, f"Score: {self.score}", 22, WIN_WIDTH / 2, WIN_HEIGHT / 2)
        self.manager.draw_ui(self.screen)
        

    def update(self, dt, events):
        from mainmenu import Main_menu

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                self.parent.running = False
            if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
                print("RETURN key pressed in GameOver screen!")
                pygame.mixer.music.stop()
                self.running = False
                self.parent.start(Main_menu)
                
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.newgame_button:
                        pygame.mixer.music.stop()
                        self.running = False
                        self.parent.start(Main_menu)

            self.manager.process_events(event)
        self.manager.update(dt)