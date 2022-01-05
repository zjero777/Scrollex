from utils import *

class Game(object):

    def __init__(self, screen):
        self.screen = screen
        self.runing = True
        self.entity = []
        self.load_music = False
        self.setPause = False
        self.active = self
        self.parent = self
        self.clock = pygame.time.Clock()
        

    def init(self):
        pass

    def GetPaused(self):
        return(self.setPause)

    def SetPause(self):
        self.runing = False
        #pygame.mixer.music.fadeout(2000)
        pygame.mixer.music.pause()

    def add(self, game, setPause=True):
        self.entity.append(game)
        game.setPause = setPause

    def start(self, entity):
        game = self.getEntity(entity)
        game.runing = True
        self.active = game
        self.active.parent = self
        if game.GetPaused():
            for i in self.entity:
                if i != Game and i != game:
                    i.SetPause()
        game.init()

    def getEntity(self, entity):
        for i in self.entity:
            if i.__class__ == entity:
                return i

    def update(self):
        # self.dt = pygame.time.get_ticks()/1000.0
        self.dt = self.clock.tick(FPS)
        # realfps=self.clock.get_fps()
        # self.dt = self.clock.tick(FPS)/1000.0
        #print(f'FPS:{realfps} dt:{self.dt} = {FPS*self.dt}')
        for i in self.entity:
            if i.runing:
                i.update(self.dt)

    def draw(self):
        for i in self.entity:
            if i.runing:
                i.draw()
        # после отрисовки всего, переворачиваем экран
        pygame.display.flip()

