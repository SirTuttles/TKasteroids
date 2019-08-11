"""The TKGFX module is a simple wrapper over the tkinter interface with
the intent of providing a more streamlined experience for use cases
dealing prodomenantly with graphics. It is tightly based around John Zelle's
graphics module."""

__version__ = "1.0.0"

import tkinter as tk
import time
import math

class Vect2D(object):
    """Basic 2 dimensional vector class."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, b):
        nx = -1
        ny = -1
        try:
            nx = self.x + b.x
            ny = self.y + b.y
            return Vect2D(nx, ny)
        except:
            pass
        try:
            nx = self.x + b
            ny = self.y + b
            return Vect2D(nx, ny)
        except Exception as e:
            raise ValueError("Vect2D given bad argument", e)
    
    def __mult__(self, b):
        pass


    def __str__(self):
        return str([self.x, self.y])

class Matrix2x2(object):
    def __init__(self):
        self.vals = self._set_vals()

    def rotation(self, deg):
        pass

    def _set_vals(self):
        vals = []
        for x in range(2):
            vals.append([])
            for y in range(2):
                vals[x].append(0)
        print(vals)
        return vals

    def __str__(self):
        vis = ""
        for x in self.vals:
            vis += "|" + str(x[0])
            vis += "," + str(x[1])
            vis += "|\n"
        return vis

class Transform(object):
    def __init__(self, width, height):
        self.x_max = width - 1
        self.y_max = height - 1
        self.auto_setting = 1
    
    def auto(self, vec):
        if self.auto_setting == 0:
            self.screen(vec)
        elif self.auto_setting == 1:
            self.y_flip(vec)
        elif self.auto_setting == 2:
            self.origin_center(vec)

    def screen(self, vec):
        pass

    def y_flip(self, vec):
        vec.y = self.y_max - vec.y

    def origin_center(self, vec):
        cx = self.x_max / 2
        cy = self.y_max / 2
        vec.x += cx
        vec.y += cy
        self.y_flip(vec)




class GWin(object):
    """GWin (Graphics Window) class intended to provide functionality
    heavily centered around custom draw graphics objects using
    the tkinter canvas object."""
    def __init__(self, width=640, height=480, title="Window"):
        self.root = tk.Tk()
        self.root.geometry("{0}x{1}".format(width, height))
        self.canvas = tk.Canvas(self.root, width=width, height=height)
        self.gobcont = []
        self.transform = Transform(width, height)
        self.transform.auto_setting = 0

        # setup canvas
        self.canvas.pack()
        self.canvas.config(bg="black", border=0, highlightthickness=0) 

    def run(self):
        self.root.mainloop()

    def setTransScreen(self):
        self.transform.auto_setting = 0

    def setTransYFlip(self):
        self.transform.auto_setting = 1

    def setTransOriginCenter(self):
        self.transform.auto_setting = 2


class GOB(object):
    """GOB (Graphics Object) to hold base attributes and functionallity
    for further objects to inherit from."""
    def __init__(self, gwin, **kw):
        self.gwin = gwin
        self.options = kw
        self.id = -1
        self.vects = []
        self.origin = None
        self.center = None

    def draw(self):
        if self.origin == None:
            self._gen_origin()
        self._draw()
        self.config(**self.options)
        self.is_drawn = True

    def undraw(self):
        self._undraw()
        self.id = -1

    def _draw(self):
        # Override me in subclass
        pass

    def _undraw(self):
        # Override me in subclass
        pass

    def config(self, **kw):
        can = self.gwin.canvas
        for key in kw:
            if key == "fill":
                can.itemconfig(self.id, fill=kw[key])
            elif key == "outline":
                can.itemconfig(self.id, outline=kw[key])
            else:
                raise tk.TclError("unknown option \"-{0}\"".format(key))
    
    def move(self, dx, dy):
        canv = self.gwin.canvas
        for v in self.vects:
            v.x += dx
            v.y += dy
        canv.coords(self.id, *self._unpack_vects())
        self._move(dx, dy)
    
    def _move(self, dx, dy):
        # Override me in subclass
        pass

    def rotate(self, angle):

        self._rotate()

    def _rotate(self, angle):
        # Override me in subclass
        pass

    def reflect(self):
        self._reflect()

    def _reflect(self):
        # Override me in sublass
        pass

    def _gen_origin(self):
        """Generates centered origin based on object's vectors.
        Also defines object's \"center.\" """
        pass

    def _unpack_vects(self):
        """Returns alternating list with alternating x and y values
        for all objects vectors. The returned coordinates are
        transformed coordinates set according to the gwin's current
        Transform object's setting. Primarily for tkinter.canvas.coords()"""
        unp = []
        for v in self.vects:
            nvec = Vect2D(v.x, v.y)
            self.gwin.transform.auto(nvec)
            unp.extend([nvec.x, nvec.y])
        return unp


class Point(GOB):
    def __init__(self, gwin, vect, **kw):
        super(Point, self).__init__(gwin, **kw)
        self.vects.extend([vect, Vect2D(vect.x+1, vect.y+1)])

    def _draw(self):
        canv = self.gwin.canvas
        self.id = canv.create_line(*self._unpack_vects())


class Line(GOB):
    def __init__(self, gwin, v1, v2, **kw):
        super(Line, self).__init__(gwin, **kw)
        self.vects.extend([v1, v2])
        
    def _draw(self):
        canv = self.gwin.canvas
        v1 = self.vects[0]
        v2 = self.vects[1]
        self.id = canv.create_line(self._unpack_vects())


class _BBox(GOB):
    def __init__(self, gwin, v1, v2, **kw):
        super(_BBox, self).__init__(gwin, **kw)
        self.vects.extend([v1,v2])


class Rectangle(_BBox):
    def _draw(self):
        canv = self.gwin.canvas
        v1 = self.vects[0]
        v2 = self.vects[1]
        self.id = canv.create_rectangle(self._unpack_vects())


class Oval(_BBox):
    def _draw(self):
        canv = self.gwin.canvas
        v1 = self.vects[0]
        v2 = self.vects[1]
        self.id = canv.create_oval(self._unpack_vects())


class Circle(_BBox):
    def __init__(self, gwin, cen, rad, **kw):
        v1 = Vect2D(cen.x - rad, cen.y - rad)
        v2 = Vect2D(cen.x + rad, cen.y + rad)
        super(Circle, self).__init__(gwin, v1, v2, **kw)

    def _draw(self):
        canv = self.gwin.canvas
        self.id = canv.create_oval(self._unpack_vects())


def main():
    gwin = GWin()
    gwin.setTransOriginCenter()
    r = 200
    for i in range(360):
        x = math.cos(i) * r
        y = math.sin(i) * r
        p = Point(gwin, Vect2D(x,y), fill="white")
        p.draw()
    mm = Matrix2x2()
    print(mm)
    gwin.run()

if __name__ == "__main__":
    main()
