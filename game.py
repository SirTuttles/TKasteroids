"""Asteroids!"""

__version__ = '0.1.0'

from gfx import *
import math
import time
        
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
        
        
        # Ship
        self.ship = Ship(self.pg, 15, 15)
        
        # Test VProjectile
        shape = Circle(Origin(0,0), Point(0,0), 10)
        shape.draw(self.pg)
        self.testVproj = VProjectile(self.pg, shape, 45, 20, 0, 0)
        
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
        self.handle_offscreen_objects()
        #self.locationCheck()
                
        endtime = time.time()
        print(round(endtime - self.gl_last_endtime, 3))
        self.gl_last_endtime = endtime
        self.pg.after(16, self.gameloop)
       
        
    def update_projectiles(self):
        # Ship
        self.ship.update(0.08)
        if self.ship.isAccelerting():
            self.ship.accel()
        if self.ship.isRotating():
            self.ship.rotate()
        
        #self.testVproj.update(0.1)
     
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
                  
    def handle_asteroid_generation(self):
        ast = Asteroid(self, x, y, ang, vel)
    
    def debug(self):
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
        self.theta = (ang * math.pi / 180) % 360
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
        self.last_pos = [x, y]

        self.debugging = False
        # Debugging attributes
        self.real_pathHist = []
        self.shape_pathHist = []
        self.vis_vel = None 
        
    def update(self, t=None):
        super().update(t)
        x0, y0 = self.last_pos[0], self.last_pos[1]
        dx, dy = self.x - x0, self.y - y0
        self.shape.move(dx, dy)
        self.last_pos = [self.x, self.y]
        
        # Debugging Visualizers
        if self.debugging:
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
            
    def rotate(self, angle):
        self.shape.rotate(-angle)
        self.addAngle(angle)
        
    def debug(self):
        self.debugging = True
    
class Ship(VProjectile):
    def __init__(self, pg, x, y):
        
        shape = Polygon(
            Origin(x, y),
            Point(10, 10),
            Point(30, 15),
            Point(10, 20))
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
     
        # Binds
        self.pg.master.bind('<Up>', self.acceleration)
        self.pg.master.bind('<KeyRelease-Up>', self.acceleration)
        self.pg.master.bind('<Down>', self.acceleration)
        self.pg.master.bind('<KeyRelease-Down>', self.acceleration)
        self.pg.master.bind('<Left>', self.rotation)
        self.pg.master.bind('<KeyRelease-Left>', self.rotation)
        self.pg.master.bind('<Right>', self.rotation)
        self.pg.master.bind('<KeyRelease-Right>', self.rotation)
    
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
        


def main():
    root = Root('TKasteroids')
    game = Game(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()