import pygame
import constants
from circleshape import CircleShape


class Player(CircleShape):
    def __init__(self, x:int, y:int):
        super().__init__(x, y, constants.PLAYER_RADIUS)
        attribute: rotation = 0

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
