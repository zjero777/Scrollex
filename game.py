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
        self.running = not pause_state # Added this line
        if self.paused:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

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
        if game.GetPaused():
            for i in self.entity:
                if i != Game and i != game:
                    i.SetPause(True)
        game.init()

    def getEntity(self, entity):
        for i in self.entity:
            if i.__class__ == entity:
                return i

    def update(self):
        self.dt = self.clock.tick(FPS)
        for entity in self.entity:
            if entity.running:
                entity.update(self.dt)

    def draw(self):
        for entity in self.entity:
            if entity.running:
                entity.draw()
        pygame.display.flip()