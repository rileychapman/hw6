"""
Created on Thu Feb 27 19:34:24 2014

@author: pruvolo
"""

import pygame
from pygame.locals import *
import random
import math
import time

class JumpGuyModel:
    """This class encodes the game state"""
    def __init__(self,size):
        self.size = size
        print 'creating an object'
       
        self.guy = Guy((255,255,255),20,100,200,450,self.size)
    def update(self):
        self.guy.update()


class Guy2(pygame.sprite.Sprite):
   def __init__(self,model):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('ball.bmp', -1) #load an image
        self.jump = False #not jumping to start
        self.pos = (0,0) #start positions
        self.height = self.pos[1] + model.window_size[1] #calculates height
        self.forces = (0.0,0.0)
        self.v = (0.0,0.0)

    def update(self):

                


class Guy():
    def __init__(self,color,height,width,x,y,window_size):
        self.color = color
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.forcex = 0.0
        self.forcey = 0.0
        self.vx = 0
        self.vy = 0
        self.jump = False
        self.window_size = window_size
        #self.grav_start = 0

    def update(self):
        """ updates the position of the guy"""

        if self.jump:
            self.vy = 50
            #grav_start = pygame.time.get_ticks()
        else:
            #grav_now = pygame.time.get_ticks()
            #time_air = grav_now-grav_start
            self.vy += .1


        self.vx += self.forcex*.001
        if self.x == -1:
            self.x = 0
        elif self.x == window_size[0]+1:
            self.x == window_size[0]


            self.x += self.vx


        if self.y < window_size[1]:
            self.y += self.vy
        else:
            self.y = window_size[1]




class View:
    """A view of brickbreaker rendered in a pygame window"""
    def __init__(self,model,screen):
        self.model = model
        self.screen = screen

    def draw(self):
        self.screen.fill(pygame.Color(0,0,0))
        pygame.draw.rect(self.screen , pygame.Color(self.model.guy.color[0],self.model.guy.color[1],self.model.guy.color[2]), pygame.Rect(self.model.guy.x,self.model.guy.y,self.model.guy.width,self.model.guy.height))

        pygame.display.update()

class keyboard_controller:
    def __init__(self,model):
        self.model = model

    def handle_keyboard_event(self,event):
  

        #keys = pygame.key.get_pressed()
        if event.type == KEYDOWN:

            if event.key == pygame.K_LEFT:
                self.model.guy.forcex = -1
            if event.key == pygame.K_RIGHT:
                self.model.guy.forcx = 1
            else:
                self.model.guy.forcx = 0

            if event.key == pygame.K_UP:
                self.model.guy.jump = True

        if event.type == KEYUP:
            if event.key == pygame.K_RIGHT and model.guy.vx < 0:
                model.guy.forcex = 5
            if event.key == pygame.K_LEFT and model.guy.vx > 0:
                model.guy.forcex = -5


if __name__ == '__main__':
    pygame.init()

    size = (640,600)
    screen = pygame.display.set_mode(size)

    model = JumpGuyModel(size)
    view = View(model,screen)
    controller = keyboard_controller(model)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN or KEYUP:
                controller.handle_keyboard_event(event)
            if event.type == QUIT:
                running = False


        model.update()
        view.draw()
        time.sleep(.001)


    pygame.quit()