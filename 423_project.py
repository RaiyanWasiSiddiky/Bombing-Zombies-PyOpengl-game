# TASK1

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# for numpy, run from terminal ---> code runner doesnt seem to run from environment for some reason
# import numpy as np
# a = np.array([1,2,3])
# print(a)

import math
import random
import time
import numpy as np

R = 0
G = 0
B = 0
WIDTH = 1200
HEIGHT = 600

pause_state = False
show_bounds = False
throw_state = False
bombs = []
new_bomb = None
zombies = []
first_time = time.time()
game_over_state = False
score = 0
print(f'SCORE: {score}')

# delta time taken after some frame rate calculation, however still inconsistent 
# delta_time = 0.001
# delta_time = 0.01
delta_time = 0.005


# box = [x, width, y, height]
# box here basically does the AABB collision functionality using bounding boxes
class Pivot:
    def __init__(self, x, y, radius = None, box = None, vx = None, vy = None, hp = None, special = None, speed = None):
        self.x = x
        self.y = y
        self.radius = radius
        self.box = box
        self.vx = vx
        self.vy = vy
        self.hp = hp
        self.special = special
        self.speed = speed

pause = Pivot(0, 280)
resume = Pivot(0, 100)
restart = Pivot(0, 0)
exit = Pivot(0, -100)
man = Pivot(-425, -185)
shield = Pivot(-350, -185)

def draw_point(x, y):
    glBegin(GL_POINTS)
    glVertex2f(x,y) 
    glEnd()

# convert is for going back to zone 0
# it is in the form - swap, xneg, yneg
# e.g. if, when going from any zone to zone 0, we swapped positions, x became negative, y became negative
# then convert = [True, True, True]
def find_and_convert_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1

    if dx >= 0 and dy >= 0:  
        if abs(dx) >= abs(dy):  
            # Zone 0
            convert = [False, False, False]
        else:  
            # Zone 1
            x1, y1 = y1, x1
            x2, y2 = y2, x2
            convert = [True, False, False]

    elif dx < 0 and dy >= 0: 
        if abs(dx) >= abs(dy):  
            # Zone 3
            x1, y1 = -x1, y1
            x2, y2 = -x2, y2
            convert = [False, True, False]
        else:  
            # Zone 2
            x1, y1 = y1, -x1
            x2, y2 = y2, -x2
            convert = [True, True, False]

    elif dx < 0 and dy < 0:  
        if abs(dx) >= abs(dy):  
            # Zone 4
            x1, y1 = -x1, -y1
            x2, y2 = -x2, -y2
            convert = [False, True, True]
        else:  
            # Zone 5
            x1, y1 = -y1, -x1
            x2, y2 = -y2, -x2
            convert = [True, True, True]

    elif dx >= 0 and dy < 0:  
        if abs(dx) >= abs(dy):  
            # Zone 7
            x1, y1 = x1, -y1
            x2, y2 = x2, -y2
            convert = [False, False, True]
        else:  
            # Zone 6
            x1, y1 = -y1, x1
            x2, y2 = -y2, x2
            convert = [True, False, True]

    return x1, y1, x2, y2, convert
        

def draw_line(x1, y1, x2, y2):

    x1, y1, x2, y2, convert = find_and_convert_zone(x1, y1, x2, y2)

    dx = x2 - x1
    dy = y2 - y1
    d = 2*dy - dx
    delE = 2*dy
    delNE = 2 * (dy - dx)


    glBegin(GL_POINTS)
    while x1 <= x2:
        # convert back to original zone
        x_draw, y_draw = x1, y1
        if convert[0]:  # Swap
            x_draw, y_draw = y_draw, x_draw
        if convert[1]:  # Negate X
            x_draw = -x_draw
        if convert[2]:  # Negate Y
            y_draw = -y_draw

        glVertex2f(x_draw,y_draw) 

        if d > 0:
            y1 += 1
            d += delNE
        else:
            d += delE
        x1 += 1 
    glEnd()

    
def draw_quad(x1, y1, x2, y2, x3, y3, x4, y4):
    draw_line(x1, y1, x2, y2)
    draw_line(x2, y2, x3, y3)
    draw_line(x3, y3, x4, y4)
    draw_line(x4, y4, x1, y1)

def draw_triangle(x1, y1, x2, y2, x3, y3):
    draw_line(x1, y1, x2, y2)
    draw_line(x2, y2, x3, y3)
    draw_line(x3, y3, x1, y1)


def draw_circle(x0, y0, radius):

    x_temp = 0
    y_temp = radius
    d = 1 - radius

    glBegin(GL_POINTS)
    while x_temp <= y_temp:
        glVertex2f(x_temp + x0, y_temp + y0)  # Zone 1
        glVertex2f(y_temp + x0, x_temp + y0)  # Zone 0
        glVertex2f(-x_temp + x0, y_temp + y0) # Zone 2
        glVertex2f(-y_temp + x0, x_temp + y0) # Zone 3
        glVertex2f(-x_temp + x0, -y_temp + y0) # Zone 5
        glVertex2f(-y_temp + x0, -x_temp + y0) # Zone 4
        glVertex2f(x_temp + x0, -y_temp + y0)  # Zone 6
        glVertex2f(y_temp + x0, -x_temp + y0)  # Zone 7

        if d >= 0:
            d += 2 * (x_temp - y_temp) + 5
            y_temp -= 1
        else:
            d += 2 * x_temp + 3

        x_temp += 1
    glEnd()



def iterate():
    global WIDTH, HEIGHT

    glViewport(0, 0, WIDTH, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-600, 600, -300, 300, 0, 1)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def animate():
    global new_bomb, bombs, man, zombies, first_time, pause_state, game_over_state, shield, delta_time, score

    prob = random.random()
    current_time = time.time()
    if (current_time - first_time)>=(10): # difficulty
        if pause_state == False and game_over_state == False:
            if prob<0.1:
                # fast zombies
                zombie = Pivot(610, -185)
                zombie.box = [zombie.x-25, 50, zombie.y-35, 70]
                zombie.hp = 1
                zombie.special = 1
                zombie.speed = 1
            
            elif 0.1<prob<0.2:
                # tanky zombies
                zombie = Pivot(610, -185)
                zombie.box = [zombie.x-25, 50, zombie.y-35, 70]
                zombie.hp = 2
                zombie.special = 0
                zombie.speed = 0.1

            else:
                # normal zombies
                zombie = Pivot(610, -185)
                zombie.box = [zombie.x-25, 50, zombie.y-35, 70]
                zombie.hp = 1
                zombie.special = 0
                zombie.speed = 0.2
            zombies.append(zombie)
            first_time = current_time

    if zombies != []:
        for zombie in zombies:
            zombie.x -= zombie.speed

            if zombie.box[0] < shield.box[0]+shield.box[1]:
                zombies.remove(zombie)

    for bomb in bombs:
        # delx = bomb.vx*(delta_time)
        bomb.x += bomb.vx*(delta_time)

        # dely = bomb.vy*(delta_time) - 0.5*9.8*(delta_time)**2
        bomb.y += bomb.vy*(delta_time)
        bomb.vy -= 36*9.8*(delta_time)

        if bomb.x > 600 or bomb.y < -220:
            bombs.remove(bomb)

        # if bomb.y < -220:
            # bomb.vy = -0.8*bomb.vy
            # if bomb.vy < 5:
            #     bombs.remove(bomb)

        for zombie in zombies:
            if (bomb.box[0] < zombie.box[0] + zombie.box[1]  and
            bomb.box[0] + bomb.box[1] > zombie.box[0]  and
            bomb.box[2] < zombie.box[2] + zombie.box[3] and
            bomb.box[2] + bomb.box[3] > zombie.box[2]):
                zombie.hp -= 1
                bombs.remove(bomb)
                if zombie.hp == 0:
                    score += 1
                    zombies.remove(zombie)
                    print(f'SCORE: {score}')

    glutPostRedisplay()

def mouseMotionListener(x, y):
    global throw_state, man, new_bomb

    mouse_x = x - 600
    mouse_y = 300 - y

    if throw_state == True:
        # print(mouse_x, mouse_y)

        # box = [x, width, y, height]
        new_bomb.x = mouse_x
        if mouse_x < man.box[0]:
            new_bomb.x = man.box[0]
        elif mouse_x > man.box[0]+man.box[1]:
            new_bomb.x = man.box[0]+man.box[1]

        new_bomb.y = mouse_y
        if mouse_y < man.box[2]:
            new_bomb.y = man.box[2]
        elif mouse_y > man.box[2]+man.box[3]:
            new_bomb.y = man.box[2]+man.box[3]

        new_bomb.vx = -3.5*(mouse_x - man.x)
        new_bomb.vy = -13*(mouse_y - man.y)


    glutPostRedisplay()


def KeyboardListen(key, x, y):
    global show_bounds

    # print(key)
    if key==b'\r':
        if show_bounds == False:
            show_bounds = True
        else:        
            show_bounds = False

    glutPostRedisplay()

def specialKeyListener(key, x, y):
    # print(key)

    glutPostRedisplay()

def mouseListener(button, state, x, y):   
    global pause, pause_state, resume, restart, exit, throw_state, bombs, new_bomb

    mouse_x = x - 600
    mouse_y = 300 - y
    # print(mouse_x, mouse_y)
        
    if button==GLUT_RIGHT_BUTTON:
        # if i dont have glut_down, this runs twice once when clicking the button once when letting go
        if state == GLUT_DOWN: 	
            pass

    if button==GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:

            if throw_state == False:
                if ((mouse_x)>=man.box[0]) and ((mouse_x)<=(man.box[0]+man.box[1])) and ((mouse_y)>=man.box[2]) and ((mouse_y)<=(man.box[2]+man.box[3])):
                    throw_state = True
                    bomb = Pivot(mouse_x, mouse_y, 10)
                    new_bomb = bomb
            else:
                throw_state = False
                # x is adjacent, y is opposite

                # adj = new_bomb.x - man.x
                # if adj == 0:
                #     adj = 0.00000001
                # theta = math.atan2((new_bomb.y-man.y)/adj)

                # apparently atan2 handles 0 error internally
                theta = math.atan2(abs(new_bomb.y - man.y), abs(new_bomb.x - man.x))
                new_bomb.vx = new_bomb.vx * math.cos(theta)
                new_bomb.vy = new_bomb.vy * math.sin(theta)
                bombs.append(new_bomb)
                new_bomb = None

            if ((mouse_x)>=pause.box[0]) and ((mouse_x)<=(pause.box[0]+pause.box[1])) and ((mouse_y)>=pause.box[2]) and ((mouse_y)<=(pause.box[2]+pause.box[3])):
                # pause
                pause_state = True

            if pause_state == True:
                if ((mouse_x)>=resume.box[0]) and ((mouse_x)<=(resume.box[0]+resume.box[1])) and ((mouse_y)>=resume.box[2]) and ((mouse_y)<=(resume.box[2]+resume.box[3])):
                    # resume
                    # print("RESUME")
                    pause_state = False

                elif ((mouse_x)>=restart.box[0]) and ((mouse_x)<=(restart.box[0]+restart.box[1])) and ((mouse_y)>=restart.box[2]) and ((mouse_y)<=(restart.box[2]+restart.box[3])):
                    # restart
                    # print("RESTART")
                    pass

                elif ((mouse_x)>=exit.box[0]) and ((mouse_x)<=(exit.box[0]+exit.box[1])) and ((mouse_y)>=exit.box[2]) and ((mouse_y)<=(exit.box[2]+exit.box[3])):
                    # exit
                    # print("EXIT")
                    glutLeaveMainLoop() 

        elif state == GLUT_UP:
            pass
                    
                    
    glutPostRedisplay()

def showScreen():
    global R, G, B, pause, pause_state, resume, restart, exit, show_bounds, man, bombs, new_bomb, zombies, throw_state

    # background
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(R/255, G/255, B/255, 0);	
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    iterate()

    #call the draw methods here

    glPointSize(2) 

    # LAND
    glColor3f(255/255, 255/255, 255/255)
    draw_line(-600, -220, 600, -220)
    

    # MAN
    glColor3f(255/255, 255/255, 255/255)
    draw_quad(man.x-25, man.y-35, man.x-25, man.y+35, man.x+25, man.y+35, man.x+25, man.y-35)
    glColor3f(63/255, 152/255, 69/255)
    man.box = [man.x-70, 140, man.y-35, 140]
    if show_bounds == True:
        draw_quad(man.box[0], man.box[2], man.box[0], man.box[2]+man.box[3], man.box[0]+man.box[1], man.box[2]+man.box[3], man.box[0]+man.box[1], man.box[2])

    # SHIELD
    glColor3f(255/255, 255/255, 255/255)
    draw_quad(shield.x-25, shield.y-35, shield.x-25, shield.y+35, shield.x+25, shield.y+35, shield.x+25, shield.y-35)
    glColor3f(63/255, 152/255, 69/255)
    shield.box = [shield.x-25, 50, shield.y-35, 70]
    if show_bounds == True:
        draw_quad(shield.box[0], shield.box[2], shield.box[0], shield.box[2]+shield.box[3], shield.box[0]+shield.box[1], shield.box[2]+shield.box[3], shield.box[0]+shield.box[1], shield.box[2])

    # ZOMBIES
    glColor3f(255/255, 255/255, 255/255)
    if zombies != []:
        for zombie in zombies:
            draw_quad(zombie.x-25, zombie.y-35, zombie.x-25, zombie.y+35, zombie.x+25, zombie.y+35, zombie.x+25, zombie.y-35)
            zombie.box = [zombie.x-25, 50, zombie.y-35, 70]
            if show_bounds == True:
                glColor3f(63/255, 152/255, 69/255)
                draw_quad(zombie.box[0], zombie.box[2], zombie.box[0], zombie.box[2]+zombie.box[3], zombie.box[0]+zombie.box[1], zombie.box[2]+zombie.box[3], zombie.box[0]+zombie.box[1], zombie.box[2])
            glColor3f(255/255, 255/255, 255/255)

    # BOMB CREATION
    glColor3f(255/255, 255/255, 255/255)
    if new_bomb != None:
        draw_circle(new_bomb.x, new_bomb.y, new_bomb.radius)
        if throw_state == True:
            draw_line(man.x-25, man.y+35, new_bomb.x, new_bomb.y)
            draw_line(man.x-25, man.y+15, new_bomb.x, new_bomb.y)

    # BOMBS
    if bombs != []:
        for bomb in bombs:
            draw_circle(bomb.x, bomb.y, bomb.radius)
            glColor3f(63/255, 152/255, 69/255)
            bomb.box = [bomb.x-bomb.radius, 2*bomb.radius, bomb.y-bomb.radius, 2*bomb.radius]
            if show_bounds == True:
                draw_quad(bomb.box[0], bomb.box[2], bomb.box[0], bomb.box[2]+bomb.box[3], bomb.box[0]+bomb.box[1], bomb.box[2]+bomb.box[3], bomb.box[0]+bomb.box[1], bomb.box[2])
            glColor3f(255/255, 255/255, 255/255)


    
    # PAUSE BUTTON
    if pause_state == False:
        glColor3f(255/255, 255/255, 255/255)
    else:
        glColor3f(107/255, 107/255, 107/255)
    draw_quad(pause.x-5, pause.y-10, pause.x-10, pause.y-10, pause.x-10, pause.y+10, pause.x-5, pause.y+10)
    draw_quad(pause.x+5, pause.y-10, pause.x+10, pause.y-10, pause.x+10, pause.y+10, pause.x+5, pause.y+10)
    glColor3f(63/255, 152/255, 69/255)
    pause.box = [pause.x-12, 24, pause.y-12, 24]
    if show_bounds == True:
        draw_quad(pause.box[0], pause.box[2], pause.box[0], pause.box[2]+pause.box[3], pause.box[0]+pause.box[1], pause.box[2]+pause.box[3], pause.box[0]+pause.box[1], pause.box[2])


    # PAUSE BOX
    resume.box = [resume.x-202, 404, resume.y-50, 102]
    restart.box = [restart.x-202, 404, restart.y-49, 98]
    exit.box = [exit.x-202, 404, exit.y-52, 100]
    if pause_state == True:
        # RESUME BUTTON
        glColor3f(255/255, 255/255, 255/255)
        draw_quad(resume.x-200, resume.y-50, resume.x-200, resume.y+50, resume.x+200, resume.y+50, resume.x+200, resume.y-50)
        draw_triangle(resume.x-30, resume.y-30, resume.x-30, resume.y+30, resume.x+30, resume.y)
        glColor3f(63/255, 152/255, 69/255)
        if show_bounds == True:
            draw_quad(resume.box[0], resume.box[2], resume.box[0], resume.box[2]+resume.box[3], resume.box[0]+resume.box[1], resume.box[2]+resume.box[3], resume.box[0]+resume.box[1], resume.box[2])


        # RESTART BUTTON
        glColor3f(255/255, 255/255, 255/255)
        draw_quad(restart.x-200, restart.y-50, restart.x-200, restart.y+50, restart.x+200, restart.y+50, restart.x+200, restart.y-50)
        draw_line(restart.x-30, restart.y, restart.x+30, restart.y)
        draw_line(restart.x-30, restart.y, restart.x-10, restart.y+20)
        draw_line(restart.x-30, restart.y, restart.x-10, restart.y-20)
        glColor3f(63/255, 152/255, 69/255)
        if show_bounds == True:
            draw_quad(restart.box[0], restart.box[2], restart.box[0], restart.box[2]+restart.box[3], restart.box[0]+restart.box[1], restart.box[2]+restart.box[3], restart.box[0]+restart.box[1], restart.box[2])


        # EXIT BUTTON
        glColor3f(255/255, 255/255, 255/255)
        draw_quad(exit.x-200, exit.y-50, exit.x-200, exit.y+50, exit.x+200, exit.y+50, exit.x+200, exit.y-50)
        draw_line(exit.x-30, exit.y-30, exit.x+30, exit.y+30)
        draw_line(exit.x-30, exit.y+30, exit.x+30, exit.y-30)
        glColor3f(63/255, 152/255, 69/255)
        if show_bounds == True:
            draw_quad(exit.box[0], exit.box[2], exit.box[0], exit.box[2]+exit.box[3], exit.box[0]+exit.box[1], exit.box[2]+exit.box[3], exit.box[0]+exit.box[1], exit.box[2])
    
    glutSwapBuffers()



glutInit()
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(WIDTH, HEIGHT) #window size
glutInitWindowPosition(180, 100)
wind = glutCreateWindow(b"423 PROJECT ZOMBBOMBS") #window name
glutDisplayFunc(showScreen)

glutIdleFunc(animate)

glutKeyboardFunc(KeyboardListen)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)

glutPassiveMotionFunc(mouseMotionListener)


glutMainLoop()


