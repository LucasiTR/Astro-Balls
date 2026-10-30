# menu.py
import pygame
import math
import constants
from leaderboard import LeaderboardManager

class MainMenu:
    def __init__(self):
        self.font_title = pygame.font.SysFont("Arial", 45, bold=True)
        self.font_options = pygame.font.SysFont("Arial", 24)
        self.leaderboard = LeaderboardManager()

        # --- CIRCULAR MENU UI BUTTONS ---
        # Establish symmetrical circular button anchors using dynamic screen bounds
        self.play_center = (constants.SCREEN_WIDTH // 2 - 120, constants.SCREEN_HEIGHT // 2 + 60)
        self.leader_center = (constants.SCREEN_WIDTH // 2 + 120, constants.SCREEN_HEIGHT // 2 + 60)
        self.radius = 60

    def process_events(self, events, is_mobile):
        """Processes event queues and returns the next target game state string."""
        for event in events:
            # 1. MOBILE TOUCH INTERACTIONS (Read as Mouse on Android)
            if is_mobile and event.type == pygame.FINGERDOWN:
                # Convert mobile floats back to real pixel scales
                px = int(event.x * constants.SCREEN_WIDTH)
                py = int(event.y * constants.SCREEN_HEIGHT)
                pos = (px, py)

                if math.hypot(pos[0] - self.play_center[0], pos[1] - self.play_center[1]) <= self.radius:
                    return "PLAYING"
                elif math.hypot(pos[0] - self.leader_center[0], pos[1] - self.leader_center[1]) <= self.radius:
                    return "LEADERBOARD"

            # PC MOUSE FALLBACK TESTING
            elif not is_mobile and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if math.hypot(event.pos[0] - self.play_center[0], event.pos[1] - self.play_center[1]) <= self.radius:
                    return "PLAYING"
                elif math.hypot(event.pos[0] - self.leader_center[0], event.pos[1] - self.leader_center[1]) <= self.radius:
                    return "LEADERBOARD"

            # 2. KEYBOARD SHORTCUTS (Great for rapid PC testing iterations)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "PLAYING"
                elif event.key == pygame.K_l:
                    return "LEADERBOARD"

        return "MAIN_MENU" # No selection made, remain on the main menu

    def draw(self, screen):
        """Renders the aesthetic layout elements onto the display surface."""
        # Render Game Title Text Header
        title_surf = self.font_title.render("ASTEROIDS MOBILE", True, "white")
        title_rect = title_surf.get_rect(center=(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 3))
        screen.blit(title_surf, title_rect)

        # --- DRAW VISUAL CIRCULAR SELECTION BUTTONS ---
        # Draw Play Button Target Node
        pygame.draw.circle(screen, "green", self.play_center, self.radius, 2)
        txt_play = self.font_options.render("PLAY", True, "green")
        rect_play = txt_play.get_rect(center=self.play_center)
        screen.blit(txt_play, rect_play)

        # Draw Leaderboard Button Target Node
        pygame.draw.circle(screen, (0, 255, 255), self.leader_center, self.radius, 2)
        txt_lead = self.font_options.render("SCORES", True, (0, 255, 255))
        rect_lead = txt_lead.get_rect(center=self.leader_center)
        screen.blit(txt_lead, rect_lead)
