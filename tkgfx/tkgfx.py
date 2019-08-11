"""The TKGFX module is a simple wrapper over the tkinter interface with
the intent of providing a more streamlined experience for use cases
dealing prodomenantly with graphics."""

__version__ = "1.0.0"

import tkinter as tk
import time


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
           
    def __str__(self):
        return str([self.x, self.y])


class GWin(object):
    def __init__(self, width=640, height=480, title="untitled"):
        self.root = tk.Tk()
        self.root.geometry("{0}x{1}".format(width, height))
        self.canvas = tk.Canvas(self.root, width=width, height=height)
        self.gobcont = []

        # setup canvas
        self.canvas.pack()
        self.canvas.config(bg="black", border=0, highlightthickness=0)


        # tk stop codes
        self.sc_tkloop = None
        

    def run(self):
        self.root.mainloop()


class GOB(object):
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
        unp = []
        for v in self.vects:
            unp.extend([v.x, v.y])
        return unp

class Point(GOB):
    def __init__(self, gwin, vect, **kw):
        super(Point, self).__init__(gwin, **kw)
        self.vects.append(vect)

    def _draw(self):
        canv = self.gwin.canvas
        x1 = self.vects[0].x
        y1 = self.vects[0].y
        x2 = x1+1
        y2 = y1+1
        self.id = canv.create_line(x1,y1,x2,y2)


class Line(GOB):
    def __init__(self, gwin, v1, v2, **kw):
        super(Line, self).__init__(gwin, **kw)
        self.vects.extend([v1, v2])
        
    def _draw(self):
        canv = self.gwin.canvas
        v1 = self.vects[0]
        v2 = self.vects[1]
        self.id = canv.create_line(v1.x, v1.y, v2.x, v2.y)


class _BBox(GOB):
    def __init__(self, gwin, v1, v2, **kw):
        super(_BBox, self).__init__(gwin, **kw)
        self.vects.extend([v1,v2])

class Rectangle(_BBox):
    def _draw(self):
        canv = self.gwin.canvas
        v1 = self.vects[0]
        v2 = self.vects[1]
        self.id = canv.create_rectangle(v1.x, v1.y, v2.x, v2.y)

class Circle(_BBox):
    def _draw(self):
        canv

def main():
    gwin = GWin()
    rec = Line(gwin, Vect2D(0,0), Vect2D(60,60), fill = "white")
    rec.draw()
    rec.move(0,50)
    gwin.run()

if __name__ == "__main__":
    main()
