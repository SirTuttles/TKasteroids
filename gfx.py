"""A wrapper over TKinter modeled after John Zelle's Graphics.py"""

__version__ = '0.9.1'

# Python 2 compatibility
try:
    import tkinter as tk
except:
    import Tkinter as tk

import math


class GraphicsError(Exception):
    """Generic exception class for graphics errors."""
    pass
    
# GraphicsError Constants
OBJ_ALREADY_DRAWN = "Object is already drawn"
OBJ_NOT_DRAWN = "Opperation attempted on undrawn object"
DRAWN_ON_CLOSED = "Cannot draw on a closed window"
INVALID_CONFIG_OPTION = "Attempted to use invalid config option"

class Root(tk.Tk):
    def __init__(self, title='Root', width=800, height=600, **options):
        super().__init__(*options)
        self.title(title)
        self.geometry('%sx%s' % (width, height))
        #self.resizable(0,0)
        # Default Binds
        self.bind('<Escape>', self._on_closing) 
        
        # Protocols
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _on_closing(self, event=None):
        self.destroy()
        
        
class Window(tk.Tk):
    def __init__(self, title='Window', width=800, height=600, **options):
        super().__init__(*options)


class Transform(object):
    """Handles 2-D coordinate transformations"""
    
    def __init__(self, w, h, xlow, ylow, xhigh, yhigh):
        xspan = (xhigh - xlow)
        yspan = (yhigh - ylow)
        self.xbase = xlow
        self.ybase = yhigh
        self.xscale = xspan/float(w-1)
        self.yscale = yspan/float(h-1)
        
    def screen(self, x, y):
        xs = (x-self.xbase) / self.xscale
        ys = (self.ybase-y) / self.yscale
        return int(xs+0.5), int(ys+0.5)
        
    def world(self, xs, ys):
        x = xs * self.xscale + self.xbase
        y = self.ybase - ys * self.yscale
        return x, y      
        
        
class PixelGrid(tk.Canvas):
    """A tkinter.Canvas() that has been abstracted supplied with various
    helpful methods."""
    
    def __init__(self, master, width=800, height=600):
        
        tk.Canvas.__init__(self, master, width=width, height=height)
        self.master = master
        self.bind('<Configure>', self._onconfigure)
        self.config(
            background = 'black',
            highlightthickness=0,
            border=0
        )
        self.w = self.winfo_reqwidth()
        self.h = self.winfo_reqheight()
        self.center = Point(self.w/2, self.h/2)
        print(self.w)
        self.trans = None
        self.objects = []
        
    def _onconfigure(self, event):
        self.w = self.winfo_width()
        self.h = self.winfo_height()
        if self.trans:
            self.trans.w = self.w
            self.trans.h = self.h
        self.redraw()
               
    def setCoords(self, xlow, ylow, xhigh, yhigh):
        self.trans = Transform(self.w, self.h, xlow, ylow, xhigh, yhigh)
        
    def move(self, shape, dx, dy):
        tk.Canvas.move(self, shape, dx, dy)

    def getWidth(self):
        return self.w
        
    def getHeight(self):
        return self.h
        
    def getCenter(self):
        return self.center
        
    def place(self, shape, x, y):
        new = []
        dx = 0
        dy = 0
        
    def toScreen(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.screen(x,y)
        return x,y
            
    def toWorld(self, xs, ys):
        trans = self.trans
        if trans:
            return self.trans.world(xs, ys)
        else:
            return xs, ys
        
    def redraw(self):
        for object in self.objects[:]:
            object.undraw()
            object.draw(self)
        
# Dictionary of default options to configure a GraphicsObject with
DEFAULT_CONFIG = {
    "fill":"",
    "outline":"white",
    "width":"1",
    "arrow":"none",
    "text":"",
    "justify":"center",
    "font": ("helvetica", 12, "normal")}
    

class GraphicsObject(object):
    """A generic graphics object intended to be subclassed"""
    def __init__(self, options):
        self.pg = None
        self.id = None
        self.origin = None
        self.points = None
        self.center = None
        
        config = {}
        for option in options:
            config[option] = DEFAULT_CONFIG[option]
        self.config = config
    
    def undraw(self):
        if self.pg and self.id:
            self.pg.delete(self.id)
            self.id = None
            self.pg.objects.remove(self)
    
    def draw(self, pg):
        if self.pg and self.id:
            raise(GraphicsError(OBJ_ALREADY_DRAWN))
        self.pg = pg
        self.id = self._draw(pg, self.config)
        pg.objects.append(self)
            
        
    def _draw(self, pg, options):
        """Draws an object with the provided options and returns
        the objects id"""
        pass # Override in sublcass
    
    def isDrawn(self):
        if self.id:
            return True
        return False
    
    def move(self, dx, dy):
        """Moves object in given distances"""
        # Points need to be moved, but aren't drawn normally?
        #if not self.id:
        #    raise(GraphicsError(OBJ_NOT_DRAWN))
            
        self._move(dx, dy)
        pg = self.pg
        if pg:
            trans = pg.trans
            if trans:
                x = dx / trans.xscale
                y = -dy / trans.yscale
            else:
                x = dx
                y = dy
            self.pg.move(self.id, x, y)   

        # Update origin position
        if self.origin:
            self.origin.move(dx, dy)
            
        if self.center:
            self.center.move(dx, dy)
                
    def rotate(self, angle):
        if not self.id:
            raise(GraphicsError(OBJ_NOT_DRAWN))
        pg = self.pg
        if pg:
            origin = self.origin
            theta = angle * math.pi / 180 
            
            new_coords = []
            new_points = []
            
            for point in self.points:
                # Rotate point
                x = point.getX() - origin.getX()
                xtemp = x
                y = point.getY() - origin.getY()
                x = x*math.cos(theta)-y*math.sin(theta)
                y = xtemp*math.sin(theta)+y*math.cos(theta)
                x, y = x + origin.getX(), y + origin.getY()
                
                # Append new point
                new_points.append(Point(x,y))     
                
                # Append new coord from point
                new_coords.extend(pg.toScreen(x,y))
            
            # Update self.points
            self.points = new_points
            
            # Apply new coordinates
            self.pg.coords(self.id, *new_coords)
 
    def setFill(self, color):
        self._reconfig('fill', color)
 
 
    def resize(self, percentage):
        
        pass
        
    def _reconfig(self, option, setting):
        if option not in self.config:
            raise(GraphicsError(INVALID_CONFIG_OPTION))
        options = self.config
        options[option] = setting
        if self.pg:
            self.pg.itemconfig(self.id, options)
    
    def getPoints(self):
        return self.points
       
    def getCenter(self):
        return self.center
       
    def findCenter(self):
        points = self.points
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
        return Point(cx, cy)
    
    
class Point(GraphicsObject):
    def __init__(self, x, y):
        super().__init__(['fill'])
        self.x = x
        self.y = y
        
        
    def getX(self): return self.x
    def getY(self): return self.y
    
    def getPos(self):
        return [self.x, self.y]
    
    def _draw(self, pg, options):
        x, y = pg.toScreen(self.x, self.y)
        return pg.create_line(x, y, x+1, y+1, options)
        
    def clone(self):
        cloned = Point(self.x, self.y)
        cloned.config = self.config.copy()
        return cloned
        
    def _move(self, dx, dy):
        self.x += dx
        self.y += dy
       
  
class Origin(Point):
    """A Point with some small additions & modifications"""
    def __init__(self, x, y):
        super().__init__(x, y)
    
    def _draw(self, pg, options):
        x, y = pg.toScreen(self.x, self.y)
        return pg.create_oval(x-5, y-5, x+5, y+5, outline='red')
  
  
class _BBox(GraphicsObject):
    def __init__(self, origin, p1, p2, options=['outline',"width","fill"]):
        super().__init__(options)
        self.points = [p1.clone(), p2.clone()]
        self.width = abs(p2.getX() - p1.getX())
        self.height = abs(p2.getY() - p1.getY())
        self.center = self.findCenter()
        if origin == 'center':
            self.origin = self.center.clone()
        else:
            self.origin = origin
        
    def _move(self, dx, dy):
        p1 = self.points[0]
        p2 = self.points[1]
        p1.x += dx
        p1.y += dy
        p2.x += dx
        p2.y += dy

    def getP1(self):
        return self.points[0].clone()
        
    def getP2(self):
        return self.points[1].clone()
        
    def getOrigin(self):
        return self.origin
        
    def getWidth(self):
        return self.width
        
    def getHeight(self):
        return self.height
        
  
class Rectangle(_BBox):
    def __init__(self, origin, p1, p2):
       super().__init__(origin, p1, p2)

    def _draw(self, pg, options):
        p1 = self.points[0]
        p2 = self.points[1]
        x1,y1 = pg.toScreen(p1.x, p1.y)
        x2, y2 = pg.toScreen(p2.x, p2.y)

        return pg.create_rectangle(x1, y1, x2, y2, options)
       
       
class Line(_BBox):
    def __init__(self, origin, p1, p2):
        super().__init__(origin, p1, p2, ["arrow","fill","width"])
        
    def _draw(self, pg, options):
        p1 = self.points[0]
        p2 = self.points[1]
        x1, y1 = pg.toScreen(p1.x, p1.y)
        x2, y2 = pg.toScreen(p2.x, p2.y)
        
        return pg.create_line(x1, y1, x2, y2, options)
       
       
class Oval(_BBox):
    def __init__(self, origin, p1, p2):
        super().__init__(origin, p1, p2)
       
    def _draw(self, pg, options):
        p1 = self.points[0]
        p2 = self.points[1]
        x1, y1 = pg.toScreen(p1.x, p1.y)
        x2, y2 = pg.toScreen(p2.x, p2.y)
        
        return pg.create_oval(x1, y1, x2, y2, options)
        
  
class Circle(Oval):
    def __init__(self, origin, center, r):
        p1 = Point(center.x - r, center.y - r)
        p2 = Point(center.x + r, center.y + r)
        super().__init__(center, p1, p2)
        self.origin = origin
        self.radius = r
        
    def _draw(self, pg, options):
        cx, cy = pg.toScreen(self.origin.x, self.origin.y)
        r = self.radius
        return pg.create_oval(cx-r, cy-r, cx+r, cy+r, options)
    
  
class Polygon(GraphicsObject):
    def __init__(self, origin, *points):
        super().__init__(['fill', 'outline'])
        self.points = points
        self.center = self.findCenter()
        if origin == 'center':
            self.origin = self.center.clone()
        else:
            self.origin = origin
        
    def _draw(self, pg, options):
        coords = []
        for point in self.points:
            x, y = pg.toScreen(point.getX(), point.getY())
            coords.extend([x, y])
        return self.pg.create_polygon(*coords, options)
        
    def _move(self, dx, dy):
        for point in self.points:
            point.move(dx, dy)


class PolyCircle(Polygon):
    def __init__(self, origin, center, r, vertices):
        points = self._getCirclePoints(center, r, vertices)
        super().__init__(origin, *points)
            
    def _getCirclePoints(self, center, r, vertices):
        per = 360 // vertices
        points = []
        for i in range(360):
            theta = i * math.pi / 180
            xmag = r * math.cos(theta)
            ymag = r * math.sin(theta)
            
            x = xmag + center.x
            y = ymag + center.y
            
            if i % per == 0:
                points.append(Point(x, y))
              
        return points
        
    def newVertCount(self, vertices):
        self.pg.coords(self.id, 30, 40, 30, 50, 40, 50)
        
        
class ExampleApp(object):
    def __init__(self, master):
        self.master = master
        self.pg = PixelGrid(master)
        self.pg.pack(fill='both', expand=1)
        self.pg.setCoords(0, 0, self.pg.getWidth()-1, self.pg.getHeight()-1)
        self.poly = Polygon(
            Point(90,50),
            Point(20,25),
            Point(30,105), 
            Point(50,0))
        self.poly.draw(self.pg)
        
        self.rec2 = Rectangle(Origin(100, 100), Point(0, 0), Point(200, 200))
        self.rec2.draw(self.pg)
        self.rec2.setFill('blue')
            
        self.rec2.origin.draw(self.pg)
        self.rec4 = Polygon(Origin(250,200), Point(200,300), Point(300,300), Point(300,100), Point(200,100))
        self.rec4.draw(self.pg)
        self.rec4.origin.draw(self.pg)
        self.circ = Circle(Origin(200, 300), Point(20, 20), 20)
        self.circ.draw(self.pg)
        
        # Poly Circles
        self.polycirc1 = PolyCircle(Origin(100,100), Point(100,100), 30, 20)
        self.polycirc1.origin.draw(self.pg)
        self.polycirc1.draw(self.pg)
        
        self.polycirc2 = PolyCircle(Origin(100,160), Point(100,160), 20, 7)
        self.polycirc2.origin.draw(self.pg)
        self.polycirc2.draw(self.pg)
        
        self.polycirc3 = PolyCircle(Origin(100,210), Point(100,210), 15, 5)
        self.polycirc3.origin.draw(self.pg)
        self.polycirc3.draw(self.pg)
        
        self.polycirc4 = PolyCircle(Origin(100,250), Point(100,250), 10, 3)
        self.polycirc4.origin.draw(self.pg)
        self.polycirc4.draw(self.pg)
        
        self.polycirc5 = PolyCircle(Origin(250, 340), Point(270,250), 10, 9)
        self.polycirc5.origin.draw(self.pg)
        self.polycirc5.draw(self.pg)
        
        self.rot_inc = 0.1
        self.mov_xinc = 0.5
        self.mov_yinc = 0.5
        
        
        self.master.bind('<Left>', self.rotation)
        self.master.bind('<Right>', self.rotation)
        self.pg.redraw()
        self.moving()
        
    def moving(self):
        origin = self.rec2.getOrigin()
        ox, oy = self.pg.toScreen(origin.getX(), origin.getY())

        if ox > self.pg.getWidth():
            self.mov_xinc = -self.mov_xinc
        elif ox < 0:
            self.mov_xinc = -self.mov_xinc
            
        if oy > self.pg.getHeight():
            self.mov_yinc = -self.mov_yinc
        elif oy < 0:
            self.mov_yinc = -self.mov_yinc
        
        # Move
        self.rec2.move(self.mov_xinc, self.mov_yinc)
        self.poly.move(self.mov_xinc, self.mov_yinc)
        self.rec4.move(self.mov_xinc, self.mov_yinc)
        self.circ.move(self.mov_xinc, self.mov_yinc)
        
        # Rotate
        self.rec2.rotate(self.rot_inc)
        self.poly.rotate(self.rot_inc)
        self.rec4.rotate(self.rot_inc)
        self.circ.rotate(self.rot_inc)
        self.polycirc1.rotate(self.rot_inc+3)
        self.polycirc2.rotate(self.rot_inc+3)
        self.polycirc3.rotate(self.rot_inc+3)
        self.polycirc4.rotate(self.rot_inc+3)
        self.polycirc5.rotate(self.rot_inc+3)
        
        self.pg.after(16, self.moving)
        
    def rotation(self, event=None):
        if event:
            if event.keysym == 'Left':
                self.poly.rotate(-self.rot_inc)
                self.rec2.rotate(-self.rot_inc)
                self.rec4.rotate(-self.rot_inc)
                self.circ.rotate(-self.rot_inc)
            if event.keysym == 'Right':
                self.poly.rotate(self.rot_inc)
                self.rec2.rotate(self.rot_inc)
                self.rec4.rotate(self.rot_inc)
                self.circ.rotate(self.rot_inc)

                
def main():
    # Basic example
    root = Root('GFX Example')
    ExampleApp(root)
    root.mainloop()
        
if __name__ == '__main__':
    main()