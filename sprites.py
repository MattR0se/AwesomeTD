import pygame as pg
import math
import sys

import settings as st

vec = pg.math.Vector2
vec3 = pg.math.Vector3

RIGHT = vec(1, 0)
LEFT = vec(1, 0)

# ------------- helper functions ----------------------------------------------

def limit(vector, length):
    if vector.length_squared() <= length * length:
        return
    else:
        vector.scale_to_length(length)
        

def remap(n, start1, stop1, start2, stop2):
    # https://p5js.org/reference/#/p5/map
    newval = (n - start1) / (stop1 - start1) * (stop2 - start2) + start2
    if (start2 < stop2):
        return constrain(newval, start2, stop2)
    else:
        return constrain(newval, stop2, start2)
    

def constrain(n, low, high):
    return max(min(n, high), low)


def scale_image(image, scale):
    rect = image.get_rect()
    return pg.transform.scale(image, (rect.w * scale, rect.h * scale))


# ----------- sprites ---------------------------------------------------------
module_dict = sys.modules[__name__].__dict__


def load_images():
    images = {
            'background1': pg.image.load('assets/level1.png').convert(),
            'tower1': pg.image.load('assets/single_images/towerDefense_tile249.png').convert_alpha(),
            'tower2': pg.image.load('assets/single_images/towerDefense_tile250.png').convert_alpha(),
            'towerbase1': pg.image.load('assets/single_images/towerDefense_tile180.png').convert_alpha(),
            'towerbase2': pg.image.load('assets/single_images/towerDefense_tile181.png').convert_alpha(),
            'mob1': pg.image.load('assets/single_images/towerDefense_tile245.png').convert_alpha(),
            'mob2': pg.image.load('assets/single_images/towerDefense_tile246.png').convert_alpha(),
            'mob3': pg.image.load('assets/single_images/towerDefense_tile247.png').convert_alpha(),
            'mob4': pg.image.load('assets/single_images/towerDefense_tile248.png').convert_alpha(),
            'mob5': pg.image.load('assets/single_images/towerDefense_tile270.png').convert_alpha(),
            'mob6': pg.image.load('assets/single_images/towerDefense_tile271.png').convert_alpha(),
            'mob7': pg.image.load('assets/single_images/towerDefense_tile268.png').convert_alpha(),
            'mob8': scale_image(pg.image.load('assets/single_images/towerDefense_tile269.png').convert_alpha(), 2),
            'bullet1': pg.image.load('assets/single_images/towerDefense_tile272.png').convert_alpha()
            }
    
    return images



class Mob(pg.sprite.Sprite):
    def __init__(self, game, position, path, type_):
        super().__init__(game.all_sprites, game.mobs)
        self.game = game
        self.type = type_
        self.image_original = self.game.images[st.mobs[self.type]['image']].copy()
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.hitbox = pg.Rect((0, 0), st.mobs[self.type]['hitbox_size'])
        
        self.health_bar = pg.Surface((40, 6))
        self.health_bar.fill(st.GREEN)
        self.health_bar_rect = self.health_bar.get_rect()
        
        self.acc = vec()
        self.vel = vec()
        self.pos = vec(position)
        self.rect.center = self.pos
        self.hitbox.center = self.rect.center
        self.path = path
        self.current_target = 0
        self.target = vec(self.path[self.current_target])
        self.speed = st.mobs[self.type]['speed']
        self.friction = 0.9
        
        self.max_hp = st.mobs[self.type]['hp']
        self.hp = self.max_hp
        self.reward = st.mobs[self.type]['reward']
        
    
    def update(self, dt):
        self.acc += self.arrive(self.target)
        self.acc += self.separation()
        self.vel += self.acc * self.speed * dt
        self.acc *= 0
        self.vel *= self.friction
        self.pos += self.vel
        
        if self.pos.x > self.game.map_rect.w:
            self.kill()
            self.game.lives -= 1
        if self.hp <= 0:
            self.game.money += self.reward
            self.kill()
        
        d = self.target - self.pos
        
        if d.length() < self.speed:
            self.current_target += 1
            self.target = self.path[self.current_target]
        
        # calculate rotation
        angle = self.vel.angle_to(RIGHT)
        self.image = pg.transform.rotate(self.image_original.copy(), angle)
        self.rect = self.image.get_rect()
        
        self.rect.center = self.pos
        self.hitbox.center = self.rect.center  
        # color
        # MEMO: make this a health bar
        
    
    def arrive(self, target):
        # make the mob move to a target position
        desired = target - self.pos
        d = desired.length()
        if d > 0:
            desired = desired.normalize()    
        radius = 100
        
        if d < radius:
            m = remap(d, 0, radius, 0, self.speed)
            desired *= m       
        else:
            desired *= self.speed
        
        # calculate steering force
        steering = desired - self.vel
        limit(steering, 1)
        
        return steering


    def separation(self):
        perception_radius = 40
        steering = vec()
        total = 0
        for other in self.game.mobs:
            if other != self:
                d = self.pos - other.pos
                dist = d.length()
                if dist < perception_radius:
                    if dist > 0:
                        d /= (dist * dist)
                    else:
                        d /= 0.001
                    steering += d
                    total += 1      
        if total > 0 and steering.length() > 0:
            try:
                steering /= total
                steering.scale_to_length(self.speed)
                steering -= self.vel
                limit(steering, 0.2)
            except:
                print('steering went wrong', steering)
            
        return steering
    
    
    def draw(self, screen):
        screen.blit(self.image, self.game.camera.apply_pos(self.rect.topleft))
        
        keys = pg.key.get_pressed()
        if keys[pg.K_LSHIFT] or keys[pg.K_CAPSLOCK]:
            pct = max(0, self.hp / self.max_hp)
            if pct > 0.5:
                lerp_pct = remap(pct, 0.5, 1, 0, 1)
                self.color = st.COLOR.yellow.lerp(st.COLOR.green, lerp_pct)
            else:
                lerp_pct = remap(pct, 0, 0.5, 0, 1)
                self.color = st.COLOR.red.lerp(st.COLOR.yellow, lerp_pct)
            self.health_bar.fill(self.color)
            self.health_bar = pg.transform.scale(self.health_bar, (int(40 * pct), 6))
            self.health_bar_rect = self.health_bar.get_rect()
            self.health_bar_rect.center = self.rect.center
            screen.blit(self.health_bar, self.game.camera.apply_rect(self.health_bar_rect))



class Shooter(pg.sprite.Sprite):
    def __init__(self, game, position, type_):
        super().__init__(game.all_sprites, game.shooters)
        self.game = game
        self.type = type_
        self.image_original = self.game.images[st.shooters[self.type]['image']].copy()
        self.image = self.image_original.copy()
        self.base_image = self.game.images[st.shooters[self.type]['base_image']].copy()
        self.rect = self.image.get_rect()
        self.base_rect = self.base_image.get_rect()
        self.pos = vec(position)
        self.rect.center = self.pos
        self.target = None
        self.aim = vec()
        self.perception_radius = st.shooters[self.type]['perception_radius']
        self.timer = 0
        self.cooldown = st.shooters[self.type]['cooldown']
        self.price = st.shooters[self.type]['price']
        self.refund = st.shooters[self.type]['refund']
        self.projectile = st.shooters[self.type]['projectile']
    
    
    def update(self, dt):        
        self.timer += dt
        # look for closest target
        self.target = None
        closest = math.inf
        for s in self.game.mobs:
            d = s.pos - self.pos
            dist = d.length()
            if dist < self.perception_radius:
                if dist < closest:
                    closest = dist
                    self.target = s
        
        
        # shoot at target
        if self.target:
            target_desired = self.target.pos + self.target.vel * 30
            self.aim = target_desired - self.pos
            angle = self.aim.angle_to(vec(1, 0)) * -1
            if self.timer >= self.cooldown:   
                # shoot bullets
                muzzle_pos = self.pos + self.aim.normalize() * 22
                module_dict[self.projectile](self.game, muzzle_pos, angle)
                self.timer = 0
            
            # image rotation
            img_temp = self.image_original.copy()
            img_temp = pg.transform.rotate(img_temp, angle * -1 - 90)
            self.image = img_temp
            self.rect = self.image.get_rect()

        self.rect.center = self.pos
        self.base_rect.center = self.rect.center
    
    
    def draw(self, screen):
        # draw base image
        screen.blit(self.base_image, 
                    self.game.camera.apply_pos(self.base_rect.topleft))
        # draw muzzle
        screen.blit(self.image, self.game.camera.apply_pos(self.rect.topleft))



class Bullet(pg.sprite.Sprite):
    def __init__(self, game, position, angle):
        super().__init__(game.all_sprites, game.bullets)
        self.game = game
        self.image_original = self.game.images['bullet1'].copy()
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.hitbox = pg.Rect(0, 0, 14, 14)
        self.pos = vec(position)
        self.rect.center = self.pos
        self.hitbox.center = self.rect.center
        self.acc = vec()
        self.acc.from_polar((1, angle))
        self.vel = vec()
        self.friction = 0.99
        self.speed = 200
        
        self.damage = 1
    
    
    def update(self, dt):
        self.vel += self.acc * self.speed * dt
        self.acc *= 0
        self.vel *= self.friction
        self.pos += self.vel
            
        self.rect.center = self.pos
        self.hitbox.center = self.rect.center
        
        if not self.game.map_rect.colliderect(self.hitbox):
            self.kill()
            
        if self.vel.length() <= 1:
            self.kill()

        for mob in self.game.mobs:
            if self.hitbox.colliderect(mob.hitbox):
                mob.hp -= self.damage
                self.kill()
    
    
    def draw(self, screen):
        screen.blit(self.image, self.game.camera.apply_pos(self.rect.topleft))
    
    

class Road(object):
    '''
    object that indicates where the road is on the map
    '''
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        
        
        