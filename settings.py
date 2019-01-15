import pygame as pg
import itertools


# display settings
DISPLAY_W = 1280
DISPLAY_H = 960
FPS = 60
GAME_SPEED = 1
FONT = 'Arial'

# gameplay settings
CAMERA_SPEED = 800
CAMERA_ZOOM = 1
TILESIZE = 64

STARTING_MONEY = 1400
STARTING_LIVES = 20

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
            'starting_time': 10
        },
        {
            'type': 'standard',
            'number': 30,
            'starting_time': 25
        },
        {
            'type': 'fast',
            'number': 20,
            'starting_time': 45
        },
        {
            'type': 'heavy',
            'number': 20,
            'starting_time': 60
        },
        {
            'type': 'standard',
            'number': 40,
            'starting_time': 80
        },
        {
            'type': 'boss',
            'number': 1,
            'starting_time': 100
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
                'price': 800,
                'refund': 300
                }
        }

shooter_it = itertools.cycle(list(shooters.keys()))