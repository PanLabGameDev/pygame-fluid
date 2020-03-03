class Vector2:
    def __init__(self, x=0, y=0):
        if type(x) == tuple:
            self.x = x[0]
            self.y = x[1]
        else:
            self.x = x
            self.y = y
