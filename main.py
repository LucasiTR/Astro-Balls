import pygame
import sys
import os
import math
import constants

from pygame.constants import K_LEFT, K_UP, QUIT
from pygame.mouse import get_pos

from asteroid import Asteroid
from asteroidfield import AsteroidField
from player import Player
from constants import ASTEROID_MIN_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT
from shot import Shot

from main_menu import MainMenu
from controls import TouchController
from logger import log_state, log_event

def main():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    FORCE_MOBILE_PREVIEW = False
    IS_MOBILE = "ANDROID ARGUMENT" in os.environ or FORCE_MOBILE_PREVIEW

    if IS_MOBILE and not FORCE_MOBILE_PREVIEW:
        info = pygame.display.Info()
        actual_w = info.current_w
        actual_h = info.current_h
        screen = pygame.display.set_mode((actual_w, actual_h), pygame.FULLSCREEN)
    else:
       actual_w = constants.SCREEN_WIDTH
       actual_h = constants.SCREEN_HEIGHT
       screen = pygame.display.set_mode((actual_w, actual_h))

    SCREEN_WIDTH = actual_w
    SCREEN_HEIGHT = actual_h

    font = pygame.font.Font(None, 26)
    laser_sound = pygame.mixer.Sound("assets/sounds/Laser.wav")
    explosion_sound = pygame.mixer.Sound("assets/sounds/Ship.wav")
    asteroid_sound = pygame.mixer.Sound("assets/sounds/Asteroid.wav")

    clock = pygame.time.Clock()
    menu_screen = MainMenu()
    touch_ctrl = TouchController(constants.SCREEN_HEIGHT, constants.SCREEN_WIDTH)

    current_state = "MAIN MENU"

    updatable = pygame.sprite.Group()
    drawable =  pygame.sprite.Group()
    shots = pygame.sprite.Group()
    asteroids =  pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Shot.containers = (shots, updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable)
    AsteroidField()

    player = None
    asteroid_field = None
    score = 0
    lives = 3
    respawn_timer = 0.0
    player_alive = False
    dt = 0.0

    while True:
        log_state()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return
        if current_state == "MAIN MENU":
            next_state = menu_screen.process_events(events, IS_MOBILE)

            if next_state == "IS PLAYING" or next_state == "PLAYING":
                updatable.empty()
                drawable.empty()
                shots.empty()
                asteroids.empty()

                player = Player(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2)
                asteroid_field = AsteroidField()
                score = 0
                lives = 3
                respawn_timer = 0.0
                player_alive = True
                current_state = "PLAYING"
            else:
                if next_state:
                    current_state = next_state

            screen.fill(getattr(constants, "COLOR_BLACK", "black"))
            if hasattr(menu_screen, "draw"):
                menu_screen.draw(screen)

        elif current_state == "PLAYING":
            if IS_MOBILE:
                signals = touch_ctrl.process_events(events, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT) # type: ignore
                if signals and signals.get("shoot"):
                    laser_sound.play()
                if Player is not None:
                    player.update(dt)
            else:
                keys = pygame.key.get_pressed()
                mouse_buttons = pygame.mouse.get_pressed()

                            # EXTRACT X AND Y DIRECTLY TO PREVENT TUPLE SUBTRACTION CRASHES:
                mx, my = pygame.mouse.get_pos()

                is_shooting = any(e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE for e in events)
                if is_shooting and player_alive:
                    laser_sound.play()

                pc_joy_center = (120, constants.SCREEN_HEIGHT - 140)

                            # USE INDIVIDUAL EXTRACTED INTEGRAL METRICS:
                dx = float(mx - pc_joy_center[0])
                dy = float(my - pc_joy_center[1])
                distance = math.hypot(dx, dy)
                is_pc_joystick_engaged = mouse_buttons[0] and distance < 120

                signals = {
                    "thrust": keys[pygame.K_w] or keys[pygame.K_UP],
                    "shoot": is_shooting,
                    "is_joystick_alive": is_pc_joystick_engaged,
                    "rotation_offset": math.atan2(dx, dy) if is_pc_joystick_engaged else 0.0,
                    "rotate_left": keys[pygame.K_a] or keys[pygame.K_LEFT],
                    "rotate_right": keys[pygame.K_a] or keys[pygame.K_RIGHT]
                }

                control_mode = "MOBILE" if is_pc_joystick_engaged else "PC"
                player.update(dt, signals, control_mode=control_mode)


        updatable.update(dt)

        for asteroid in asteroids:
            if player_alive and asteroid.collides_with(player):
                explosion_sound.play()
                lives -= 1
                log_event("player_hit")
                if lives == 0:
                    print("Game over!")
                    sys.exit()
                else:
                    player.kill()
                    player_alive = False
                    respawn_timer = 5.0
            for shot in shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    asteroid_sound.play()
                    score += asteroid.score(ASTEROID_MIN_RADIUS)
                    asteroid.split()
                    shot.kill()
        if not player_alive and current_state == "PLAYING":
            respawn_timer -= dt
            if respawn_timer <= 0:
            # RECREATE THE INSTANCE OBJECT DIRECTLY:
            # This automatically populates updatable and drawable containers via Pygame
                player = Player(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2) # type: ignore
                player.physics.position = pygame.Vector2(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2)
                player.physics.velocity = pygame.Vector2(0, 0)

                player_alive = True
        screen.fill("black")

        score_surface = font.render(f"Score: {score}", True, "white")
        screen.blit(score_surface, (10, 10))
        lives_surface = font.render(f"Lives: {lives}", True, "white")
        screen.blit(lives_surface, (10, 60))

        for obj in drawable:
            obj.draw(screen)

        if IS_MOBILE:
            touch_ctrl.draw_overlay(screen, constants.SCREEN_HEIGHT)

        elif current_state == "LEADERBOARD":
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = "MAIN_MENU"
                elif IS_MOBILE and event.type == pygame.FINGERDOWN:
                    current_state = "MAIN_MENU"
            screen.fill("black")
            over_surface = font.reader("GAME OVER - Tap screen or press ESC to exit", True, "red")
            screen.blit(over_surface, (constants.SCREEN_WIDTH // 2 - 180, constants.SCREEN_HEIGHT // 2))
        pygame.display.flip()
        dt = clock.tick(60) / 1000
        print(dt)
    print(f"Starting Asteroids with pygame version {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}")

if __name__ == "__main__":
    main()
