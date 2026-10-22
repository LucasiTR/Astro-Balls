import pygame
import math

class TouchController:
    def __init__(self, SCREEN_HEIGHT, SCREEN_WIDTH) -> None:
        self.style = "JOYSTICK"

                # --- CIRCULAR BUTTON DEFINITIONS ---
                # Define buttons by their (Center X, Center Y) coordinates and Radius
        self.thrust_center = (screen_width - 100, screen_height - 220)
        self.thrust_radius = 45

        self.fire_center = (screen_width - 220, screen_height - 120)
        self.fire_radius = 45

                # Joystick configuration parameters (Already naturally circular)
        self.joy_center = (120, screen_height - 140)
        self.joy_max_radius = 70
        self.joy_knob_pos = list(self.joy_center)

        self.active_touches = {}
        self.signals = {"thrust": False, "shoot": False, "rotation_offset": 0.0, "rotate_left": False, "rotate_right": False}

        def check_circle_collision(self, pos, center, radius):
            dx = pos[0] - center[0]
            dy = pos[1] - center[1]
            return math.hypot(dx, dy) <= radius

        def process_events(self, events, screen_width, screen_height):
            self.signals["shoot"] = False

            for event in events:
                if event.type == pygame.FINGERDOWN:
                    px = int(event.x * screen_width)
                    py = int(event.y * screen_height)
                    pos = (px, py)

                        # Check circular interactions using distance math
                    if self.check_circle_collision(pos, self.thrust_center, self.thrust_radius):
                        self.signals["thrust"] = True
                        self.active_touches[event.finger_id] = "THRUST"
                    elif self.check_circle_collision(pos, self.fire_center, self.fire_radius):
                        self.signals["shoot"] = True
                        self.active_touches[event.finger_id] = "FIRE"

                        # Left side controls
                    else:
                        if self.style == "JOYSTICK":
                            if self.check_circle_collision(pos, self.joy_center, self.joy_max_radius + 30):
                                self.active_touches[event.finger_id] = "STEER"
                        elif self.style == "DPAD":
                                # If you want your alternative D-pad layout to ALSO be circles:
                            if self.check_circle_collision(pos, (60, screen_height - 120), 35): # Left
                                self.signals["rotate_left"] = True
                                self.active_touches[event.finger_id] = "STEER_L"
                            elif self.check_circle_collision(pos, (180, screen_height - 120), 35): # Right
                                self.signals["rotate_right"] = True
                                self.active_touches[event.finger_id] = "STEER_R"
                            elif self.check_circle_collision(pos, (120, screen_height - 180), 35): # Up
                                self.signals["thrust"] = True
                                self.active_touches[event.finger_id] = "STEER_U"

                    # (Keep FINGERMOTION and FINGERUP blocks completely matching your original logic)
                elif event.type == pygame.FINGERMOTION:
                    px = int(event.x * screen_width)
                    py = int(event.y * screen_height)
                    if event.finger_id in self.active_touches and self.active_touches[event.finger_id] == "STEER":
                        dx = px - self.joy_center[0]
                        dy = py - self.joy_center[1]
                        distance = math.hypot(dx, dy)
                        angle = math.atan2(dy, dx)
                        self.signals["rotation_offset"] = angle
                        if distance > self.joy_max_radius:
                            self.joy_knob_pos = [self.joy_center[0] + int(math.cos(angle) * self.joy_max_radius),
                                                self.joy_center[1] + int(math.sin(angle) * self.joy_max_radius)]
                        else:
                            self.joy_knob_pos = [px, py]

                    elif event.type == pygame.FINGERUP:
                        if event.finger_id in self.active_touches:
                            role = self.active_touches.pop(event.finger_id)
                            if role in ["THRUST", "STEER_U"]: self.signals["thrust"] = False
                            elif role == "STEER_L": self.signals["rotate_left"] = False
                            elif role == "STEER_R": self.signals["rotate_right"] = False
                            elif role == "STEER": self.joy_knob_pos = list(self.joy_center)

                return self.signals

            def draw_overlay(self, screen, screen_height):
                """Renders cleanly using circle drawing functions."""
                # Thrust Button (Solid Green if active, hollow circle if unpressed)
                thrust_color = (0, 255, 0) if self.signals["thrust"] else (100, 100, 100)
                pygame.draw.circle(screen, thrust_color, self.thrust_center, self.thrust_radius, 2 if not self.signals["thrust"] else 0)

                # Fire Button (Hollow Red Circle)
                pygame.draw.circle(screen, (255, 0, 0), self.fire_center, self.fire_radius, 2)

                # Draw Left Steering Group
                if self.style == "JOYSTICK":
                    pygame.draw.circle(screen, (150, 150, 150), self.joy_center, self.joy_max_radius, 2)
                    pygame.draw.circle(screen, (0, 255, 255), self.joy_knob_pos, 25)
                elif self.style == "DPAD":
                    # Render a cluster of circular directional targets instead of boxes
                    pygame.draw.circle(screen, (150, 150, 150), (120, screen_height - 180), 35, 2) # Up Arrow Circle
                    pygame.draw.circle(screen, (150, 150, 150), (60, screen_height - 120), 35, 2)  # Left Arrow Circle
                    pygame.draw.circle(screen, (150, 150, 150), (180, screen_height - 120), 35, 2) # Right Arrow Circle
