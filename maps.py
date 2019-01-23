import pygame as pg
from queue import Queue
from pytmx.util_pygame import load_pygame

#import settings as st


vec = pg.math.Vector2


def get_path_length(path):
    # calculate the length of a given path of nodes
    length = 0
    for i in range(len(path) - 1):
        d = path[i].position.distance_to(path[i + 1].position)
        length += d
    return length


def breadth_first_search(start, goal):
    # https://www.redblobgames.com/pathfinding/a-star/introduction.html
    frontier = Queue()
    frontier.put(start)
    came_from = {}
    came_from[start] = None
    # visit all nodes
    while not frontier.empty():
        current = frontier.get()
        for next in current.find_neighbors():
            if next not in came_from:
                frontier.put(next)
                came_from[next] = current
    # get path with the fewest nodes
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path


def find_paths(start, goal):
    q = Queue()
    path = []
    paths = []
    path.append(start)
    q.put(path)
    while not q.empty():
        path = q.get()
        last = path[-1]
        if last == goal:
            paths.append(path)
        
        for node in last.neighbors:
            if node not in path:
                newpath = list(path)
                newpath.append(node)
                q.put(newpath)
    #return sorted(paths, key=len)
    return sorted(paths, key=get_path_length)


def load_map(file):
        tiled_map = load_pygame('assets/{}.tmx'.format(file))
        bg_image = pg.Surface((tiled_map.width * tiled_map.tilewidth,
                              tiled_map.height * tiled_map.tileheight))
        map_objects = tiled_map.get_layer_by_name('objects1')
        for layer in tiled_map.layers:
            if 'tiles' in layer.name:
                for x, y, image in layer.tiles():
                    bg_image.blit(image, (x * tiled_map.tilewidth, 
                                          y * tiled_map.tileheight))
        return bg_image, map_objects



class Node:
    def __init__(self, game, position, size):
        self.game = game
        self.rect = pg.Rect(position, size)
        self.rect.topleft = position
        self.position = vec(self.rect.center)
        self.neighbors = []
    
    
    def __repr__(self):
        return str(self.position)
        
    
    def find_neighbors(self):
        # cast a ray to each other node and if it doesn't intersect a wall
        # add that node to neighbors
        self.neighbors.clear()
        for node in self.game.nodes:
            if node != self:
                dist = Line(self.position, node.position)
                intersects = False
                for wall in self.game.walls:
                    if dist.intersects_rect(wall.rect):
                        intersects = True
                for other in self.game.nodes:
                    if (other != self and other != node and
                        dist.intersects_rect(other.rect)):
                        intersects = True
                if not intersects:
                    self.neighbors.append(node)
        return self.neighbors
    

class Wall:
    def __init__(self, game, position, size):
        self.game = game
        self.rect = pg.Rect(position, size)
        self.rect.topleft = position
        self.position = vec(position)
    
                

class Line:
    # class that represents a line from one point to another
    def __init__(self, start, end):
        self.start = vec(start)
        self.end = vec(end)
        
    
    def intersects_line(self, other):
        # checks if two Line objects intersect
        #http://www.jeffreythompson.org/collision-detection/line-rect.php
        # calculate denominators for uA and uB
        denA = ((other.end.y - other.start.y) * (self.end.x - self.start.x) - 
                (other.end.x - other.start.x) * (self.end.y - self.start.y))
        denB = ((other.end.y - other.start.y) * (self.end.x - self.start.x) - 
                (other.end.x - other.start.x) * (self.end.y - self.start.y))
        if denA == 0 or denB == 0:
            # if any denominator is 0, the lines are parallel and don't intersect
            return False
        else:
            # calculate numerators for uA and uB
            numA = ((other.end.x - other.start.x) * (self.start.y - other.start.y) - 
                    (other.end.y - other.start.y) * (self.start.x - other.start.x))
            numB = ((self.end.x - self.start.x) * (self.start.y - other.start.y) - 
                    (self.end.y - self.start.y) * (self.start.x - other.start.x))
            uA = numA / denA
            uB = numB / denB
            return (uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1)

    
    def get_lines_from_rect(self, rect):
        # returns a list with all 4 sides of a given rect as Line objects
        l1 = Line(rect.topleft, rect.topright)
        l2 = Line(rect.topright, rect.bottomright)
        l3 = Line(rect.bottomright, rect.bottomleft)
        l4 = Line(rect.bottomleft, rect.topleft)
        return [l1, l2, l3, l4]

    
    def intersects_rect(self, rect):
        # checks if this line intersects any lines from a given rect
        lines = self.get_lines_from_rect(rect)
        for line in lines:
            if self.intersects_line(line):
                return True
        return False