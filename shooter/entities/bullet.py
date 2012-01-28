from bulletml import Bullet, BulletML, collision

from shooter.texture import Texture


class MyBullet(Bullet):
    def __init__(self, radius=8, root=False, **kwargs):
        Bullet.__init__(self, radius=radius, **kwargs)
        for tag in self.tags:
            if tag.startswith("texture="):
                self.texture = Texture(tag[len("texture="):])
                break
        else:
            self.texture = None
        self.root = root
        self.z = 0

class BulletSet(set):
    def update_roots(self, entity):
        for bullet in self:
            if bullet.root:
                bullet.x = entity.x
                bullet.y = entity.y

    def step(self, w,h,t):
        new_bullets = set()
        dead_bullets = set()

        for bullet in self:
            new_bullets.update(bullet.step())
            if bullet.finished:
                dead_bullets.add(bullet)

            if not (-t <= bullet.x <= w+t) or not (-t <= bullet.y <= h+t):
                dead_bullets.add(bullet)

        self |= new_bullets
        self -= dead_bullets

    def collides(self, other):
        return collision.collides_all(other, list(self))

    def load(self, filename, source, target, rank=0.5):
        bullet = MyBullet.FromDocument(BulletML.FromDocument(open("bml/" + filename, "rU")), source.x, source.y, target=target, rank=rank)
        bullet.root = True
        self.add(bullet)
