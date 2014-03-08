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
        self.score = 0
        for y_coins in range(0,self.size[1],100):
            coin = Coin(self,20,y_coins)
            self.coins.append(coin)
        block_test = Block(self,0,0)

        self.border = []
        for x_border in range(0,self.size[1],block_test.height):
            block = Block(self,0,x_border)
            self.border.append(block)


        self.blocks = []
        for x_blocks in range (0,self.size[0]-50,block_test.width):
            block = Block(self,x_blocks,400)
            self.blocks.append(block)


        self.allsprites = pygame.sprite.Group((self.guy))
        for coin in self.coins:
            pygame.sprite.Group.add(self.allsprites,coin)
        for block in self.blocks:
            pygame.sprite.Group.add(self.allsprites,block)
        for block in self.border:
            pygame.sprite.Group.add(self.allsprites,block)

        #initalizing block collision stuff
        self.Left_Collide = False
        self.Right_Collide = False
        self.Bottom_Collide = False
        self.Top_Collide = False


    def update(self):
        for coin in self.coins:
            if coin.disappear:
                self.allsprites.remove(coin)
                self.coins.remove(coin)
                self.score +=1

        blocks_hit_list = pygame.sprite.spritecollide(self.guy, self.blocks+self.border, False)
        if len(blocks_hit_list) > 0:
            for hitblock in blocks_hit_list:
                if not self.Right_Collide:
                    self.Right_Collide =  self.guy.rect.topright[0] >= hitblock.rect.topleft[0] 
                if not self.Left_Collide:          
                    self.Left_Collide =  self.guy.rect.topleft[0] >= hitblock.rect.topright[0]
                if not self.Top_Collide:    
                    self.Top_Collide =  self.guy.rect.bottomleft[1] >= hitblock.rect.topleft[1]
                if not self.Bottom_Collide:
                    self.Bottom_Collide =  self.guy.rect.topleft[1] >= hitblock.rect.bottomleft[1]

                print self.Right_Collide, self.Left_Collide, self.Top_Collide
        else:
            self.Left_Collide = False
            self.Right_Collide = False
            self.Bottom_Collide = False
            self.Top_Collide = False
        #self.Right_Collide =  self.guy.rect.topright[0] >= blocks_hit_list[0].rect.left[0]
        #self.Left_Collide =  self.guy.rect.topleft[0] >= blocks_hit_list[0].rect.topright[0]
        

        self.allsprites.update()


class Block(pygame.sprite.Sprite):
    """Makes the blocks that the guy jumps around on"""
    def __init__(self,model,x,y):
        self.model = model
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image, self.rect = load_image('grass.png', -1) #load an image
        self.rect.topleft = (self.x,self.y)
        self.exist = True
        self.width = self.rect.width
        self.height = self.rect.height
    def update(self):
        self.exist = True



        
class Coin(pygame.sprite.Sprite):
    def __init__(self,model,x,y):
        self.model = model
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image('coin.png', -1) #load an image
        self.x = x 
        self.y = y
        self.width = self.rect.width
        self.height = self.rect.height
        self.disappear = False 
        self.rect.topleft = (self.x,self.y)
    def update(self):
        #if abs(self.model.guy.x -self.x) < (self.rect.width - self.model.guy.width)/2 and abs(self.model.guy.y -self.y) < (self.rect.height- self.model.guy.height)/2:
        x_colide = abs(self.model.guy.x -self.x) < self.width + self.model.guy.width/2
        y_colide = abs(self.model.guy.y -self.y) <  (self.height + self.model.guy.height)/2 
        if x_colide and y_colide: #abs(self.model.guy.y -self.y) < 10:
            
            self.disappear = True
            print self.disappear




                


class Guy(pygame.sprite.Sprite):
    def __init__(self,color,height,width,x,y,window_size):      
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image('finn1.png', -1) #load an image


        self.color = color
        self.height = self.rect.height
        self.width = self.rect.width
        self.x = x#self.rect.topleft[0]
        self.y = y#Sself.rect.topleft[1]
        self.forcex = 0.0
        self.forcey = 0.0
        self.stopforce = 0.0
        self.vx = 0
        self.vy = 0
        self.jump = False
        self.window_size = window_size
        self.vx_inter = 0.0
        self.vx_jump = 0.0
        #self.grav_start = 0

    def update(self):
        """ updates the position of the guy"""

        if self.jump and self.y == self.window_size[1]-self.height :
            self.vy = -5
        elif self.jump and self.x == 0:
            self.vy = -3
            self.vx_jump = 3
        elif self.jump and self.x+self.width == self.window_size[0]:
            self.vy = -3
            self.vx_jump = -3
        else:
            self.vy += .1
            self.vx_jump = 0


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

        self.vx = self.vx_inter #+ self.vx_jump

#code  that keeps the guy ouside of the blocks

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

        if pygame.font:
            font = pygame.font.Font(None, 36)

            text = font.render("Jump Guy!", 1, (255, 255, 10))
            textpos = text.get_rect(centerx=model.size[0]/2)
            screen.blit(text, textpos)
            score_str = str(model.score)
            score_text = 'Score:'+score_str
            print_score = font.render(score_text, 1, (255, 255, 10))
            score_pos = print_score.get_rect(topright = (model.size[0],50))
            screen.blit(print_score,score_pos)


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