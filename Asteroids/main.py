#
# "RiceRocks" (Asteroids).
#
# since code was initially written in codeSkulptor we need to install SimpleGUICS2Pygame
# $ python -m pip install SimpleGUICS2Pygame
try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import random
import math

WIDTH = 800
HEIGHT = 600

MOTION_KEYS = ["left", "right", "up", "space"]
THRUST = 0.1
ANGLE_VELOCITY = 0.05
FRICTION = 0.01

ROCK_ANGLE_VELOCITY = 0.1
ROCK_MIN_ANGLE_VELOCITY = -0.15
ROCK_MAX_ANGLE_VELOCITY = 0.15
ROCK_MIN_VELOCITY = -1
ROCK_MAX_VELOCITY = 1
VELOCITY_SCALING_FACTOR = 10
MAX_NUMBER_OF_ROCKS = 12

MISSILE_SPEED = 8

EXPLOSION_ANIMATIONS = 24

VOLUME = 0.5

MAX_LIVES = 3
SCORE_SCALING_FACTOR = 10

FONT_SIZE = 25
FONT_COLOR = 'White'
FONT_FACE = 'sans-serif'
score = 0

lives = MAX_LIVES
time = 0
started = False
rock_group = set([])
missile_group = set([])
explosion_group = set([])


class ImageInfo:
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):

        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):

        return self.center

    def get_size(self):

        return self.size

    def get_radius(self):

        return self.radius

    def get_lifespan(self):

        return self.lifespan

    def get_animated(self):

        return self.animated


debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

missile_info = ImageInfo([5, 5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

soundtrack = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(VOLUME)
ship_thrust_sound = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")


def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]


def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0

        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()

    def draw(self, canvas):
        if not self.thrust:
            canvas.draw_image(self.image,
                              (self.image_center[0], self.image_center[1]),
                              (self.image_size[0], self.image_size[1]),
                              (self.pos[0], self.pos[1]),
                              (self.image_size[0], self.image_size[1]),
                              self.angle)
        else:
            canvas.draw_image(self.image,
                              (3 * self.image_center[0], self.image_center[1]),
                              (self.image_size[0], self.image_size[1]),
                              (self.pos[0], self.pos[1]),
                              (self.image_size[0], self.image_size[1]),
                              self.angle)

        return None

    def update(self):
        self.angle += self.angle_vel

        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT

        self.vel[0] *= (1 - FRICTION)
        self.vel[1] *= (1 - FRICTION)

        if self.thrust:
            forward = angle_to_vector(self.angle)
            self.vel[0] += forward[0] * THRUST
            self.vel[1] += forward[1] * THRUST

        return None

    def adjust_orientation(self, angle_vel):
        self.angle_vel += angle_vel

        return None

    def set_thrust(self, on_off):
        self.thrust = on_off

        if self.thrust:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()

        return None

    def shoot(self):
        forward = angle_to_vector(self.angle)

        missile_pos = [self.pos[0] + self.radius * forward[0],
                       self.pos[1] + self.radius * forward[1]]

        missile_vel = [self.vel[0] + MISSILE_SPEED * forward[0],
                       self.vel[1] + MISSILE_SPEED * forward[1]]

        a_missile = Sprite(missile_pos, missile_vel,
                           self.angle, 0, missile_image,
                           missile_info, missile_sound)

        global missile_group
        missile_group.add(a_missile)

        return None

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius


class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound=None):
        self.pos = [pos[0], pos[1]]

        self.vel = [vel[0], vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()

    def draw(self, canvas):
        if not self.animated:
            canvas.draw_image(self.image, self.image_center,
                              self.image_size, self.pos,
                              self.image_size, self.angle)
        else:

            image_index = (self.age % EXPLOSION_ANIMATIONS) // 1
            image_center = [self.image_center[0] + (self.image_size[0] * image_index),
                            self.image_center[1]]
            canvas.draw_image(self.image, image_center,
                              self.image_size, self.pos,
                              self.image_size, self.angle)

        return None

    def update(self):
        self.angle += self.angle_vel

        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
        self.age += 1
        if self.age >= self.lifespan:
            return True
        else:
            return False

    def collide(self, other_object):
        if dist(self.pos, other_object.get_position()) < (self.radius + other_object.get_radius()):
            return True
        else:
            return False

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius


def draw(canvas):
    global time
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2],
                      [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    global lives
    canvas.draw_text("Lives: " + str(lives),
                     [WIDTH // 8, HEIGHT // 8],
                     FONT_SIZE, FONT_COLOR, FONT_FACE)

    global score
    score_text = "Score: " + str(score)
    score_textwidth_in_px = frame.get_canvas_textwidth(score_text, FONT_SIZE, FONT_FACE)
    score_point_x = WIDTH - (WIDTH // 8) - (score_textwidth_in_px)
    score_point_y = HEIGHT // 8
    canvas.draw_text(score_text,
                     [score_point_x, score_point_y],
                     FONT_SIZE, FONT_COLOR, FONT_FACE)

    global rock_group, missile_group, explosion_group
    my_ship.draw(canvas)
    if rock_group:
        process_sprite_group(canvas, rock_group, "draw")
    if missile_group:
        process_sprite_group(canvas, missile_group, "draw")
    if explosion_group:
        process_sprite_group(canvas, explosion_group, "draw")

    my_ship.update()
    if rock_group:
        process_sprite_group(None, rock_group, "update")
    if missile_group:
        process_sprite_group(None, missile_group, "update")
    if explosion_group:
        process_sprite_group(None, explosion_group, "update")

    if group_collide(rock_group, my_ship):
        lives -= 1

    global started
    if lives == 0:
        started = False
        rock_group = set([])

    score += group_group_collide(rock_group, missile_group) * SCORE_SCALING_FACTOR

    if not started:
        canvas.draw_image(splash_image,
                          splash_info.get_center(),
                          splash_info.get_size(),
                          [WIDTH / 2, HEIGHT / 2],
                          splash_info.get_size())

    return None


def rock_spawner():
    if not started:
        return None

    global rock_group

    if len(rock_group) >= MAX_NUMBER_OF_ROCKS:
        return None

    velocity_range = ROCK_MAX_VELOCITY - ROCK_MIN_VELOCITY
    rock_vel = [random.random() * velocity_range + ROCK_MIN_VELOCITY,
                random.random() * velocity_range + ROCK_MIN_VELOCITY]

    if score > 0:
        rock_vel = [rock_vel[0] * math.ceil(float(score) / (VELOCITY_SCALING_FACTOR * SCORE_SCALING_FACTOR)),
                    rock_vel[1] * math.ceil(float(score) / (VELOCITY_SCALING_FACTOR * SCORE_SCALING_FACTOR))]

    angle_velocity_range = ROCK_MAX_ANGLE_VELOCITY - ROCK_MIN_ANGLE_VELOCITY
    rock_angle_vel = random.random() * angle_velocity_range + ROCK_MIN_ANGLE_VELOCITY

    rock_pos = [random.randrange(0, WIDTH - 1),
                random.randrange(0, HEIGHT - 1)]

    ship_radius = ship_info.get_radius()
    rock_radius = asteroid_info.get_radius()
    while dist(rock_pos, my_ship.pos) < ((2 * ship_radius) + rock_radius):
        rock_pos = [random.randrange(0, WIDTH - 1),
                    random.randrange(0, HEIGHT - 1)]

    a_rock = Sprite(rock_pos, rock_vel,
                    0, rock_angle_vel,
                    asteroid_image, asteroid_info)

    rock_group.add(a_rock)

    return None


def process_sprite_group(canvas, sprite_group, method):
    group_copy = set(sprite_group)
    for sprite in group_copy:
        if method == "draw":
            sprite.draw(canvas)
        else:
            remove_sprite = sprite.update()
            if remove_sprite:
                sprite_group.remove(sprite)

    return None


def group_collide(group, other_object):
    collision = False
    group_copy = set(group)
    for object in group_copy:
        if object.collide(other_object):
            group.remove(object)
            collision = True
            explosion = Sprite(object.get_position(),
                               [0, 0], 0, 0,
                               explosion_image,
                               explosion_info,
                               explosion_sound)
            explosion_group.add(explosion)

    return collision


def group_group_collide(group_1, group_2):
    number_of_collisions = 0

    group_copy_1 = set(group_1)
    for object in group_copy_1:
        collision = group_collide(group_2, object)
        if collision:
            group_1.discard(object)
            number_of_collisions += 1

    return number_of_collisions


def keydown_handler(key):
    if key == simplegui.KEY_MAP[MOTION_KEYS[0]]:
        my_ship.adjust_orientation(-ANGLE_VELOCITY)

    if key == simplegui.KEY_MAP[MOTION_KEYS[1]]:
        my_ship.adjust_orientation(ANGLE_VELOCITY)

    if key == simplegui.KEY_MAP[MOTION_KEYS[2]]:
        my_ship.set_thrust(True)

    if key == simplegui.KEY_MAP[MOTION_KEYS[3]]:
        my_ship.shoot()

    return None


def keyup_handler(key):
    if key == simplegui.KEY_MAP[MOTION_KEYS[0]]:
        my_ship.adjust_orientation(ANGLE_VELOCITY)

    if key == simplegui.KEY_MAP[MOTION_KEYS[1]]:
        my_ship.adjust_orientation(-ANGLE_VELOCITY)

    if key == simplegui.KEY_MAP[MOTION_KEYS[2]]:
        my_ship.set_thrust(False)

    return None


def click(pos):
    center = [WIDTH / 2, HEIGHT / 2]

    size = splash_info.get_size()

    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)

    global started, lives, score, my_ship
    if (not started) and inwidth and inheight:
        started = True
        lives = MAX_LIVES
        score = 0
        soundtrack.rewind()
        soundtrack.play()

    return None


frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0],
               0, ship_image, ship_info)

frame.set_draw_handler(draw)

frame.set_keydown_handler(keydown_handler)
frame.set_keyup_handler(keyup_handler)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

# Start the "Timer".
timer.start()
frame.start()
soundtrack.play()
