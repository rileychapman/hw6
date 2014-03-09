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
       
        self.guy = Guy((255,255,255),20,100,200,300,self.size,self)
        self.coins = []
        self.score = 0
        for y_coins in range(0,self.size[1],100):
            coin = Coin(self,20,y_coins)
            self.coins.append(coin)

        block_test = Block(self,0,0)
        self.block_test = block_test
        
        self.border = []
        for x_border in range(0,self.size[1],block_test.height):
            block = Block(self,0,x_border)
            block1 = Block(self,self.size[0] - block_test.width,x_border)
            self.border.append(block)
            self.border.append(block1)

        for y_border in range(0,self.size[0],block_test.width):
            block = Block(self,y_border,0)
            block2 = Block(self,y_border,self.size[1]-block_test.height)
            self.border.append(block)
            self.border.append(block2)



        self.blocks = []
        for x_blocks in range (0,self.size[0]-100,block_test.width):
            block1 = Block(self,x_blocks,200)
            self.blocks.append(block1)

        self.allsprites = pygame.sprite.Group(self.guy)
        self.coinsprites = pygame.sprite.Group()
        self.blocksprites = pygame.sprite.Group()
        for coin in self.coins:
            pygame.sprite.Group.add(self.coinsprites,coin)
        for block in self.blocks:
            pygame.sprite.Group.add(self.blocksprites,block)
        for block in self.border:
            pygame.sprite.Group.add(self.blocksprites,block)

        #initalizing block collision stuff
        self.Left_Collide = False
        self.Right_Collide = False
        self.Bottom_Collide = False
        self.Top_Collide = False
        #record the blocks that we have colided with so that we know where to move the guy to 
        self.Lcol_block = []
        self.Rcol_block = []
        self.Bcol_block = []
        self.Tcol_block = []


    def update(self):
        for coin in self.coins:
            if coin.disappear:
                self.coinsprites.remove(coin)
                self.coins.remove(coin)
                self.score +=1

        blocks_hit_list = pygame.sprite.spritecollide(self.guy, self.blocksprites, False)
        #spritecollide(sprite, group, dokill, collided = None)

        self.Left_Collide = False
        self.Right_Collide = False
        self.Bottom_Collide = False
        self.Top_Collide = False

        self.Lcol_block = []
        self.Rcol_block = []
        self.Bcol_block = []
        self.Tcol_block = []
   


        if len(blocks_hit_list) > 0:
            for hitblock in blocks_hit_list:
                x_distance = self.guy.rect.center[0] - hitblock.rect.center[0]
                y_distance = self.guy.rect.center[1] - hitblock.rect.center[1]
                if abs(x_distance) < abs(y_distance): # we collided on top or bottom 
                    if y_distance <= 0:#self.guy.rect.height/2 + self.block_test.height/2: #bottom collision
                        #self.Bottom_Collide = True

                        if abs(self.guy.rect.topleft[0] - hitblock.rect.topright[0]) < 3 or abs(self.guy.rect.topright[0] - hitblock.rect.topleft[0]) < 3 and not self.Bottom_Collide:
                            self.Bottom_Collide = False
                        else:
                            self.Bottom_Collide = True
                        self.Bcol_block = [hitblock]
                    else: #top collision
                        self.Top_Collide = True
                        self.Tcol_block = [hitblock]
                else: #we collided on left or right 
                    if x_distance >= 0: #left collision
                        self.Left_Collide = True
                        self.Lcol_block = [hitblock]
                    else: #right collision
                        self.Right_Collide = True
                        self.Rcol_block = [hitblock]



        else:
            self.Left_Collide = False
            self.Right_Collide = False
            self.Bottom_Collide = False
            self.Top_Collide = False
        #self.Right_Collide =  self.guy.rect.topright[0] >= blocks_hit_list[0].rect.left[0]
        #self.Left_Collide =  self.guy.rect.topleft[0] >= blocks_hit_list[0].rect.topright[0]
        

        self.allsprites.update()
        self.coinsprites.update()
        self.blocksprites.update()


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
    def __init__(self,color,height,width,x,y,window_size,model):      
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
        self.oposx = 0
        self.oposy = 0
        self.ooposx = 0
        self.ooposy = 0
        #self.grav_start = 0
        self.rect.topleft = (x,y)
        self.model = model
        self.jumpup = False

    def update(self):
        """ updates the position of the guy"""

        if self.jump and self.model.Bottom_Collide and not self.model.Left_Collide and not self.model.Right_Collide:
            self.vy = -5
            self.jump = False
        elif self.jump and self.model.Left_Collide:
            self.vy = -5
            self.vx_jump = 2
            self.jump = False
            print 'wall jump'
        elif self.jump and self.model.Right_Collide:
            self.vy = -5
            self.vx_jump = -2
            self.jump = False
            print 'wall jump'
        else:
            self.vy += .1
            self.vx_jump = 0

        self.vx_inter = self.vx
        self.vx_inter += self.forcex*.03

        #if self.stopforce != 0 and self.vx <0 and self.forcex ==0:\
        if self.forcex == 0 and self.vx< 0:
            self.vx_inter +=.05#self.stopforce*.05
            if self.vx_inter > -.06:
                self.vx_inter = 0
        #elif self.stopforce != 0 and self.vx> 0 and self.forcex ==0:
        elif self.forcex ==0  and self.vx>.05:
            self.vx_inter -=   .05#self.stopforce*.05
            if self.vx_inter <.06:
                self.vx_inter = 0
        else:
            self.stopforce = 0

        speed_cap = 2

        if self.vx_inter < -speed_cap:
            self.vx_inter = -speed_cap
        elif self.vx_inter > speed_cap:
            self.vx_inter = speed_cap

        else:
            self.vx_inter = self.vx_inter 


        self.vx = self.vx_inter+ self.vx_jump

#code  that keeps the guy ouside of the blocks


        if model.Right_Collide:
            if self.vx>0:
                self.x = self.model.Rcol_block[0].rect.topleft[0]-self.width
            else:
                self.x += self.vx
        elif model.Left_Collide:
            if self.vx <0:
                self.x = self.model.Lcol_block[0].rect.topright[0]
            else:
                self.x += self.vx
        else:
            self.x += self.vx

        #making code to determine if the sprite is in the window or not
        #UP = model.Top_Collide #self.y <=0
        #DOWN = model.Bottom_Collide# self.y>= self.window_size[1]-self.height

        if model.Top_Collide:
            if self.vy < 0:
                self.y = self.y

            else: 
                self.y +=self.vy
        elif model.Bottom_Collide:
            if self.vy > 0.0:
                
                self.y = self.model.Bcol_block[0].rect.topleft[1]-self.height+1
                self.vy = 0

                
            else: 
                self.y += self.vy
        else:
            self.y += self.vy


        self.ooposx = self.oposx
        self.ooposy = self.oposy
        self.oposx = self.rect.topleft[0]
        self.oposy = self.rect.topleft[1]
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
        model.coinsprites.draw(screen)
        model.blocksprites.draw(screen)

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
                self.model.guy.jumpup = False




        if event.type == KEYUP:
            if event.key == pygame.K_RIGHT:# and model.guy.vx > 0:
                model.guy.stopforce = -2
                model.guy.forcex = 0

            if event.key == pygame.K_LEFT: #and model.guy.vx < 0:
                model.guy.stopforce = 2
                model.guy.forcex = 0
            if event.key == pygame.K_RIGHT:
                model.guy.jumpup = True


if __name__ == '__main__':
    pygame.init()
    size_scale = 4
    size_scalex = 6
    size_scaley = 4
    size = (size_scalex*30*size_scale,size_scaley*30*size_scale)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()


    model = JumpGuyModel(size)
    view = View(model,screen)
    controller = keyboard_controller(model)

    running = True

    while running:
        clock.tick(120) #makes the game run at a constant rate 

        for event in pygame.event.get():
            if event.type == KEYDOWN or KEYUP:
                controller.handle_keyboard_event(event)
            if event.type == QUIT:
                running = False


        model.update()
        view.draw()
        time.sleep(.001)

    pygame.quit()