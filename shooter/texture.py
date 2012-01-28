import os.path

import gutil

class _Texture(object):
    def __init__(self, texname):
        filename = os.path.join('data', texname)
        filename += ".png"

        self.id, self.width, self.height = gutil.loadImage(filename)

    def __del__(self):
        if self.id != None:
            gutil.delTexture(self.id)
            self.id = None
            
TEXTURES = {}
def Texture(texname):
    try:
        return TEXTURES[texname]
    except KeyError:
        tex = TEXTURES[texname] = _Texture(texname)
        return tex