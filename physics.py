import pygame
import math


class PhysicsEntity:
    def __init__(self, x: float, y: float, radius: float):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.radius = radius
        self.angle = 0.0  # degrees

        # Classic Asteroids + light resistance
        self.max_speed = 420.0
        self.thrust_power = 580.0      # strong forward
        self.reverse_power = 180.0     # weak reverse (S key)
        self.friction = 0.55           # light drag (0 = pure classic)

    def apply_thrust(self, amount: float):
        """
        amount > 0 → forward thrust
        amount < 0 → weak reverse thrust
        """
        if abs(amount) < 0.05:
            return

        rad = math.radians(self.angle)
        forward = pygame.Vector2(math.sin(rad), -math.cos(rad))

        if amount > 0:
            self.acceleration = forward * self.thrust_power * amount
        else:
            self.acceleration = forward * self.reverse_power * amount

    def update(self, dt: float):
        # Apply acceleration
        self.velocity += self.acceleration * dt

        # Light resistance
        if self.friction > 0 and self.velocity.length() > 0:
            drag = self.velocity.normalize() * self.friction * self.velocity.length() * dt
            self.velocity -= drag

        # Hard speed limit
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        # Move
        self.position += self.velocity * dt

        # Reset acceleration every frame
        self.acceleration = pygame.Vector2(0, 0)

    def screen_wrap(self, screen_width: int, screen_height: int):
        if self.position.x < -self.radius:
            self.position.x = screen_width + self.radius
        elif self.position.x > screen_width + self.radius:
            self.position.x = -self.radius

        if self.position.y < -self.radius:
            self.position.y = screen_height + self.radius
        elif self.position.y > screen_height + self.radius:
            self.position.y = -self.radius
