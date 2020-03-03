from Pixel import Pixel
from Vector2 import Vector2

class PixelBoard:
    def __init__(self, x, y):
        self.pixels = []
        self.resolution = Vector2(x, y)
        for _ in range(x * y):
            self.pixels.append([])

        self.pixel_list = []
        self.conflicting_pixels = [] # List of sets(!), Not Vector2, must be immutable

    def has_conflicts(self):
        return len(self.conflicting_pixels) != 0

    def resolve_conflicts(self):
        print("has_conflicts", time.time())
        print("conflicts: ", len(self.conflicting_pixels))

        tmp_conflict_list = []
        for conflict in self.conflicting_pixels:
            print("At: ", conflict)
            tmp_conflict_list.append(conflict)

        #self.conflicting_pixels = []

        for conflict_pos in tmp_conflict_list:
            conflict = self.get_pixel(conflict_pos[0], conflict_pos[1])

            # for i in range(1, len(conflict)-1): # skip first participant
            first_omitted = True # TODO should be random
            for conf_participant in conflict: # skip first participant
                if not first_omitted:
                    first_omitted = True
                    continue
                conf_participant.resolve_conflict()


    def _conv(self, x,y):
        return x + y * self.resolution.x

    def add_pixel(self, x, y): # Adds pixel to the board
        if self.get_pixel(x, y):
            # print(f"There is already something on {x}|{y}")
            return

        pixel = Pixel(self, x, y)
        self.pixel_list.append(pixel)
        self.set_pixel(pixel, x, y)

    def set_pixel(self, pixel, x, y): # Adds pixel to one field
        field = self.get_pixel(x, y)
        field.append(pixel)

        if len(field) == 2: # only add to conflicting pixels the first time the limit is exceeded
            self.conflicting_pixels.append((x, y))

        #print("Set pixel", x, y)

    def get_pixel(self, x, y):
        return self.pixels[self._conv(x,y)]

    def clear_pixel(self, pixel, x, y):
        field = self.get_pixel(x,y)
        field.remove(pixel)

        if len(field) == 1:
            self.conflicting_pixels.remove((x, y))

    def clear(self):
        for p in self.pixel_list:
            # self.remove_pixel(p) # Not necessary because list will be cleared completely
            self.clear_pixel(p, p.target_x, p.target_y)
            p.free()

        self.pixel_list.clear()

    def remove_pixel(self, pixel):
        self.pixel_list.remove(pixel)
        self.clear_pixel(pixel, pixel.target_x, pixel.target_y)
        pixel.free()

    def __len__(self):
        return len(self.pixel_list)

    def __iter__(self):
        for p in self.pixel_list:
            try:
                yield p
            except IndexError:
                yield None

    def check_orphans(self):
        global paused
        p_counter = sum([len(p) for p in self.pixels])
        orphans = p_counter - len(self.pixel_list)

        if orphans != 0:
            print("orphaned pixels: ", orphans)
            raise Exception("Orphan created")

    def update(self):
        while self.has_conflicts(): # asdf should use while
        # if self.has_conflicts():
            self.resolve_conflicts()
        #else:
        for pixel in self.pixel_list:
            pixel.handle_no_conflict()
            if not pixel.sleeping:
                pixel.update()

    def wake_neighbors(self, p):
        test_pixels = [
            (p.x - 1, p.y),
            (p.x + 1, p.y),
            (p.x, p.y - 1),
            (p.x, p.y + 1)
        ]

        for tp in test_pixels:
            try:
                f = self.get_pixel(tp[0], tp[1])
                for p in f:
                    p.wake_up()
            except IndexError:
                pass