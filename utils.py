import pygame
from gameconst import *
from os import path
import random

font_name = pygame.font.match_font('arial')

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group() 
bullets = pygame.sprite.Group() 

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


# This class handles sprite sheets
# This was taken from www.scriptefun.com/transcript-2-using
# sprite-sheets-and-drawing-the-background
# I've added some code to fail if the file wasn't found..
# Note: When calling images_at the rect is the format:
# (x, y, x + offset, y + offset)

class spritesheet(object):
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert_alpha()
        image.fill((0,0,0,0))
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)
    def images_slice(self, column, rows, colorkey = None):
        rect = self.sheet.get_rect()
        tups = [(rect[0]+rect[2]*y//column, rect[1]+rect[3]*x//rows, rect[2]//column, rect[3]//rows) for x in range(column) for y in range(rows)]
        #print(tups)
        return self.images_at(tups, colorkey)

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        draw_text(screen, self.text, 22, self.rect.centerx, self.rect.y + 10)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def load_explosion_animation():
    explosion_anim = {}
    explosion_anim['lg'] = []
    explosion_anim['sm'] = []
    explosion_sheet = spritesheet(path.join(img_dir, 'explosion_transparent.png'))
    for i in range(25):
        img = explosion_sheet.image_at((i % 5 * 64, i // 5 * 64, 64, 64))
        img_lg = pygame.transform.scale(img, (75, 75))
        explosion_anim['lg'].append(img_lg)
        img_sm = pygame.transform.scale(img, (32, 32))
        explosion_anim['sm'].append(img_sm)
    return explosion_anim

def create_starfield(width, height, num_stars, color, size_range):
    stars = pygame.Surface((width, height), pygame.SRCALPHA)
    for _ in range(num_stars):
        x = random.randrange(width)
        y = random.randrange(height)
        size = random.uniform(size_range[0], size_range[1])
        pygame.draw.circle(stars, color, (x, y), size)
    return stars