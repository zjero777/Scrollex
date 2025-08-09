import pygame
import pygame_gui

from game import Game
from scrollex import ScrollexGame
from gameconst import *


class Main_menu(Game):
    def __init__(self, screen):
        super().__init__(screen)
        self.background = pygame.image.load(
            path.join(img_dir, 'bg1920.jpg')).convert()
        self.background_rect = self.background.get_rect()

        self.manager = pygame_gui.UIManager((WIN_WIDTH, WIN_HEIGHT))
        self.start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIN_WIDTH/2-400/2, 375), (400, 80)),
                                                         text='Start',
                                                         manager=self.manager)
        self.quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIN_WIDTH/2-400/2, 475), (400, 80)),
                                                        text='Quit',
                                                        manager=self.manager)

    def init(self):
        pygame.mixer.music.load(path.join(snd_dir, 'Flying me softly.mp3'))
        pygame.mixer.music.set_volume(0.12)
        pygame.mixer.music.play(loops=-1, fade_ms=2000)

    def draw(self):
        self.screen.blit(self.background, self.background_rect)
        self.manager.draw_ui(self.screen)

    def update(self, dt):
        # print("Updating Main_menu")
        # держим цикл на правильной скорости
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                self.running = False
                self.parent.SetPause(True) # Changed from self.parent.running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.start_button:
                        # init and start main game
                        self.parent.start(ScrollexGame, new_game=True)
                        self.running = False
                    if event.ui_element == self.quit_button:
                        self.running = False
                        self.parent.SetPause(True) # Changed from self.parent.running = False
            self.manager.process_events(event)
        self.manager.update(dt)
