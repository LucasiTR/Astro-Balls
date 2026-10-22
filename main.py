from textwrap import fill

import pygame
import sys
import os
from asteroid import Asteroid
from asteroidfield import AsteroidField
from player import Player
from constants import ASTEROID_MIN_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT
from logger import log_state, log_event
from shot import Shot
from main_menu import MainMenu

def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.font.init()
    pygame.mixer.init()
    font = pygame.font.Font(None, 26)
    laser_sound = pygame.mixer.Sound("assets/sounds/Laser.wav")
    explosion_sound = pygame.mixer.Sound("assets/sounds/Ship.wav")
    asteroid_sound = pygame.mixer.Sound("assets/sounds/Asteroid.wav")

    updatable = pygame.sprite.Group()
    drawable =  pygame.sprite.Group()
    Player.containers = (updatable, drawable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    shots = pygame.sprite.Group()
    Shot.containers = (shots, updatable, drawable)
    asteroids =  pygame.sprite.Group()
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable)
    AsteroidField()
    score = 0
    lives = 3
    respawn_timer = 0.0
    player_alive = True
    dt = 0.0
    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
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
        if not player_alive:
            respawn_timer -= dt
            if respawn_timer <= 0:
                player.respawn(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                player.add(updatable, drawable)
                player_alive = True
        screen.fill("black")
        score_surface = font.render(f"Score: {score}", True, "white")
        screen.blit(score_surface, (10, 10))
        lives_surface = font.render(f"Lives: {lives}", True, "white")
        screen.blit(lives_surface, (10, 60))
        for obj in drawable:
            obj.draw(screen)
        pygame.display.flip()
        dt = clock.tick(60) / 1000
        print(dt)
    print(f"Starting Asteroids with pygame version {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}")

if __name__ == "__main__":
    main()
