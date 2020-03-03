import pygame
import random
import time
import json

from Vector2 import Vector2
from Board import PixelBoard


with open("config.json") as f:
    conf = json.load(f)


# Define Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BG_COLOR = [44] * 3
GRID_COLOR = [22] * 3
CURSOR_COLOR = [255, 127, 0]

# Configuration
DEBUG = conf['debug']

GRID_SIZE = conf['grid_size']
SCREEN_SIZE = Vector2(conf['screen_x'], conf['screen_y'])
SCREEN_SIZE.x = int(SCREEN_SIZE.x / GRID_SIZE) * GRID_SIZE
SCREEN_SIZE.y = int(SCREEN_SIZE.y / GRID_SIZE) * GRID_SIZE
GRID_RESOLUTION = Vector2(int(SCREEN_SIZE.x / GRID_SIZE), int(SCREEN_SIZE.y / GRID_SIZE))
BRUSH_SIZE = conf['brush_size']
print(f"Screen size: {SCREEN_SIZE.x} | {SCREEN_SIZE.y}")
print(f"Grid size: {GRID_RESOLUTION.x} | {GRID_RESOLUTION.y}")


FPS = conf['fps']

# Members
running = True
paused = False
recording = False

pixels = PixelBoard(GRID_RESOLUTION.x, GRID_RESOLUTION.y)
brush_size = BRUSH_SIZE

def screen_to_pixel_coordinates(screen_pos):
    return Vector2(int(screen_pos.x / GRID_SIZE), int(screen_pos.y / GRID_SIZE))

mousedown = False
mousepos_in_game_coo = None
clear = False

def process_input():
    global running
    global paused
    global mousedown
    global mousepos_in_game_coo
    global clear
    global brush_size
    global recording
    global DEBUG

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_F8]:
                running = False
            elif event.key in [pygame.K_RETURN]:
                update(True)
                # render()
            elif event.key in [pygame.K_r]:
                recording = not recording
                print(f"Recording: {recording}")
            elif event.key in [pygame.K_p, pygame.K_SPACE]:
                paused = not paused
            elif event.key in [pygame.K_BACKSPACE]:
                pixels.clear()
                # render()
            elif event.key in [pygame.K_TAB]:
                DEBUG = not DEBUG

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = Vector2(pygame.mouse.get_pos())
            mousepos_in_game_coo = screen_to_pixel_coordinates(pos)
            if event.button == pygame.BUTTON_LEFT:
                mousedown = True
                brush_draw_pixels(mousepos_in_game_coo) # Allow adding Pixel when paused
            elif event.button == pygame.BUTTON_RIGHT:
                clear = True
            elif event.button == pygame.BUTTON_WHEELUP:
                brush_size += 1
            elif event.button == pygame.BUTTON_WHEELDOWN:
                brush_size = max(1, brush_size - 1)


        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                mousedown = False
            elif event.button == pygame.BUTTON_RIGHT:
                clear = False

            mousepos_in_game_coo = None
        elif event.type == pygame.MOUSEMOTION:
            pos = Vector2(pygame.mouse.get_pos())
            mousepos_in_game_coo = screen_to_pixel_coordinates(pos)


def brush_draw_pixels(pos, clearing=False):
    radius = brush_size
    for y in range(-radius, radius + 1):
        for x in range(-radius, radius + 1):
            screen_x = pos.x + x
            screen_y = pos.y + y
            if 0 <= screen_x < GRID_RESOLUTION.x and 0 <= screen_y < GRID_RESOLUTION.y:
                if x*x + y*y < radius * radius: # Make round brush
                    if clearing:
                        f = pixels.get_pixel(screen_x, screen_y)
                        for p in f:
                            pixels.remove_pixel(p)
                    else:
                        spawn_pixel(Vector2(screen_x, screen_y))



tick_spawn_counter = 0
tick_spawn_duration = 3

def update(force = False):
    global tick_spawn_counter
    global tick_spawn_duration

    if force or not paused:
        if conf["water_running"]:
            tick_spawn_counter += 1

            if tick_spawn_counter >= tick_spawn_duration:
                tick_spawn_counter -= tick_spawn_duration

                pixels.add_pixel(Vector2(int(GRID_RESOLUTION.x * 0.5), 0))

        pixels.update()

        if DEBUG:
            pixels.check_orphans()

    if mousepos_in_game_coo != None:
        if clear:
            brush_draw_pixels(mousepos_in_game_coo, True)
        elif mousedown:
            brush_draw_pixels(mousepos_in_game_coo)

recording_counter = 0
def render():
    global recording_counter
    screen.fill(BG_COLOR)

    def draw_pixels():
        i = 0 # was pixel.id
        for pixel in pixels:
            #val = int((i / len(pixels)) * 127 + 100)
            val = int((i / len(pixels)) * 255)
            col = (0, 0, val)
            pygame.draw.rect(screen, col,(pixel.x * GRID_SIZE, pixel.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

            if DEBUG:
                if pixel.sleeping:
                    screen.blit(rect_outline, (pixel.x * GRID_SIZE, pixel.y * GRID_SIZE))
            i += 1

    # Overlay
    def draw_overlays():
        # Draw cursor
        pos = Vector2(pygame.mouse.get_pos())
        pos.x = int(pos.x / GRID_SIZE) * GRID_SIZE + int(GRID_SIZE*0.5)
        pos.y = int(pos.y / GRID_SIZE) * GRID_SIZE + int(GRID_SIZE*0.5)
        pygame.draw.circle(screen, CURSOR_COLOR, [pos.x, pos.y], brush_size * GRID_SIZE, 1)

    if DEBUG:
        draw_grid()

    draw_pixels()
    draw_overlays()

    pygame.display.flip()
    if recording:
        rec_id = str(recording_counter)
        rec_id = rec_id.zfill(5)
        pygame.image.save(screen, f"Recordings/recording_{rec_id}.png")
        recording_counter += 1



def _draw_initial_grid():
    for x in range(int(SCREEN_SIZE.x / GRID_SIZE)):
        pygame.draw.line(background, GRID_COLOR, (x * GRID_SIZE, 0), (x*GRID_SIZE, SCREEN_SIZE.y))

    for y in range(int(SCREEN_SIZE.y / GRID_SIZE)):
        pygame.draw.line(background, GRID_COLOR, (0, y * GRID_SIZE), (SCREEN_SIZE.x, y*GRID_SIZE))

def draw_grid():
    screen.blit(background, (0, 0))



def game_loop():
    while running:
        process_input()
        update()
        render()
        clock.tick(FPS)

def spawn_pixel(p):
    pixels.add_pixel(p.x, p.y)

pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((SCREEN_SIZE.x, SCREEN_SIZE.y))
pygame.display.set_caption(f"Fluid Simulation {SCREEN_SIZE.x}x{SCREEN_SIZE.y} - [{GRID_SIZE}]")
clock = pygame.time.Clock()     ## For syncing the FPS

# Surface blits
background = pygame.Surface((SCREEN_SIZE.x, SCREEN_SIZE.y), pygame.SRCALPHA, 32)
_draw_initial_grid()

rect_outline = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA, 32)
# col = [55] * 3
col = (127, 0, 127)
col = (0, 127, 0)
pygame.draw.rect(rect_outline, col, (0, 0, GRID_SIZE, GRID_SIZE), 1)


game_loop()
pygame.quit()
