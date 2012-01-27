from bulletml import Bullet, BulletML

class Player(object):
    def __init__(self):
        self.x = 0
        self.y = 0

doc = BulletML.FromDocument(open("test.xml", "rU"))
player = Player()  # On your own here, but it needs x and y fields.
rank = 0.5 # Player difficulty, 0 to 1

bullet = Bullet.FromDocument(doc, 1, 1, target=player, rank=rank)
bullets = [bullet]


for bullet in bullets:
    bullets.extend(bullet.step())
    
#print bullets


import pygame
from pygame.locals import *
from OpenGL.GL import *
import gutil
import os


class Image:
    def __init__(self, texname):
        filename = os.path.join('data', texname)
        filename += ".png"

        self.texture, self.width, self.height = gutil.loadImage(filename)
        self.displayList = gutil.createTexDL(self.texture, self.width, self.height)
   

    def __del__(self):
        if self.texture != None:
            gutil.delTexture(self.texture)
            self.texture = None
        if self.displayList != None:
            gutil.delDL(self.displayList)
            self.displayList = None


    def draw(self, pos=None, width = None, height = None, color=(1,1,1,1), rotation=0, rotationCenter=None):
        glColor4fv(color)

        if pos:
            glLoadIdentity()
            glTranslate(pos[0],pos[1],0)

        if rotation != 0:
                if rotationCenter == None:
                    rotationCenter = (self.width / 2, self.height / 2)
                (w,h) = rotationCenter
                glTranslate(rotationCenter[0],rotationCenter[1],0)
                glRotate(rotation,0,0,-1)
                glTranslate(-rotationCenter[0],-rotationCenter[1],0)

        if width or height:
            if not width:
                width = self.width
            elif not height:
                height = self.height

            glScalef(width/(self.width*1.0), height/(self.height*1.0), 1.0)
                

        glCallList(self.displayList)


class Text(Image):

    def __init__(self, text, fontsize = 24, color = (0,0,0,0), font = None, antialias = 1):
        texttexture = gutil.loadText(text, fontsize, color, font, antialias)
        self.texture = texttexture[0]
        self.width = texttexture[1]
        self.height = texttexture[2]
        self.texture_width = texttexture[3]
        self.texture_height = texttexture[4]
        self.displayList = gutil.createTexDL(self.texture, self.texture_width, self.texture_height)


def main():
    pygame.init()
    gutil.initializeDisplay(800, 600)

    done = False

    cow = Image('cow')
    alien = Image('alien')

    white = (255,255,255,255)
    string1 = Text("Cow!", fontsize=256, color=white)
    string2 = Text("Rotation!", color=white)

    while not done:
        glClear(GL_COLOR_BUFFER_BIT)
        cow.draw(pos=(100,100),width=128,height=128)
        string1.draw(pos=(100,0), width=128,height=128)
        alien.draw(pos=(400, 400),rotation=-15,color=(.9,.3,.2,1))
        string2.draw(pos=(600, 400), rotation=20, color=(.2,.3,.9,1))

        pygame.display.flip()

        eventlist = pygame.event.get()
        for event in eventlist:
            if event.type == QUIT \
               or event.type == KEYDOWN and event.key == K_ESCAPE:
                done = True

if __name__ == '__main__':
    main()
