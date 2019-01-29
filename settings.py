import pygame as pg
import itertools


# display settings
SCREEN_W = 1280
SCREEN_H = 960
RESOLUTIONS = [
        (1280, 960),
        (1024, 768),
        (800, 600)
        ]
DISPLAY_SIZE = RESOLUTIONS[0]
DISPLAY_W = DISPLAY_SIZE[0]
DISPLAY_H = DISPLAY_SIZE[1]
TILESIZE = 64
FPS = 60
GAME_SPEED = 1
FONT = 'Arial'

# gameplay settings
# MEMO make this a dict, these aren't constants
CAMERA_SPEED = 800
ALWAYS_SHOW_LIFEBARS = True

STARTING_MONEY = 1400
STARTING_LIVES = 40

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
TRANS = (0, 0, 0, 0)

vec = pg.math.Vector2
vec3 = pg.math.Vector3


class COLOR:
    red = vec3(RED)
    green = vec3(GREEN)
    yellow = vec3(YELLOW)
    
    
# configurations
mobs = {
        'standard': {
                'hitbox_size': (20, 20),
                'image': 'mob1',
                'hp': 10,
                'speed': 12,
                'reward': 10
                },
        'fast': {
                'hitbox_size': (20, 20),
                'image': 'mob2',
                'hp': 6,
                'speed': 28,
                'reward': 20
                },
        'heavy': {
                'hitbox_size': (20, 20),
                'image': 'mob3',
                'hp': 40,
                'speed': 6,
                'reward': 30
                },
        'boss': {
                'hitbox_size': (80, 80),
                'image': 'mob8',
                'hp': 260,
                'speed': 10,
                'reward': 500
                },
        }

waves = [{
            'type': 'standard',
            'number': 10,
            'starting_time': 1
        },
        {
            'type': 'standard',
            'number': 30,
            'starting_time': 15
        },
        {
            'type': 'fast',
            'number': 25,
            'starting_time': 30
        },
        {
            'type': 'heavy',
            'number': 20,
            'starting_time': 60
        },
        {
            'type': 'standard',
            'number': 40,
            'starting_time': 90
        },
        {
            'type': 'boss',
            'number': 1,
            'starting_time': 120
        },
        {
            'starting_time': 2000        
        }]

shooters = {
        'standard': {
                'size': (16, 16),
                'image': 'tower1',
                'base_image': 'towerbase1',
                'cooldown': 0.2,
                'perception_radius': 200,
                'projectile': 'Bullet',
                'damage': 1,
                'price': 200,
                'refund': 80
                },
        'machine_gun': {
                'size': (12, 12),
                'image': 'tower2',
                'base_image': 'towerbase2',
                'cooldown': 0.04,
                'perception_radius': 180,
                'projectile': 'Bullet',
                'damage': 0.5,
                'price': 800,
                'refund': 300
                },
        'anti_air': {
                'size': (12, 12),
                'image': 'tower3',
                'base_image': 'towerbase2',
                'cooldown': 3,
                'perception_radius': 500,
                'projectile': 'Rocket',
                'damage': 10,
                'price': 100,
                'refund': 0
                }
        }

shooter_it = itertools.cycle(list(shooters.keys()))