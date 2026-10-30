from multiprocessing import set_executable

import pygame
import constants
import math
from circleshape import CircleShape
from shot import Shot
from physics import PhysicsEntity


class Player(CircleShape):
    INVINCIBILITY_DURATION = 2.0

    def __init__(self, x:int, y:int, radius=15):
        super().__init__(x, y, constants.PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0
        self.laser_sound = pygame.mixer.Sound("assets/sounds/Laser.wav")
        self.explosion_sound = pygame.mixer.Sound("assets/sounds/Ship.wav")
        self.invincible = False
        self.invincible_timer = 0.0

        self.physics = PhysicsEntity(x, y, constants.PLAYER_RADIUS)
        self.physics.max_forward_speed = 400.0
        self.physics.max_reverse_speed = 150.0

    def respawn(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.invincible = True
        self.invincible_timer = Player.INVINCIBILITY_DURATION

        self.physics.position = pygame.Vector2(x, y)
        self.physics.velocity = pygame.Vector2(0, 0)

    def draw(self, screen: pygame.Surface)-> None:
        if self.invincible and int(self.invincible_timer * 10) % 2 == 0:
            return
        pygame.draw.polygon(screen, "white", self.triangle(), constants.LINE_WIDTH)

    def rotate(self, dt: float) -> None:
        self.rotation += constants.PLAYER_TURN_SPEED * dt

    def move(self, dt: float, direction: int, joystick_y_axis) -> None:
            if joystick_y_axis == 0.0 and pygame.key.get_pressed()[pygame.K_w]: joystick_y_axis = -1.0
            rad = math.radians(self.rotation - 180.0)
            forward_vector = pygame.Vector2(math.sin(rad), -math.cos(rad))

            # Apply speed and direction directly to the vector position coordinates
            self.position += forward_vector * constants.PLAYER_SPEED * direction * dt
            self.physics.angle = self.rotation - 180.0
            self.physics.handle_joystick_thrust(joystick_y_axis, constants.PLAYER_SPEED)
            self.physics.update(dt)
            self.position = self.physics.position
    def shoot(self):
        if self.shoot_timer > 0:
            return
        self.shoot_timer = constants.PLAYER_SHOOT_COOLDOWN_SECONDS
        self.laser_sound.play()
        shot = Shot(self.position.x, self.position.y)
        direction = pygame.Vector2(0, 1)
        direction = direction.rotate(self.rotation)
        shot.velocity = direction * constants.PLAYER_SHOOT_SPEED

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        self.shoot_timer -= dt

        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_SPACE]:
            self.shoot()


    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius // 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
