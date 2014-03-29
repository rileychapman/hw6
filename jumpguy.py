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
       
        self.guy = Guy((255,255,255),20,100,200,500,self.size,self) #makes a character
        self.coins = [] #intializes list of coins to place
        self.score = 0
        coin_pos = [(100,500),(200,500),(300,500),(100,300),(800,300),(800,100)] #coins are located at the points in this list
        for pos in coin_pos:    #makes coins at the postition that thye should be at and adds them to the list of coins
            coin = Coin(self,pos[0],pos[1])
            self.coins.append(coin)

        block_test = Block(self,0,0) #block to find size
        self.block_test = block_test
        
        self.border = [] #list of blocks on the borders
        for x_border in range(0,self.size[1],block_test.height): #places border on left and right
            block = Block(self,0,x_border)
            block1 = Block(self,self.size[0] - block_test.width,x_border) 
            self.border.append(block)
            self.border.append(block1)

        for y_border in range(0,self.size[0],block_test.width): #places border on top and bottom
            block = Block(self,y_border,0)
            block2 = Block(self,y_border,self.size[1]-block_test.height)
            self.border.append(block)
            self.border.append(block2)



        self.blocks = [] #list of blocks in the platforms
        for x_blocks in range (0,self.size[0]-200,block_test.width):
            block1 = Block(self,x_blocks,400)
            self.blocks.append(block1)


        for x_blocks in range (200,self.size[0]-30,block_test.width):
            block1 = Block(self,x_blocks,200)
            self.blocks.append(block1)            

        #add all of the sprites to sprite lists
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


        self.Win = False #you have not won
        self.lose = False #you have not lost

        #initializing enemies
        self.enemy1 = Enemy((255,255,255),20,100,500,100,self.size,self)
        self.enemy2 = Enemy((255,255,255),20,100,100,100,self.size,self)
        self.enemy3 = Enemy((255,255,255),20,100,800,100,self.size,self)

        self.enemysprites.add(self.enemy1)
        self.enemysprites.add(self.enemy2)
        self.enemysprites.add(self.enemy3)


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
        #collisiion detections to see if the moving things have hit blocks or not
        self.blocks_hit_list = pygame.sprite.spritecollide(self.guy, self.blocksprites, False)
        self.enemy1.enemy_block_list = pygame.sprite.spritecollide(self.enemy1, self.blocksprites, False)
        self.enemy2.enemy_block_list = pygame.sprite.spritecollide(self.enemy2, self.blocksprites, False)
        self.enemy3.enemy_block_list = pygame.sprite.spritecollide(self.enemy3, self.blocksprites, False)

        #collision detections to see if the enemies have hit the guy
        self.enemy_hit = pygame.sprite.spritecollide(self.guy, self.enemysprites, False)

        if len(self.enemy_hit) > 0: #if the enmies have hit the guy, stop animating and end
            self.lose = True
            self.allsprites.remove(self.guy)
        #spritecollide(sprite, group, dokill, collided = None)
        #updates all of the sprites
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
        self.disappear = False #the coin is displayed by default
        self.rect.topleft = (self.x,self.y)
    def update(self):
        """ Detects if the coin has been collected and removes it from the model if it has been"""
        #checking to see if a colission has occured
        x_colide = abs(self.model.guy.x -self.x) < self.width + self.model.guy.width/2
        y_colide = abs(self.model.guy.y -self.y) <  (self.height + self.model.guy.height)/2 
        if x_colide and y_colide: #abs(self.model.guy.y -self.y) < 10:
            # look this up: http://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.kill
            self.disappear = True

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
        #by default the block is not coliding
        self.Left_Collide = False
        self.Right_Collide = False
        self.Bottom_Collide = False
        self.Top_Collide = False
        # The default is already set in the constructor.

        #checks for colissions and determines what side the colision is on
        if len(self.enemy_block_list) > 0:
            for hitblock in self.enemy_block_list:
                x_distance = self.rect.center[0] - hitblock.rect.center[0]
                y_distance = self.rect.center[1] - hitblock.rect.center[1]
                if abs(x_distance) < abs(y_distance): # we collided on top or bottom 
                    if y_distance <= 0: #colided on the bottom
                        #if the character is only penetrating a block by only 3 pixels then it assumes it is hitting a wall and penetrating a bit and not on a floor. If it is on a floor there will be at least 1 block with a greater collision
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

        self.vy += .1 #gravity

#code  that keeps the guy ouside of the blocks
        #bounces off of obstacles to the left and right
        if self.Right_Collide:
            self.vx = -self.vx
        elif self.Left_Collide:
            self.vx = -self.vx

        '''
        Why is this next section necessary for an enemy? 
        If they're not allowed to jump, then they can't move upward at all.

        '''
        #making code to determine if the sprite is in the window or not
        #UP = model.Top_Collide #self.y <=0
        #DOWN = model.Bottom_Collide# self.y>= self.window_size[1]-self.height
        if self.Top_Collide:
            if self.vy < 0:
                self.y = self.Tcol_block.rect.bottomright[1]
                self.vy =  0#  self.y
            else: 
                self.y +=self.vy
        elif self.Bottom_Collide: #doesn't go through blocks, but instad of falling off, switches direction
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
                self.y += 4 #mob falls to platform quickly
        self.x += self.vx

        self.rect.topleft = (self.x,self.y)

                


class Guy(pygame.sprite.Sprite):
    """ Defines the character sprite"""
    def __init__(self,color,height,width,x,y,window_size,model):    
        """sets and initalizes variables and loads the image for the sprite"""
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image('game_images/crono_left_run.000.gif', -1) #load an image


        # document some of these initial values because I have no clue what they're supposed to be...
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
        #-------------------------------------------------------
        #isn't colliding by default
        self.Left_Collide = False
        self.Right_Collide = False
        self.Bottom_Collide = False
        self.Top_Collide = False

        if len(self.model.blocks_hit_list) > 0: #for each element that is coliding, determine the side that it is coliding on 
            for hitblock in self.model.blocks_hit_list:
                x_distance = self.rect.center[0] - hitblock.rect.center[0]
                y_distance = self.rect.center[1] - hitblock.rect.center[1]
                if abs(x_distance) < abs(y_distance): # we collided on top or bottom 
                    if y_distance <= 0:

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


        if self.jump and self.Bottom_Collide and not self.Left_Collide and not self.Right_Collide: #normal jump
            self.vy = -6
            self.jump = False
        elif self.jump and self.Left_Collide: #wall jumping
            self.vy = -6
            self.vx_jump = 2
            self.jump = False
        elif self.jump and self.Right_Collide: #wall jumping
            self.vy = -6
            self.vx_jump = -2
            self.jump = False
        else:
            self.vy += .1
            self.vx_jump = 0

        self.vx_inter = self.vx
        self.vx_inter += self.forcex*.03 #accelerate in x direction

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

        '''
        More efficient way of writing the following if...elif...else loop (also, no need for else)
        if abs(self.vx_inter) > speed_cap: 
            self.vx_inter *= speed_cap / self.vs_inter 
        '''
        if self.vx_inter < -speed_cap: # x speed can't be larger than a certain value. If it is, set it to that value
            self.vx_inter = -speed_cap
        elif self.vx_inter > speed_cap:
            self.vx_inter = speed_cap

        else:
            self.vx_inter = self.vx_inter 


        self.vx = self.vx_inter+ self.vx_jump #add together the wall jumping speeds and the controlled speed

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

  
        #check if the character is on top or below a wall block

        if self.Top_Collide:
            if self.vy < 0:
                self.y = self.y

            else: 
                self.y +=self.vy
        elif self.Bottom_Collide:
            if self.oovy >10: # if the character is falling to fast, they die
                self.model.lose = True
                self.falldeath = True
                #print self.lose
            if self.vy > 0.0:
                
                self.y = self.Bcol_block[0].rect.topleft[1]-self.height+1 #if the character hits a block, set the character to the location of the block
                self.vy = 0

                
            else: 
                self.y += self.vy #character moves by the speed
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
            if self.counter ==25: #waits 25 frames to stop animating so that the final coin has time to disappear
                self.after_win = True 
        if not self.after_win: 
            self.screen.fill(pygame.Color(0,0,0)) 
            #model.allsprites.draw(screen)
            if self.model.guy.vx > 0:
                if not self.model.guy.Bottom_Collide:  # self.model.guy.vy >0:
                    direction = 'right_jump' #us the animation right jump
                else:
                    direction = 'right' #use the animation right
            elif self.model.guy.vx == 0:
                direction = 'stop' #use the anmatino stop

            else:
                if not self.model.guy.Bottom_Collide:
                    direction = 'left_jump' #use the anmiation left jump
                else:
                    direction = 'left' #use the animation left
            if self.model.lose:
                direction = 'fall' #play the smoke animations
            moveConductor.play()
            #play the anmiations
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
            #draw all of the sprites
            model.coinsprites.draw(screen)
            model.blocksprites.draw(screen)
            model.enemysprites.draw(screen)
            for coin in self.model.coins:
                if coin.disappear:
                    self.coin.play()
            #display text on the screen
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

            if model.lose: #if the character loses

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
                pass
        else: #if the player wins

            #self.screen.fill(pygame.Color(0,0,0))
            if self.counter<50:
                self.counter +=1
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
        #checks keyboard events and feeds them to the model and to the guy
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
    #scales the screen
    size_scale = 6
    size_scalex = 6 #sets aspect ratio
    size_scaley = 4 #sets aspec ratio
    size = (size_scalex*30*size_scale,size_scaley*30*size_scale) #makeks screen
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()


    model = JumpGuyModel(size)
    view = View(model,screen)
    controller = keyboard_controller(model)

    running = True
    #import images for the animations
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
        # clock.tick(120) #makes the game run at a constant rate 

        for event in pygame.event.get():
            if event.type == KEYDOWN or KEYUP:
                controller.handle_keyboard_event(event)
            if event.type == QUIT:
                running = False


        model.update()
        view.draw()
        time.sleep(.001)

    pygame.quit()