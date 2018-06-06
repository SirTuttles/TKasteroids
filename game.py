"""Asteroids!"""

__version__ = '0.1.0'

from gfx import *
import math
import time
import random


class CollisionError(Exception):
    pass

COLLIDERS_INCOMPATIBLE = "Collision check attempted with incompatible colliders."
    
    
class Game(object):
    def __init__(self, master):
        self.master = master
        
        # PixelGrid
        self.pg = PixelGrid(self.master)
        self.pg.setCoords(0, 0, self.pg.getWidth()-1, self.pg.getHeight()-1)
        self.pg.pack(fill='both', expand=1)
        
        # Backend statistics
        self.fps = 0
        self.gl_exec_time = 0
        
        self.cnode_tree = [[[]]]
        
        # Ship
        self.ship = Ship(self.pg, self.pg.center.x, self.pg.center.y)
        self.shots = []
        
        # Asteroids
        self.asteroids = []
        self.ast_gen_freq = 0.5 #seconds
        self.ast_last_gen_time = time.time()
        self.ast_update_i = 0
        self.ast_max = 20
        
        self.remove = []
        
        # Stopcodes
        self.sc_gameloop = None
        
        # Binds
        
        
        # Toggle Debugging Features per object
        #self.debug()
        #self.ship.debug()
        
        self.gl_last_endtime = time.time()
        self.start()

    def start(self):
        self.gameloop()

    def gameloop(self):
        self.update_projectiles()
        self.check_collisions()
        self.handle_offscreen_objects()
        self.handle_asteroid_generation()
        self.handle_ship_fire()
        endtime = time.time()
        self.gl_last_endtime = endtime
        self.pg.after(16, self.gameloop)
    
    def update_projectiles(self):
        # Ship
        self.ship.update(0.08)
        if self.ship.isAccelerting():
            self.ship.accel()
        if self.ship.isRotating():
            self.ship.rotate()
        
        # Asteroids
        for asteroid in self.asteroids:
            asteroid.update(0.1)
            asteroid.rotate(1)
                
        # Shots
        for shot in self.shots:
            shot.update(0.1)
        
        # BAD METHOD? Rework somehow? Probably not.
        #if len(self.asteroids) != 0:
        #    ast = self.asteroids[self.ast_update_i]
        #    ast.update(1)
        #    self.ast_update_i += 1
        #    if self.ast_update_i == len(self.asteroids):
        #        self.ast_update_i = 0
     
    def handle_offscreen_objects(self):
        # What to do if ship escapes an edge of window
        if self.ship.getX() > self.pg.w:
            self.ship.move(-self.ship.getX(), 0)
        elif self.ship.getX() < 0:
            self.ship.move(self.pg.w, 0)
        
        if self.ship.getY() > self.pg.h:
            self.ship.move(0, -self.ship.getY())
        elif self.ship.getY() < 0:
            self.ship.move(0, self.pg.h)
            
        for asteroid in self.asteroids:
            if asteroid.getX() > self.pg.w:
                asteroid.move(-asteroid.getX(), 0)
            elif asteroid.getX() < 0:
                asteroid.move(self.pg.w, 0)
            
            if asteroid.getY() > self.pg.h:
                asteroid.move(0, -asteroid.getY())
            elif asteroid.getY() < 0:
                asteroid.move(0, self.pg.h)
                  
    def check_collisions(self):
        for asteroid in self.asteroids[:]:
            if asteroid.checkCollide(self.ship):
                asteroid.handle_collision()
                self.ship.handle_collision()
                self.asteroids.remove(asteroid)
            
            for shot in self.shots:
                if asteroid.checkCollide(shot):
                    asteroid.handle_collision()

    def handle_ship_fire(self):
        shot = self.ship.getShot()
        if shot:
            print('HERE')
            self.shots.append(shot)
            
                  
    def handle_asteroid_generation(self):
        since_last_gen = time.time() - self.ast_last_gen_time
        max_reached = len(self.asteroids) == self.ast_max
        if since_last_gen >= self.ast_gen_freq and not max_reached:
            w = self.pg.getWidth()
            h = self.pg.getHeight()
            
            # Start on x or y?
            plane = random.randrange(0,2)
            
            # Start on x
            if plane == 0:
                x_choices = [0, w]
                choice = random.randrange(0,2)
                if choice == 0:
                    ang = random.randrange(-85, 86)
                else:
                    ang = random.randrange(105, 265)
                x = x_choices[choice]
                y = random.randrange(0,h)
            # Start on y
            else:
                y_choices = [0, h]
                choice = random.randrange(0,2)
                if choice == 0:
                    ang = random.randrange(20, 160)
                else:
                    ang = random.randrange(190, 340)
                y = y_choices[choice]
                x = random.randrange(0,w)
            
            vel = random.randrange(10,15)
            ast = Asteroid(self.pg, ang, vel, x, y)
            #ast.debug()
            self.asteroids.append(ast)
            self.ast_last_gen_time = time.time()
    
    def debug(self):
        pass
        
    def kill_projectile(self, proj):
        pass
        

class Player(object):
    def __init__(self, name):
        self.name = name
        self.score = 0
        
    def save(self):
        pass
        
        
class Projectile(object):
    """A projectile class that keeps track and updates a virtual projectile
    with a given amount of time"""
    def __init__(self, ang, vel, x, y):
        self.theta = ((ang%360) * math.pi / 180)
        self.xvel = vel * math.cos(self.theta)
        self.yvel = vel * math.sin(self.theta)
        self.x = x
        self.y = y
        self.sx = x
        self.sy = y
        self.t = 0.1
        self.grav = [0,0]
    
    def update(self, t=None):
        # Interpretor has not read self.__init__ yet (self.t not yet defined)
        if t == None:
            t = self.t
        xvel1 = self.xvel - self.grav[0] * t
        self.x = self.x + ((self.xvel + xvel1) / 2)* t
        self.xvel = xvel1
        yvel1 = self.yvel - self.grav[1] * t
        self.y = self.y + ((self.yvel + yvel1) / 2) * t
        self.yvel = yvel1
        
    def setPos(self, x, y):
        self.x = x
        self.y = y
        
    def getPos(self):
        return [self.x, self.y]
       
    def setXVel(self, x):
        return self.xvel
        
    def setYVel(self, y):
        return self.yvel
        
    def setVel(self, vel):
        self.xvel = vel & math.cos(self.theta)
        self.yvel = vel * math.sin(self.theta)
        
    def setAngle(self, ang):
        self.theta = (ang * math.pi / 180) % 360
        
    def addAngle(self, amount):
        degrees = self.theta * 180 / math.pi
        degrees += amount
        self.theta = degrees * math.pi / 180        
        
    def addXVel(self, amount):
        self.xvel = self.xvel + amount
        
    def addYVel(self, amount):
        self.yvel = self.yvel + amount
        
    def addVel(self, amount):
        ixvel = amount * math.cos(self.theta)
        iyvel = amount * math.sin(self.theta)
        
        
        self.xvel = self.xvel + ixvel
        self.yvel = self.yvel - iyvel
        
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
        
    def setX(self, x):
        self.x = x
    
    def setY(self, y):
        self.y = y
        
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
       
       
class VProjectile(Projectile):
    def __init__(self, pg, shape, ang, vel, x, y):
        super().__init__(ang, vel, x, y)
        self.pg = pg
        self.shape = shape
        self.collider = genCollisionBox(shape)
        self.last_pos = [x, y]
        self.collision = False
        
        self.debugging = False
        # Debugging attributes
        self.real_pathHist = []
        self.shape_pathHist = []
        self.vis_vel = None 
        self.vis_top_edge = None
        self.vis_right_edge = None
        self.vis_bottom_edge = None
        self.vis_left_edge = None
        
    def update(self, t=None):
        super().update(t)
        x0, y0 = self.last_pos[0], self.last_pos[1]
        dx, dy = self.x - x0, self.y - y0
        self.shape.move(dx, dy)
        self.collider.move(dx, dy)
        self.last_pos = [self.x, self.y]
    
    # Debugging Visualizers
    if self.debugging:
        # Make collider visible
        if not self.collider.isDrawn():
            self.collider.draw(self.pg)
    
        # Path history of real projectile
        hist_point1 = Point(x0, y0)
        hist_point1.draw(self.pg)
        hist_point1.setFill('lightgreen')
        self.real_pathHist.append(hist_point1)
        if len(self.real_pathHist) > 100:
            dead = self.real_pathHist.pop(0)
            dead.undraw()
            
        # Path history of shape shadowing projectile
        xh = self.shape.origin.getX()
        yh = self.shape.origin.getY()
        hist_point2 = Point(xh, yh)
        hist_point2.setFill('blue')
        hist_point2.draw(self.pg)
        self.shape_pathHist.append(hist_point2)
        if len(self.shape_pathHist) > 150:
            dead = self.shape_pathHist.pop(0)
            dead.undraw()
        
        # Visualize Velocity
        if self.vis_vel:
            self.vis_vel.undraw()
        self.vis_vel = Line(
            Origin(xh, yh),
            Point(xh, yh),
            Point(xh+self.xvel, yh+self.yvel))
        self.vis_vel.draw(self.pg)
        self.vis_vel.setFill('red')
            
    def handle_collision(self):
        self.collision = True
        self._handle_collision()
            
    def rotate(self, angle):
        if not self.impact:
            self.shape.rotate(-angle)
            self.addAngle(angle)
        
    def debug(self):
        self.debugging = True
        
    def checkCollide(self, vproj):
        return self.collider.checkCollide(vproj)
        
    
class Ship(VProjectile):
    def __init__(self, pg, x, y):
        
        shape = Polygon(
            'center',
            Point(x-8, y+8),
            Point(x+15, y),
            Point(x-8, y-8))
        shape.draw(pg)
        super().__init__(pg, shape, 0, 0, x, y)
        
        # Base Attributes
        self.max_accel = 100
        self.inc_accel = 1
        self.inc_rotate = 6
        self.dir_accel = self.inc_accel
        self.dir_rot = self.inc_rotate
        
        # Movement checks
        self.rotating = False
        self.accelerating = False
     
        # Current shot
        self.shot = None
     
        # Binds
        self.pg.master.bind('<Up>', self.acceleration)
        self.pg.master.bind('<KeyRelease-Up>', self.acceleration)
        self.pg.master.bind('<Down>', self.acceleration)
        self.pg.master.bind('<KeyRelease-Down>', self.acceleration)
        self.pg.master.bind('<Left>', self.rotation)
        self.pg.master.bind('<KeyRelease-Left>', self.rotation)
        self.pg.master.bind('<Right>', self.rotation)
        self.pg.master.bind('<KeyRelease-Right>', self.rotation)
        self.pg.master.bind('<space>', self.fire)
        
        # Stop Codes
        self.sc_accelerating = None
        self.sc_rotating = None
        
    def acceleration(self, event):
        if event.type == '3':
            if self.accelerating:
                self.accelerating = False
                return False
                
        if not self.accelerating:
            if event.keysym == 'Up':
                self.dir_accel = self.inc_accel
                self.accelerating = True
            elif event.keysym == 'Down':
                self.dir_accel = -self.inc_accel
                self.accelerating = True

        
    def accel(self):
        super().addVel(self.dir_accel)
        
    def isAccelerting(self):
        return self.accelerating
        
    def rotation(self, event):
        if event.type == '3':
            if self.rotating:
                self.rotating = False
                return True
                
        if not self.rotating:
            if event.keysym == 'Right':
                self.dir_rotate = self.inc_rotate
                self.rotating = True
            elif event.keysym == 'Left':
                self.dir_rotate = -self.inc_rotate
                self.rotating = True
    
    def rotate(self):
        super().rotate(self.dir_rotate)

    def isRotating(self):
        return self.rotating
        
    def _handle_collision(self):
        self.accelerating = False
        self.rotating = False
        self.shape.undraw()
       
    def getShot(self):
        shot = self.shot
        if shot:
            self.shot = None
        return shot
        
    def fire(self, event):
        angle = self.theta*180/math.pi
        shot = Shot(self.pg, -angle, 30, self.x, self.y)
        self.shot = shot
        

class Shot(VProjectile):
    def __init__(self, pg, ang, vel, x, y):
        shape = PolyCircle('center', Point(x, y), 4, 5)
        shape.draw(pg)
        super().__init__(pg, shape, ang, vel, x, y)
        
        
class Asteroid(VProjectile):
    def __init__(self, pg, ang, vel, x, y):
        self.max_verts = 15
        self.max_size = 40
        shape = self._genShape(x, y)
        shape.draw(pg)
        super().__init__(pg, shape, ang, vel, x, y)
        
    def _genShape(self, x, y):
        verts = random.randrange(7, self.max_verts + 1)
        size = random.randrange(10, self.max_size + 1)
        per = 360 // verts
        points = []
        for i in range(360):
            theta = i * math.pi / 180
            xmag = size * math.cos(theta)
            ymag = size * math.sin(theta)
            xmag += random.random() * 10 
            ymag += random.random() * 10
            px = xmag + x
            py = ymag + y
            
            if i % per == 0:
                points.append(Point(px, py))
        
        shape = Polygon('center', *points)
        return shape
        
    def _handle_collision(self):
        self.max_size -= 2
        self.shape.undraw()
        
        
        
class CollisionBox(Polygon):
    def __init__(self, origin, p1, p2):
        p3, p4 = self._getOtherPoints(p1, p2)
        self.w = abs(p2.x - p1.x)
        self.h = abs(p3.y - p1.y)
        super().__init__(origin, p1, p3, p2, p4)
        
    def checkCollide(self, vproj):
        if not isinstance(vproj.collider, CollisionBox):
            raise(CollisionError, COLLIDERS_INCOMPATIBLE)
            
        check = vproj.collider
        wh, hh = self.w / 2, self.h / 2
        c = self.center
        for point in check.getPoints():
            if point.x <= c.x + wh and point.x >= c.x - wh:
                if point.y <= c.y + hh and point.y >= c.y - hh:
                    return True
        return False

        
    def _getOtherPoints(self, p1, p2):
        p3x, p3y, p4x, p4y = 0, 0, 0, 0
        
        if p1.x < p2.x:            
            if p1.y < p2.y:
                p3x, p3y = p1.x, p2.y
                p4x, p4y = p2.x, p1.y
            elif p2.y < p1.y:
                p3x, p3y = p1.x, p2.y
                p4x, p4y = p2.x, p1.y
        elif p2.x < p1.x:
            if p1.y < p2.y:
                p3x, p3y, p2.x, p1.y
                p4x, p4y, p1.x, p2.y
            elif p2.y < p1.y:
                p3x, p3y, p1.x, p2.y
                p4x, p4y, p2.x, p1.y
        
        return Point(p3x, p3y), Point(p4x, p4y)
    
    def getWidth(self):
        return self.w
        
    def getHeight(self):
        return self.h
    
        
def genCollisionBox(shape):
    points = shape.getPoints()
    lowx = points[0].x
    highx = points[0].x
    lowy = points[0].y
    highy = points[0].y
    
    for point in points:
        x, y = point.getX(), point.getY()
        if x > highx:
            highx = x
        if x < lowx:
            lowx = x
            
        if y > highy:
            highy = y
        if y < lowy:
            lowy = y
        
    cx = lowx + (highx - lowx) / 2
    cy = lowy + (highy - lowy) / 2
    return CollisionBox(Origin(cx, cy), Point(lowx, lowy), Point(highx, highy))
     
def main():
    root = Root('TKasteroids')
    root.resizable(0, 0)
    game = Game(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()