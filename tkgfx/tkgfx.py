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
    
    def __sub__(self, b):
        nx = -1
        ny = -1
        try:
            nx = self.x - b.x
            ny = self.y - b.y
            return Vect2D(nx, ny)
        except:
            pass
        try:
            nx = self.x - b
            ny = self.y - b
            return Vect2D(nx, ny)
        except Exception as e:
            raise ValueError("Vect2D given bad argument", e)
    

    def __mul__(self, b):
        try:
            vec = Vect2D(0,0)
            vec.x = (self.x * b[0][0]) + (self.y * b[1][0])
            vec.y = (self.x * b[0][1]) + (self.y * b[1][1])
            return vec
        except:
            pass
        try:
            vec = Vect2D(0,0)
            vec.x = self.x * b
            vec.y = self.y * b
            return vec
        except:
            raise ValueError("Vect2D cannot multiply by {0}".format(b.__name__))


    def __str__(self):
        return str([self.x, self.y])

    def copyFromVec(self, vect):
        self.x = vect.x
        self.y = vect.y


class Matrix2x2(object):
    def __init__(self):
        self.matrix = self._make_matrix()

    def __getitem__(self, val):
        return self.matrix[val]

    def rotation(self, deg):
        mat = self.matrix
        theta = math.radians(deg)
        mat[0][0] = math.cos(theta)
        mat[0][1] = math.sin(theta)
        mat[1][0] = -math.sin(theta)
        mat[1][1] = math.cos(theta)

    def _make_matrix(self):
        vals = []
        for x in range(2):
            vals.append([])
            for y in range(2):
                vals[x].append(0)
        return vals

    def __str__(self):
        vis = ""
        for x in self.matrix:
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

class TkTask(object):
    def __init__(self, gwin, ms, callback, *args, **kw):
        self.interval = ms
        self.callback = callback
        self.gwin = gwin
        self.args = args
        self.recurring = False
        self.config(**kw)
        self.stopcode = None
        self.run()

    def config(self, **kw):
        if "recurring" in kw:
            if kw["recurring"] == True:
                self.recurring = True
            elif kw["recurring"] == False:
                self.recurring = False
            else:
                raise ValueError("recurring cannot be:" + kw["recurring"])

    def run(self):
        if self.recurring:
            self.callback(*self.args)
            self.stopcode = self.gwin.root.after(self.interval, self.run)
        else:
            self.stopcode = self.gwin.root.after(self.time, self.callback, *self.args)

    def stop(self):
        self.gwin.root.after_cancel(self.stopcode)


class GWin(object):
    """GWin (Graphics Window) class intended to provide functionality
    heavily centered around custom draw graphics objects using
    the tkinter canvas object. Subclass and override onUpdate() method."""
    def __init__(self, width=640, height=480, title="Window"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("{0}x{1}".format(width, height))
        self.canvas = tk.Canvas(self.root, width=width, height=height)
        self.gobcont = []
        self.tasks = []
        self.transform = Transform(width, height)
        self.transform.auto_setting = 0

        # setup canvas
        self.canvas.pack()
        self.canvas.config(bg="black", border=0, highlightthickness=0) 

        # TK Loop vars
        self.tk_interval = 16 #ms
        self.tk_lastrun = 0

    def run(self):
        self._tkloop()
        self.root.mainloop()

    def setTransScreen(self):
        self.transform.auto_setting = 0

    def setTransYFlip(self):
        self.transform.auto_setting = 1

    def setTransOriginCenter(self):
        self.transform.auto_setting = 2

    def _tkloop(self):
        self.tk_lastrun = time.time()
        self.onUpdate()
        self.root.after(self.tk_interval, self._tkloop)

    def onUpdate(self):
        #override me in subclass
        pass

    def addTask(self, ms, callback, *args, **kw):
        task = TkTask(ms, callback, *args, **kw)
        self.tasks.append(task)
        return task

    def addEvent(self, etype, callback):
        self.root.bind(etype, callback)

    def removeTask(self, stopcode):
        for task in self.tasks[:]:
            if stopcode == task.stopcode:
                task.stop()
                self.tasks.remove(task)



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
        self.gwin.gobcont.append(self)

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
        if len(kw) == 0:
            self.default_config()

    def default_config(self):
        # Override me in subclass
        pass

    def move(self, dx, dy):
        canv = self.gwin.canvas
        self.origin += Vect2D(dx, dy)
        self.center += Vect2D(dx, dy)
        for v in self.vects:
            v.x += dx
            v.y += dy
        canv.coords(self.id, *self._unpack_vects())
        self._move(dx, dy)
    
    def _move(self, dx, dy):
        # Override me in subclass
        pass

    def rotate(self, angle):
        canv = self.gwin.canvas
        mat = Matrix2x2()
        mat.rotation(angle)
        for vec in self.vects:
            vec.copyFromVec(vec - self.origin)
            vec.copyFromVec(vec * mat)
            vec.copyFromVec(vec + self.origin)
        canv.coords(self.id, *self._unpack_vects())
        

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
        c = Vect2D(0,0)
        xmax = self.vects[0].x
        xmin = xmax
        ymax = self.vects[1].y
        ymin = ymax
        for v in self.vects:
            if v.x > xmax:
                xmax = v.x
            elif v.x < xmin:
                xmin = v.x
            if v.y > ymax:
                ymax = v.y
            elif v.y < ymin:
                ymin = v.y

        xmid = (xmax - xmin) / 2 + xmin
        ymid = (ymax - ymin) / 2 + ymin
        self.origin = Vect2D(xmid, ymid)
        self.center = Vect2D(xmid, ymid)


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

    def default_config(self):
        self.config(fill="green")


class Line(GOB):
    def __init__(self, gwin, v1, v2, **kw):
        super(Line, self).__init__(gwin, **kw)
        self.vects.extend([v1, v2])
        
    def _draw(self):
        canv = self.gwin.canvas
        v1 = self.vects[0]
        v2 = self.vects[1]
        self.id = canv.create_line(self._unpack_vects())

    def default_config(self, **kw):
        self.config(fill="green")

class _BBox(GOB):
    def __init__(self, gwin, v1, v2, **kw):
        super(_BBox, self).__init__(gwin, **kw)
        self.vects.extend([v1,v2])

    def default_config(self):
        self.config(fill ="black", outline="green")


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
    rect = Rectangle(gwin,Vect2D(-400,-400),Vect2D(400,400))
    rect.draw()
    oval = Oval(gwin, Vect2D(40,40), Vect2D(80,80))
    oval.draw()
    task = gwin.addTask(gwin, 1, oval.rotate, 1, recurring=True)
    gwin.run()

if __name__ == "__main__":
    main()
