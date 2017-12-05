import numpy as np
import random
import math
ratio = 4
nx = 2
ny = 2
l = float(400/(nx+ny))
c_dx = [1, 0, -1, 0]
c_dy = [0, 1, 0, -1]
l_dx = [0, -1, 0, 1]
l_dy = [1, 0, -1, 0]
st1 = 0
st2 = [0, 0, 0, 0, 0, 0, 0, 0]
pp = np.zeros((nx,ny,4))
mycross = []
Cars = []
num_frame = int(200/ratio)
cur_frame = 0
waiting = np.zeros((nx,ny,4,2))
not_waiting = np.zeros((nx,ny,4,2))
sx = np.zeros((nx,ny,4,2))
sy = np.zeros((nx,ny,4,2))
p = np.zeros((nx,ny,4,2))
width = 2000
height = 2000
s_total_time = [0,0,0,0]
Log = open('Log_simulation.txt', 'w')
Log.close()

def write_log(S):
    Log = open('Log_simulation.txt', 'a')
    Log.write(S+"\n")
    Log.close()

def get_signal():
    line = raw_input()
    while line!="2X": line+=raw_input()
    #write_log("Recieved signal " + line)

def print_out(S):
    get_signal()
    Msg = open("Msg2.txt", "w")
    Msg.write(S+"\n")
    Msg.close()
    print("C2")
    #write_log("Sent signal C2")

def get_input():
    get_signal()
    Msg = open("MsgC2.txt", "r")
    line = Msg.readline().rstrip("\n")
    if len(line)>10 : write_log("Received message length of " + str(len(line)))
    else : write_log("Received message : " + line)
    Msg.close()
    print("2O")
    return line

def send_point():
  global s_total_time, Cars
  #write_log("Total number of cars : " + str(len(Cars)))
  total_time = [0,0,0,0]
  for i in range(len(Cars)):
    C = Cars[i]
    t = C.t
    total_time[C.crossnum]+=(t*t)
  S = ""
  for i in range(4):
    if total_time[i]>s_total_time[i]: S+="0"
    else: S+="1" 
    s_total_time[i]=total_time[i]
  print_out(S)
  write_log("Point " + S + " sent")

class Cross:
  def __init__(self, center_x, center_y):
    self.center_x = center_x
    self.center_y = center_y
    self.mylight = []
    for i in range(4):
      self.mylight.append(Light(0, i, center_x, center_y))

class Light:
  def __init__(self, lmod, num, cx, cy):
    global l
    self.lmod = lmod
    self.num = num
    self.di = num
    self.ldx = 0
    self.ldy = 1

    self.ry = 4*l/16
    self.yy = 7*l/16
    self.ly = 10*l/16
    self.gy = 13*l/16

    self.trsx = cx
    self.trsy = cy
    self.h = 2*l/5
    self.w = 14*l/15

class Car:
  def __init__(self, x, y, i, j, di, mod):
    global l, nx
    self.v=ratio*6*l/200
    self.w=l/6
    self.crossnum = nx*j + i
    self.di = di
    self.x = x
    self.y = y
    self.xx = i
    self.yy = j
    self.di = di
    self.mod = mod
    if self.mod == 0: self.turn = 2
    else: self.turn = 2 * random.randrange(2) + 1
    self.ang = math.pi/2 * di
    self.turning = False
    self.t=0

  def go_straight(self):
    global c_dx, c_dy
    self.x += self.v*c_dx[self.di]
    self.y += self.v*c_dy[self.di]

  def turn_left(self, cx, cy, ang):
    self.ang += ang
    newx = (self.x-cx) * math.cos(ang) - (self.y-cy) * math.sin(ang)
    newy = (self.x-cx) * math.sin(ang) + (self.y-cy) * math.cos(ang)
    self.x = newx + cx
    self.y = newy + cy

  def changenum(self, n, d):
    global nx,ny
    self.crossnum = n
    self.xx = n % nx
    self.yy = n / ny
    self.di = d
    self.ang = math.pi/2 * self.di

  def whereami(self):
    global nx,ny,width,height
    ex = width/nx
    ey = height/ny
    self.xx = (int)(self.x/ex)
    self.yy = (int)(self.y/ey)
    if self.xx>=nx: self.xx-=1
    if self.yy>=ny: self.yy-=1
    if self.yy<0:
      print(self.x, self.y)
    self.crossnum = nx*self.yy + self.xx
  
  def print_data(self):
    write_log("x: "+str(self.x)+", y: "+str(self.y)+", turn: "+str(self.turn)+", turning: "+str(self.turning))
def int_to_string(value, size):
  S = str(int(value))
  len_extra = size-len(S)
  res = ""
  for i in range(len_extra):res+="0"
  return res+S

def generate(gen):
  global st1
  t = cur_frame
  if ratio*(t-st1)>60:
    st1 = cur_frame
    for j in range(ny):
      for i in range(nx):
        for k in range(4):
          for m in range(2):
            r = random.randrange(0,100)
            if gen:
              if r<p[i][j][k][m]: Cars.append(Car(sx[i][j][k][m], sy[i][j][k][m], i, j, k, m))
            if len(Cars)==0: continue
            C = Cars[len(Cars)-1]
            crossnum = C.crossnum
            di = C.di
            mod = C.mod
            w = C.w
            if di==0:
              for q in range(len(Cars)-2,0,-1):
                K = Cars[q]
                if K.crossnum==crossnum and K.di == di and K.mod == mod:
                  if K.x - C.x < 1.5*w and K.x - C.x > 0: Cars.pop()
                  break
            elif di==1:
              for q in range(len(Cars)-2,0,-1):
                K = Cars[q]
                if K.crossnum==crossnum and K.di == di and K.mod == mod:
                  if K.y - C.y < 1.5*w and K.y - C.y > 0: Cars.pop()
                  break
            elif di==2:
              for q in range(len(Cars)-2,0,-1):
                K = Cars[q]
                if K.crossnum==crossnum and K.di == di and K.mod == mod:
                  if C.x - K.x < 1.5*w and C.x - K.x > 0: Cars.pop()
                  break
            elif di==3:
              for q in range(len(Cars)-2,0,-1):
                K = Cars[q]
                if K.crossnum==crossnum and K.di == di and K.mod == mod:
                  if C.y - K.y < 1.5*w and C.y - K.y > 0: Cars.pop()
                  break

def delete():
  global Cars
  Car_tmp = []
  for i in range(len(Cars)):
    C = Cars[i]
    if C.x>width or C.x<0 or C.y>height or C.y<0: continue
    Car_tmp.append(C)
  Cars = Car_tmp


def change():
  global Cars
  for i in range(len(Cars)):
    C = Cars[i]
    C.whereami()

def move():
  global waiting, not_waiting, Cars, mycross 
  for i in range(nx):
    for j in range(ny):
      for k in range(4):
        waiting[i][j][k][0] = waiting[i][j][k][1] = not_waiting[i][j][k][0] = not_waiting[i][j][k][1] = 0
  for i in range(len(Cars)):
    C = Cars[i]
    crossnum = C.crossnum
    xx = C.xx
    yy = C.yy
    di = C.di
    mod = C.mod
    turn = C.turn
    lmod = mycross[xx][yy].mylight[di].lmod
    w = C.w
    cancarmove = True

    if turn == 1:
      if lmod == 1 or lmod == 3: go = 1
      else: go = 0
    elif turn == 2:
       if lmod == 2 or lmod == 3: go = 2
       else: go = 0
    else: go = 3
    if mycross[xx][yy].center_x - l <= C.x and C.x <= mycross[xx][yy].center_x + l and mycross[xx][yy].center_y - l <= C.y and C.y <= mycross[xx][yy].center_y + l:
      C.t = 0
      if C.turning:
        if turn == 2:
         if di == 0: C.turn_left(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y - l, -C.v/(5*l/4))
         elif di == 1: C.turn_left(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y - l, -C.v/(5*l/4))
         elif di == 2: C.turn_left(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y + l, -C.v/(5*l/4))
         elif di == 3: C.turn_left(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y + l, -C.v/(5*l/4))
        elif turn == 3:
         if di == 0: C.turn_left(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y + l, C.v/(l/4))
         elif di == 1: C.turn_left(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y - l, C.v/(l/4))
         elif di == 2: C.turn_left(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y - l, C.v/(l/4))
         elif di == 3: C.turn_left(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y + l, C.v/(l/4))
        continue

      if go == 2 :
         C.turning = True
         if di == 0: C.turn_left(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y - l, -C.v/(5*l/4))
         elif di == 1: C.turn_left(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y - l, -C.v/(5*l/4))
         elif di == 2: C.turn_left(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y + l, -C.v/(5*l/4))
         elif di == 3: C.turn_left(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y + l, -C.v/(5*l/4))

      elif go == 3:
         C.turning = True
         if di == 0: C.turn_left(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y + l, C.v/(l/4))
         elif di == 1: C.turn_left(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y - l, C.v/(l/4))
         elif di == 2: C.turn_left(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y - l, C.v/(l/4))
         elif di == 3: C.turn_left(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y + l, C.v/(l/4))

      if not C.turning: C.go_straight()

    else:
      if turn == 2 and C.turning == True:
        C.turning = False
        if di==0: C.changenum(C.crossnum,3)
        elif di==1: C.changenum(C.crossnum,0)
        elif di==2: C.changenum(C.crossnum,1)
        elif di==3: C.changenum(C.crossnum,2)

      elif turn == 3 and C.turning == True:
        C.turning = False
        if di==0: C.changenum(C.crossnum,1)
        elif di==1: C.changenum(C.crossnum,2)
        elif di==2: C.changenum(C.crossnum,3)
        elif di==3: C.changenum(C.crossnum,0)

      if go == 0:
        if di==0:
          if C.x <= mycross[xx][yy].center_x - l - w and C.x >= mycross[xx][yy].center_x - l - w - C.v: cancarmove = False
        elif di==1:
          if C.y <= mycross[xx][yy].center_y - l - w and C.y >= mycross[xx][yy].center_y - l - w - C.v: cancarmove = False
        elif di==2:
          if C.x <= mycross[xx][yy].center_x + l + w and C.x >= mycross[xx][yy].center_x + l + w - C.v: cancarmove = False
        elif di==3:
          if C.y <= mycross[xx][yy].center_y + l + w and C.y >= mycross[xx][yy].center_y + l + w - C.v: cancarmove = False

      if di==0:
        for j in range(len(Cars)):
          K = Cars[j]
          if K.crossnum==crossnum and K.di == di and K.mod == mod :
            if K.x - C.x < 1.5*w and K.x - C.x > 0:
               cancarmove=False
               break

      elif di==1:
        for j in range(len(Cars)):
          K = Cars[j]
          if K.crossnum==crossnum and K.di == di and K.mod == mod :
            if K.y - C.y < 1.5*w and K.y - C.y > 0:
               cancarmove=False
               break

      elif di==2:
        for j in range(len(Cars)):
          K = Cars[j]
          if K.crossnum==crossnum and K.di == di and K.mod == mod :
            if C.x - K.x < 1.5*w and C.x - K.x > 0:
               cancarmove=False
               break

      elif di==3:
        for j in range(len(Cars)):
          K = Cars[j]
          if K.crossnum==crossnum and K.di == di and K.mod == mod :
            if C.y - K.y < 1.5*w and C.y - K.y > 0:
               cancarmove=False
               break

      if cancarmove:
        not_waiting[xx][yy][di][mod] += 1
        C.t = 0
        C.go_straight()
      elif not C.turning:
        waiting[xx][yy][di][mod] += 1
        C.t+= 1

def draw2():
  global cur_frame
  if cur_frame%num_frame==0:
    send_data()
    res = get_input()
    light_change_string(res)
  if (cur_frame+1)%num_frame==0:
  	send_point()
  cur_frame += 1
  generate(True)
  #if cur_frame<200: generate(True)
  #else: generate(False)
  delete()
  change()
  light_change()
  move()

def light_change():
  global t,nx,ny,mycross,ratio,pp
  t = cur_frame
  for i in range(nx):
    for j in range(ny):
      for k in range(4):
        if mycross[i][j].mylight[k].lmod==9 and ratio*(t - st2[i]) > 60:
          mycross[i][j].mylight[k].lmod = int(pp[i][j][k])
          pp[i][j][k] = 9

def light_change_string(S):
  res = ""
  global cur_frame,pp,st2,mycross,nx,ny
  for i in range(nx):
  	  for j in range(ny):
  	  	  for k in range(4):
  	  	  	  res+=str(mycross[i][j].mylight[k].lmod)
  for C in Cars:
  	  C.print_data()
  write_log("Old signal : " + res)
  write_log("Changed signal to "+S)
  for i in range(nx):
    for j in range(ny):
      for k in range(4):
        x = int(S[(i*ny+j)*4+k])
        if mycross[i][j].mylight[k].lmod != x:
          mycross[i][j].mylight[k].lmod = 9
          st2[i] = cur_frame
          pp[i][j][k] = x

def send_data():
  global waiting, not_waiting, nx, ny
  S = ""
  move()
  for i in range(nx):
    for j in range(ny):
      for k in range(4):
        S+=int_to_string(waiting[i][j][k][0], 2)
        S+=int_to_string(waiting[i][j][k][1], 2)
        S+=int_to_string(not_waiting[i][j][k][0] + not_waiting[i][j][k][1], 2)
  print_out(S)
 
  write_log("Data sent : " + S + "(length = "+str(len(S))+")")

for i in range(nx):
  tmp = []
  for j in range(ny):
    tmp.append(Cross(width/(nx*2) * (2*i+1), height/(ny*2) * (2*j+1)))
    for k in range(4): pp[i][j][k] = 0
  mycross.append(tmp)

for j in range(ny):
  for i in range(nx):
    for k in range(4):
      for m in range(2):
        if k==0:
          sx[i][j][k][m] = mycross[i][j].center_x - width/nx/2.0
          sy[i][j][k][m] = mycross[i][j].center_y + l/4*(2*m+1)
        if k==1:
          sx[i][j][k][m] = mycross[i][j].center_x - l/4*(2*m+1)
          sy[i][j][k][m] = mycross[i][j].center_y - height/ny/2.0
        if k==2:
          sx[i][j][k][m] = mycross[i][j].center_x + width/nx/2.0
          sy[i][j][k][m] = mycross[i][j].center_y - l/4*(2*m+1)
        if k==3:
          sx[i][j][k][m] = mycross[i][j].center_x + l/4*(2*m+1)
          sy[i][j][k][m] = mycross[i][j].center_y + height/ny/2.0

for i in range(nx):
  p[i][0][1][0] = 25
  p[i][0][1][1] = 25
  p[i][ny-1][3][0] = 25
  p[i][ny-1][3][1] = 25

for j in range(ny):
  p[0][j][0][0] = 25
  p[0][j][0][1] = 25
  p[nx-1][j][2][0] = 25
  p[nx-1][j][2][1] = 25

while True: draw2()
