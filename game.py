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
        self.gl_exec_time = 0
        
        # Blackholes
        self.bh_gen_freq = 1 # seconds
        self.bh_last_gen_time = time.time()
        self.bh_max = 2
        self.bh_count = 0
        
        # Asteroids
        self.ast_gen_freq = 0.1 #seconds
        self.ast_last_gen_time = time.time()
        self.ast_update_i = 0
        self.ast_max = 20
        self.ast_count = 0
        
        # Shots
        self.shot_max_dist = 200
        
        # Object container
        self.objects = []
        self.new_object_queue = []
        self.remove = []
        
        # Stopcodes
        self.sc_gameloop = None

        # Toggle Debugging Features per object
        #self.debug()
        #self.ship.debug()
        
        # Player
        self.player = Player('AAA')
        
        # Player Lives
        self.player_lives_vis_container = []
        self.updatePlayerLives()
        
        # Player Score
        px, py = self.pg.getWidth() / 2, self.pg.getHeight()
        self.txt_score_title = Text(Origin(px, py), Point(px, py-20), 'Score')
        self.txt_score_title.draw(self.pg)
        self.txt_score = Text(Origin(px, py), Point(px, py-40), '')
        self.txt_score.draw(self.pg)
        self.txt_score.setFont('courier new')
        score_str = self.updatePlayerScore()
        self.gl_last_endtime = time.time()
        
        # Game over
        self.time_to_reset = 3 # seconds
        self.game_over_title = None
        self.game_over_time = None
        
        self.start()

    def start(self):
        # Ship
        self.ship = Ship(self.pg, self.pg.center.x, self.pg.center.y)
        self.ship.rotate(90)
        self.append_new_object(self.ship)
        self.bind_ship()
        self.player.setLives(3)
        self.gameloop()
                
    def stop(self):
        if self.sc_gameloop:
            self.pg.after_cancel(self.sc_gameloop)
            self.sc_gameloop = None
        
    def gameloop(self):
        self.sc_gameloop = self.pg.after(16, self.gameloop)
        self.master.update_idletasks()
        self.handle_ship_fire()
        self.check_collisions()
        
        # Call this before any methods that might affect undrawn objects
        self.delete_removable()
        self.handle_new_objects()
        
        self.update_projectiles()
        self.handle_offscreen_objects()
        self.handle_asteroid_generation()
        self.handle_blackhole_generation()
        self.updatePlayerScore()
        self.updatePlayerLives()
        self.handle_gameOver()
        endtime = time.time()
        #print((endtime - self.gl_last_endtime))
        self.gl_last_endtime = endtime
        
    def checkGameOver(self):
        if self.player.getLives() < 0:
            return True
        return False
    
    def updatePlayerScore(self):
        self.txt_score.setText('[%s]' % self.player.getScore())
    
    def updatePlayerLives(self):
        # Remove old lives
        for item in self.player_lives_vis_container[:]:
            item.shape.undraw()
            self.player_lives_vis_container.remove(item)
        
        # Add new
        startx = self.pg.getWidth() - 150
        starty = self.pg.getHeight() - 40
        for i in range(self.player.getLives()):
            spacing = i*30
            ship = Ship(self.pg, startx+spacing, starty)
            ship.rotate(90)
            self.player_lives_vis_container.append(ship)
            
    def delete_removable(self):
        for object in self.remove:
            if object.__class__ == Asteroid:
                self.ast_count -= 1
            elif object.__class__ == BlackHole:
                self.bh_count -= 1
            object.undraw()
            self.objects.remove(object)
        self.remove = []
    
    def update_projectiles(self):
        for object in self.objects:
            if object.getMaxLifetime():
                if object.getMaxLifetime() <= object.getLifetime():
                    self.add_remove(object)
                    continue
            
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

                
            # Shot
            elif isinstance(object, Shot):
                shot = object
                if shot.getDistance() > self.shot_max_dist:
                    self.add_remove(shot)
                    shot.shape.undraw()
                    continue
                    
                
            object.update(0.1)
    
    def handle_gameOver(self):
        if self.checkGameOver():
            if not self.game_over_time:
                self.game_over_time = time.time()
            if not self.game_over_title:
                c = self.pg.center
                text = 'Game Over'
                self.game_over_title = Text(Origin(c.x, c.y), c, text)
                self.game_over_title.draw(self.pg)
                self.game_over_title.setSize(56)
                self.game_over_title.setFont('courier')
             
            if time.time() - self.game_over_time >= self.time_to_reset:
                if self.game_over_title:
                    self.game_over_title.undraw()
                    self.game_over_title = None
                self.game_over_time = None
                self.add_remove_all()
                self.pg.after_cancel(self.sc_gameloop)
                self.start()
                
    def handle_new_objects(self):
        for object in self.new_object_queue[:]:
            if isinstance(object, Asteroid):
                self.ast_count +=1
            elif isinstance(object, BlackHole):
                self.bh_count +=1
                
            self.objects.append(object)
            self.new_object_queue.remove(object)
            
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
            if not hasattr(object, 'collider'):
                continue
            for check in self.objects[:]:
                if not hasattr(check, 'collider'):
                    continue
                exclude = exclusions.get(object.__class__, [])
                if not check.__class__ in exclude and object != check:
                    if object.checkCollide(check):
                        self.handle_collision(object, check)

    def handle_ship_fire(self):
        shot = self.ship.getShot()
        if shot:
            self.append_new_object(shot)
          
    def handle_collision(self, object, check):
        # Handle object specific collision things
        object.handle_collision(check)
        
        # Handle collision things directly related to game class
        if object.__class__ == Shot:
            shot = object
            if check.__class__ == Asteroid:
                 self.add_remove(shot)
                 shot.undraw()
                 self.player.addScore(check.size)
        elif object.__class__ == Ship:
            ship = object
            if check.__class__ == Asteroid:
                self.explosion(ship.getX(), ship.getY(), 5)
                self.add_remove(ship)
                self.ship.undraw()
                self.player.addLives(-1)
                if not self.checkGameOver():
                    self.ship = Ship(self.pg, self.pg.center.x, self.pg.center.y)
                    self.ship.rotate(90)
                    self.bind_ship()
                    self.append_new_object(self.ship)
            elif check.__class__ == BlackHole:
                pass

        elif object.__class__ == Asteroid:
            ast = object
            if check.__class__ == Shot:
                self.explosion(ast.getX(), ast.getY(), 3)
                self.add_remove(ast)
                ast.undraw()
                if ast.isBreakable():
                    self.append_new_object(ast.break_apart())
                    
            elif check.__class__ == Ship:
                self.explosion(ast.getX(), ast.getY(), 3)
                self.add_remove(ast)
                ast.undraw()
                if ast.isBreakable():
                    self.append_new_object(ast.break_apart())
                    
            elif check.__class__ == Asteroid:
                self.explosion(ast.getX(), ast.getY(), 3)
                self.add_remove(ast)
                ast.undraw()
                if ast.isBreakable():
                    self.append_new_object(ast.break_apart())
                
        elif object.__class__ == BlackHole:
            bh = object
            if check.__class__ == BlackHole:
                pass
        
       
    def explosion(self, x, y, density):
        for i in range(density):
            p = Particle(self.pg, x, y)
            self.append_new_object(p)
       
    def handle_blackhole_generation(self):
        since_last_gen = time.time() - self.bh_last_gen_time
        max_reached = self.bh_count >= self.bh_max
        
        w = self.pg.getWidth()
        h = self.pg.getHeight()
        px = random.randrange(1, w)
        py = random.randrange(1, h)
        if since_last_gen >= self.bh_gen_freq and not max_reached:
            blackhole = BlackHole(self.pg, px, py)
            self.append_new_object(blackhole)
            self.bh_last_gen_time = time.time()
          
    def handle_asteroid_generation(self):
        since_last_gen = time.time() - self.ast_last_gen_time
        max_reached = self.ast_count >= self.ast_max
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
                if not hasattr(object, 'collider'):
                    continue
                if object.checkCollide(ast):
                    ast.shape.undraw()
                    return False
               
            self.append_new_object(ast)
            self.ast_last_gen_time = time.time()
    
    def bind_ship(self):
        self.pg.master.bind('<Up>', self.ship.acceleration)
        self.pg.master.bind('<KeyRelease-Up>', self.ship.acceleration)
        self.pg.master.bind('<Down>', self.ship.acceleration)
        self.pg.master.bind('<KeyRelease-Down>', self.ship.acceleration)
        self.pg.master.bind('<Left>', self.ship.rotation)
        self.pg.master.bind('<KeyRelease-Left>', self.ship.rotation)
        self.pg.master.bind('<Right>', self.ship.rotation)
        self.pg.master.bind('<KeyRelease-Right>', self.ship.rotation)
        self.pg.master.bind('<space>', self.ship.fire)
            
    def add_remove(self, object):
        if not object in self.remove:
            self.remove.append(object)
    
    def debug(self):
        pass
        
    def add_remove_all(self):
        for object in self.objects:
            self.add_remove(object)
            
    def append_new_object(self, object):
        if isinstance(object, [].__class__):
            for item in object:
                self.new_object_queue.append(item)
        else:
            self.new_object_queue.append(object)
        

class Player(object):
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.lives = 0
        
    def save(self):
        pass
        
    def getScore(self):
        return self.score
        
    def addScore(self, amount):
        self.score += amount
        
    def addLives(self, amount):
        self.lives += amount
        
    def setLives(self, amount):
        self.lives = amount
    
    def getLives(self):
        return self.lives
        
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
        self.original_grav = self.grav
        self.distance = [0,0]
        self.lifetime = 0
        self.last_time_check = time.time()
        self.max_lifetime = None
    
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
        
        self.vel = math.sqrt(self.yvel**2 + self.xvel**2)
        
        end = [self.x, self.y]
        dx, dy = end[0] - start[0], end[1] - start[1]
        self.distance[0] += dx
        self.distance[1] += dy
        
        self.lifetime += time.time() - self.last_time_check
        self.last_time_check = time.time()
        
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
        self.xvel = vel * math.cos(theta)
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
       
    def setGravity(self, x, y):
        self.grav = [x, y]
       
    def addGravity(self, x, y):
        self.grav[0] += x
        self.grav[1] += y
       
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
       
    def getLifetime(self):
        return self.lifetime
        
    def getMaxLifetime(self):
        return self.max_lifetime
       
       
class VProjectile(Projectile):
    def __init__(self, pg, shape, ang, vel, x, y):
        super().__init__(ang, vel, x, y)
        self.pg = pg
        self.shape = shape
        self.collider = genCollisionBox(shape)
        self.last_pos = [x, y]
        self.collision = False
        self.undrawn = False
        
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
        self.vis_ang = None
        
    def undraw(self):
        self.shape.undraw()
        if self.debugging:
            self.collider.undraw()
            if self.vis_vel:
                self.vis_vel.undraw()
            if self.vis_top_edge:
                self.vis_top_edge.undraw()
            if self.vis_right_edge:    
                self.vis_right_edge.undraw()
            if self.vis_bottom_edge:
                self.vis_bottom_edge.undraw()
            if self.vis_left_edge:
                self.vis_left_edge.undraw()
            if self.vis_ang:
                self.vis_ang.undraw()
            for hist in self.real_pathHist:
                hist.undraw()
            for hist in self.shape_pathHist:
                hist.undraw()
                
        self.undrawn = True
        
    def update(self, t=None):
        super().update(t)
        x0, y0 = self.last_pos[0], self.last_pos[1]
        dx, dy = self.x - x0, self.y - y0
        self.shape.move(dx, dy)
        self.collider.move(dx, dy)
        self.last_pos = [self.x, self.y]
        
        # For any potential extra processing on children classes
        self._update()
            
        self._update()
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
            if len(self.real_pathHist) > 20:
                dead = self.real_pathHist.pop(0)
                dead.undraw()
                
            # Path history of shape shadowing projectile
            xh = self.shape.origin.getX()
            yh = self.shape.origin.getY()
            hist_point2 = Point(xh, yh)
            hist_point2.setFill('blue')
            hist_point2.draw(self.pg)
            self.shape_pathHist.append(hist_point2)
            if len(self.shape_pathHist) > 20:
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
               
                
    def handle_collision(self, check):
        if self.debugging:
            self.collider.setOutline('red')
        self.collision = True  
        self._handle_collision(check)
            
    def _handle_collision(self, check):
        pass
            
    def rotate(self, angle=None):
        if callable(getattr(self, '_rotate', None)):
            self._rotate(angle)
        else:
            self.shape.rotate(-angle)
            self.addAngle(angle)
        
    def debug(self):
        self.debugging = True
        
    def checkCollide(self, vproj):
        collision = self.collider.checkCollide(vproj)
        return collision
        
    def _update(self):
        pass
        
    
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
        
        # Stop Codes
        self.sc_accelerating = None
        self.sc_rotating = None
        
    def acceleration(self, event):
        if event.type == '3':
            if self.accelerating:
                self.accelerating = False
            return True
                
        if not self.accelerating:
            if event.keysym == 'Up':
                self.dir_accel = self.inc_accel
                self.accelerating = True
            elif event.keysym == 'Down':
                self.dir_accel = -self.inc_accel
                self.accelerating = True

    def accel(self):
        # START HERE
        if not self.vel + self.dir_accel > self.max_accel:
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
                self.dir_rot = -self.inc_rotate
                self.rotating = True
            elif event.keysym == 'Left':
                self.dir_rot = self.inc_rotate
                self.rotating = True
    
    def _rotate(self, ang=None):
        if not ang:
            ang = self.dir_rot
        self.shape.rotate(ang)
        self.addAngle(ang)

    def isRotating(self):
        return self.rotating
        
    def _handle_collision(self, check):
        pass
        #self.accelerating = False
        #self.rotating = False
       
    def getShot(self):
        shot = self.shot
        if shot:
            self.shot = None
        return shot
        
    def fire(self, event):
        angle = self.ang
        shot = Shot(self.pg, self)
        self.shot = shot
        
    def removebinds(self):
        self.pg.master.unbind('<Up>')
        self.pg.master.unbind('<KeyRelease-Up>')
        self.pg.master.unbind('<Down>')
        self.pg.master.unbind('<KeyRelease-Down>')
        self.pg.master.unbind('<Left>')
        self.pg.master.unbind('<KeyRelease-Left>')
        self.pg.master.unbind('<Right>')
        self.pg.master.unbind('<KeyRelease-Right>')
        self.pg.master.unbind('<space>')

    def _update(self):
        pass
    
        
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
        
    def _handle_collision(self, check):
        pass
        
        
class Asteroid(VProjectile):
    def __init__(self, pg, ang, vel, x, y, min_size = 10, max_size=40):
        self.max_verts = 10
        self.max_size = max_size
        self.min_size = min_size
        self.breakable = True
        shape = self._genShape(x, y)
        shape.draw(pg)
        super().__init__(pg, shape, ang, vel, x, y)
        
    def _genShape(self, x, y):
        verts = random.randrange(7, self.max_verts + 1)
        size = random.randrange(self.min_size, self.max_size + 1)
        self.size = size
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
        
        # If too small, not breakable        
        if self.size <= 30:
            self.breakable = False
        shape = Polygon('center', *points)
        return shape
        
    def getSize(self):
        return self.size
     
    def isBreakable(self):
        return self.breakable
    
    def break_apart(self):
        new = []
        span = 360 / 3
        for i in range(3):
            sang = (i * span) * math.pi / 180
            x = self.x + self.size * math.cos(sang)
            y = self.y + self.size * math.sin(sang)
            
            ang = random.randrange(1,361)
            vel = random.randrange(3,15)
            ast = Asteroid(self.pg, ang, vel, x, y, int(self.min_size*0.3) , (self.max_size*0.4))
            ast.breakable = False
            new.append(ast)
   
        return new
     
    def _handle_collision(self, check):
        pass
        
    def _update(self):
        self.rotate(1)
        
        
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
        
    
class BlackHole(VProjectile):
    def __init__(self, pg, x, y):
        ang = random.randrange(1,361)
        self.radius = random.randrange(30, 100)
        shape = PolyCircle(Origin(x, y), Point(x, y), self.radius, 10)
        shape.setOutline('blue')
        shape.draw(pg)
        vel = random.randrange(5, 10)
        self.gravity_center = 100
        super().__init__(pg, shape, ang, vel, x, y)
        self.inside = []
        
    def _handle_collision(self, check):  
        dx, dy = self.getX() - check.getX(), self.getY() - check.getY()
        if dx == 0:
            angle = 0
        else:
            angle = math.atan(abs(dy/dx))
        
        # Visual feedback of being inside bh
        self.rotate(-angle)
        
        rx = self.radius * math.cos(angle)
        ry = self.radius * math.sin(angle)
        
        if dx > 0:
            rx = -rx
        if dy > 0:
            ry = -ry
            
        gx = rx - dx
        gy = ry - dy
        if not check in self.inside:
            self.inside.append(check)
        check.setGravity(gx*0.1, gy*0.1)
        
    def _update(self):
        if self.debugging:
            if len(self.inside) == 0:
                self.collider.setOutline('white')
        self.rotate(1)
        for item in self.inside[:]:
            if not self.checkCollide(item):
                item.setGravity(0,0)
                
                # Object no longer colliding with blackhole
                item.collider.setOutline('white')
                self.inside.remove(item)
    
        
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
                
     
class Particle(VProjectile):
    def __init__(self, pg, x, y):
        ang = random.randrange(1,361)
        vel = random.randrange(1,30)
        self.rotby = random.randrange(1, 15)
        length = random.randrange(1,5)
        shape = Line('center', Point(x, y), Point(x+length, y+length))
        shape.draw(pg)
        shape.setOutline('white')
        super().__init__(pg, shape, ang, vel, shape.center.x, shape.center.y)
        self.max_lifetime = 0.5 # seconds
        
    def _update(self):
        pass
        self.rotate(self.rotby)
     
     
def main():
    root = Root('TKasteroids')
    root.resizable(0, 0)
    game = Game(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()