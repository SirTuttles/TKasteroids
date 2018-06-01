import tkinter as tk
import math

class PixelGrid(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        self.master = master
        self.w = 0
        self.h = 0
        self.bind('<Configure>', self._onconfigure)
        
    def _onconfigure(self, event):
        self.w = self.winfo_width()
        self.h = self.winfo_height()
        print(self.w,self.h)
        
    def create_circle(self, x, y, r, **args):
        return self.create_oval(x-r, y-r, x+r, y+r, **args)
       
    def move(self, shape, dx, dy):
        dy = -dy
        tk.Canvas.move(self, shape, dx, dy)

    def getWidth(self):
        return self.w
        
    def getHeight(self):
        return self.h
        
    def place(self, shape, x, y):
        new = []
        dx = 0
        dy = 0
        

class Game(object):
    def __init__(self, master):
        self.master = master
        
        # PixelGrid
        self.pg = PixelGrid(self.master)
        self.pg.pack(fill='both', expand=1)
        self.pg.config(border=0, highlightthickness=0, bg='black')
        
        # Stopcodes
        self.sc_ptest = False

        # DELETE ME #
        self.w = self.pg.winfo_reqwidth()
        self.h = self.pg.winfo_reqheight()
        self.ship = Ship(self.pg, 10, 10)
        self.test()
        # DELETE ME #
        
        
    def test(self):
        self.ship.vproj.update(0.1)
        if self.ship.getVX() > self.pg.getWidth() + 15:
            self.ship.setX(-15)
            
        if self.ship.getVX() < -15:
            self.ship.setX(self.pg.getWidth() + 15)
        
        if self.ship.getVY() > self.pg.getHeight() + 15:
            print(self.ship.getY())
            self.ship.setY(-15)
            
        if self.ship.getVY() < -15:
            self.ship.setY(-self.pg.getHeight())
        print(self.ship.getY(), self.ship.getVY())
        self.sc_ptest = self.master.after(15, self.test) 

    def start(self):
        pass
        

class Player(object):
    def __init__(self, name):
        self.name = name
        self.score = 0
        
    def save(self):
        pass

        
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def getX(self): return self.x
    def getY(self): return self.y
    
        
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
        
        
class VProjectile(Projectile):
    def __init__(self, pg, shape, ang, vel, x, y):
        Projectile.__init__(self, ang, vel, x, y)
        self.pg = pg
        w = self.pg.winfo_reqwidth()
        h = self.pg.winfo_reqheight()
        self.vis = shape
        self.vx = x
        self.vy = y
        self.origin = [x, y]
        
        self.pg.bind('<Button-1>', lambda: self.setY(0))
        
        # For updating vis location
        self.last_pos = [x, y]
        
        # VISUALIZATIONS
        self.debugging = True
        
        # Direction Vector
        self.dir_vec = None
        
        # Path History
        self.path_history = []
        
    def getPoints(self):
        points = []
        isX = True
        x = 0
        y = 0
        for coord in self.pg.coords(self.vis):
            if isX:
                isX = False
                x = coord
            else:
                isX = True
                y = coord
                points.append([x, y])
        
        return points

    def update(self, t=None):
        Projectile.update(self, t)
        
        curpos = self.getPos()
        dx = curpos[0] - self.last_pos[0]
        dy = curpos[1] - self.last_pos[1]
        self.pg.move(self.vis, dx, dy)
        self.last_pos = curpos
        
        self.vx = self.x
        self.vy = self.vy - dy
        
        self.origin = [self.vx,self.vy]

        # Update Debugging visualizations
        if self.debugging:
            # Direction vector
            if self.dir_vec != None:
                self.pg.delete(self.dir_vec)
            p1 = [self.vx, self.vy]
            p2 = [self.vx+self.xvel, self.vy+-self.yvel]
            self.dir_vec = self.pg.create_line(*p1, *p2, fill='red')
            
            # Path history
            if len(self.path_history) == 100:
                rmv = self.path_history.pop(0)
                self.pg.delete(rmv)
            self.path_history.append(self.pg.create_line(
                self.vx, self.vy, self.vx+1, self.vy+1, fill='lightgreen'
                ))
        
    def getVisPos(self):
        return [self.vx, self.vy]  
        
    def rotate(self, amount):
        theta = amount * math.pi / 180 
        new_points = []
        for point in self.getPoints():
            x = point[0] - self.origin[0]
            xtemp = x
            y = point[1] - self.origin[1]
            x = x*math.cos(theta)-y*math.sin(theta)
            y = xtemp*math.sin(theta)+y*math.cos(theta)
            x = x + self.origin[0]
            y = y + self.origin[1]
            new = [x,y]
            
            new_points.append(new)
        self.pg.coords(self.vis, *self.pointsToCoords(new_points))
        
    def pointsToCoords(self, points):
        coords = []
        for point in points:
            coords.append(point[0])
            coords.append(point[1])
            
        return coords
  
    def getVX(self):
        return self.vx
        
    def getVY(self):
        return self.vy
    
    
class Ship(object):
    def __init__(self, pg, x, y):
        self.pg = pg
        self.shape = self.pg.create_polygon(
            x-9, y-6, 
            x+9, y, 
            x-9, y+6,
            outline='white'
        )
        
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
        
    def getVX(self):
        return self.vproj.getVX()
        
    def getVY(self):
        return self.vproj.getVY()
    
    def setPos(self, x, y):
        self.vproj.setPos(x, y)
        
    def setX(self, x):
        self.vproj.setX(x)
        
    def setY(self, y):
        self.vproj.setY(y)
        
    
        
def main():
    root = tk.Tk()
    root.geometry('800x800')
    root.configure(bg='black')
    game = Game(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()