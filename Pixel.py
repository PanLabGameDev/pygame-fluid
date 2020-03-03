import random

class Pixel:
    id_counter = 0
    def __init__(self, board, x=0, y=0):
        self.board = board
        self.x = x
        self.y = y

        self.target_x = x
        self.target_y = y

        self.sleeping = False

        self.id = Pixel.id_counter

        Pixel.id_counter += 1

    def move_possible(self, x, y):
        test_x = self.x + x
        test_y = self.y + y


        if not (0 <= test_x < self.board.resolution.x):
            return False
        if not (0 <= test_y < self.board.resolution.y):
            return False

        # return True # asdf wip

        if self.board.get_pixel(test_x, test_y):
            return False
        else:
            return True

    def move(self, x,y):
        self.board.wake_neighbors(self)

        self.board.clear_pixel(self, self.x, self.y)

        self.target_x += x
        self.target_y += y

        self.board.set_pixel(self, self.target_x, self.target_y)

    def update(self):
        down_possible = False
        left_possible = False
        right_possible = False

        if self.move_possible(0, 1):
            down_possible = True
        else:
            if self.move_possible(-1, 0):
                left_possible = True
            if self.move_possible(1, 0):
                right_possible = True

        if down_possible:
            self.move(0, 1)
        elif left_possible and right_possible:
            if random.random() > 0.5:
                self.move(-1, 0)
            else:
                self.move(1, 0)
        elif left_possible:
            self.move(-1, 0)
        elif right_possible:
            self.move(1, 0)
        else:
            self.sleeping = True



    def resolve_conflict(self):
        self.board.clear_pixel(self, self.target_x, self.target_y)
        self.target_x = self.x
        self.target_y = self.y
        self.board.set_pixel(self, self.x, self.y)

    def handle_no_conflict(self):
        self.x = self.target_x
        self.y = self.target_y

    def sleep(self):
        self.sleeping = True

    def wake_up(self):
        self.sleeping = False

    def free(self):
        self.board.wake_neighbors(self)