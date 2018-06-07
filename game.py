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
        
        # Asteroids
        self.ast_gen_freq = 0.5 #seconds
        self.ast_last_gen_time = time.time()
        self.ast_update_i = 0
        self.ast_max = 50
        self.ast_count = 0
        
        # Shots
        self.shot_max_dist = 200
        
        # Object container
        self.objects = [self.ship]
        self.remove = []
        
        # Stopcodes
        self.sc_gameloop = None
        
        # Binds
        
        
        # Toggle Debugging Features per object
        self.debug()
        self.ship.debug()
        
        self.gl_last_endtime = time.time()
        self.start()
        
        
        # Player
        self.player = Player('AAA')

    def start(self):
        self.gameloop()

    def gameloop(self):
        self.handle_ship_fire()
        self.check_collisions()
        
        # Call this before any methods that might affect undrawn objects
        self.delete_removable()
        
        self.update_projectiles()
        self.handle_offscreen_objects()
        self.handle_asteroid_generation()
        endtime = time.time()
        #print(round(endtime - self.gl_last_endtime, 3))
        self.gl_last_endtime = endtime
        self.pg.after(16, self.gameloop)
    
    def delete_removable(self):
        for object in self.remove:
            self.objects.remove(object)
        self.remove = []
    
    def update_projectiles(self):
        ast_count = 0
        self.pg.master.update_idletasks()
        for object in self.objects:
            # Ship
            if isinstance(object, Ship):
                ship = object
                if ship.isAccelerting():
                    ship.accel()
                if ship.isRotating():
                    ship.rotate()
            
            # Asteroid
            elif isinstance(object, Asteroid):
                ast = object
                ast.rotate(1)
                ast_count += 1
                
            # Shot
            elif isinstance(object, Shot):
                shot = object
                if shot.getDistance() > self.shot_max_dist:
                    self.add_remove(shot)
                    shot.shape.undraw()
                    continue
                
            object.update(0.1)
        self.ast_count = ast_count
     
    def handle_offscreen_objects(self):
        # What to do if ship escapes an edge of window
        for object in self.objects:
            if object.getX() > self.pg.w:
                object.move(-object.getX(), 0)
            elif object.getX() < 0:
                object.move(self.pg.w, 0)
            
            if object.getY() > self.pg.h:
                object.move(0, -object.getY())
            elif object.getY() < 0:
                object.move(0, self.pg.h)
            

    def check_collisions(self):
        exclusions = {
            Ship: [Shot],
            Shot: [Ship, Shot]
        }
        for object in self.objects[:]:
            for check in self.objects[:]:
                exclude = exclusions.get(object.__class__, [])
                if not check.__class__ in exclude and object != check:
                    if object.checkCollide(check):
                        object.handle_collision()
                        self.add_remove(object)
                        
                    
    def handle_ship_fire(self):
        shot = self.ship.getShot()
        if shot:
            self.objects.append(shot)
            
          
    def handle_asteroid_generation(self):
        since_last_gen = time.time() - self.ast_last_gen_time
        max_reached = self.ast_count == self.ast_max
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
            
            vel = random.randrange(5,30)
            ast = Asteroid(self.pg, ang, vel, x, y)
            
            # Re-implement! Prevents spawning on objects
            for object in self.objects:
                if object.checkCollide(ast):
                    ast.shape.undraw()
                    return False
                    
            self.objects.append(ast)
            self.ast_last_gen_time = time.time()
    
    def add_remove(self, object):
        if not object in self.remove:
            self.remove.append(object)
    
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
        self.ang = ang%360
        theta = ang * math.pi / 180
        self.vel = vel
        self.xvel = vel * math.cos(theta)
        self.yvel = vel * math.sin(theta)
        self.x = x
        self.y = y
        self.sx = x
        self.sy = y
        self.t = 0.1
        self.grav = [0,0]
        self.distance = [0,0]
    
    def update(self, t=None):
        # Interpretor has not read self.__init__ yet (self.t not yet defined)
        if t == None:
            t = self.t
        start = [self.x, self.y]
            
        xvel1 = self.xvel - self.grav[0] * t
        self.x = self.x + ((self.xvel + xvel1) / 2)* t
        self.xvel = xvel1
        yvel1 = self.yvel - self.grav[1] * t
        self.y = self.y + ((self.yvel + yvel1) / 2) * t
        self.yvel = yvel1
        
        end = [self.x, self.y]
        dx, dy = end[0] - start[0], end[1] - start[1]
        self.distance[0] += dx
        self.distance[1] += dy
        
    def setPos(self, x, y):
        self.x = x
        self.y = y
        
    def getPos(self):
        return [self.x, self.y]
       
    def getDistance(self):
        mag = math.sqrt(self.distance[0]**2 + self.distance[1]**2)
        return mag
       
    def setXVel(self, x):
        return self.xvel
        
    def setYVel(self, y):
        return self.yvel
        
    def setVel(self, vel):
        theta = self.ang * math.pi / 180
        self.xvel = vel & math.cos(theta)
        self.yvel = vel * math.sin(theta)
        
    def setAngle(self, ang):
        self.ang = ang % 360
        
    def addAngle(self, amount):
        self.ang = (self.ang + amount) % 360
        
    def addXVel(self, amount):
        self.xvel = self.xvel + amount
        
    def addYVel(self, amount):
        self.yvel = self.yvel + amount
        
    def addVel(self, amount):
        theta = self.ang * math.pi / 180
        ixvel = amount * math.cos(theta)
        iyvel = amount * math.sin(theta)
        
        self.xvel = self.xvel + ixvel
        self.yvel = self.yvel + iyvel
        self.vel = math.sqrt(self.xvel**2 + self.yvel**2)
        
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
        self.vis_ang = None
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
            if len(self.real_pathHist) > 50:
                dead = self.real_pathHist.pop(0)
                dead.undraw()
                
            # Path history of shape shadowing projectile
            xh = self.shape.origin.getX()
            yh = self.shape.origin.getY()
            hist_point2 = Point(xh, yh)
            hist_point2.setFill('blue')
            hist_point2.draw(self.pg)
            self.shape_pathHist.append(hist_point2)
            if len(self.shape_pathHist) > 75:
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
            
            # Visualize angle
            ang = self.ang * math.pi / 180
            ax, ay = xh + 30 *math.cos(ang), yh + 30 * math.sin(ang)
            
            if self.vis_ang:
                self.vis_ang.undraw()
            self.vis_ang = Line(
                Origin(xh, yh),
                Point(xh, yh),
                Point(ax, ay))
            self.vis_ang.draw(self.pg)
            self.vis_ang.setFill('purple')
               
                
    def handle_collision(self):
        self.collision = True  
            
        self._handle_collision()
            
    def rotate(self, angle=0):
        if callable(getattr(self, '_rotate', None)):
            self._rotate()
        else:
            self.shape.rotate(-angle)
            self.addAngle(angle)
        
    def debug(self):
        self.debugging = True
        
    def checkCollide(self, vproj):
        collision = self.collider.checkCollide(vproj)
        return collision
        
    
class Ship(VProjectile):
    def __init__(self, pg, x, y):
        
        shape = Polygon(
            'center',
            Point(x-8, y+8),
            Point(x+15, y),
            Point(x-8, y-8))
        shape.draw(pg)
        super().__init__(pg, shape, 0, 0, shape.center.x, shape.center.y)
        
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
                self.dir_rotate = -self.inc_rotate
                self.rotating = True
            elif event.keysym == 'Left':
                self.dir_rotate = self.inc_rotate
                self.rotating = True
    
    def _rotate(self):
        self.shape.rotate(self.dir_rotate)
        self.addAngle(self.dir_rotate)

    def isRotating(self):
        return self.rotating
        
    def _handle_collision(self):
        self.shape.undraw()
        self.accelerating = False
        self.rotating = False
       
    def getShot(self):
        shot = self.shot
        if shot:
            self.shot = None
        return shot
        
    def fire(self, event):
        angle = self.ang
        shot = Shot(self.pg, self)
        self.shot = shot
        

class Shot(VProjectile):
    def __init__(self, pg, ship):
        self.ship = ship
        x = ship.getX()
        y = ship.getY()
        vel = ship.vel
        ang = ship.ang
        shape = PolyCircle('center', Point(x, y), 1, 3)
        shape.draw(pg)
        super().__init__(pg, shape, ang, 0, x, y)
        self.xvel = ship.xvel
        self.yvel = ship.yvel
        self.addVel(100)
        
    def _handle_collision(self):
        self.shape.undraw()
        pass
        
        
class Asteroid(VProjectile):
    def __init__(self, pg, ang, vel, x, y):
        self.max_verts = 10
        self.max_size = 40
        shape = self._genShape(x, y)
        shape.draw(pg)
        super().__init__(pg, shape, ang, vel, x, y)
        
    def _genShape(self, x, y):
        verts = random.randrange(7, self.max_verts + 1)
        size = random.randrange(10, self.max_size + 1)
        per = 360 // verts
        points = []
        for i in range(1,361):
            theta = i * math.pi / 180
            xmag = size * math.cos(theta)
            ymag = size * math.sin(theta)
            xmag += random.random() * 5
            ymag += random.random() * 5
            px = xmag + x
            py = ymag + y
            
            if i % per == 0:
                points.append(Point(px, py))
        
        shape = Polygon('center', *points)
        return shape
        
    def _handle_collision(self):
        self.shape.undraw()
        self.max_size -= 2
        
        
        
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
        
        shw, shh = self.w / 2, self.h / 2
        chw, chh = check.w / 2, check.h / 2
        sc = self.center
        cc = check.center
        
        cRight = cc.x + chw
        cLeft = cc.x - chw
        cTop = cc.y + chh
        cBot = cc.y - chh
        
        sRight = sc.x + shw
        sLeft = sc.x - shw
        sTop = sc.y + shh
        sBot = sc.y - shh
        happened = []
        # Top
        if sTop > cBot and sBot < cBot:
            if cLeft < sRight and cRight > sLeft:
                return True
        # Bot
        if sBot < cTop and sTop > cTop:
            if cLeft < sRight and cRight > sLeft:
                return True
                
        # Left
        if sLeft < cRight and sRight > cRight:
            if cTop > sBot and cBot < sTop:
                return True
        
        # Right
        if sRight > cLeft and sLeft < cLeft:
            if cTop > sBot and cBot < sTop:
                return True

        # Check if inside
        if sRight < cRight and sLeft > cLeft and sTop < cTop and sBot > cBot:
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