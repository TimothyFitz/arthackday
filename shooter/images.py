import os
import time
import copy

from OpenGL.GL import *
from OpenGL.arrays import vbo
import gutil

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

