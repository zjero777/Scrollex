import pygame
import pygame_gui

from game import Game
from utils import *


class Pause_menu(Game):
    def __init__(self, screen):
        super().__init__(screen)
        self.running = False
        self.background = pygame.image.load(
            path.join(img_dir, 'bg1920.jpg')).convert()
        self.background_rect = self.background.get_rect()
        self.manager = pygame_gui.UIManager((WIN_WIDTH, WIN_HEIGHT))
        self.resume_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIN_WIDTH/2-400/2, 375), (400, 80)),
                                                          text='Resume',
                                                          manager=self.manager)
        self.quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIN_WIDTH/2-400/2, 475), (400, 80)),
                                                        text='Quit main menu',
                                                        manager=self.manager)

    def draw(self):
        # self.screen.blit(self.background, self.background_rect)
        self.manager.draw_ui(self.screen)

    def update(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.parent.running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.resume_button:
                        from scrollex import ScrollexGame
                        self.running = False
                        self.parent.active = self.parent.getEntity(ScrollexGame)
                    if event.ui_element == self.quit_button:
                        from mainmenu import Main_menu
                        self.running = False
                        self.parent.start(Main_menu)

            self.manager.process_events(event)
        self.manager.update(dt)
