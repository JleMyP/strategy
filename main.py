# -*- coding: utf-8 -*-

import pygame, sys, os
from pygame.locals import *
from random import randrange as rnd, choice


class Window_build(object):
  def __init__(self, w, h):
    self.width, self.height = w, h
    self.rect = pygame.Rect(((win_w-w)//2, (win_h-h)//2, w, h))
    self.image = pygame.Surface((w, h))
    self.image.fill((255,255,0))
    ramka(self.image, w, h, 20, (0,255,0))
    ramka(self.image, w-40, h-70, 20, (0,0,255), pos=(20,50))
    ramka(self.image, 40, 40, 10, (255,0,0), pos=(w-45, 5))
    pygame.draw.line(self.image, 0, (w-35, 15), (w-15, 35), 3)
    pygame.draw.line(self.image, 0, (w-35, 35), (w-15, 15), 3)

    self.size = (w-40)//4
    tab = self.size//20
    font_size = (self.size-tab)//4
    self.font_cell = pygame.font.Font("freesansbold.ttf", font_size)
    self.values = (
      (House, (1,1,2), 'House', 1, 2), (House, (2,2,1), 'House', 2, 2), (House, (2,3,2), 'House', 2, 3),
      (House, (3,3,3), 'House', 3, 3), (House, (4,3,2), 'House', 4, 3), (House, (4,5,2), 'House', 4, 5),
      (House, (5,5,1), 'House', 5, 5), (Home, (), ru('Дом'), 4, 4))
    for x in range(4):
      for y in range(int((h-70)/self.size)):
        px, py = 20+tab+x*self.size, 50+tab+y*self.size
        ramka(self.image, self.size-2*tab, self.size-2*tab, tab*2, (255,255,255), pos=(px, py))
        p = x + 4*y
        if p < len(self.values):
          v = self.values[p]
          l1 = self.font_cell.render(v[2], True, (0,0,0))
          l2 = self.font_cell.render(u'%ix%i'%(v[3], v[4]), True, (0,0,0))
          l1rect, l2rect = l1.get_rect(), l2.get_rect()
          l1rect.center = px+self.size//2, py+self.size//4
          l2rect.center = px+self.size//2, py+self.size//4*3
          self.image.blit(l1, l1rect)
          self.image.blit(l2, l2rect)


    self.image.set_colorkey((255,255,0))
    self.image = self.image.convert_alpha()

    self.visible = False
    self.quit_button = pygame.Rect((w-45, 5, 40, 40))

  def show(self):
    pass

  def event_callback(self, event):
    global build
    if event.type != MOUSEBUTTONDOWN:
      return
    px, py = event.pos[0]-self.rect.x, event.pos[1]-self.rect.y
    if self.quit_button.collidepoint((px, py)):
      self.visible = False
    if 20 < px < self.width-20 and 50 < py < self.height-20:
      p = (px-20)//self.size + 4*((py-50)//self.size)
      if p < len(self.values):
        cls, args, label, w, h = self.values[p]
        x, y = int(camera.x/cell+display_map_w/2-w/2), int(camera.y/cell+display_map_h/2-h/2)
        build = [None, None, (), cls(*args, pos=(x, y), place=False)]
        collide(build)
        self.visible = False


class Window_tools(object):
  def __init__(self, rows, cols, size, buttons, bg=(0,255,0)):
    # img, func
    self.width, self.height = 5+cols*(size+5), 5+rows*(size+5)
    self.rect = pygame.Rect(((win_w-self.width)//2, (win_h-self.height)//2, self.width, self.height))
    self.buttons = buttons
    self.image = pygame.Surface((self.width, self.height))
    self.image.fill((255,255,0))
    ramka(self.image, self.width, self.height, 10, bg)
    self.buttons = [(b[0] if b[0] else ramka(None, size, size, 10, (255,255,255)).convert_alpha(), b[1],
                     pygame.Rect((5+(size+5)*(i%cols), 5+(size+5)*(i//cols), size, size)))
                     for i, b in enumerate(buttons)]
    for b in self.buttons:
      self.image.blit(b[0], b[2])
    self.image.set_colorkey((255,255,0))
    self.image = self.image.convert_alpha()

  def event_callback(self, event):
    if event.type != MOUSEBUTTONDOWN or not self.rect.collidepoint(event.pos):
      return
    px, py = event.pos[0]-self.rect.x, event.pos[1]-self.rect.y
    for b in self.buttons:
      if b[2].collidepoint((px, py)):
        b[1]()


class Window_info(object):
  def __init__(self, w, size):
    self.w, self.size = w, size
    self.spoiler = [ru('спойлер'), ru('это самый пиздатый гребаный спойлер мать вашу')]


class House(object):
  def __init__(self, width, height, v, pos, surf=None, place=True):
    v = float(v)/1.4
    self.width, self.height, self.pos, self.v = width, height, pos, v
    if not surf:
      surf = (255, 0, 0)
    if isinstance(surf, (tuple, list)):
      image = parall(None, width*cell, height*cell, v*cell, None, surf)
      self.image = image.convert_alpha()
    else:
      image = surf
      self.image = image.convert_alpha()

    focus_image = pygame.Surface(image.get_size())
    focus_image.fill((255,255,255))
    pygame.draw.lines(focus_image, (0,255,0), True, pygame.mask.from_surface(image).outline(3), 4)
    focus_image.set_colorkey((255,255,255))
    self.focus_image = focus_image.convert_alpha()

    image_alpha = image.copy()
    image_alpha.set_alpha(100)
    self.image_alpha = image_alpha.convert_alpha()

    self.image_rotate = pygame.transform.flip(pygame.transform.rotate(self.image, -90), True, False)
    self.image_rotate_alpha = pygame.transform.flip(pygame.transform.rotate(self.image_alpha, -90), True, False)

    self.win_tools = Window_tools(1, 2, 70, ((0, self.move),(0, self.destroy)))
    self.win_build = Window_tools(1, 2, 70, (
      (ramka(None, 70, 70, 10, (0, 255, 0)).convert_alpha(), build_create),
      (ramka(None, 70, 70, 10, (255, 0, 0)).convert_alpha(), build_cancle)
    ))
    self.calc_rect()
    #village.append(self)
    #all_drawing.append(self)
    if place:
      self.place()

  def calc_rect(self):
    self.rect = pygame.Rect((
      (self.pos[0]-self.v)*cell, (self.pos[1]-self.v)*cell,
       (self.width+self.v)*cell+2, (self.height+self.v)*cell+2
    ))

  def draw(self):
    cx, cy = camera.x//cell, camera.y//cell
    px, py = cx*cell-camera.x, cy*cell-camera.y
    rect = self.rect.move(-camera.x, -camera.y)
    if build or view:
      pygame.draw.rect(window, 0, ((
        self.pos[0]-cx)*cell+px, (self.pos[1]-cy)*cell+py, self.width*cell, self.height*cell), 2)
      window.blit(self.image_alpha, rect)
    else:
      window.blit(self.image, rect)
    if focus == self:
      window.blit(self.focus_image, rect)

  def draw_win(self, win):
    rect = self.rect.move(-camera.x, -camera.y)
    y = rect.top-win.height-10 if rect.top-win.height-10 > 0 else rect.bottom+10
    x = rect.center[0] - win.width//2
    if x < 10:
      x = 10
    elif x + win.width+10 > win_w:
      x = win_w-self.win.width-10
    win.rect.x, win.rect.y = x, y
    window.blit(win.image, win.rect)

  def rotate(self, in_place=False):
    self.image, self.image_rotate = self.image_rotate, self.image
    self.image_alpha, self.image_rotate_alpha = self.image_rotate_alpha, self.image_alpha
    if not in_place:
      self.pos = map_h-self.pos[1]-self.height, self.pos[0]
    self.width, self.height = self.height, self.width

  def place(self):
    self.calc_rect()
    for x in range(self.pos[0], self.pos[0]+self.width):
      for y in range(self.pos[1], self.pos[1]+self.height):
        if map[x][y]:
          map[x][y].remove()
        map[x][y] = self
    self.map =  set((x+self.pos[0], y+self.pos[1]) for x in range(self.width) for y in range(self.height))
    if self not in village:
      village.append(self)
      all_drawing.append(self)
    all_drawing.sort(cmp=sort_lst)
  #  sort_map()

  def remove(self):
    for x, y in self.map:
      map[x][y] = 0

  def move(self):
    global build
    self.destroy()
    build = [None, None, (), self]

  def destroy(self):
    self.remove()
    village.remove(self)
    all_drawing.remove(self)

  def collidepoint(self, pos):
    x, y = pos[0]+camera.x, pos[1]+camera.y
    if not self.rect.collidepoint((x, y)):
      return False
    if self.image.get_at((x-self.rect.x, y-self.rect.y)).a != 0:
      return True


class Home(House):
  def __init__(self, pos, place=True):
    House.__init__(self, 4, 4, 2, pos, (255,255,0), place)
    self.living, self.limit = [], 3


class Tile(object):
  def __init__(self, pos, v, image, name, **kwargs):
    self.name, self.pos, self.v = name, pos, v
    self.width = self.height = 1
    if isinstance(image, (tuple, list)):
      self.image = parall(None, cell-4, cell-4, v, (2,2), image)
    else:
      self.image = image
    self.__dict__.update(kwargs)
    tiles.append(self)
    all_drawing.append(self)
    self.rect = pygame.Rect((self.pos[0]*cell-self.v, self.pos[1]*cell-self.v, cell+self.v, cell+self.v))

  def draw(self):
    cx, cy = camera.x//cell, camera.y//cell
    px, py = cx*cell-camera.x, cy*cell-camera.y
    window.blit(self.image, ((self.pos[0]-cx)*cell+px-self.v, (self.pos[1]-cy)*cell+py-self.v))

  def rotate(self):
    self.pos = map_h-self.pos[1]-1, self.pos[0]
  
  def remove(self):
    map[self.pos[0]][self.pos[1]] = 0
    tiles.remove(self)
    all_drawing.remove(self)


class Villager(object):
  def __init__(self, sex, age, name, parents=None):
    self.sex, self.name, self.parents = sex, name, parents
    if parents:
      skills = [skill for skill in self.get_all_skills(parents) if skill['value'] > 50]
      if len(set(skills)) < 3:
        self.tallants = [skill['name'] for skill in set(skills)]
      else:
        self.tallants = []
        for i in range(3):
          t = choice(skills)
          while t in self.tallants:
            t = choice(skills)
          self.tallants.append(t['name'])
    else:
      self.tallants = []
    self.age, self.tasks = (age, 0, 0), []
    self.path, self.pos = (), (0, 0)
    self.home = self.parents[0].home if self.parents else self.find_home()
    self.home.living.append(self)

  def get_all_skils(self, parents):
    skills = []
    while parents:
      if parents[0].parents:
        parents += parents[0].parents
        skills += parents[0].skills
      del parents[0]

  def find_home(self):
    for h in village:
      if isinstance(h, Home) and len(h.living) != h.limit:
        return h

  def update(self):
    pass


class Images(object):
  def __init__(self):
    self.btn_cv = ramka(None, 100, 50, 10, (0,255,0)) # change_view
    self.btn_r = ramka(None, 100, 50, 10, (255,255,0)) # rotate
    self.btn_sb = ramka(None, 100, 50, 10, (0,255,255)) # show_build
    self.btn_cc = ramka(None, 100, 50, 10, (255,0,255)) # change_cells
    #self.grass = pygame.transform.scale(pygame.image.load('grass.jpg'), (cell, cell))
    tree = pygame.image.load("tree.png")
    w, h = tree.get_size()
    self.tree = pygame.transform.scale(tree, (cell, cell*3))#h*cell/w))


def event_callback():
  global run, build, move_camera, focus
  for event in pygame.event.get() :
    if w_build.visible and event.type in (MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP):
      w_build.event_callback(event)
      continue
    elif build:
      build[3].win_build.event_callback(event)
    elif focus:
      focus.win_tools.event_callback(event)
    if event.type == QUIT:
      run = False
    elif event.type == KEYDOWN:
      if event.key == K_ESCAPE:
        run = False
    elif event.type == MOUSEBUTTONDOWN :
      px, py = event.pos
      if py < win_h-bottom_bar:
        x, y = (px+camera.x)//cell, (py+camera.y)//cell
        if build and build[3].pos[0] <= x <= build[3].pos[0]+build[3].width and \
                     build[3].pos[1] <= y <= build[3].pos[1]+build[3].height:
          build[0], build[1] = x-build[3].pos[0], y-build[3].pos[1]
        else:
          move_camera = [True, event.pos]
      for btn in btn_list:
        if btn[0].collidepoint((px, py)):
          btn[2]()
    elif event.type == MOUSEMOTION:
      px, py = event.pos
      if event.pos == (0, 0): pass
      if move_camera:
        if event.pos != move_camera[1]:
          move_camera[0] = 0
        px, py = event.pos
        mx, my = move_camera[1][0]-event.pos[0], move_camera[1][1]-event.pos[1]
        if camera.x+mx < -cell*2:
          mx = -camera.x-cell*2
        elif camera.x+mx > (map_w-display_map_w)*cell+cell/2:
          mx = (map_w-display_map_w)*cell-camera.x+cell/2
        if camera.y+my < -cell*2:
          my = -camera.y-cell*2
        elif camera.y+my > (map_h-display_map_h)*cell+cell/2:
          my = (map_h-display_map_h)*cell-camera.y+cell/2
        if not fix_camera[0]:
          camera.move_ip(mx, 0)
        if not fix_camera[1]:
          camera.move_ip(0, my)
        move_camera[1] = event.pos
      elif build and build[0] != None and build[1] != None and py < win_h-bottom_bar:
        x, y = (px+camera.x)//cell, (py+camera.y)//cell
        if 0 <= x-build[0] <= map_w-build[3].width and 0 <= y-build[1] <= map_h-build[3].height:
          build[3].pos = x-build[0], y-build[1]
          build[3].calc_rect()
          collide(build)
    elif event.type == MOUSEBUTTONUP:
      if build:
        build[0] = build[1] = None
      if move_camera:
        if move_camera[0]:
          if not focus:
            for h in camera.collidelistall(village)[::-1]:
              if village[h].collidepoint(event.pos):
                focus = village[h]
                break
          else:
            if not focus.collidepoint(event.pos):
              focus = None
        move_camera = None

def draw():
  window.fill((255, 255, 255))
  cx, cy = camera.x//cell, camera.y//cell
  rx, ry = display_map_w, display_map_h
  if camera.x < 0:
    cx = 0
    rx += camera.x//cell
  if camera.y < 0:
    cy = 0
    ry += camera.y//cell
  px, py = cx*cell-camera.x, cy*cell-camera.y

  if cx + rx < map_w:
    rx += 1
  if cy + ry < map_h:
    ry += 1
  if rx + cx > map_w:
    rx = map_w-cx

  if fix_camera[0]:
    px, rx, cx = -camera.x, map_w, 0
  if fix_camera[1]:
    py, ry, cy = -camera.y, map_h, 0
  if ry + cy > map_h:
    ry = map_h-cy
  pygame.draw.rect(window, 0, (-camera.x, -camera.y, cell*map_w, cell*map_h), 2)
  for y in xrange(ry):
    for x in xrange(rx):
      m = map[x+cx][y+cy]
      if (build or view) and cells:
        pygame.draw.rect(window, 0, (x*cell+px, y*cell+py, cell, cell), 1)
  if build:
    h = build[3]
    pygame.draw.rect(window, (0,255,0), ((h.pos[0]-cx)*cell+px, (h.pos[1]-cy)*cell+py, h.width*cell, h.height*cell))
    for pos in build[2]:
      pygame.draw.rect(window, (255,0,0), ((pos[0]-cx)*cell+px, (pos[1]-cy)*cell+py, cell, cell))
  for v in camera.collidelistall(all_drawing):
    all_drawing[v].draw()
  if build and camera.colliderect(build[3].rect):
    build[3].draw()
    build[3].draw_win(build[3].win_build)

  pygame.draw.rect(window, (255,255,255), (0, win_h-bottom_bar, win_w, bottom_bar))
  for btn in btn_list:
    window.blit(btn[1], btn[0])
  fps = clock.get_fps()
  window.blit(font30.render(ru(fps), True, (0,0,0)), (win_w-70, win_h-40))

  if w_build.visible:
    window.blit(shadow, (0,0))
    window.blit(w_build.image, w_build.rect)
  elif focus:
    focus.draw_win(focus.win_tools)
  pygame.display.update()

def ramka(surf, w, h, r, clr1, clr2=0, pos=(0,0), lw=2):
  new = False
  x, y = pos
  if not surf:
    bg = clr1[0]//2, clr1[1]//2, clr1[2]//2
    surf = pygame.Surface((w, h))
    surf.fill(bg)
    new = True
  for cx, cy in ((x+r, y+r), (x+w-r, y+r), (x+w-r, y+h-r), (x+r, y+h-r)):
    pygame.draw.circle(surf, clr1, (int(cx), int(cy)), r)
    pygame.draw.circle(surf, clr2, (int(cx), int(cy)), r, lw)
  pygame.draw.rect(surf, clr1, (x, y+r, w, h-2*r))
  pygame.draw.rect(surf, clr1, (x+r, y, w-2*r, h))
  for p1, p2 in ([(x, y+r), (x, y+h-r)], [(x+r, y), (x+w-r, y)],
                 [(x+w-2, y+r), (x+w-2, y+h-r)], [(x+r, y+h-2), (x+w-r, y+h-2)]):
    pygame.draw.line(surf, clr2, p1, p2, lw)
  if new:
    surf.set_colorkey(bg)
    return surf.convert_alpha()

def parall(surf, w, h, v, pos, clr=(255,0,0)):
  new = False
  if not surf:
    surf = pygame.Surface((w+v, h+v))
    surf.fill((255,255,255))
    pos = v, v
    new = True
  x, y = pos
  pygame.draw.polygon(surf, clr, ((x-v, y-v), (x+w-v, y-v), (x+w, y), (x+w, y+h), (x, y+h), (x-v, y+h-v)))
  pygame.draw.rect(surf, 0, (x-v, y-v, w, h), 2)
  for px, py in ((x-v, y-v+h), (x-v+w, y-v+h), (x-v+w, y-v)):
    pygame.draw.line(surf, 0, (px, py), (px+v, py+v), 2)
  pygame.draw.line(surf, 0, (x, y+h-2), (x+w, y+h-2), 2)
  pygame.draw.line(surf, 0, (x+w-2, y+h), (x+w-2, y), 2)
  if new:
    surf.set_colorkey((255,255,255))
    return surf

def rotate_map(po_chas=True):
  global map, map_w, map_h, fix_camera
  for h in village:
    h.remove()
  nmap = []
  for y in xrange(map_h):
    n = [map[x][y] for x in xrange(map_w)]
    if not po_chas :
      n.reverse()
    nmap.append(n)
  if po_chas :
    nmap.reverse()
  map = nmap
  for h in village+tiles :
    h.rotate()
    if not isinstance(h, Tile):
      h.place()
  map_w, map_h = map_h, map_w
  camera.x, camera.y = 0, 0
  calc_fix()
  all_drawing.sort(cmp=sort_lst)
  #sort_map()

def calc_fix():
  global fix_camera
  fix_camera = [0, 0]
  if map_w < display_map_w:
    fix_camera[0] = True
    camera.x = -(display_map_w-map_w)//2*cell
  if map_h < display_map_h:
    fix_camera[1] = True
    camera.y = -(display_map_h-map_h)//2*cell

def sort_lst(a, b):
  atx, aty = a.pos
  abx, aby = atx+a.width, aty+a.height
  btx, bty = b.pos
  bbx, bby = btx+b.width, bty+b.height
  if (aty < bty and atx < bbx) or (atx < btx and aty < bby):
    return -1
  else:
    return 1

def sort_map():
  i = 0
  while i < len(all_drawing)-1:
    if sort_lst(all_drawing[i], all_drawing[i+1]) == -1:
      all_drawing[i], all_drawing[i+1] = all_drawing[i+1], all_drawing[i]
      if i:
        i -= 1
    i += 1
    print i

def collide(build):
  s = set((build[3].pos[0]+x, build[3].pos[1]+y) for x in range(build[3].width) for y in range(build[3].height))
  build[2] = ()
  for hh in village:
    if hh.map & s:
      build[2] += tuple(hh.map & s)

def build_create():
  global build
  if build and not build[2]:
    build[3].place()
    build = None

def build_cancle():
  global build
  build = None

def change_view():
  global view
  view = not view

def change_cells():
  global cells
  cells = not cells

def show_build():
  w_build.visible = True

def rotate():
  if build:
    build[3].rotate(True)
    collide(build)
  else:
    rotate_map()

def wrap(text, font, width):
  lst = text.split()
  lines = [[]]



sys.stderr = sys.stdout = open('err.txt','w')
os.environ['SDL_VIDEO_CENTERED'] = "1"
ru = lambda x : str(x).decode('utf-8')

win_w, win_h = 0, 0
pygame.init()
window = pygame.display.set_mode((win_w, win_h), FULLSCREEN)
win_w, win_h = window.get_size()
pygame.display.set_caption('strategy')
clock = pygame.time.Clock()
font30 = pygame.font.Font('freesansbold.ttf',30)

shadow = pygame.Surface((win_w, win_h))
shadow.fill(0)
shadow.set_colorkey((255,255,255))
shadow.set_alpha(150)
shadow = shadow.convert_alpha()

cell = 20
bottom_bar = 150
map_w, map_h = 60, 60
view, cells = False, True
build = move_camera = focus = None
# build: px-x, py-y, lst, house
fix_camera = [None, None]
w_build = Window_build(win_w//2, win_h*0.75)
camera = pygame.Rect((0, 0, win_w, win_h-bottom_bar))
display_map_w, display_map_h = win_w//cell, (win_h-bottom_bar)//cell
calc_fix()

images = Images()
tiles, village, all_drawing = [], [], []
map = [[Tile((x,y), 10 if not y%2 else 0, (10, 255, 10) if not x%3 else (50, 100, 150), 'grass')
        for y in xrange(map_h)] for x in xrange(map_w)]
Home((5, 5))

btn_list = [
  (pygame.Rect((100, win_h-140, 100, 50)), images.btn_cv, change_view),
  (pygame.Rect((100, win_h-70, 100, 50)), images.btn_r, rotate),
  (pygame.Rect((220, win_h-140, 100, 50)), images.btn_sb, show_build),
  (pygame.Rect((220, win_h-70, 100, 50)), images.btn_cc, change_cells)
]

run = True
#sort_map()
while run:
  event_callback()
  draw()
  clock.tick()

pygame.quit()