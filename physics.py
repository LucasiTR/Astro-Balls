import pygame
import math

class PhysicsEntity:
    def __init__(self, x, y, radius):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.radius = radius
        self.angle = 0  # In degrees

        # Skill-based movement tuning parameters
        self.max_forward_speed = 400.0
        self.max_reverse_speed = 150.0  # Strict cap to keep it skill-based

    def handle_joystick_thrust(self, joystick_y_axis, thrust_power):
        """
        Handles movement using a joystick axis.
        Negative Y-axis moves forward, positive Y-axis triggers limited reverse thrust.
        """
        # Ensure joystick is past a small deadzone
        if abs(joystick_y_axis) < 0.1:
            return

        rad = math.radians(self.angle)

        # Calculate full direction vectors based on rotation angle
        forward_vector = pygame.Vector2(math.sin(rad), -math.cos(rad))

        if joystick_y_axis < 0:
            # Forward thrust scaled by how far the stick is pushed
            intensity = abs(joystick_y_axis)
            self.acceleration = forward_vector * thrust_power * intensity
        else:
            # Reverse thrust triggers backward movement
            intensity = joystick_y_axis
            self.acceleration = -forward_vector * thrust_power * intensity

    def update(self, dt):
        """Updates physics with zero friction and applies skill-based limits."""
        # Zero friction: velocity only changes if acceleration is applied
        self.velocity += self.acceleration * dt

        # Enforce speed restrictions dynamically based on travel direction
        current_speed = self.velocity.length()
        if current_speed > 0.01:
            rad = math.radians(self.angle)
            forward_vector = pygame.Vector2(math.sin(rad), -math.cos(rad))

            # Use dot product to check if traveling forward or backward
            direction_dot = self.velocity.dot(forward_vector)

            if direction_dot >= 0:
                # Limit forward movement speed
                if current_speed > self.max_forward_speed:
                    self.velocity = self.velocity.normalize() * self.max_forward_speed
            else:
                # Clamp reverse movement strictly to keep it skill-based
                if current_speed > self.max_reverse_speed:
                    self.velocity = self.velocity.normalize() * self.max_reverse_speed

        # Apply velocity to update coordinate position
        self.position += self.velocity * dt

        # Reset acceleration forces for the next game frame loop
        self.acceleration = pygame.Vector2(0, 0)

    def screen_wrap(self, screen_width, screen_height):
        """Classic screen wrapping logic."""
        if self.position.x < -self.radius:
            self.position.x = screen_width + self.radius
        elif self.position.x > screen_width + self.radius:
            self.position.x = -self.radius

        if self.position.y < -self.radius:
            self.position.y = screen_height + self.radius
        elif self.position.y > screen_height + self.radius:
            self.position.y = -self.radius
