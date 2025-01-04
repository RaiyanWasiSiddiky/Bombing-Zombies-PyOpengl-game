# strange bug where minimizing the window results in collision of zombie with
# both man and shield, causing shield to lose hp and game over
# not sure how to fix

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

R = 0
G = 0
B = 0
WIDTH = 1300
HEIGHT = 700

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

difficulty = 0
time_diff = 0
boss_spawn = False
spikes = False
spikes_time = 0
hp_boost = 0
hp_change = False
hp_time = 0
color_up = False
cg, cb, cr = 255, 255, 255
boss_time = 0


yellow_ball = None
yellow_quantity = 0
last_yellow_ball_spawn_time = time.time()

green_ball = None 
last_green_ball_spawn_time = time.time()  # Track the last spawn time of the green ball

red_ball = None
last_red_ball_spawn_time = time.time()  # Track the last spawn time of the red ball


def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))



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

pause = Pivot(0, 310)
resume = Pivot(0, 100)
restart = Pivot(0, 0)
exit = Pivot(0, -100)
man = Pivot(-425, -185)

shield = Pivot(-350, -185)
shield.hp = 3
max_shield = 3



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

def draw_ninja_star(x, y, size):
    """Draws a ninja star at (x, y) with the specified size using gl_points."""
    for i in range(4):  # 4 blades
        # Calculate angles for each blade
        angle1 = math.pi / 4 + i * math.pi / 2  # Start angle for each blade
        angle2 = angle1 + math.pi / 4          # End angle for each blade

        # Outer tip of the blade
        x1 = x + size * math.cos(angle1)
        y1 = y + size * math.sin(angle1)

        # Inner tip of the blade
        x2 = x + (size / 2) * math.cos(angle2)
        y2 = y + (size / 2) * math.sin(angle2)

        # Center point
        cx, cy = x, y

        # Draw blade as a quadrilateral using the draw_line function
        draw_triangle(cx, cy, x1, y1, x2, y2)

    # Optionally, draw a central circle or a small square to represent the hub
    # Example: a circle at the center
    draw_circle(x, y, size / 10)  # A small circle in the center

def draw_player(x, y):
    """Draws a cooler ninja-style player character at (x, y)."""
    # Head with ninja mask
    glColor3f(1.0, 1.0, 1.0)  # Dark gray/black for ninja mask
    draw_circle(x, y + 35, 12)  # Larger head for a bold look

    # Mask covering lower face
    glColor3f(0.2, 0.2, 0.2)
    draw_quad(x - 7, y + 30, x - 7, y + 35, x + 7, y + 35, x + 7, y + 30)  # Mouth cover

    # Bandana on head with flowing ties
    glColor3f(1.0, 0.0, 0.0)  # Red for bandana
    draw_quad(x - 10, y + 38, x - 10, y + 42, x + 10, y + 42, x + 10, y + 38)  # Headband front
    draw_triangle(x + 10, y + 42, x + 18, y + 48, x + 12, y + 44)  # Right tie
    draw_triangle(x - 10, y + 42, x - 18, y + 48, x - 12, y + 44)  # Left tie

    # Eyes with fierce expression
    glColor3f(1.0, 1.0, 1.0)  # White for eyes
    draw_quad(x - 5, y + 36, x - 5, y + 39, x - 1, y + 39, x - 1, y + 36)  # Left eye
    draw_quad(x + 1, y + 36, x + 1, y + 39, x + 5, y + 39, x + 5, y + 36)  # Right eye

    # Arms in ready-to-attack pose
    glColor3f(1.0, 1.0, 1.0)
    # draw_line(x, y + 15, x - 15, y + 10)  # Left arm raised
    # draw_line(x, y + 15, x + 15, y + 10)  # Right arm lowered

    # Body (muscular torso)
    draw_quad(x - 8, y + 20, x - 8, y - 20, x + 8, y - 20, x + 8, y + 20)

    # Legs with a dynamic stance
    draw_line(x, y - 20, x - 10, y - 35)  # Left leg stepping back
    draw_line(x, y - 20, x + 12, y - 35)  # Right leg ready to spring forward

def draw_normal_zombie(x, y):
    """Draws a cool-looking normal zombie at (x, y)."""
    glColor3f(0.3, 0.8, 0.3)  # Sickly green for zombie skin
    draw_circle(x, y + 35, 12)  # Head
    glColor3f(0.1, 0.1, 0.1)  # Dark gray for sunken eyes
    draw_quad(x - 4, y + 38, x - 4, y + 41, x - 1, y + 41, x - 1, y + 38)  # Left eye
    draw_quad(x + 1, y + 38, x + 1, y + 41, x + 4, y + 41, x + 4, y + 38)  # Right eye
    glColor3f(1.0, 0.0, 0.0)  # Red for bloody mouth
    draw_triangle(x - 3, y + 30, x + 3, y + 30, x, y + 25)  # Mouth
    glColor3f(0.4, 0.2, 0.2)  # Tattered clothes
    draw_quad(x - 10, y + 20, x - 10, y - 20, x + 10, y - 20, x + 10, y + 20)
    glColor3f(0.3, 0.8, 0.3)  # Arms with claws
    draw_line(x - 10, y + 10, x - 18, y + 5)  # Left arm
    draw_line(x + 10, y + 10, x + 18, y + 5)  # Right arm
    draw_line(x - 18, y + 5, x - 20, y + 3)  # Left claw
    draw_line(x + 18, y + 5, x + 20, y + 3)  # Right claw

def draw_fast_zombie(x, y):
    """Draws a fast, feral zombie at (x, y)."""
    glColor3f(0.2, 0.7, 0.2)  # Dark green for decayed skin
    draw_circle(x, y + 30, 10)  # Small head
    glColor3f(0.8, 0.1, 0.1)  # Blood red eyes
    draw_circle(x - 3, y + 32, 2)  # Left eye
    draw_circle(x + 3, y + 32, 2)  # Right eye
    glColor3f(0.3, 0.3, 0.3)  # Torn clothes
    draw_quad(x - 7, y + 15, x - 7, y - 15, x + 7, y - 15, x + 7, y + 15)
    glColor3f(0.2, 0.7, 0.2)  # Thin arms and legs
    draw_line(x, y + 5, x - 10, y)  # Left arm
    draw_line(x, y + 5, x + 10, y)  # Right arm

def draw_slow_zombie(x, y):
    """Draws a tanky zombie at (x, y)."""
    glColor3f(0.4, 0.7, 0.4)  # Greenish-gray for tough skin
    draw_circle(x, y + 40, 15)  # Large head
    glColor3f(1.0, 1.0, 1.0)  # Armor patches
    draw_quad(x - 30, y + 20, x - 30, y - 20, x + 30, y - 20, x + 30, y + 20)
    draw_quad(x - 10, y - 5, x - 10, y - 10, x + 10, y - 10, x + 10, y - 5)  # Stomach armor
    glColor3f(0.4, 0.7, 0.4)  # Thick arms and legs
    draw_line(x - 15, y + 10, x - 20, y)  # Left arm
    draw_line(x + 15, y + 10, x + 20, y)  # Right arm
    draw_line(x - 10, y - 20, x - 15, y - 50)  # Left leg
    draw_line(x + 10, y - 20, x + 15, y - 50)  # Right leg

def draw_zombie_boss(x, y):
    """Draws a larger and more menacing zombie boss at (x, y)."""
    # Massive head with glowing eyes
    glColor3f(0.1, 0.1, 0.1)  # Dark gray for shadowy skin
    draw_circle(x, y + 70, 25)  # Larger head for boss

    glColor3f(1.0, 0.0, 0.0)  # Bright red for glowing eyes
    draw_circle(x - 10, y + 75, 5)  # Left eye
    draw_circle(x + 10, y + 75, 5)  # Right eye

    glColor3f(0.0, 0.0, 0.0)  # Black for fanged mouth
    draw_triangle(x - 7, y + 62, x + 7, y + 62, x, y + 55)  # Open mouth

    # Large torso with spikes
    glColor3f(0.4, 0.2, 0.2)  # Dark armor
    draw_quad(x - 50, y + 40, x - 50, y - 40, x + 50, y - 40, x + 50, y + 40)

    glColor3f(0.5, 0.1, 0.1)  # Spikes
    draw_triangle(x - 35, y + 35, x - 25, y + 50, x - 35, y + 65)  # Left upper spike
    draw_triangle(x + 35, y + 35, x + 25, y + 50, x + 35, y + 65)  # Right upper spike
    draw_triangle(x - 35, y - 15, x - 25, y - 5, x - 35, y + 5)  # Left lower spike
    draw_triangle(x + 35, y - 15, x + 25, y - 5, x + 35, y + 5)  # Right lower spike

    # Arms with claws
    glColor3f(0.1, 0.1, 0.1)
    draw_line(x - 30, y + 10, x - 45, y)  # Left arm
    draw_line(x + 30, y + 10, x + 45, y)  # Right arm
    draw_line(x - 45, y, x - 50, y - 5)  # Left claw
    draw_line(x + 45, y, x + 50, y - 5)  # Right claw

    # Thick legs in a sturdy stance
    draw_line(x, y - 40, x - 20, y - 80)  # Left leg
    draw_line(x, y - 40, x + 20, y - 80)  # Right leg



def iterate():
    global WIDTH, HEIGHT

    glViewport(0, 0, WIDTH, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-650, 650, -350, 350, 0, 1)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()


def animate():
    global new_bomb, bombs, man, zombies, first_time, pause_state, game_over_state
    global shield, delta_time, score, difficulty, time_diff, boss_spawn, spikes, spikes_time
    global hp_change, hp_boost, hp_time, boss_time, max_shield

    global yellow_ball, yellow_quantity, last_yellow_ball_spawn_time
    global last_green_ball_spawn_time, green_ball
    global red_ball, last_red_ball_spawn_time
  

    if pause_state == False and game_over_state == False:
        prob = random.random()
        current_time = time.time()

        if yellow_ball is None:
            # Check if 60 seconds have passed since the last yellow ball spawn
            if current_time - last_yellow_ball_spawn_time >= 60:
                yellow_ball = Pivot(650, -185, 10)
                last_yellow_ball_spawn_time = current_time  # Update the last spawn time

        # Move the yellow ball towards the player
        elif yellow_ball is not None:
            yellow_ball.x -= 2

            # Check for collision with bombs
            for bomb in bombs:
                if (bomb.box[0] < yellow_ball.box[0] + yellow_ball.box[1]  and
                bomb.box[0] + bomb.box[1] > yellow_ball.box[0]  and
                bomb.box[2] < yellow_ball.box[2] + yellow_ball.box[3] and
                bomb.box[2] + bomb.box[3] > yellow_ball.box[2]):
                    # Bomb hits the yellow ball
                    yellow_quantity += 1
                    yellow_ball = None
                    break

            # DOES NOT DAMAGE OR KILL
            if yellow_ball is not None:
                if yellow_ball.x < -650:  # Assuming -650 is the left of your window
                    yellow_ball = None  # Remove the yellow ball after it goes off-screen



        # Red ball
        if red_ball is None:

            # Check if enough time has passed to spawn a new red ball
            if current_time - last_red_ball_spawn_time >= 40:
                red_ball = Pivot(random.randint(-600, 600), 360, 10)  # Spawn at a random x-coordinate at the top
                last_red_ball_spawn_time = current_time  # Update the last spawn time

        # Move the red ball down
        elif red_ball is not None:
            red_ball.y -= 0.5

            # Check for collision with bombs
            for bomb in bombs:
                if (bomb.box[0] < red_ball.box[0] + red_ball.box[1]  and
                bomb.box[0] + bomb.box[1] > red_ball.box[0]  and
                bomb.box[2] < red_ball.box[2] + red_ball.box[3] and
                bomb.box[2] + bomb.box[3] > red_ball.box[2]):
                    # Bomb hits the red ball
                    shield.hp -= 1
                    red_ball = None  # Remove the red ball after it is hit
                    break  # Exit the loop after hitting the ball

                if shield.hp == 0:
                    shield.box = [-1000, 0, -1000, 0]
                    # game_over_state = True
                    # print("GAME OVER")
                    # print(f'SCORE: {score}')

            if red_ball is not None:
                if red_ball.y < -220:  
                    red_ball = None  # Remove the red ball after it goes off-screen



        #green ball
        if green_ball is None:

            # Check if enough time has passed to spawn a new green ball
            if current_time - last_green_ball_spawn_time >= 100:
                green_ball = Pivot(random.randint(-600, 600), 350, 10)  # Spawn at a random x-coordinate at the top
                last_green_ball_spawn_time = current_time  # Update the last spawn time

        # Move the green ball down
        elif green_ball is not None:
            green_ball.y -= 0.5
       
            # Check for collision with bombs
            for bomb in bombs:
                if (bomb.box[0] < green_ball.box[0] + green_ball.box[1]  and
                bomb.box[0] + bomb.box[1] > green_ball.box[0]  and
                bomb.box[2] < green_ball.box[2] + green_ball.box[3] and
                bomb.box[2] + bomb.box[3] > green_ball.box[2]):
                    if shield.hp<max_shield:
                        shield.hp += 1  # Increase shield health

                    else:
                        pass
                    green_ball = None  # Remove the green ball after it is hit
                    break  # Exit the loop after hitting the bal

            if green_ball is not None:
                if green_ball.y < -220:  # Assuming -350 is the bottom of your window
                    green_ball = None 
  


        if (current_time - first_time)>=(10 - difficulty): # difficulty
            if prob<0.15+hp_boost/2:
                # fast zombies
                zombie = Pivot(680, -185)
                zombie.box = [zombie.x-30, 60, zombie.y-35, 50]
                zombie.hp = 1 
                zombie.special = 1
                zombie.speed = 1
            
            elif 0.15+hp_boost/2<prob<0.3+hp_boost:
                # tanky zombies
                zombie = Pivot(690, -185)
                zombie.box = [zombie.x-40, 80, zombie.y-35, 100]
                zombie.hp = 2 + hp_boost
                zombie.special = 2
                zombie.speed = 0.1

            else:
                # normal zombies
                zombie = Pivot(675, -185)
                zombie.box = [zombie.x-25, 50, zombie.y-35, 70]
                zombie.hp = 1 + hp_boost
                zombie.special = 0
                zombie.speed = 0.2
            zombies.append(zombie)
            first_time = current_time

        if score%15==0 and boss_spawn == False:
            boss = Pivot(710, -185)
            boss.box = [boss.x-60, 120, boss.y-35, 150]
            boss.hp = 4 + score//15 + hp_boost
            boss.special = 3
            boss.speed = 0.05
            zombies.append(boss)
            boss_spawn = True
            boss_time = time.time()


        if zombies != []:
            for zombie in zombies:
                zombie.x -= zombie.speed

                if zombie.box[0] < shield.box[0]+shield.box[1]:
                    spikes = True
                    spikes_time = time.time()

                    if zombie.special == 3:
                        shield.hp = 0
                        zombie.hp -= 1
                        if zombie.hp == 0:
                            score += 5
                            zombies.remove(zombie)
                            print(f'SCORE: {score}')
                    else:
                        zombies.remove(zombie)
                        score += 1
                        print(f'SCORE: {score}')
                        shield.hp -= 1

                    if shield.hp == 0:
                        shield.box = [-1000, 0, -1000, 0]
                        # game_over_state = True
                        # print("GAME OVER")
                        # print(f'SCORE: {score}')

                if zombie.box[0] < man.box[0]+man.box[1]:
                    # strange bug where minimizing the window results in collision of zombie with
                    # both man and shield, causing shield to lose hp and game over
                    game_over_state = True
                    print("GAME OVER")
                    print(f'FINAL SCORE: {score}')


        for bomb in bombs:
            # delx = bomb.vx*(delta_time)
            bomb.x += bomb.vx*(delta_time)

            # dely = bomb.vy*(delta_time) - 0.5*9.8*(delta_time)**2
            bomb.y += bomb.vy*(delta_time)
            bomb.vy -= 36*9.8*(delta_time)

            for zombie in zombies:
                if (bomb.box[0] < zombie.box[0] + zombie.box[1]  and
                bomb.box[0] + bomb.box[1] > zombie.box[0]  and
                bomb.box[2] < zombie.box[2] + zombie.box[3] and
                bomb.box[2] + bomb.box[3] > zombie.box[2]):
                    zombie.hp -= 1
                    if bomb in bombs:
                        bombs.remove(bomb)
                    if zombie.hp == 0:
                        if zombie.special == 3:
                            score += 5
                        else:
                            score += 1
                        zombies.remove(zombie)
                        print(f'SCORE: {score}')

            if bomb.x > 650 or bomb.y < -220:
                if bomb in bombs:
                    bombs.remove(bomb)

            # TBD: BOMB BOUNCE
            # if bomb.y < -220:
                # bomb.vy = -0.8*bomb.vy
                # if bomb.vy < 5:
                #     if bomb in bombs:
                #         bombs.remove(bomb)

        if (10 - difficulty)>3:
            difficulty += 0.00004

        if (score > 4 and score % 50 in {0, 1, 2, 3, 4} and not hp_change):
            hp_boost += 1
            hp_change = True
            hp_time = time.time()

    if pause_state == True:
        # for preserving the time difference between each zombie
        current_time = time.time()
        first_time = current_time - time_diff

    if spikes == True:
        if (time.time() - spikes_time) > 1:
            spikes = False

    if hp_change == True:
        if (time.time() - hp_time) > 5:
            if (score % 50) not in {0, 1, 2, 3, 4}:
                hp_change = False

    if boss_spawn == True:
        if (time.time() - boss_time) > 7:
            if score%15!=0:
                boss_spawn = False

    glutPostRedisplay()



def mouseMotionListener(x, y):
    global throw_state, man, new_bomb

    mouse_x = x - 650
    mouse_y = 350 - y

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
    global show_bounds,show_bounds, yellow_quantity, zombies,score
    

    # print(key)
    if key==b'\r':
        if show_bounds == False:
            show_bounds = True
        else:        
            show_bounds = False
    
    if key == b'p':
        if yellow_quantity > 0:
            score +=len(zombies)
            print(f'SCORE: {score}')


            zombies.clear()  # Remove all zombies
            yellow_quantity -=1 

    glutPostRedisplay()

def specialKeyListener(key, x, y):
    # print(key)

    glutPostRedisplay()

def mouseListener(button, state, x, y):   
    global pause_state, show_bounds, throw_state, bombs, new_bomb, zombies, first_time
    global game_over_state, score, delta_time, difficulty, time_diff, pause, resume, restart
    global exit, man, shield, max_shield, boss_spawn, spikes, spikes_time, hp_boost, hp_change
    global color_up, cg, cb, cr, boss_time

    global yellow_ball, yellow_quantity, last_yellow_ball_spawn_time, green_ball
    global last_green_ball_spawn_time, red_ball, last_red_ball_spawn_time

    mouse_x = x - 650
    mouse_y = 350 - y
    # print(mouse_x, mouse_y)
        
    if button==GLUT_RIGHT_BUTTON:
        # if i dont have glut_down, this runs twice once when clicking the button once when letting go
        if state == GLUT_DOWN: 	
            pass

    if button==GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:

            if pause_state == False and game_over_state == False:

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
                    # theta = math.atan2((new_bomb.y-man.y), adj)

                    # apparently atan2 handles 0 error internally
                    theta = math.atan2(abs(new_bomb.y - man.y), abs(new_bomb.x - man.x))
                    new_bomb.vx = new_bomb.vx * math.cos(theta)
                    new_bomb.vy = new_bomb.vy * math.sin(theta)
                    bombs.append(new_bomb)
                    new_bomb = None

                if ((mouse_x)>=pause.box[0]) and ((mouse_x)<=(pause.box[0]+pause.box[1])) and ((mouse_y)>=pause.box[2]) and ((mouse_y)<=(pause.box[2]+pause.box[3])):
                    # pause
                    pause_state = True
                    time_diff = time.time() - first_time
                

            if pause_state == True or game_over_state == True:
                if pause_state == True:
                    if ((mouse_x)>=resume.box[0]) and ((mouse_x)<=(resume.box[0]+resume.box[1])) and ((mouse_y)>=resume.box[2]) and ((mouse_y)<=(resume.box[2]+resume.box[3])):
                        # resume
                        # print("RESUME")
                        pause_state = False

                if ((mouse_x)>=restart.box[0]) and ((mouse_x)<=(restart.box[0]+restart.box[1])) and ((mouse_y)>=restart.box[2]) and ((mouse_y)<=(restart.box[2]+restart.box[3])):
                    # restart
                    # print("RESTART")
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
                    delta_time = 0.005

                    difficulty = 0
                    time_diff = 0

                    boss_spawn = False
                    spikes = False
                    spikes_time = 0
                    hp_boost = 0
                    hp_change = False
                    color_up = False
                    cg, cb, cr = 255, 255, 255
                    boss_time = 0

                    yellow_ball = None
                    yellow_quantity = 0
                    last_yellow_ball_spawn_time = time.time()
                    green_ball = None 
                    last_green_ball_spawn_time = time.time()  # Track the last spawn time of the green ball
                    red_ball = None
                    last_red_ball_spawn_time = time.time()  # Track the last spawn time of the red ball

                    pause = Pivot(0, 310)
                    resume = Pivot(0, 100)
                    restart = Pivot(0, 0)
                    exit = Pivot(0, -100)
                    man = Pivot(-425, -185)
                    shield = Pivot(-350, -185)
                    shield.hp = 3
                    max_shield = 3

                elif ((mouse_x)>=exit.box[0]) and ((mouse_x)<=(exit.box[0]+exit.box[1])) and ((mouse_y)>=exit.box[2]) and ((mouse_y)<=(exit.box[2]+exit.box[3])):
                    # exit
                    # print("EXIT")
                    print("GAME OVER")
                    print(f'FINAL SCORE: {score}')
                    glutLeaveMainLoop() 

        elif state == GLUT_UP:
            pass
                    
                    
    glutPostRedisplay()

def showScreen():
    global R, G, B, pause, pause_state, resume, restart, exit, show_bounds, man, bombs, new_bomb
    global zombies, throw_state, max_shield, spikes, shield, game_over_state, hp_change
    global color_up, cg, cb, cr, boss_spawn
    
    global yellow_ball, red_ball, green_ball, yellow_quantity

    # background
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(R/255, G/255, B/255, 0);	
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    iterate()
    

    #call the draw methods here

    glPointSize(2) 


    # Draw the yellow ball if it's on-screen
    if yellow_ball is not None:
        glColor3f(1.0, 1.0, 0.0)  # Yellow color
        draw_circle(yellow_ball.x, yellow_ball.y, yellow_ball.radius)
        glColor3f(63/255, 152/255, 69/255)
        yellow_ball.box = [yellow_ball.x-10, 20, yellow_ball.y-10, 20]
        if show_bounds == True:
            draw_quad(yellow_ball.box[0], yellow_ball.box[2], yellow_ball.box[0], yellow_ball.box[2]+yellow_ball.box[3], yellow_ball.box[0]+yellow_ball.box[1], yellow_ball.box[2]+yellow_ball.box[3], yellow_ball.box[0]+yellow_ball.box[1], yellow_ball.box[2])


    if red_ball is not None:
        glColor3f(1.0, 0.0, 0.0)  # Red color
        draw_circle(red_ball.x, red_ball.y, red_ball.radius)
        glColor3f(63/255, 152/255, 69/255)
        red_ball.box = [red_ball.x-10, 20, red_ball.y-10, 20]
        if show_bounds == True:
            draw_quad(red_ball.box[0], red_ball.box[2], red_ball.box[0], red_ball.box[2]+red_ball.box[3], red_ball.box[0]+red_ball.box[1], red_ball.box[2]+red_ball.box[3], red_ball.box[0]+red_ball.box[1], red_ball.box[2])


    if green_ball is not None:
        glColor3f(0.0, 1.0, 0.0)  # Green color
        draw_circle(green_ball.x, green_ball.y, green_ball.radius)
        glColor3f(63/255, 152/255, 69/255)
        green_ball.box = [green_ball.x-10, 20, green_ball.y-10, 20]
        if show_bounds == True:
            draw_quad(green_ball.box[0], green_ball.box[2], green_ball.box[0], green_ball.box[2]+green_ball.box[3], green_ball.box[0]+green_ball.box[1], green_ball.box[2]+green_ball.box[3], green_ball.box[0]+green_ball.box[1], green_ball.box[2])


    # Draw the yellow quantity text
    glColor3f(1.0, 1.0, 0.0)  # Yellow superpower
    draw_text(-600, 280, f"ZOMBIE ANNIHILATOR (press P): {yellow_quantity}")

    glColor3f(1.0, 1.0, 1.0)  # White score
    draw_text(-600, 320, f"SCORE: {score}")

    # LAND
    glColor3f(255/255, 255/255, 255/255)
    draw_line(-650, -220, 650, -220)
    

    # MAN
    glColor3f(255/255, 255/255, 255/255)
    # draw_quad(man.x-25, man.y-35, man.x-25, man.y+35, man.x+25, man.y+35, man.x+25, man.y-35)
    draw_player(man.x, man.y)
    glColor3f(63/255, 152/255, 69/255)
    man.box = [man.x-70, 100, man.y-35, 140]
    if show_bounds == True:
        draw_quad(man.box[0], man.box[2], man.box[0], man.box[2]+man.box[3], man.box[0]+man.box[1], man.box[2]+man.box[3], man.box[0]+man.box[1], man.box[2])

    # SHIELD
    if shield.hp != 0:
        glColor3f(255/255, 255/255, 255/255)
        draw_triangle(shield.x-25, shield.y-35, shield.x+25, shield.y+35, shield.x+25, shield.y-35)

        # SHIELD HP BAR
        draw_quad(shield.x-30, shield.y+40, shield.x-30, shield.y+50, shield.x+30, shield.y+50, shield.x+30, shield.y+40)
        glPointSize(10)
        glColor3f(63/255, 152/255, 69/255)
        # print(shield.x-25, shield.x+(25-((max_shield-shield.hp)*(50/shield.hp))))
        draw_line(shield.x-25, shield.y+45, shield.x+(25-((max_shield-shield.hp)*(50/max_shield))), shield.y+45)
        
        # SHIELD BOUNDING BOX
        glPointSize(2)
        glColor3f(63/255, 152/255, 69/255)
        shield.box = [shield.x, 25, shield.y-35, 70]
        if show_bounds == True:
            draw_quad(shield.box[0], shield.box[2], shield.box[0], shield.box[2]+shield.box[3], shield.box[0]+shield.box[1], shield.box[2]+shield.box[3], shield.box[0]+shield.box[1], shield.box[2])

    # SPIKES
    if spikes == True:
        glColor3f(255/255, 0/255, 0/255)
        draw_triangle(shield.x+25, shield.y+35, shield.x+50, shield.y+23.33, shield.x+25, shield.y+11.67)
        draw_triangle(shield.x+25, shield.y+11.67, shield.x+50, shield.y, shield.x+25, shield.y-11.67)
        draw_triangle(shield.x+25, shield.y-11.67, shield.x+50, shield.y-23.33, shield.x+25, shield.y-35)
        glColor3f(255/255, 255/255, 255/255)

    if boss_spawn == True:
        # SKULL AND BONES
        if cg == 255 and cb == 255 and cr == 255:
            color_up = False
        if cg == 0 and cb == 0  and cr == 0:
            color_up = True
        if color_up == False:
            cg, cb, cr = cg-1, cb-1, cr-1
        else:
            cg, cb, cr = cg+1, cb+1, cr+1

        glColor3f(cg/255, cb/255, cr/255)
        # SKULL
        draw_circle(-18, 165, 10)
        draw_circle(18, 165, 10)
        draw_triangle(-10, 130, 10, 130, 0, 145)
        draw_line(-25, 200, 25, 200)
        draw_line(-25, 200, -40, 170)
        draw_line(25, 200, 40, 170)
        draw_line(-40, 170, -40, 140)
        draw_line(40, 170, 40, 140)
        draw_line(-40, 140, -25, 140)
        draw_line(40, 140, 25, 140)
        draw_line(-25, 140, -25, 110)
        draw_line(25, 140, 25, 110)
        draw_line(-25, 110, -12.5, 125)
        draw_line(25, 110, 12.5, 125)
        draw_line(-12.5, 125, 0, 110)
        draw_line(12.5, 125, 0, 110)
        # BONES
        # Top-Left Bone
        draw_line(-35, 185, -63, 207)
        draw_line(-38, 175, -70, 195)
        draw_line(-63, 207, -70, 195)

        # Top-Right Bone
        draw_line(35, 185, 63, 207)
        draw_line(38, 175, 70, 195)
        draw_line(63, 207, 70, 195)

        # Bottom-Left Bone
        draw_line(-25, 125, -63, 93)
        draw_line(-28, 135, -70, 105)
        draw_line(-63, 93, -70, 105)

        # Bottom-Right Bone
        draw_line(25, 125, 63, 93)
        draw_line(28, 135, 70, 105)
        draw_line(63, 93, 70, 105)

    if hp_change == True:
        glColor3f(255/255, 255/255, 255/255)
        gap_hp = 40  # Horizontal adjustment for "HP"
        gap_up = 0   # Horizontal adjustment for "UP"

        # H
        draw_line(-200 + gap_hp, 160, -200 + gap_hp, 65)
        draw_line(-150 + gap_hp, 160, -150 + gap_hp, 65)
        draw_line(-200 + gap_hp, 110, -150 + gap_hp, 110)

        # P
        draw_line(-125 + gap_hp, 160, -125 + gap_hp, 65)
        draw_line(-125 + gap_hp, 160, -80 + gap_hp, 160)
        draw_line(-80 + gap_hp, 160, -80 + gap_hp, 110)
        draw_line(-80 + gap_hp, 110, -125 + gap_hp, 110)

        # U
        draw_line(20 + gap_up, 160, 20 + gap_up, 65)
        draw_line(20 + gap_up, 65, 65 + gap_up, 65)
        draw_line(65 + gap_up, 160, 65 + gap_up, 65)

        # P
        draw_line(90 + gap_up, 160, 90 + gap_up, 65)
        draw_line(90 + gap_up, 160, 135 + gap_up, 160)
        draw_line(135 + gap_up, 160, 135 + gap_up, 110)
        draw_line(135 + gap_up, 110, 90 + gap_up, 110)

    

    # ZOMBIES
    glColor3f(255/255, 255/255, 255/255)
    if zombies != []:
        for zombie in zombies:
            if zombie.special == 0:
                # regular zombies
                draw_normal_zombie(zombie.x, zombie.y-15)
                # draw_quad(zombie.x-25, zombie.y-35, zombie.x-25, zombie.y+35, zombie.x+25, zombie.y+35, zombie.x+25, zombie.y-35)
                zombie.box = [zombie.x-25, 50, zombie.y-35, 70]
                if show_bounds == True:
                    glColor3f(63/255, 152/255, 69/255)
                    draw_quad(zombie.box[0], zombie.box[2], zombie.box[0], zombie.box[2]+zombie.box[3], zombie.box[0]+zombie.box[1], zombie.box[2]+zombie.box[3], zombie.box[0]+zombie.box[1], zombie.box[2])
            elif zombie.special == 1:
                # fast zombies
                draw_fast_zombie(zombie.x, zombie.y-25)
                # draw_quad(zombie.x-30, zombie.y-35, zombie.x-30, zombie.y+15, zombie.x+30, zombie.y+15, zombie.x+30, zombie.y-35)
                zombie.box = [zombie.x-30, 60, zombie.y-35, 50]
                if show_bounds == True:
                    glColor3f(63/255, 152/255, 69/255)
                    draw_quad(zombie.box[0], zombie.box[2], zombie.box[0], zombie.box[2]+zombie.box[3], zombie.box[0]+zombie.box[1], zombie.box[2]+zombie.box[3], zombie.box[0]+zombie.box[1], zombie.box[2])
            elif zombie.special == 2:
                # tanky zombies
                draw_slow_zombie(zombie.x, zombie.y+10)
                # draw_quad(zombie.x-40, zombie.y-35, zombie.x-40, zombie.y+65, zombie.x+40, zombie.y+65, zombie.x+40, zombie.y-35)
                zombie.box = [zombie.x-40, 80, zombie.y-35, 100]
                if show_bounds == True:
                    glColor3f(63/255, 152/255, 69/255)
                    draw_quad(zombie.box[0], zombie.box[2], zombie.box[0], zombie.box[2]+zombie.box[3], zombie.box[0]+zombie.box[1], zombie.box[2]+zombie.box[3], zombie.box[0]+zombie.box[1], zombie.box[2])
            elif zombie.special == 3:
                # boss zombies
                draw_zombie_boss(zombie.x, zombie.y+20)
                # draw_quad(zombie.x-60, zombie.y-35, zombie.x-60, zombie.y+115, zombie.x+60, zombie.y+115, zombie.x+60, zombie.y-35)
                zombie.box = [zombie.x-60, 120, zombie.y-35, 150]
                if show_bounds == True:
                    glColor3f(63/255, 152/255, 69/255)
                    draw_quad(zombie.box[0], zombie.box[2], zombie.box[0], zombie.box[2]+zombie.box[3], zombie.box[0]+zombie.box[1], zombie.box[2]+zombie.box[3], zombie.box[0]+zombie.box[1], zombie.box[2])
            glColor3f(255/255, 255/255, 255/255)

    # BOMB CREATION
    glColor3f(255/255, 255/255, 255/255)
    if new_bomb != None:
        draw_ninja_star(new_bomb.x, new_bomb.y, new_bomb.radius)
        if throw_state == True:
            draw_line(man.x-10, man.y+15, new_bomb.x, new_bomb.y)
            draw_line(man.x-10, man.y, new_bomb.x, new_bomb.y)

    # BOMBS
    if bombs != []:
        for bomb in bombs:
            draw_ninja_star(bomb.x, bomb.y, bomb.radius)
            glColor3f(63/255, 152/255, 69/255)
            bomb.box = [bomb.x-bomb.radius, 2*bomb.radius, bomb.y-bomb.radius, 2*bomb.radius]
            if show_bounds == True:
                draw_quad(bomb.box[0], bomb.box[2], bomb.box[0], bomb.box[2]+bomb.box[3], bomb.box[0]+bomb.box[1], bomb.box[2]+bomb.box[3], bomb.box[0]+bomb.box[1], bomb.box[2])
            glColor3f(255/255, 255/255, 255/255)


    
    # PAUSE BUTTON
    if pause_state == False and game_over_state == False:
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
    if pause_state == True or game_over_state == True:
        if pause_state == True:
            # RESUME BUTTON
            glColor3f(255/255, 255/255, 255/255)
            draw_quad(resume.x-200, resume.y-50, resume.x-200, resume.y+50, resume.x+200, resume.y+50, resume.x+200, resume.y-50)
            draw_triangle(resume.x-30, resume.y-30, resume.x-30, resume.y+30, resume.x+30, resume.y)
            glColor3f(63/255, 152/255, 69/255)
            if show_bounds == True:
                draw_quad(resume.box[0], resume.box[2], resume.box[0], resume.box[2]+resume.box[3], resume.box[0]+resume.box[1], resume.box[2]+resume.box[3], resume.box[0]+resume.box[1], resume.box[2])

        if game_over_state == True:
            # GAME OVER
            # Define gaps for positioning(wrote the letters myself but 
            # positioning was done using CHATGPT)
            gap_game = -20  # Horizontal adjustment for "GAME"
            gap_over = -20    # Extra horizontal space between "GAME" and "OVER"

            # G
            glColor3f(255/255, 255/255, 255/255)
            draw_line(-260 + gap_game, 160, -215 + gap_game, 160)
            draw_line(-260 + gap_game, 160, -260 + gap_game, 65)
            draw_line(-260 + gap_game, 65, -215 + gap_game, 65)
            draw_line(-215 + gap_game, 65, -215 + gap_game, 110)
            draw_line(-215 + gap_game, 110, -235 + gap_game, 110)
            # A
            draw_line(-180 + gap_game, 160, -135 + gap_game, 160)
            draw_line(-135 + gap_game, 160, -135 + gap_game, 65)
            draw_line(-180 + gap_game, 160, -180 + gap_game, 65)
            draw_line(-180 + gap_game, 110, -135 + gap_game, 110)
            # M
            draw_line(-110 + gap_game, 160, -110 + gap_game, 65)
            draw_line(-65 + gap_game, 160, -65 + gap_game, 65)
            draw_line(-110 + gap_game, 160, -87.5 + gap_game, 110)
            draw_line(-87.5 + gap_game, 110, -65 + gap_game, 160)
            # E
            draw_line(-40 + gap_game, 160, -40 + gap_game, 65)
            draw_line(-40 + gap_game, 160, 5 + gap_game, 160)
            draw_line(-40 + gap_game, 110, 5 + gap_game, 110)
            draw_line(-40 + gap_game, 65, 5 + gap_game, 65)

            # O
            draw_quad(70 + gap_over, 160, 70 + gap_over, 65, 115 + gap_over, 65, 115 + gap_over, 160)
            # V
            draw_line(140 + gap_over, 160, 165 + gap_over, 65)
            draw_line(165 + gap_over, 65, 190 + gap_over, 160)
            # E
            draw_line(215 + gap_over, 160, 215 + gap_over, 65)
            draw_line(215 + gap_over, 160, 260 + gap_over, 160)
            draw_line(215 + gap_over, 110, 260 + gap_over, 110)
            draw_line(215 + gap_over, 65, 260 + gap_over, 65)
            # R
            draw_line(285 + gap_over, 160, 285 + gap_over, 65)
            draw_line(285 + gap_over, 160, 330 + gap_over, 160)
            draw_line(285 + gap_over, 110, 330 + gap_over, 110)
            draw_line(330 + gap_over, 160, 330 + gap_over, 110)
            draw_line(285 + gap_over, 110, 330 + gap_over, 65)


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
glutInitWindowPosition(110, 28)
wind = glutCreateWindow(b"423 PROJECT ZOMBBOMBS") #window name
glutDisplayFunc(showScreen)

glutIdleFunc(animate)

glutKeyboardFunc(KeyboardListen)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)

glutPassiveMotionFunc(mouseMotionListener)

glutMainLoop()


