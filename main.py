# main.py
import sys
import pygame
import json
import random
import math
import os
from enum import Enum

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TILE_SIZE = 32
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Add new difficulty settings
EASY_DISTANCE = 1000  # Original distance
MEDIUM_DISTANCE = 2500  # New medium level
HARD_DISTANCE = 4000  # New hard level
EXPERT_DISTANCE = 6000  # New expert level
MASTER_DISTANCE = 8500  # New master level

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    LEVEL_COMPLETE = 5

class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4

class Sprite:
    def __init__(self, image_path, scale=1):
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, 
            (self.original_image.get_width() * scale,
             self.original_image.get_height() * scale))
        self.rect = self.image.get_rect()

    def draw(self, surface, x, y):
        self.rect.x = x
        self.rect.y = y
        surface.blit(self.image, self.rect)

class AnimatedSprite(Sprite):
    def __init__(self, sprite_sheet_path, frame_width, frame_height, scale=1):
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames = self.split_sprite_sheet()
        self.current_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        self.scale = scale
        
        # Scale frames
        for i in range(len(self.frames)):
            self.frames[i] = pygame.transform.scale(self.frames[i],
                (frame_width * scale, frame_height * scale))
        
        self.image = self.frames[0]
        self.rect = self.image.get_rect()

    def split_sprite_sheet(self):
        frames = []
        sheet_width = self.sprite_sheet.get_width()
        sheet_height = self.sprite_sheet.get_height()
        
        for y in range(0, sheet_height, self.frame_height):
            for x in range(0, sheet_width, self.frame_width):
                frame = self.sprite_sheet.subsurface((x, y, self.frame_width, self.frame_height))
                frames.append(frame)
        return frames

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def draw(self, surface, x, y):
        self.rect.x = x
        self.rect.y = y
        surface.blit(self.image, self.rect)

class Player:
    def __init__(self, x, y):
        self.sprite = AnimatedSprite("assets/player_sprite.png", 32, 32, 1.5)
        self.x = x
        self.y = y
        self.width = self.sprite.frame_width * self.sprite.scale
        self.height = self.sprite.frame_height * self.sprite.scale
        self.speed = 300
        self.oxygen = 100
        self.energy = 100
        self.direction = Direction.RIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.items = []

    def move(self, dx, dy, dt, walls):
        new_x = self.x + dx * self.speed * dt
        new_y = self.y + dy * self.speed * dt
        
        # Create temporary rectangles for collision testing
        temp_rect_x = pygame.Rect(new_x, self.y, self.width, self.height)
        temp_rect_y = pygame.Rect(self.x, new_y, self.width, self.height)
        
        # Check horizontal movement
        can_move_x = True
        for wall in walls:
            if temp_rect_x.colliderect(wall.rect):
                can_move_x = False
                break
        
        # Check vertical movement
        can_move_y = True
        for wall in walls:
            if temp_rect_y.colliderect(wall.rect):
                can_move_y = False
                break
        
        # Update position if movement is valid
        if can_move_x:
            self.x = new_x
        if can_move_y:
            self.y = new_y
            
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Update sprite direction
        if dx > 0:
            self.direction = Direction.RIGHT
        elif dx < 0:
            self.direction = Direction.LEFT

    def update(self, dt):
        self.oxygen -= 5 * dt
        if self.oxygen < 0:
            self.oxygen = 0
        self.sprite.update(dt)

    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Flip sprite based on direction
        if self.direction == Direction.LEFT:
            flipped_image = pygame.transform.flip(self.sprite.image, True, False)
            surface.blit(flipped_image, (screen_x, screen_y))
        else:
            self.sprite.draw(surface, screen_x, screen_y)

class Voidwalker:
    def __init__(self, x, y):
        self.sprite = AnimatedSprite("assets/voidwalker_sprite.png", 32, 32, 1.5)
        self.x = x
        self.y = y
        self.width = self.sprite.frame_width * self.sprite.scale
        self.height = self.sprite.frame_height * self.sprite.scale
        self.speed = 60
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.direction = Direction.RIGHT
        self.patrol_point_a = x
        self.patrol_point_b = x + 200
        self.moving_right = True
        self.detection_range = 200
        self.chase_mode = False
        self.original_speed = self.speed
        self.attack_cooldown = 0
        self.can_teleport = True
        self.teleport_cooldown = 0

    def patrol(self, dt):
        if self.moving_right:
            if self.x < self.patrol_point_b:
                self.x += self.speed * dt
                self.direction = Direction.RIGHT
            else:
                self.moving_right = False
        else:
            if self.x > self.patrol_point_a:
                self.x -= self.speed * dt
                self.direction = Direction.LEFT
            else:
                self.moving_right = True

    def chase_player(self, player, dt, walls):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance != 0:
            dx = dx / distance
            dy = dy / distance
            
            # Test movement for collision
            new_x = self.x + dx * self.speed * dt
            new_y = self.y + dy * self.speed * dt
            
            temp_rect_x = pygame.Rect(new_x, self.y, self.width, self.height)
            temp_rect_y = pygame.Rect(self.x, new_y, self.width, self.height)
            
            can_move_x = True
            can_move_y = True
            
            for wall in walls:
                if temp_rect_x.colliderect(wall.rect):
                    can_move_x = False
                if temp_rect_y.colliderect(wall.rect):
                    can_move_y = False
            
            if can_move_x:
                self.x = new_x
            if can_move_y:
                self.y = new_y
                
            if dx > 0:
                self.direction = Direction.RIGHT
            elif dx < 0:
                self.direction = Direction.LEFT

    def special_attack(self, player):
        if self.attack_cooldown <= 0:
            # Implement special attacks
            self.attack_cooldown = 3.0  # Cooldown in seconds

    def update(self, player, dt, walls):
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Check if player is in detection range
        if distance <= self.detection_range:
            self.chase_mode = True
            self.speed = self.original_speed * 1.5
            self.chase_player(player, dt, walls)
        else:
            self.chase_mode = False
            self.speed = self.original_speed
            self.patrol(dt)
            
        self.rect.x = self.x
        self.rect.y = self.y
        self.sprite.update(dt)

    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if self.direction == Direction.LEFT:
            flipped_image = pygame.transform.flip(self.sprite.image, True, False)
            surface.blit(flipped_image, (screen_x, screen_y))
        else:
            self.sprite.draw(surface, screen_x, screen_y)

class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (128, 128, 128)  # Gray color for walls
        self.border_color = (200, 200, 200)  # Light gray for border
        # Remove sprite loading since we'll use rectangles for now
        self.has_sprite = False

    def draw(self, surface, camera_x, camera_y):
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Draw the main wall rectangle
        pygame.draw.rect(surface, self.color, 
                        (screen_x, screen_y, self.rect.width, self.rect.height))
        # Draw border for better visibility
        pygame.draw.rect(surface, self.border_color, 
                        (screen_x, screen_y, self.rect.width, self.rect.height), 2)

class OxygenStation:
    def __init__(self, x, y):
        self.sprite = Sprite("assets/oxygen_station_sprite.png")
        self.x = x
        self.y = y
        self.width = self.sprite.rect.width
        self.height = self.sprite.rect.height
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        self.sprite.draw(surface, screen_x, screen_y)

class Level:
    def __init__(self, level_data):
        self.walls = []
        self.oxygen_stations = []
        self.voidwalkers = []
        self.width = level_data["width"] * TILE_SIZE
        self.height = level_data["height"] * TILE_SIZE
        
        # Create level objects from data
        for wall in level_data["walls"]:
            # Convert tile coordinates and dimensions to pixels
            x = wall["x"] * TILE_SIZE
            y = wall["y"] * TILE_SIZE
            width = wall["width"] * TILE_SIZE
            height = wall["height"] * TILE_SIZE
            self.walls.append(Wall(x, y, width, height))
        
        for station in level_data["oxygen_stations"]:
            self.oxygen_stations.append(OxygenStation(station["x"] * TILE_SIZE,
                                                    station["y"] * TILE_SIZE))
        
        for voidwalker in level_data["voidwalkers"]:
            self.voidwalkers.append(Voidwalker(voidwalker["x"] * TILE_SIZE,
                                             voidwalker["y"] * TILE_SIZE))
        
        self.player_start = (level_data["player_start"]["x"] * TILE_SIZE,
                           level_data["player_start"]["y"] * TILE_SIZE)
        
        self.exit_rect = pygame.Rect(level_data["exit"]["x"] * TILE_SIZE,
                                   level_data["exit"]["y"] * TILE_SIZE,
                                   TILE_SIZE, TILE_SIZE)

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def update(self, target_x, target_y, level_width, level_height):
        # Center the camera on the target
        self.x = target_x - WINDOW_WIDTH // 2
        self.y = target_y - WINDOW_HEIGHT // 2
        
        # Keep the camera within the level bounds
        self.x = max(0, min(self.x, level_width - WINDOW_WIDTH))
        self.y = max(0, min(self.y, level_height - WINDOW_HEIGHT))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Eclipse Protocol: Lost in the Void")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.state = GameState.MENU
        self.current_level = 1
        self.victory = False
        self.level_timer = 0
        self.score = 0
        self.game_speed = 1
        self.current_distance = EASY_DISTANCE
        self.death_cause = None
        
        # Load levels
        with open("assets/levels.json", "r") as f:
            self.level_data = json.load(f)
        
        # Load sounds
        pygame.mixer.music.load("assets/background_music.mp3")
        self.collect_sound = pygame.mixer.Sound("assets/collect.wav")
        self.damage_sound = pygame.mixer.Sound("assets/damage.wav")
        
        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.reset_level()

    def reset_level(self):
        level_info = self.level_data["levels"][self.current_level]
        self.level = Level(level_info)
        self.player = Player(*self.level.player_start)
        pygame.mixer.music.play(-1)

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        self.player.move(dx, dy, dt, self.level.walls)

    def update(self, dt):
        if self.state == GameState.PLAYING:
            self.player.update(dt)
            
            # Update camera
            self.camera.update(self.player.x, self.player.y,
                             self.level.width, self.level.height)
            
            # Update voidwalkers
            for voidwalker in self.level.voidwalkers:
                voidwalker.update(self.player, dt, self.level.walls)
                if self.player.rect.colliderect(voidwalker.rect):
                    self.damage_sound.play()
                    self.state = GameState.GAME_OVER
                    self.death_cause = "voidwalker"
            
            # Check oxygen stations
            for station in self.level.oxygen_stations:
                if self.player.rect.colliderect(station.rect):
                    self.player.oxygen = min(100, self.player.oxygen + 30 * dt)
                    self.collect_sound.play()
            
            # Check level exit
            if self.player.rect.colliderect(self.level.exit_rect):
                if self.current_level < len(self.level_data["levels"]) - 1:
                    self.state = GameState.LEVEL_COMPLETE
                    self.current_level += 1
                else:
                    self.state = GameState.GAME_OVER
                    self.victory = True
            
            # Check game over conditions
            if self.player.oxygen <= 0:
                self.state = GameState.GAME_OVER
                self.death_cause = "oxygen"

    def draw_hud(self):
        # Draw oxygen bar
        pygame.draw.rect(self.screen, BLACK, (10, 10, 204, 24))
        pygame.draw.rect(self.screen, BLUE, (12, 12, self.player.oxygen * 2, 20))
        oxygen_text = self.font.render(f"Oxygen: {int(self.player.oxygen)}%", True, WHITE)
        self.screen.blit(oxygen_text, (220, 12))
        
        # Draw level indicator
        level_text = self.font.render(f"Level: {self.current_level}", True, WHITE)
        self.screen.blit(level_text, (WINDOW_WIDTH - 120, 12))

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == GameState.MENU:
            # Draw menu
            title = self.font.render("Eclipse Protocol: Lost in the Void", True, WHITE)
            start_text = self.font.render("Press SPACE to Start", True, WHITE)
            controls_text = self.font.render("WASD to move", True, WHITE)
            
            self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//3))
            self.screen.blit(start_text, (WINDOW_WIDTH//2 - start_text.get_width()//2, WINDOW_HEIGHT//2))
            self.screen.blit(controls_text, (WINDOW_WIDTH//2 - controls_text.get_width()//2, WINDOW_HEIGHT//2 + 50))
        
        elif self.state == GameState.PLAYING:
            # Draw level
            for wall in self.level.walls:
                wall.draw(self.screen, self.camera.x, self.camera.y)
            
            for station in self.level.oxygen_stations:
                station.draw(self.screen, self.camera.x, self.camera.y)
            
            # Draw exit
            exit_screen_x = self.level.exit_rect.x - self.camera.x
            exit_screen_y = self.level.exit_rect.y - self.camera.y
            pygame.draw.rect(self.screen, GREEN, (exit_screen_x, exit_screen_y, TILE_SIZE, TILE_SIZE))
            
            # Draw voidwalkers
            for voidwalker in self.level.voidwalkers:
                voidwalker.draw(self.screen, self.camera.x, self.camera.y)
            
            # Draw player
            self.player.draw(self.screen, self.camera.x, self.camera.y)
            
            # Draw HUD
            self.draw_hud()
        
        elif self.state == GameState.GAME_OVER:
            if self.victory:
                victory_text = self.font.render("Congratulations! You Reached Your Home!", True, WHITE)
                restart_text = self.font.render("Press R to Play Again", True, WHITE)
                
                self.screen.blit(victory_text, 
                               (WINDOW_WIDTH//2 - victory_text.get_width()//2, WINDOW_HEIGHT//3))
                self.screen.blit(restart_text, 
                               (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2))
            else:
                # Different messages based on death type
                if self.death_cause == "oxygen":
                    death_messages = [
                        "Oops! Forgot to breathe?"
                    ]
                elif self.death_cause == "voidwalker":
                    death_messages = [
                        "Voidwalker just wanted a hug!"
                    ]
                
                # Pick a random message
                game_over_text = self.font.render(random.choice(death_messages), True, WHITE)
                restart_text = self.font.render("Press R to Restart", True, WHITE)
                
                self.screen.blit(game_over_text, 
                               (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//3))
                self.screen.blit(restart_text, 
                               (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2))
        
        elif self.state == GameState.LEVEL_COMPLETE:
            complete_text = self.font.render("Level Complete!", True, WHITE)
            next_text = self.font.render("Press SPACE for Next Level", True, WHITE)
            
            self.screen.blit(complete_text, 
                           (WINDOW_WIDTH//2 - complete_text.get_width()//2, WINDOW_HEIGHT//3))
            self.screen.blit(next_text, 
                           (WINDOW_WIDTH//2 - next_text.get_width()//2, WINDOW_HEIGHT//2))

        pygame.display.flip()

    def reset_game(self):
        self.score = 0
        self.game_speed = 1
        self.current_distance = EASY_DISTANCE
        self.current_level = 1
        self.state = GameState.PLAYING
        self.victory = False
        self.death_cause = None
        self.reset_level()

    def run(self):
        last_time = pygame.time.get_ticks()
        
        running = True
        
        while running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.state == GameState.MENU:
                            self.state = GameState.PLAYING
                        elif self.state == GameState.LEVEL_COMPLETE:
                            self.reset_level()
                            self.state = GameState.PLAYING
                    elif event.key == pygame.K_r and self.state == GameState.GAME_OVER:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        if self.state == GameState.PLAYING:
                            self.state = GameState.PAUSED
                        elif self.state == GameState.PAUSED:
                            self.state = GameState.PLAYING

            if self.state == GameState.PLAYING:
                self.handle_input(dt)
                self.update(dt)
            
                # Update distance based on level
                if self.score >= self.current_distance:
                    self.current_level += 1
                    if self.current_level == 2:
                        self.current_distance = MEDIUM_DISTANCE
                        self.game_speed = 2.5
                    elif self.current_level == 3:
                        self.current_distance = HARD_DISTANCE
                        self.game_speed = 4
                    elif self.current_level == 4:
                        self.current_distance = EXPERT_DISTANCE
                        self.game_speed = 5.5
                    elif self.current_level == 5:
                        self.current_distance = MASTER_DISTANCE
                        self.game_speed = 7
                    elif self.current_level > 5:
                        self.victory = True
                        self.state = GameState.GAME_OVER
                    
                    print(f"Level {self.current_level} reached! Speed: {self.game_speed}x")
            
            # Display level and progress
            level_text = self.font.render(f"Level: {self.current_level}", True, WHITE)
            progress_text = self.font.render(f"Progress: {self.score}/{self.current_distance}", True, WHITE)
            self.screen.blit(level_text, (10, 40))
            self.screen.blit(progress_text, (10, 70))
            
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()