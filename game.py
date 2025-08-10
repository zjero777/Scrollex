from utils import *

class Game(object):

    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.entity = []
        self.load_music = False
        self.setPause = False
        self.active = None # Changed from self to None
        self.parent = self
        self.clock = pygame.time.Clock()
        self.paused = False

    def init(self):
        pass

    def GetPaused(self):
        return self.paused

    def SetPause(self, pause_state):
        self.paused = pause_state

    def add(self, game, setPause=True):
        self.entity.append(game)
        game.setPause = setPause

    def start(self, entity, new_game=False, **kwargs):
        # print(f"Starting {entity.__name__}")
        from gameover import GameOver # Import GameOver locally to break circular dependency

        if new_game or entity == GameOver: # Always create new instance for GameOver
            for i, e in enumerate(self.entity):
                if isinstance(e, entity):
                    self.entity.pop(i)
                    break
            game = entity(self.screen, **kwargs)
            self.add(game)
        else:
            game = self.getEntity(entity)
            if not game:
                game = entity(self.screen, **kwargs)
                self.add(game)

        game.running = True
        self.active = game
        self.active.parent = self
        self.active.init()
        if game.GetPaused():
            for i in self.entity:
                if i != Game and i != game:
                    i.SetPause(True)

    def getEntity(self, entity):
        for i in self.entity:
            if i.__class__ == entity:
                return i

    def update(self):
        self.dt = self.clock.tick(FPS)
        events = pygame.event.get()
        if self.active and self.active.running:
            self.active.update(self.dt, events)

    def draw(self):
        from scrollex import ScrollexGame
        if self.paused:
            game_instance = self.getEntity(ScrollexGame)
            if game_instance:
                game_instance.draw()
        
        if self.active and self.active.running:
            self.active.draw()

        pygame.display.flip()