from bulletml import Bullet, BulletML, collision

from shooter.texture import Texture


class MyBullet(Bullet):
    def __init__(self, radius=8, **kwargs):
        Bullet.__init__(self, radius=radius, **kwargs)
        for tag in self.tags:
            if tag.startswith("texture="):
                self.texture = Texture(tag[len("texture="):])
                break
        else:
            self.texture = None

class BulletSet(object):
    def __init__(self, bullet):
        self.root = bullet
        self.bullets = set([bullet])

    def step(self):
        new_bullets = set()
        dead_bullets = set()

        for bullet in self.bullets:
            new_bullets.update(bullet.step())
            if bullet.finished:
                dead_bullets.add(bullet)

        self.bullets |= new_bullets
        self.bullets -= dead_bullets
    
    def collides(self, other):
        return collision.collides_all(other, list(self))

    def cull(self, w,h,t):
        for bullet in self:
            if not (-t >= bullet.x >= w+t) or not (-t >= bullet.y >= h+t):
                bullet.finished = True

    @classmethod
    def load(cls, filename, (x,y), target, rank=0.5):
        return cls(MyBullet.FromDocument(BulletML.FromDocument(open("bml/" + filename, "rU")), x,y, target=target, rank=rank))

    def __iter__(self):
        return iter(self.bullets)
