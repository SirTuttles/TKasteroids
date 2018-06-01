"""Asteroids!"""

__version__ = '0.1.0'

import gfx
import math

        
class Game(object):
    def __init__(self, master):
        self.master = master
        
        # PixelGrid
        self.pg = gfx.PixelGrid(self.master)
        self.pg.pack(fill='both', expand=1)
        self.pg.config(border=0, highlightthickness=0, bg='black')
        
        # Stopcodes
        self.sc_ptest = False

    def start(self):
        pass
        

class Player(object):
    def __init__(self, name):
        self.name = name
        self.score = 0
        
    def save(self):
        pass
        
class Projectile(object):
    def __init__(self, ang, vel, x, y):
        self.theta = (ang * math.pi / 180) % 360
        self.xvel = vel * math.cos(self.theta)
        self.yvel = vel * math.sin(self.theta)
        self.x = x
        self.y = y
        self.sx = x
        self.sy = y
        self.t = 0.001
        self.grav = 0
    
    def update(self, t=None):
        # Interpretor has not read self.__init__ yet (self.t not yet defined)
        if t == None:
            t = self.t

        self.x = self.x + self.xvel * t
        yvel1 = self.yvel - self.grav * t
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
        

    def update(self, t=None):
        Projectile.update(self, t)
        

  

class Ship(object):
    def __init__(self, pg, x, y):
        self.pg = pg
        
        self.max_velocity = 30
        self.incVel = 1
        self.incRot = 4
        self.vproj = VProjectile(pg, self.shape, 0, 0, x, y)

        # Helpers to check current movement
        self.rotating = False
        self.rotating_dir = 0
        self.accelerating = False
        self.acceleration_dir = 0
        
        # Binds
        self.pg.master.bind('<Left>', self.rotation)
        self.pg.master.bind('<Right>', self.rotation)
        self.pg.master.bind('<Up>', self.acceleration)
        self.pg.master.bind('<Down>', self.acceleration)
        self.pg.master.bind('<KeyRelease-Left>', self.rotation)
        self.pg.master.bind('<KeyRelease-Right>', self.rotation)
        self.pg.master.bind('<KeyRelease-Up>', self.acceleration)
        self.pg.master.bind('<KeyRelease-Down>', self.acceleration)
        
        # Stop codes
        self.sc_rotating = None
        self.sc_accelerating = None
        
    def rotation(self, event):
        if event.type == '3':
            self.pg.after_cancel(self.sc_rotating)
            self.rotating = False
            return False
            
        if not self.rotating:
            if event.keysym == 'Left':
                self.rotating_dir = -self.incRot
            elif event.keysym == 'Right':
                self.rotating_dir = self.incRot
            else:
                pass
                
            self._rotation()
    
    def _rotation(self):
        self.vproj.addAngle(self.rotating_dir)
        self.vproj.rotate(self.rotating_dir)
        self.rotating = True
        self.sc_rotating = self.pg.after(15, self._rotation)

    def acceleration(self, event):
        if event.type == '3':
            self.pg.after_cancel(self.sc_accelerating)
            self.accelerating = False
            return False
        if not self.accelerating:
            if event.keysym == 'Up':
                self.acceleration_dir = self.incVel
            elif event.keysym == 'Down':
                self.acceleration_dir = -self.incVel
            
            self._acceleration()

    def _acceleration(self):
        self.vproj.addVel(self.acceleration_dir)
        self.sc_accelerating = self.pg.after(15, self._acceleration)
        self.accelerating = True
                
    def getX(self):
        return self.vproj.getX()
        
    def getY(self):
        return self.vproj.getY()
    
    def setPos(self, x, y):
        self.vproj.setPos(x, y)
        
    def setX(self, x):
        self.vproj.setX(x)
        
    def setY(self, y):
        self.vproj.setY(y)
        

def main():
    root = gfx.Root()
    root.geometry('800x800')
    root.configure(bg='black')
    game = Game(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()