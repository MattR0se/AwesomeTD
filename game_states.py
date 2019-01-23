import pygame as pg
from random import randint, choice
from pytmx.util_pygame import load_pygame
#import traceback

import sprites as spr
import settings as st
import maps as mp

vec = pg.math.Vector2


# PUT THIS ELSEWHERE?
class Wave(object):
    def __init__(self, game):
        self.game = game
        self.done = False
        self.counter = 0
        self.timer = 0
        self.delay = 0.3
    
    
    def spawn_wave(self, n, dt):
        pos = self.game.start_node.position + vec(0, randint(-1, 1))
        self.timer += dt
        
        if not self.done and self.timer > self.delay:
            self.timer = 0
            spr.Mob(self.game, pos, choice(self.game.paths), st.waves[n]['type'])
            self.counter += 1
            if self.counter >= st.waves[n]['number']:
                self.counter = 0
                self.done = True
    
    

class Camera(object):
    def __init__(self, game):
        self.game = game
        self.speed = st.CAMERA_SPEED
        self.offset = vec()
        self.move = vec()
        
    
    def update(self, dt):
        if pg.mouse.get_pressed()[1]:
            self.move *= 0
            for event in self.game.event_list:
                if event.type == pg.MOUSEMOTION:
                    self.move.x = event.rel[0]
                    self.move.y = event.rel[1]
                    self.move *= st.CAMERA_SPEED / 10000
        else:
            keys = pg.key.get_pressed()
            self.move.x = keys[pg.K_a] - keys[pg.K_d]
            self.move.y = keys[pg.K_w] - keys[pg.K_s]
            spr.limit(self.move, 1)
        
        self.offset += (int(self.move.x * self.speed * dt), 
                        int(self.move.y * self.speed * dt))
        
        # camera can't go over upper left borders
        self.offset.x = min(self.offset.x, 0)
        self.offset.y = min(self.offset.y, 0)
        # camera can't go over bottom right borders
        self.offset.x = max(self.offset.x, (self.game.map_rect.w - 
                                            self.game.screen_rect.w) * -1)
        self.offset.y = max(self.offset.y, (self.game.map_rect.h - 
                                            self.game.screen_rect.h) * -1)
        
    
    def apply_mouse(self, m_pos):
        return m_pos - self.offset
    

    def apply_pos(self, pos):
        return pos + self.offset


    def apply_rect(self, rect):
        return pg.Rect(rect.topleft + self.offset, rect.size)
    


class State(object):
    '''
    Parent class for game states
    '''
    def __init__(self, game):
        self.game = game
        self.done = False
        self.next = None
    
    def startup(self):
        pass
    
    def cleanup(self):
        self.done = False
        
    def update(self, dt):
        pass
    
    def draw(self, screen):
        pass
    


class Ingame(State):
    def __init__(self, game):
        super().__init__(game)
        self.next = 'Game_lost'
    
    
    def startup(self):
        super().startup()
        self.game.elapsed_seconds = 0
    
    
    def spawn_waves(self, game, dt):
        if game.elapsed_seconds >= st.waves[game.current_wave]['starting_time']:
            game.wave_spawner.spawn_wave(game.current_wave, dt)
            if game.wave_spawner.done:
                game.current_wave += 1
                game.wave_spawner.done = False
    
    
    def update(self, dt):
        self.game.all_sprites.update(dt)
        
        # place turret
        m_pos = self.game.camera.apply_mouse(self.game.mouse_pos)
        if self.game.mouse_pressed[0]:
            # prevent placement on a road
            road_hits = [x.rect.collidepoint(m_pos) for x in self.game.roads]
            if not 1 in road_hits:
                if self.game.money >= st.shooters[self.game.selected_shooter]['price']:
                    s = spr.Shooter(self.game, m_pos, self.game.selected_shooter)
                    # prevent placement on other towers
                    hits = pg.sprite.spritecollide(s, self.game.shooters, False)
                    for hit in hits:
                        if hit != s:
                            s.kill()
                            break
                    else:
                        self.game.money -= s.price          
        if self.game.mouse_pressed[2]:
            for s in self.game.shooters:
                if s.rect.collidepoint(m_pos):
                    self.game.money += s.refund
                    s.kill()
              
        # camera control
        self.game.camera.update(dt)

        self.spawn_waves(self.game, dt)
    
        # select a different tower
        if self.game.key_pressed == pg.K_t:
            self.game.selected_shooter = next(st.shooter_it)
        
        if self.game.lives <= 0:
            self.done = True
        
        # DEBUG STUFF
        if self.game.key_pressed == pg.K_h:
            self.game.debug_mode = not self.game.debug_mode
            
        if self.game.debug_mode:
            c = 'FPS: {}   DEBUG MODE ACTIVATED'.format(round(self.game.clock.get_fps(), 2))
        else:          
            c = 'FPS: {}'.format(round(self.game.clock.get_fps(), 2))
        pg.display.set_caption(c)
        
            


    def draw(self, screen):
        #self.game.camera.apply_rect(self.game.map_rect)
        screen.blit(self.game.bg_image, self.game.map_rect.topleft + self.game.camera.offset)
        self.game.draw_sprites(screen)
        # draw text on screen
        text = 'Money: {}'.format(self.game.money)
        txt_surf = self.game.font.render(text, False, st.WHITE)
        screen.blit(txt_surf, (10, 10))        
        
        seconds = int(self.game.elapsed_seconds % 60)
        minutes = int(self.game.elapsed_seconds / 60)
        text = 'Elapsed time: {x:02d}:{y:02d}'.format(x=minutes, y=seconds)
        txt_surf = self.game.font.render(text, False, st.WHITE)
        screen.blit(txt_surf, (160, 10))
        
        s_to_wave = (st.waves[self.game.current_wave]['starting_time'] 
                     - self.game.elapsed_seconds)
        s_to_wave = max(0, s_to_wave)
        seconds = int(s_to_wave % 60)
        minutes = int(s_to_wave / 60)
        text = 'Time until next wave: {x:02d}:{y:02d}'.format(
                x=minutes, y=seconds)
        txt_surf = self.game.font.render(text, False, st.WHITE)
        screen.blit(txt_surf, (360, 10))
        
        text = 'Lives: {}'.format(self.game.lives)
        txt_surf = self.game.font.render(text, False, st.WHITE)
        screen.blit(txt_surf, (680, 10))
               
        # draw a sample shooter
        r = st.shooters[self.game.selected_shooter]['perception_radius']
        radius_surf = pg.Surface((r * 2,r * 2), pg.SRCALPHA)
        radius_surf.fill(st.TRANS)
        pg.draw.ellipse(radius_surf, (20, 20, 20), radius_surf.get_rect())     
        sample_shooter = self.game.images[st.shooters[self.game.selected_shooter]['image']]
        size = sample_shooter.get_rect().size
        p = (self.game.mouse_pos.x - r, self.game.mouse_pos.y - r)
        screen.blit(radius_surf, p, special_flags=pg.BLEND_RGBA_SUB)       
        screen.blit(sample_shooter, self.game.mouse_pos - vec(size) / 2)
        
        self.draw_minimap(screen)
                    
        # DEBUG STUFF!!!!
        if self.game.debug_mode:
            camera = self.game.camera
            for s in self.game.shooters:
                if s.target:
                    start = camera.apply_pos(s.pos)
                    end =camera.apply_pos(s.pos + s.aim)
                    pg.draw.line(screen, st.WHITE, start, end)
                    
            for m in self.game.mobs:
                start = camera.apply_pos(m.pos)
                end = camera.apply_pos(m.pos + m.vel * 20)
                pg.draw.line(screen, st.WHITE, start, end, 2)
            
                if len(m.path) > 1:
                    path_ = list(map(lambda x: camera.apply_pos(x.position), m.path))
                    pg.draw.lines(screen, st.WHITE, False, path_)
                     
            # draw rects
            for sprite in self.game.all_sprites:
                if hasattr(sprite, 'hitbox'):
                    pg.draw.rect(screen, st.RED, self.game.camera.apply_rect(sprite.hitbox), 1)
            
            for road in self.game.roads:
                pg.draw.rect(screen, st.WHITE, self.game.camera.apply_rect(road.rect), 1)
                
    
    def draw_minimap(self, screen):
        map_w, map_h = 256, 200
        map_surf = pg.Surface((map_w, map_h), pg.SRCALPHA)
        map_surf.fill((0, 0, 0, 100))
        gm_w, gm_h = self.game.map_rect.size
        for mob in self.game.mobs:
            pos_x = int(mob.rect.x / gm_w * map_w)
            pos_y = int(mob.rect.y / gm_h * map_h)
            pg.draw.rect(map_surf, (180, 0, 0), ((pos_x, pos_y), (4, 4)))
        
        for shooter in self.game.shooters:
            pos_x = int(shooter.base_rect.x / gm_w * map_w)
            pos_y = int(shooter.base_rect.y / gm_h * map_h)
            pg.draw.rect(map_surf, (100, 200, 100), ((pos_x, pos_y), (6, 6)))
        
        # draw camera rect
        cam_p = self.game.camera.offset * -1
        pos_x = int(cam_p.x / gm_w * map_w)
        pos_y = int(cam_p.y / gm_h * map_h)
        w = int(st.DISPLAY_W / gm_w * map_w)
        h = int(st.DISPLAY_H / gm_h * map_h)
        pg.draw.rect(map_surf, (255, 255, 255), ((pos_x, pos_y), (w, h)), 1)
        
        screen.blit(map_surf, (st.DISPLAY_W - map_w - 10, 10))
        
    
    
class Game_lost(State):
    def __init__(self, game):
        super().__init__(game)
        self.next = 'Ingame'
    
    
    def startup(self):
        pg.mouse.set_visible(True)
        
        
    def update(self, dt):
        if self.game.key_pressed == pg.K_r:
            self.done = True
    
    
    def draw(self, screen):
        screen.blit(self.game.bg_image, (0, 0))
        self.game.all_sprites.draw(screen)
        
        # draw text on screen
        text = 'You lost the game :(   Press R to restart'
        txt_surf = self.game.font.render(text, False, st.WHITE)
        pos = (self.game.screen_rect.w // 2, self.game.screen_rect.h // 2)
        txt_rect = txt_surf.get_rect()
        txt_rect.center = pos
        screen.blit(txt_surf, txt_rect)
        
    
    def cleanup(self):
        super().cleanup()
        pg.mouse.set_visible(False)
        self.game.start()
        
        
        
class Start_screen(State):
    def __init__(self, game):
        super().__init__(game)
        self.next = 'Ingame'
        pg.time.wait(500)
        pg.event.wait()      
        self.options = ['New Game',
                   'Options',
                   'Exit']     
        self.options_pos = 0
        
        self.font = pg.font.SysFont('Arial', 40)
        self.font_bold = pg.font.SysFont('Arial', 52, bold=True)
    
    
    def update(self, dt):
        key = self.game.key_pressed
        if key == pg.K_s:
            self.options_pos = (self.options_pos + 1) % len(self.options)
        elif key == pg.K_w:
           self.options_pos = (self.options_pos - 1) % len(self.options)
        elif key == pg.K_RETURN:
            self.execute_option()

    
    def execute_option(self):
        if self.options_pos == 0:
            self.next = 'Ingame'
            pg.mouse.set_visible(False)
            self.done = True
        elif self.options_pos == 1:
            self.next = 'Options'
            self.done = True
        elif self.options_pos == 2:
            self.game.running = False
        
    
    def draw(self, screen):
        screen.blit(self.game.images['title_screen'], (0, 0)) 
            
        for i in range(len(self.options)):
            if self.options_pos == i:
                text_surface = self.font_bold.render(self.options[i], False, st.BLACK)
            else:
                text_surface = self.font.render(self.options[i], False, st.BLACK)
            text_rect = text_surface.get_rect()
            height = st.DISPLAY_H // 18 * (i + 7)
            text_rect.center = ((st.DISPLAY_W // 2, height))
            screen.blit(text_surface, text_rect)
            
            if text_rect.collidepoint(self.game.mouse_pos):
                self.options_pos = i
                if self.game.mouse_pressed[0]:
                    self.execute_option()



class Options(State):
    def __init__(self, game):
        super().__init__(game)
        self.next = 'Start_screen'    
        self.options = [
                        'Display mode: Windowed',
                        'Always show health bar: Yes',
                        f'Scroll speed: {st.CAMERA_SPEED}',
                        '',
                        'Save changes',
                        'Back to title screen'
                        ]     
        self.options_pos = 0
        
        self.font = pg.font.SysFont('Arial', 40)
        self.font_bold = pg.font.SysFont('Arial', 52, bold=True)
    
    
    def update(self, dt):
        key = self.game.key_pressed
        if key == pg.K_s:
            self.options_pos = (self.options_pos + 1) % len(self.options)
        elif key == pg.K_w:
           self.options_pos = (self.options_pos - 1) % len(self.options)
        elif key == pg.K_RETURN:
            self.execute_option()

    
    def execute_option(self):
        if self.options_pos == 0:
            self.game.toggle_fullscreen()
            if self.game.display.get_flags() & pg.FULLSCREEN:
                self.options[0] = 'Display mode: Full screen'
            else:
                self.options[0] = 'Display mode: Windowed'
        
        elif self.options_pos == 1:
            st.ALWAYS_SHOW_LIFEBARS = not st.ALWAYS_SHOW_LIFEBARS
            if st.ALWAYS_SHOW_LIFEBARS:
                self.options[1] = 'Always show health bar: Yes'
            else:
                self.options[1] = 'Always show health bar: No'
        
        elif self.options_pos == 5:
            self.done = True
        
    
    def draw(self, screen):
        screen.fill(st.BLACK)
            
        for i in range(len(self.options)):
            if self.options_pos == i:
                text_surface = self.font_bold.render(self.options[i], False, st.WHITE)
            else:
                text_surface = self.font.render(self.options[i], False, st.WHITE)
            text_rect = text_surface.get_rect()
            height = st.DISPLAY_H // 18 * (i + 7)
            text_rect.center = ((st.DISPLAY_W // 2, height))
            screen.blit(text_surface, text_rect)
            
            if text_rect.collidepoint(self.game.mouse_pos):
                self.options_pos = i
                if self.game.mouse_pressed[0]:
                    self.execute_option()
        


class Game:
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        pg.mouse.set_visible(True)
        self.display = pg.display.set_mode((st.DISPLAY_W, st.DISPLAY_H))
        self.screen = pg.Surface((st.DISPLAY_W, st.DISPLAY_H))
        self.screen_rect = self.screen.get_rect()                      
        self.event_list = []
        self.font = pg.font.SysFont('Arial', 24)
        # MEMO: make a 'fonts' dict with different fonts
        
        self.states_dict = {
                'Start_screen': Start_screen(self),
                'Options': Options(self),
                'Ingame': Ingame(self),
                'Game_lost': Game_lost(self)
                }
        self.state = self.states_dict['Start_screen']
        
        self.images = spr.load_images()
        
        self.start()
        
        self.debug_mode = False
        
    
    def start(self):
        # call this function when restarting the game
        # to avoid recursion 
        self.all_sprites = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.shooters = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        
        self.game_lost = False
        self.money = st.STARTING_MONEY
        self.lives = st.STARTING_LIVES
        self.current_wave = 0
        self.wave_spawner = Wave(self)
        self.elapsed_seconds = 0
        # load objects from tmx data
        self.bg_image, map_objects = mp.load_map('level2')
        self.roads = []
        self.nodes = []
        self.walls = []
        for obj in map_objects:
            if obj.name == 'Road':
                self.roads.append(spr.Road(obj.x, obj.y, obj.width, obj.height))
            elif obj.name == 'node':
                self.nodes.append(mp.Node(self, (obj.x, obj.y), (obj.width, obj.height)))
            elif obj.name == 'Wall':
                self.walls.append(mp.Wall(self, (obj.x, obj.y), (obj.width, obj.height)))
        
        self.map_rect = self.bg_image.get_rect()
        self.map_rect.topleft = (0, 0)
        self.start_node = mp.Node(self, (-2 * st.TILESIZE, self.map_rect.h // 2), (64, 64))
        self.end_node = mp.Node(self, (41 * st.TILESIZE, self.map_rect.h // 2), (64, 64))
        self.nodes.append(self.start_node)
        self.nodes.append(self.end_node)
        for node in self.nodes:
            node.find_neighbors()
        # find paths along the nodes
        self.paths = mp.find_paths(self.start_node, self.end_node)
              
        self.selected_shooter = next(st.shooter_it)     
        self.camera = Camera(self)


    def load_map(self, file):
        self.tiled_map = load_pygame('assets/{}.tmx'.format(file))
        self.bg_image = pg.Surface((self.tiled_map.width * self.tiled_map.tilewidth,
                              self.tiled_map.height * self.tiled_map.tileheight))
        self.map_objects = self.tiled_map.get_layer_by_name('objects1')
        for layer in self.tiled_map.layers:
            if 'tiles' in layer.name:
                for x, y, image in layer.tiles():
                    self.bg_image.blit(image, (x * self.tiled_map.tilewidth, 
                                               y * self.tiled_map.tileheight))
        
        for obj in self.map_objects:
            if obj.name == 'Road':
                self.roads.append(spr.Road(obj.x, obj.y, obj.width, obj.height))
        
        
    def events(self):
        self.mouse_pressed = [0, 0, 0, 0, 0]
        self.mouse_released = [0, 0, 0, 0, 0]
        self.mouse_pos = vec(pg.mouse.get_pos())
        self.key_pressed = None
        self.event_list = pg.event.get()
        for event in self.event_list:
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_pressed[event.button - 1] = 1
            elif event.type == pg.MOUSEBUTTONUP:
                self.mouse_released[event.button - 1] = 1
            elif event.type == pg.KEYDOWN:
                self.key_pressed = event.key
                
    
    def switch_states(self):
        if self.state.done:
            self.state.cleanup()
            self.state = self.states_dict[self.state.next]
            self.state.startup()
            
    
    def toggle_fullscreen(self):
        if self.display.get_flags() & pg.FULLSCREEN:
            pg.display.set_mode(st.DISPLAY_SIZE)
        else:
            pg.display.set_mode(st.DISPLAY_SIZE, pg.FULLSCREEN)
            
    
    def update(self, dt):  
        if self.key_pressed == pg.K_F4:
            self.toggle_fullscreen()
        self.state.update(dt)
    
    
    def draw(self):
        self.screen.fill(st.BLACK)
        self.state.draw(self.screen)
        w, h = self.screen.get_size()
        if st.CAMERA_ZOOM == 1:
            pg.transform.scale(self.screen, (w, h), self.display)
        else:
            s = pg.transform.scale(self.screen, (int(w * st.CAMERA_ZOOM),
                                                 int(h * st.CAMERA_ZOOM)))
            self.display.blit(s, (0, 0))              
        pg.display.update()
    
    
    def draw_sprites(self, screen):
        for sprite in self.all_sprites:
            sprite.draw(screen)
    
        
    def run(self):
        #self.start()
        self.running = True
        while self.running:
            delta_time = self.clock.tick(st.FPS) / (1000.0 / st.GAME_SPEED)
            self.elapsed_seconds += delta_time
            if delta_time <= 0.1:
                self.events()
                self.switch_states()
                self.update(delta_time)
                self.draw()
        
        pg.quit()