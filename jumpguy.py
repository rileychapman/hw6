"""
Created on Thu Feb 27 19:34:24 2014

@author: Riley Chapman and Paul Titchner 
"""

import pygame
from pygame.locals import *
import random
import math
import time
import sys,os

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        try:
            image = pygame.image.load(name)
        except pygame.error, message:
            print 'Cannot load image:', name
            raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


class JumpGuyModel:
    """This class encodes the game state"""
    def __init__(self,size):
        self.size = size
        print 'creating an object'
       
        self.guy = Guy((255,255,255),20,100,200,450,self.size)
        self.coins = []

        for y in range(0,self.size[1],100):
            coin = Coin(self,20,y)
            self.coins.append(coin)



        self.allsprites = pygame.sprite.Group((self.guy))
        for coin in self.coins:
                pygame.sprite.Group.add(self.allsprites,coin)

    def update(self):
        for coin in self.coins:
            if coin.disappear:
                self.allsprites.remove(coin)
                print 'a'
        self.allsprites.update()



            


        
class Coin(pygame.sprite.Sprite):
    def __init__(self,model,x,y):
        self.model = model
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image('finn1.png', -1) #load an image
        self.x = x 
        self.y = y
        self.width = self.rect.width
        self.height = self.rect.height
        self.disappear = False 
        self.rect.topleft = (self.x,self.y)
    def update(self):
        #if abs(self.model.guy.x -self.x) < (self.rect.width - self.model.guy.width)/2 and abs(self.model.guy.y -self.y) < (self.rect.height- self.model.guy.height)/2:
        
        if abs(self.model.guy.y -self.y) < 10:
            
            self.disappear = True
            print self.disappear




                


class Guy(pygame.sprite.Sprite):
    def __init__(self,color,height,width,x,y,window_size):      
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image('finn1.png', -1) #load an image


        self.color = color
        self.height = self.rect.height
        self.width = self.rect.width
        self.x = self.rect.topleft[0]
        self.y = self.rect.topleft[1]
        self.forcex = 0.0
        self.forcey = 0.0
        self.stopforce = 0.0
        self.vx = 0
        self.vy = 0
        self.jump = False
        self.window_size = window_size
        self.vx_inter = 0.0
        #self.grav_start = 0

    def update(self):
        """ updates the position of the guy"""

        if self.jump and self.y == self.window_size[1]-self.height :
            self.vy = -5
        elif self.jump and self.x == 0:
            self.vy = -3
        elif self.jump and self.x+self.width == self.window_size[0]:
            self.vy = -3
        else:
            self.vy += .1

        self.vx_inter += self.forcex*.2

        if self.stopforce > 0 and self.vx <0:
            self.vx_inter +=self.stopforce*.01
        elif self.stopforce <0 and self.vx > 0:
            self.vx_inter +=self.stopforce*.01



        speed_cap = 2

        if self.vx_inter < -speed_cap:
            self.vx_inter = -speed_cap
        elif self.vx_inter > speed_cap:
            self.vx_inter = speed_cap

        else:
            self.vx_inter = self.vx_inter

        self.vx = self.vx_inter

        #making code to keep the sprite in the left and right of the window

        LEFT = self.x <= 0
        RIGHT = self.x >= self.window_size[0]-self.width
        IN_horoz = not LEFT and not RIGHT

        if LEFT:
            if self.vx<0:
                self.x = 0
            else:
                self.x += self.vx
        elif RIGHT:
            if self.vx >0:
                self.x = self.window_size[0]-self.width
            else:
                self.x += self.vx
        elif IN_horoz:
            self.x += self.vx

        #making code to determine if the sprite is in the window or not
        UP = self.y <=0
        DOWN = self.y>= self.window_size[1]-self.height
        IN = not UP and not DOWN

        if IN:
            self.y += self.vy
        elif DOWN:
            if self.vy > 0:
                self.y = self.window_size[1]-self.height
            else: 
                self.y +=self.vy
        elif UP:
            if self.vy<0:
                self.y = 0
            if self.vy>0:
                self.y += self.vy



        self.rect.topleft = (self.x,self.y)


class View:
    """A view of brickbreaker rendered in a pygame window"""
    def __init__(self,model,screen):
        self.model = model
        self.screen = screen

    def draw(self):
        self.screen.fill(pygame.Color(0,0,0))
        #pygame.draw.rect(self.screen , pygame.Color(self.model.guy.color[0],self.model.guy.color[1],self.model.guy.color[2]), pygame.Rect(self.model.guy.x,self.model.guy.y,self.model.guy.width,self.model.guy.height))
        model.allsprites.draw(screen)

        pygame.display.update()

class keyboard_controller:
    def __init__(self,model):
        self.model = model

    def handle_keyboard_event(self,event):

        self.model.guy.jump = False
        if event.type == KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.model.guy.forcex = -1
            elif event.key == pygame.K_RIGHT:
                self.model.guy.forcex = 1
            #else:
                #self.model.guy.forcex = 0

            if event.key == pygame.K_UP:
                self.model.guy.jump = True

        if event.type == KEYUP:
            if event.key == pygame.K_RIGHT:# and model.guy.vx > 0:
                model.guy.stopforce = -2
                model.guy.forcex = 0

            if event.key == pygame.K_LEFT: #and model.guy.vx < 0:
                model.guy.stopforce = 2
                model.guy.forcex = 0


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