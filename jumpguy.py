"""
Created on Thu Feb 27 19:34:24 2014

@author: Riley Chapman and Paul Titchener 
"""

import pygame
from pygame.locals import *
import random
import math
import time
import sys,os
import pyganim

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

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    try:
        sound = pygame.mixer.Sound(name)
    except pygame.error, message:
        print 'Cannot load sound:', wav
        raise SystemExit, message
    return sound



class JumpGuyModel:
    """This class encodes the game state. Sprites are initialized and interactions between sprites are detected. The individaul sprite movements are within the sprite classes
    Sets up the stage and coin positions"""
    def __init__(self,size):
        """Initialize Jump Guy Model"""

        self.size = size
        print 'creating an object'
       
        self.guy = Guy((255,255,255),20,100,200,300,self.size,self)
        self.coins = []
        self.score = 0
        for y_coins in range(400,500,100):
            coin = Coin(self,40,y_coins)
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
        for x_blocks in range (0,self.size[0]-200,block_test.width):
            block1 = Block(self,x_blocks,400)
            self.blocks.append(block1)


        for x_blocks in range (200,self.size[0]-30,block_test.width):
            block1 = Block(self,x_blocks,200)
            self.blocks.append(block1)            

        self.allsprites = pygame.sprite.Group(self.guy)
        self.coinsprites = pygame.sprite.Group()
        self.blocksprites = pygame.sprite.Group()
        self.enemysprites = pygame.sprite.Group()
        for coin in self.coins:
            pygame.sprite.Group.add(self.coinsprites,coin)
        for block in self.blocks:
            pygame.sprite.Group.add(self.blocksprites,block)
        for block in self.border:
            pygame.sprite.Group.add(self.blocksprites,block)


        self.Win = False
        self.lose = False

        self.enemy1 = Enemy((255,255,255),20,100,500,100,self.size,self)
        self.enemy2 = Enemy((255,255,255),20,100,100,100,self.size,self)
        self.enemysprites.add(self.enemy1)
        self.enemysprites.add(self.enemy2)


        self.blocks_hit_list    = []

    def update(self):
        """ Update JumpGuyModel. Tracks coins and collisions"""
        for coin in self.coins:
            if coin.disappear:
                self.coinsprites.remove(coin)
                self.coins.remove(coin)
                self.score +=1
        if len(self.coins) == 0:
            self.Win = True

        self.blocks_hit_list = pygame.sprite.spritecollide(self.guy, self.blocksprites, False)
        self.enemy1.enemy_block_list = pygame.sprite.spritecollide(self.enemy1, self.blocksprites, False)
        self.enemy2.enemy_block_list = pygame.sprite.spritecollide(self.enemy2, self.blocksprites, False)

        self.enemy_hit = pygame.sprite.spritecollide(self.guy, self.enemysprites, False)

        if len(self.enemy_hit) > 0:
            self.lose = True
            self.allsprites.remove(self.guy)
        #spritecollide(sprite, group, dokill, collided = None)

        self.allsprites.update()
        self.coinsprites.update()
        self.blocksprites.update()
        self.enemysprites.update()




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
        """Currently and empty function, if the blocks need to change it will be filled"""
        self.exist = True




        
class Coin(pygame.sprite.Sprite):
    """Defines a coin that jump guy can pick up and increase his score"""

    def __init__(self,model,x,y):
        """Initialized variables and loads the coin image"""
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
        """ Detects if the coin has been collected and removes it from the model if it has been"""
        #if abs(self.model.guy.x -self.x) < (self.rect.width - self.model.guy.width)/2 and abs(self.model.guy.y -self.y) < (self.rect.height- self.model.guy.height)/2:
        x_colide = abs(self.model.guy.x -self.x) < self.width + self.model.guy.width/2
        y_colide = abs(self.model.guy.y -self.y) <  (self.height + self.model.guy.height)/2 
        if x_colide and y_colide: #abs(self.model.guy.y -self.y) < 10:
            
            self.disappear = True
            print self.disappear

class Enemy(pygame.sprite.Sprite):
    """Defines and enemy that will kill the jump guy if it hits him"""
    def __init__(self,color,height,width,x,y,window_size,model):
        """Initializes variables for the enemy sprite"""

        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image('enemy1.png', -1) #load an image


        self.color = color
        self.height = self.rect.height
        self.width = self.rect.width
        self.x = x#self.rect.topleft[0]
        self.y = y#Sself.rect.topleft[1]
        self.forcex = 0.0
        self.forcey = 0.0
        self.stopforce = 0.0
        self.vx = 4
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
        self.Left_Collide = False
        self.Right_Collide = False
        self.Top_Collide = False
        self.Bottom_Collide = False
        self.On_platform = False
        self.enemy_block_list = []


    def update(self):
        """ updates the position of the enemy"""
                #--------------------------------------------------------
        self.Left_Collide = False
        self.Right_Collide = False
        self.Bottom_Collide = False
        self.Top_Collide = False

        if len(self.enemy_block_list) > 0:
            for hitblock in self.enemy_block_list:
                x_distance = self.rect.center[0] - hitblock.rect.center[0]
                y_distance = self.rect.center[1] - hitblock.rect.center[1]
                if abs(x_distance) < abs(y_distance): # we collided on top or bottom 
                    if y_distance <= 0:#self.guy.rect.height/2 + self.block_test.height/2: #bottom collision
                        #self.Bottom_Collide = True

                        if abs(self.rect.topleft[0] - hitblock.rect.topright[0]) < 3 or abs(self.rect.topright[0] - hitblock.rect.topleft[0]) < 3 and not self.Bottom_Collide:
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

        self.vy += .1

#code  that keeps the guy ouside of the blocks

        if self.Right_Collide:
            self.vx = -self.vx
        elif self.Left_Collide:
            self.vx = -self.vx

        #making code to determine if the sprite is in the window or not
        #UP = model.Top_Collide #self.y <=0
        #DOWN = model.Bottom_Collide# self.y>= self.window_size[1]-self.height
        if self.Top_Collide:
            if self.vy < 0:
                self.y = self.Tcol_block.rect.bottomright[1]
                self.vy =  0#  self.y
            else: 
                self.y +=self.vy
        elif self.Bottom_Collide:
            if self.vy > 0.0:
                self.y =  self.Bcol_block[0].rect.topright[1]-self.height+1 
    
                self.vy = 0
            else: 
                self.y += self.vy
            self.On_platform = True
        else:
            if self.On_platform: #not self.Bottom_Collide:# and On_platform:
                self.y = self.y
                self.vx = -self.vx
            else:
                self.y += 4
        self.x += self.vx

        self.rect.topleft = (self.x,self.y)

                


class Guy(pygame.sprite.Sprite):
    """ Defines the character sprite"""
    def __init__(self,color,height,width,x,y,window_size,model):    
        """sets and initalizes variables and loads the image for the sprite"""
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image('game_images/crono_left_run.000.gif', -1) #load an image


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
        self.ovy = 0
        self.oovy =0 
        #self.grav_start = 0
        self.rect.topleft = (x,y)
        self.model = model
        self.jumpup = False
        self.Left_Collide = False
        self.Right_Collide = False
        self.Bottom_Collide = False
        self.Top_Collide = False
        self.Lcol_block = []
        self.Rcol_block = []
        self.Bcol_block = []
        self.Tcol_block = []
        self.falldeath = False

    def update(self):
        """ updates the position of the guy"""
        #--------------------------------------------------------
        self.Left_Collide = False
        self.Right_Collide = False
        self.Bottom_Collide = False
        self.Top_Collide = False
        if len(self.model.blocks_hit_list) > 0:
            for hitblock in self.model.blocks_hit_list:
                x_distance = self.rect.center[0] - hitblock.rect.center[0]
                y_distance = self.rect.center[1] - hitblock.rect.center[1]
                if abs(x_distance) < abs(y_distance): # we collided on top or bottom 
                    if y_distance <= 0:#self.guy.rect.height/2 + self.block_test.height/2: #bottom collision
                        #self.Bottom_Collide = True

                        if abs(self.rect.topleft[0] - hitblock.rect.topright[0]) < 3 or abs(self.rect.topright[0] - hitblock.rect.topleft[0]) < 3 and not self.Bottom_Collide:
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


        if self.jump and self.Bottom_Collide and not self.Left_Collide and not self.Right_Collide:
            self.vy = -6
            self.jump = False
        elif self.jump and self.Left_Collide:
            self.vy = -6
            self.vx_jump = 2
            self.jump = False
        elif self.jump and self.Right_Collide:
            self.vy = -6
            self.vx_jump = -2
            self.jump = False
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


        if self.Right_Collide:
            if self.vx>0:
                self.x = self.Rcol_block[0].rect.topleft[0]-self.width
            else:
                self.x += self.vx
        elif self.Left_Collide:
            if self.vx <0:
                self.x = self.Lcol_block[0].rect.topright[0]
            else:
                self.x += self.vx
        else:
            self.x += self.vx

        #making code to determine if the sprite is in the window or not
        #UP = model.Top_Collide #self.y <=0
        #DOWN = model.Bottom_Collide# self.y>= self.window_size[1]-self.height

        if self.Top_Collide:
            if self.vy < 0:
                self.y = self.y

            else: 
                self.y +=self.vy
        elif self.Bottom_Collide:
            if self.oovy >10:
                self.model.lose = True
                self.falldeath = True
                #print self.lose
            if self.vy > 0.0:
                
                self.y = self.Bcol_block[0].rect.topleft[1]-self.height+1
                self.vy = 0

                
            else: 
                self.y += self.vy
        else:
            self.y += self.vy


        self.ooposx = self.oposx
        self.ooposy = self.oposy
        self.oposx = self.rect.topleft[0]
        self.oposy = self.rect.topleft[1]
        self.oovy = self.ovy
        self.ovy = self.vy

        self.rect.topleft = (self.x,self.y)



        


class View:
    """A view of brickbreaker rendered in a pygame window"""
    def __init__(self,model,screen):
        self.model = model
        self.screen = screen
        self.coin = load_sound('coin.wav')
        self.lose = load_sound('death.wav')
        self.lose_once = True
        self.gameover = False
        self.counter = 0  #Counter set to zero so that we can stop animating a certain number of frames after death
        self.after_win = False #becomes true a number of frames after a win

    def draw(self):
        """draws the model on the pygame screen"""
        if model.Win:
            self.counter+=1
            if self.counter ==25:
                self.after_win = True
        if not self.after_win: #not model.Win:

            self.screen.fill(pygame.Color(0,0,0))
            #model.allsprites.draw(screen)
            if self.model.guy.vx > 0:
                if not self.model.guy.Bottom_Collide:  # self.model.guy.vy >0:
                    direction = 'right_jump'
                else:
                    direction = 'right'
            elif self.model.guy.vx == 0:
                direction = 'stop'

            else:
                if not self.model.guy.Bottom_Collide:
                    direction = 'left_jump'
                else:
                    direction = 'left'
            if self.model.lose:
                direction = 'fall'
            moveConductor.play()

            if direction == 'right':
                animObjs['right_run'].blit(screen, (self.model.guy.x, self.model.guy.y)) 
            elif direction == 'left':
                animObjs['left_run'].blit(screen, (self.model.guy.x, self.model.guy.y))
            elif direction == 'right_jump':
                animObjs['right_jump'].blit(screen, (self.model.guy.x, self.model.guy.y)) 
            elif direction == 'left_jump':
                animObjs['left_jump'].blit(screen, (self.model.guy.x, self.model.guy.y)) 
            elif direction == 'stop':
                animObjs['stop'].blit(screen, (self.model.guy.x, self.model.guy.y)) 
            elif direction == 'fall':
                animObjs['smoke'].blit(screen, (self.model.guy.x, self.model.guy.y)) 
                self.gameover = True

            model.coinsprites.draw(screen)
            model.blocksprites.draw(screen)
            model.enemysprites.draw(screen)
            for coin in self.model.coins:
                if coin.disappear:
                    self.coin.play()

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
            if model.lose:

                if pygame.font:
                    if self.lose_once:
                        self.lose.play()
                        self.lose_once = False
                    font = pygame.font.Font(None, 100)

                    text = font.render("You Lose!", 1, (255, 10, 10))
                    textpos = text.get_rect(centerx=model.size[0]/2,centery = model.size[1]/2)
                    screen.blit(text, textpos)

            if not self.gameover: #if the game has not ended keep rendering
                pygame.display.update()

            elif self.counter < 43: # if the game has ended, but a certain number of frames has not passed, keep rendering
                pygame.display.update()
                self.counter +=1
            else:
                print 'over'

        else: #if the player wins

            #self.screen.fill(pygame.Color(0,0,0))
            if self.counter<50:
                self.counter +=1
                print self.counter
                if pygame.font:
                    font = pygame.font.Font(None, 100)

                    text = font.render("You Win!", 1, (255, 255, 10))
                    textpos = text.get_rect(centerx=model.size[0]/2,centery = model.size[1]/2)
                    screen.blit(text, textpos)
            elif self.counter<100:
                self.counter +=1
            else:
                self.counter = 0

                pygame.display.update()




class keyboard_controller:
    """Logs keyboard events and changes the model accordingly"""
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
    pygame.mixer.init()

    size_scale = 6
    size_scalex = 6
    size_scaley = 4
    size = (size_scalex*30*size_scale,size_scaley*30*size_scale)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()


    model = JumpGuyModel(size)
    view = View(model,screen)
    controller = keyboard_controller(model)

    running = True

    animObjs = {}
    animObjs['left_run'] = pyganim.PygAnimation([('game_images/crono_left_run.000.gif', 0.1), #grabs images 
                                                 ('game_images/crono_left_run.001.gif', 0.1),
                                                 ('game_images/crono_left_run.002.gif', 0.1),
                                                 ('game_images/crono_left_run.003.gif', 0.1),
                                                 ('game_images/crono_left_run.004.gif', 0.1),
                                                 ('game_images/crono_left_run.005.gif', 0.1)])

    animObjs['smoke'] = pyganim.PygAnimation([('game_images/smoke_puff_0001.png', 0.05),
                                              ('game_images/smoke_puff_0002.png', 0.05),
                                              ('game_images/smoke_puff_0003.png', 0.05),
                                              ('game_images/smoke_puff_0004.png', 0.05),
                                              ('game_images/smoke_puff_0005.png', 0.05),
                                              ('game_images/smoke_puff_0006.png', 0.05),
                                              ('game_images/smoke_puff_0007.png', 0.05),
                                              ('game_images/smoke_puff_0008.png', 0.1),
                                              ('game_images/smoke_puff_0009.png', 0.1),
                                              ('game_images/smoke_puff_0010.png', 0.1)], loop=False)

    animObjs['right_run'] = animObjs['left_run'].getCopy() #flips images for running in other direction
    animObjs['right_run'].flip(True, False)
    animObjs['right_run'].makeTransformsPermanent()

    animObjs['left_jump'] = pyganim.PygAnimation([('game_images/crono_left_run.001.gif', 0.1)]) #grabs an image for jumping left

    animObjs['right_jump'] = animObjs['left_jump'].getCopy() #flips images for jumpingin other direction
    animObjs['right_jump'].flip(True, False)
    animObjs['right_jump'].makeTransformsPermanent()

    animObjs['stop'] = pyganim.PygAnimation([('game_images/crono_front.gif', 0.1)]) #grabs an image for stopping
    animObjs['fall'] = pyganim.PygAnimation([('game_images/crono_down.gif', 0.1)]) #grabs an image for stopping



    direction = 'right'

    moveConductor = pyganim.PygConductor(animObjs)

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