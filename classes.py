import time

class Animation:
    def __init__(self, images, fps):#list, int
        self.image = 0
        self.images = images
        self.fps = fps
        self.oldtime = time.time()
        self.cooldown = 1/fps
    def update(self, config, images):
        self.fps = config["fps"]
        self.cooldown = 1/self.fps
        acttime = time.time()
        if acttime >= self.oldtime + self.cooldown:
            self.oldtime = acttime
            self.image += 1
    def draw(self):
        try:
            return self.images[self.image]
        except:
            self.image = 0
            return self.images[0]
    def list_update(self, images):
        self.images = images