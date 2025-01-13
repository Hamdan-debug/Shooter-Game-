import pygame
import os
import random

# Initialize Pygame
pygame.init()

# Screen Setup
win_width, win_height = 800, 400
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("1v1 Shooter Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Load Images
# Ensure Assets folder and Background image are properly set
background = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Background.png")), (win_width, win_height))
bullet_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "bullet.png")), (10,10))

# Platforms
platforms = [(150, 300, 100, 10), (300, 200, 150, 10), (550, 250, 120, 10)]

# Font
font = pygame.font.Font(None, 50)

# Classes
class Player:
    def __init__(self, x, y, color, controls):
        self.reset(x, y, color, controls)

    def reset(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.color = color
        self.controls = controls
        self.velx = 7
        self.vely = 0  # Start with no vertical velocity
        self.gravity = 0.5  # Set gravity strength
        self.jump_strength = -15  # Set jump strength
        self.is_jumping = False
        self.on_platform = False
        self.bullets = []
        self.cool_down_count = 0
        self.health = 100
        self.alive = True
        self.facing_right = True
        self.hitbox = (self.x, self.y, self.width, self.height)

    def move(self, userInput):
        # Horizontal Movement
        if userInput[self.controls['left']] and self.x > 0:
            self.x -= self.velx
            self.facing_right = False
        if userInput[self.controls['right']] and self.x < win_width - self.width:
            self.x += self.velx
            self.facing_right = True

        # Jumping
        if self.on_platform and not self.is_jumping and userInput[self.controls['jump']]:
            self.vely = self.jump_strength  # Set upward velocity
            self.is_jumping = True  
            self.on_platform = False  

    def apply_gravity(self):
        # Apply gravity only if the player is in the air
        if not self.on_platform:
            self.vely += self.gravity  # Increase vertical velocity due to gravity
        self.y += self.vely  
        self.on_platform = False  

        # Check collision with platforms
        for platform in platforms:
            px, py, pw, ph = platform
            # Check for collision with platforms
            if (self.x + self.width > px and self.x < px + pw and 
                self.y + self.height <= py + self.vely and 
                self.y + self.height + self.vely > py):  # Falling onto the platform
                self.y = py - self.height  
                self.on_platform = True  
                self.vely = 0  
                self.is_jumping = False  
                break  

        # Check collision with the ground
        if self.y > win_height - self.height:
            self.y = win_height - self.height
            self.on_platform = True
            self.vely = 0  # Reset vertical velocity
            self.is_jumping = False  

        # Top Boundary
        if self.y < 0:
            self.y = 0

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        self.hitbox = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(win, RED, (self.x, self.y - 15, 100, 10))
        pygame.draw.rect(win, GREEN, (self.x, self.y - 15, self.health, 10))



    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        self.hitbox = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(win, RED, (self.x, self.y - 15, 100, 10))
        pygame.draw.rect(win, GREEN, (self.x, self.y - 15, self.health, 10))

    def cooldown(self):
        if self.cool_down_count >= 10:
            self.cool_down_count = 0
        elif self.cool_down_count > 0:
            self.cool_down_count += 1

    def shoot(self, userInput):
        self.cooldown()
        if userInput[self.controls['shoot']] and self.cool_down_count == 0:
            direction = 1 if self.facing_right else -1
            bullet = Bullet(self.x + self.width // 2, self.y + self.height // 2, direction, self.color)
            self.bullets.append(bullet)
            self.cool_down_count = 1

    def take_damage(self, damage):
        if self.health > 0:
            self.health -= damage
        if self.health <= 0:
            self.alive = False

    def heal(self, amount):
        self.health = min(100, self.health + amount)


class Bullet:
    def __init__(self, x, y, direction, color):
        self.x = x
        self.y = y
        self.vel = 15 * direction
        self.color = color
        self.width = 10
        self.height = 5

    def move(self):
        self.x += self.vel

    def draw(self, win):
        win.blit(bullet_img, (self.x, self.y))

    def off_screen(self):
        return not (0 <= self.x <= win_width)

    def collide(self, player):
        bx, by, bw, bh = self.x, self.y, self.width, self.height
        px, py, pw, ph = player.hitbox
        return bx < px + pw and bx + bw > px and by < py + ph and by + bh > py


class HealthPowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.color = GREEN
        self.active = True

    def draw(self, win):
        if self.active:
            pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

    def collide(self, player):
        if self.active:
            px, py, pw, ph = player.hitbox
            return self.x < px + pw and self.x + self.width > px and self.y < py + ph and self.y + self.height > py
        return False

    def reset_position(self):
        self.x = random.randint(0, win_width - self.width)
        self.y = random.randint(50, win_height - 70)
        self.active = True


# Initialize Players and Power-Up
player1 = Player(100, 300, BLUE, {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'shoot': pygame.K_f})
player2 = Player(600, 300, RED, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'shoot': pygame.K_RSHIFT})
health_power_up = HealthPowerUp(400, 150)

# Main Game Loop
run = True
clock = pygame.time.Clock()

while run:
    clock.tick(30)
    win.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    userInput = pygame.key.get_pressed()

    # Player Actions
    for player in [player1, player2]:
        player.move(userInput)
        player.apply_gravity()
        player.shoot(userInput)
        player.draw(win)

        # Handle bullets
        for bullet in player.bullets[:]:
            bullet.move()
            if bullet.off_screen():
                player.bullets.remove(bullet)
            else:
                bullet.draw(win)

            # Collision Detection
            opponent = player1 if player == player2 else player2
            if bullet.collide(opponent):
                opponent.take_damage(5)
                player.bullets.remove(bullet)

    # Draw Platforms
    for platform in platforms:
        pygame.draw.rect(win, WHITE, platform)

    # Health Power-Up Logic
    health_power_up.draw(win)
    for player in [player1, player2]:
        if health_power_up.collide(player):
            player.heal(20)
            health_power_up.active = False
            health_power_up.reset_position()  # Reset position after being collected

    # Check Game Over
    if  player1.alive and not player2.alive:
        win.fill((0, 0, 0))
        text = font.render('Player 1 Won!! Press R to Restart and Q to Quit', True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (win_width // 2, win_height // 2)
        win.blit(text, textRect)
        if userInput[pygame.K_r]:
            player1.reset(100, 300, BLUE, {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'shoot': pygame.K_f})
            player2.reset(600, 300, RED, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'shoot': pygame.K_RSHIFT})
            health_power_up.reset_position()  # Reset position of health power-up
        if userInput[pygame.K_q]:
            run = False

    if player2.alive and not player1.alive:
        win.fill((255,255,255))
        text = font.render('Player 2 Won!! Press R to Restart and Q to Quit', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (win_width // 2, win_height // 2)
        win.blit(text, textRect)
        if userInput[pygame.K_r]:
            player1.reset(100, 300, BLUE, {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'shoot': pygame.K_f})
            player2.reset(600, 300, RED, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'shoot': pygame.K_RSHIFT})
            health_power_up.reset_position()  # Reset position of health power-up
        if userInput[pygame.K_q]:
            run = False


    pygame.display.update()

pygame.quit()