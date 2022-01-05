import scrollex
from game import Game
from utils import *


class Pause_menu(Game):
    def __init__(self, screen):
        super().__init__(screen)
        self.background = pygame.image.load(
            path.join(img_dir, 'bg1920.jpg')).convert()
        self.background_rect = self.background.get_rect()
        self.manager = pygame_gui.UIManager((WIN_WIDTH, WIN_HEIGHT))
        self.resume_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIN_WIDTH/2-400/2, 375), (400, 80)),
                                                          text='Resume',
                                                          manager=self.manager)
        self.quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIN_WIDTH/2-400/2, 475), (400, 80)),
                                                        text='Quit',
                                                        manager=self.manager)

    def draw(self):
        self.screen.blit(self.background, self.background_rect)
        self.manager.draw_ui(self.screen)

    def update(self, dt):
        # держим цикл на правильной скорости
        #self.dt = self.clock.tick(60)/1000.0
        keystate = pygame.key.get_pressed()

        for event in pygame.event.get():
            # check for closing window

            if event.type == pygame.QUIT:
                self.runing = False
                self.parent.SetPause()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.resume_button:
                        self.parent.start(scrollex.Scrollex)
                    if event.ui_element == self.quit_button:
                        self.runing = False
                        self.parent.SetPause()
            self.manager.process_events(event)
        self.manager.update(dt)
