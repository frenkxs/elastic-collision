#===============================================================================
# Classical mechanics simulation of movement and collisions of particles (balls).
# It calculates movement and collisions of particles given their mass, speed,  
# elasticity, gas(air) density, and gravity. Users can also grab the particles 
# with their mouse and fling them around the canvas.
#
# Based on: http://www.petercollingridge.co.uk/pygame-physics-simulation
# 
# Autor: Premysl Velek, premysl.velek@gmail.com 
#===============================================================================


import pygame
import random
import math

# constant variables
HEIGHT = 400
WIDTH = 600
BACKGROUND_COLOUR = (255, 255, 255)
NUMBER_OF_PARTICLES = 3
GRAVITY = (- 0.5 * math.pi, 0.000)  

# elasticity of the particles: 1 = absolutely elastic, 0 = absolutely inelastic (not implemented!!!)
ELASTICITY = 0.98   

# the higher the number, the higher the density
AIR_DENSITY = 0.08    


# adds two vectors. It takes two vectors and their angles and
# returns a single vector and angle
def add_vector((angle_1, speed_1), (angle_2, speed_2)):
    x = math.sin(angle_1) * speed_1 + math.sin(angle_2) * speed_2
    y = math.cos(angle_1) * speed_1 + math.cos(angle_2) * speed_2

    new_speed = math.hypot(x, y)
    new_angle = 0.5 * math.pi - math.atan2(y, x)

    return (new_angle, new_speed)


# calculates speed and angle of a particle after collision. More info: 
# http://www.phy.ntnu.edu.tw/ntnujava/index.php?topic=4.msg9#msg9
# ELASTIC COLLISIONS ONLY!!! The equations won't work ror elasticity approaching 0!!!  
def collide(item_1, item_2):
    
    dist_x = (item_1.pos_x - item_2.pos_x)
    dist_y = (item_1.pos_y - item_2.pos_y)
    
    axe = math.atan2(dist_y, dist_x * -1)
    
    angle_to_pass = axe - math.pi * 0.5
         
    speed_to_collide_1 = math.cos(axe - item_1.angle) * item_1.speed
    speed_to_pass_1 = math.sin(axe - item_1.angle) * item_1.speed
    
    speed_to_collide_2 = math.cos(axe - item_2.angle) * item_2.speed
    speed_to_pass_2 = math.sin(axe - item_2.angle) * item_2.speed
       
    speed_after_1 = (speed_to_collide_1 * (item_1.mass - item_2.mass) + 2 * item_2.mass * speed_to_collide_2) / (item_1.mass + item_2.mass)
    speed_after_2 = (speed_to_collide_2 * (item_2.mass - item_1.mass) + 2 * item_1.mass * speed_to_collide_1) / (item_1.mass + item_2.mass)
        
    (item_1.angle, item_1.speed) = add_vector((axe, speed_after_1), (angle_to_pass, speed_to_pass_1))
    (item_2.angle, item_2.speed) = add_vector((axe, speed_after_2), (angle_to_pass, speed_to_pass_2))

    # prevents particles from overlapping
    overlap = 0.5 * (item_1.radius + item_2.radius - math.hypot(dist_x, dist_y) + 1)
    item_1.pos_x -= math.cos(axe) * overlap
    item_2.pos_x += math.cos(axe) * overlap
    item_1.pos_y += math.sin(axe) * overlap
    item_2.pos_y -= math.sin(axe) * overlap


# checks if mouse has selected any particle
def is_selected(group, mouse):
    for item in group:
        if math.hypot(item.pos_x - mouse[0], item.pos_y - mouse[1]) <= item.radius:
            return item
    return None 



#========================================================
# particle class: stores info about particle objects:
# position, radius, colour, mass, speed, and angle of movement
#========================================================
class Particle():

    def __init__(self, colour, radius, (pos_x, pos_y), mass = 1):
        self.colour = colour
        self.radius = radius
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.speed = 0
        self.angle = 0
        self.mass = mass
        
        # calculates the air drag given the air density and the particle size and mass. 
        # APPROXIMATION!!! The exact formula for calculating the drag force: 
        # http://en.wikipedia.org/wiki/Drag_equation
        self.drag = (self.mass / (self.mass + AIR_DENSITY)) ** self.radius
        
    # detects collisions between particles
    def is_colliding(self, other_particle):
        dist_x = self.pos_x - other_particle.pos_x
        dist_y = self.pos_y - other_particle.pos_y

        if math.hypot(dist_x, dist_y) < self.radius + other_particle.radius:
            return True
        else:
            return False

    # movement
    def move(self):
        (self.angle, self.speed) = add_vector((self.angle, self.speed), GRAVITY)
        
        self.pos_x += math.cos(self.angle) * self.speed
        self.pos_y -= math.sin(self.angle) * self.speed
        
        self.speed *= self.drag

    # bouncing off the canvas
    def bounce(self):

        # horizontal bounce - right
        if self.pos_x > WIDTH - self.radius:
            self.pos_x = WIDTH - self.radius
            self.angle = math.pi - self.angle
            self.speed *= ELASTICITY

        # horizontal bounce - left
        elif self.pos_x < self.radius:
            self.pos_x = self.radius
            self.angle = math.pi - self.angle 
            self.speed *= ELASTICITY

        # vertical bounce - bottom
        if self.pos_y > HEIGHT - self.radius:
            self.pos_y = HEIGHT - self.radius
            self.angle = - self.angle
            self.speed *= ELASTICITY

        # vertical bounce - top
        elif self.pos_y < self.radius:
            self.pos_y = self.radius
            self.angle = - self.angle
            self.speed *= ELASTICITY

    # draws particles on canvas
    def draw(self):
        pygame.draw.circle(my_canvas, self.colour, (int(self.pos_x), int(self.pos_y)), self.radius)


# creates pygame canvas
my_canvas = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Classical mechanics 101")


# creates set of particles - a set of Particle class objects
particles_group = ([])

for item in range(NUMBER_OF_PARTICLES):
    radius = random.randint(19, 30)
    pos_x = random.randint(radius, WIDTH - radius)
    pos_y = random.randint(radius, HEIGHT - radius)
        
    density = random.randint(1, 23)
    mass = density * radius ** 2 
    
    # the lower the particle's mass is, the lighter the colour is 
    colour = (230 - density * random.randint(1, 10), 230 - density * random.randint(1, 10), 230 - density * random.randint(1, 10))   
    
    a_particle = (Particle(colour, radius, (pos_x, pos_y), mass))
    
    a_particle.speed = random.uniform(0, 0.6)
    a_particle.angle = random.uniform(-math.pi, math.pi)   
    
    particles_group.append(a_particle)
    
    
# displays the canvas, implements the mouse interactions and get things rolling 
is_running = True
selected_particle = None

while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        
        # selects particle with mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            selected_particle = is_selected(particles_group, mouse_pos)
        
        # releases particle once the mouse button is released        
        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_particle:
                selected_particle.colour = (random.randint(10, 200), random.randint(10, 200), random.randint(10, 200))
            selected_particle = None    
        
        # drags particle with mouse and fling it around the canvas
        if selected_particle:
            mouse = pygame.mouse.get_pos()
            
            dist_x = selected_particle.pos_x - mouse[0] 
            dist_y = selected_particle.pos_y - mouse[1]
            
            selected_particle.angle = math.atan2(dist_y, dist_x * -1) 
            selected_particle.speed = math.hypot(-dist_y, dist_x) * 0.04
            
            selected_particle.colour = (255, 0, 0)
            (selected_particle.pos_x, selected_particle.pos_y) = pygame.mouse.get_pos()
                       
    my_canvas.fill(BACKGROUND_COLOUR)

    # puts it all together and rolls it out
    for i, item_1 in enumerate(particles_group):
        if item_1 != selected_particle:
            item_1.move()
            item_1.bounce()
        for item_2 in particles_group[i + 1:]:
            if item_1.is_colliding(item_2):
                collide(item_1, item_2)
        item_1.draw()

    pygame.display.flip()

