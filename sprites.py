import pygame
import math
from constants import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, path):
        super().__init__()
        self.image = pygame.image.load('assets/goblin.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (ENEMY_SIZE, ENEMY_SIZE))
        self.rect = self.image.get_rect()
        self.path = path
        self.path_index = 0
        self.rect.centerx = path[0][0]
        self.rect.centery = path[0][1]
        self.health = ENEMY_HP
        self.max_health = ENEMY_HP
        self.pos = pygame.math.Vector2(self.rect.center)
        self.reward = 20  # Gold reward for killing this enemy
        
    def update(self):
        if self.path_index < len(self.path) - 1:
            target = pygame.math.Vector2(self.path[self.path_index + 1])
            movement = target - self.pos
            if movement.length() <= ENEMY_SPEED:
                self.pos = target
                self.path_index += 1
            else:
                movement.scale_to_length(ENEMY_SPEED)
                self.pos += movement
                
        self.rect.center = self.pos
        
    def draw_health(self, screen):
        health_width = self.rect.width * (self.health / self.max_health)
        health_bar = pygame.Rect(self.rect.x, self.rect.y + self.rect.height + 5, health_width, 5)
        pygame.draw.rect(screen, GREEN, health_bar)

class Arrow(pygame.sprite.Sprite):
    def __init__(self, start_pos, target, damage, projectile_type="arrow", splash_radius_multiplier=1.0):
        super().__init__()
        self.projectile_type = projectile_type
        self.splash_start_time = None
        self.splash_pos = None
        self.splash_current_radius = 0
        self.splash_radius_multiplier = splash_radius_multiplier
        self.enemies_hit = set()  # Track enemies hit by splash
        self.visible = True
        
        if projectile_type == "arrow":
            self.image = pygame.Surface((10, 3), pygame.SRCALPHA)
            pygame.draw.rect(self.image, WHITE, (0, 0, 10, 3))
        elif projectile_type == "fireball":
            size = 18
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 0), (size//2, size//2), size//2)
            pygame.draw.circle(self.image, (255, 140, 0), (size//2, size//2), size//3)
            pygame.draw.circle(self.image, (255, 255, 0), (size//2, size//2), size//4)
        else:  # catapult ball
            size = 18
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, BLACK, (size//2, size//2), size//2)
        
        self.pos = pygame.math.Vector2(start_pos)
        target_pos = pygame.math.Vector2(target.rect.center)
        self.direction = (target_pos - self.pos).normalize()
        
        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(self.image, angle)
        
        self.rect = self.image.get_rect(center=self.pos)
        self.speed = 10 if projectile_type == "arrow" else 8
        self.damage = damage
        self.original_image = self.image  # Store original image for later

    def update(self):
        if self.splash_start_time is None:
            self.pos += self.direction * self.speed
            self.rect.center = self.pos
        else:
            if self.visible:  # Only hide the projectile once
                self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
                self.visible = False
            current_time = pygame.time.get_ticks()
            progress = (current_time - self.splash_start_time) / CATAPULT_SPLASH_DURATION
            if progress >= 1:
                self.kill()
            else:
                self.splash_current_radius = CATAPULT_SPLASH_RADIUS * self.splash_radius_multiplier * progress

    def start_splash_effect(self, pos):
        if self.projectile_type == "catapult":
            self.splash_start_time = pygame.time.get_ticks()
            self.splash_pos = pos
            self.pos = pygame.math.Vector2(pos)
            self.rect.center = pos

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, self.rect)
        if self.splash_start_time is not None:
            # Draw two circles for better visibility - a thicker orange one
            pygame.draw.circle(screen, (255, 140, 0), self.splash_pos, self.splash_current_radius, 3)
            # Draw a thinner, brighter inner circle
            pygame.draw.circle(screen, (255, 200, 0), self.splash_pos, self.splash_current_radius - 1, 1)

class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y, tower_type="archer"):
        super().__init__()
        self.tower_type = tower_type
        
        # Load and scale tower image based on type
        if tower_type == "mage":
            image_name = 'mage-tower.png'
        elif tower_type == "catapult":
            image_name = 'catapult.png'
        else:  # archer
            image_name = 'tower.png'
            
        self.image = pygame.image.load(f'assets/{image_name}').convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(TOWER_SIZE), int(TOWER_SIZE)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.last_shot = pygame.time.get_ticks()
        self.arrows = pygame.sprite.Group()
        
        # Set initial stats based on tower type
        self.level = 1
        if tower_type == "archer":
            self.damage = TOWER_DAMAGE
            self.cooldown = TOWER_COOLDOWN
            self.radius = TOWER_RADIUS
            self.base_cost = TOWER_COST
        elif tower_type == "mage":
            self.damage = MAGE_TOWER_DAMAGE
            self.cooldown = MAGE_TOWER_COOLDOWN
            self.radius = MAGE_TOWER_RADIUS
            self.base_cost = MAGE_TOWER_COST
        else:  # catapult
            self.damage = CATAPULT_TOWER_DAMAGE
            self.cooldown = CATAPULT_TOWER_COOLDOWN
            self.radius = CATAPULT_TOWER_RADIUS
            self.base_cost = CATAPULT_TOWER_COST
            
        self.upgrade_cost = int(self.base_cost * TOWER_UPGRADE_MULTIPLIER)
        self.total_cost = self.base_cost
        self.upgrade_hover = False
        self.sell_hover = False
        
    def can_shoot(self):
        now = pygame.time.get_ticks()
        return now - self.last_shot >= self.cooldown
        
    def upgrade(self):
        if self.level < TOWER_MAX_LEVEL:
            self.level += 1
            self.damage *= TOWER_UPGRADE_MULTIPLIER
            if self.tower_type != "catapult":  # Catapult doesn't get radius upgrades
                self.radius *= TOWER_RADIUS_MULTIPLIER
            if self.tower_type != "catapult":  # Catapult doesn't get speed upgrades
                self.cooldown /= TOWER_SPEED_MULTIPLIER
            self.total_cost += self.upgrade_cost
            self.upgrade_cost = int(self.upgrade_cost * TOWER_UPGRADE_MULTIPLIER)
            return True
        return False
    
    def get_sell_value(self):
        # Return 75% of total investment
        return int(self.total_cost * 0.75)
    
    def draw_level(self, screen):
        # Draw level text below tower
        font = pygame.font.Font(None, 24)
        text = font.render(f"lvl {self.level}", True, WHITE)
        text_rect = text.get_rect(centerx=self.rect.centerx, 
                                top=self.rect.bottom + 5)
        screen.blit(text, text_rect)
    
    def draw_upgrade_button(self, screen, selected=False, player_gold=0):
        if selected and self.level < TOWER_MAX_LEVEL:
            # Draw upgrade button above tower
            circle_radius = 15
            button_center = (self.rect.centerx, self.rect.top - circle_radius - 5)
            
            # Check if player has enough gold
            has_enough_gold = player_gold >= self.upgrade_cost
            
            # Choose color based on affordability
            button_color = GREEN if has_enough_gold else LIGHT_GREY
            cost_color = YELLOW if has_enough_gold else LIGHT_GREY
            
            # Get button rect for hover detection
            button_rect = pygame.Rect(button_center[0] - circle_radius,
                                    button_center[1] - circle_radius,
                                    circle_radius * 2, circle_radius * 2)
            
            # Check hover state
            mouse_pos = pygame.mouse.get_pos()
            self.upgrade_hover = button_rect.collidepoint(mouse_pos)
            
            # Draw circle with arrow
            pygame.draw.circle(screen, button_color, button_center, circle_radius, 2)
            
            # Draw up arrow
            arrow_size = 8
            pygame.draw.line(screen, button_color,
                           (button_center[0], button_center[1] + arrow_size),
                           (button_center[0], button_center[1] - arrow_size), 2)
            pygame.draw.line(screen, button_color,
                           (button_center[0], button_center[1] - arrow_size),
                           (button_center[0] - arrow_size//2, button_center[1] - arrow_size//2), 2)
            pygame.draw.line(screen, button_color,
                           (button_center[0], button_center[1] - arrow_size),
                           (button_center[0] + arrow_size//2, button_center[1] - arrow_size//2), 2)
            
            # Draw upgrade cost
            font = pygame.font.Font(None, 20)
            cost_text = font.render(f"${self.upgrade_cost}", True, cost_color)
            text_rect = cost_text.get_rect(centerx=button_center[0],
                                         bottom=button_center[1] - circle_radius - 5)
            screen.blit(cost_text, text_rect)
            
            return button_rect
        return None
    
    def draw_sell_button(self, screen, selected=False):
        if selected:
            # Draw sell button below tower
            circle_radius = 15
            button_center = (self.rect.centerx, self.rect.bottom + circle_radius + 5)
            
            # Get button rect for hover detection
            button_rect = pygame.Rect(button_center[0] - circle_radius,
                                    button_center[1] - circle_radius,
                                    circle_radius * 2, circle_radius * 2)
            
            # Check hover state
            mouse_pos = pygame.mouse.get_pos()
            self.sell_hover = button_rect.collidepoint(mouse_pos)
            
            # Draw yellow circle outline
            pygame.draw.circle(screen, YELLOW, button_center, circle_radius, 2)
            
            # Draw dollar sign
            font = pygame.font.Font(None, 24)
            dollar_text = font.render("$", True, YELLOW)
            text_rect = dollar_text.get_rect(center=button_center)
            screen.blit(dollar_text, text_rect)
            
            # Draw sell value
            sell_value = self.get_sell_value()
            value_text = font.render(f"+{sell_value}", True, YELLOW)
            value_rect = value_text.get_rect(centerx=button_center[0],
                                         top=button_center[1] + circle_radius + 5)
            screen.blit(value_text, value_rect)
            
            return button_rect
        return None
        
    def shoot(self, enemies):
        targets = []
        for enemy in enemies:
            distance = math.sqrt((enemy.rect.centerx - self.rect.centerx)**2 + 
                               (enemy.rect.centery - self.rect.centery)**2)
            if distance <= self.radius:
                targets.append(enemy)
                
        if targets and self.can_shoot():
            # Create new projectile based on tower type
            projectile_type = "arrow"
            if self.tower_type == "mage":
                projectile_type = "fireball"
            elif self.tower_type == "catapult":
                projectile_type = "catapult"
            
            # Calculate splash radius multiplier for catapult
            splash_radius_multiplier = 1.0
            if self.tower_type == "catapult":
                splash_radius_multiplier = pow(TOWER_RADIUS_MULTIPLIER, self.level - 1)
                
            arrow = Arrow(self.rect.center, targets[0], self.damage, projectile_type, splash_radius_multiplier)
            self.arrows.add(arrow)
            self.last_shot = pygame.time.get_ticks()
        
        # Update existing arrows
        self.arrows.update()
        
        # Check arrow collisions with enemies
        for arrow in self.arrows:
            # For splash damage tracking
            hit_enemies = []
            
            for enemy in enemies:
                if arrow.rect.colliderect(enemy.rect):
                    if arrow.projectile_type == "catapult":
                        if arrow.splash_start_time is None:
                            arrow.start_splash_effect(arrow.rect.center)
                            enemy.health -= arrow.damage  # Direct hit damage
                            hit_enemies.append(enemy)
                    else:
                        enemy.health -= arrow.damage
                        arrow.kill()
                        break
            
            # Apply splash damage to all enemies in range
            if arrow.splash_start_time is not None and arrow.projectile_type == "catapult":
                for enemy in enemies:
                    if enemy not in hit_enemies and enemy not in arrow.enemies_hit:
                        distance = math.sqrt((enemy.rect.centerx - arrow.splash_pos[0])**2 + 
                                          (enemy.rect.centery - arrow.splash_pos[1])**2)
                        if distance <= arrow.splash_current_radius:
                            enemy.health -= arrow.damage
                            arrow.enemies_hit.add(enemy)
                            hit_enemies.append(enemy)
            
            # Remove arrows that have gone off screen
            if (arrow.splash_start_time is None and 
                not pygame.display.get_surface().get_rect().colliderect(arrow.rect)):
                arrow.kill()

class Button:
    def __init__(self, x, y, width, height, text, color):
        super().__init__()
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.text = text
        self.color = color
        self.is_tower_button = False
        self.is_pause_button = False
        self.tower_icon = None
        self.text_color = None  # New property for text color
        
    def setup_tower_button(self, tower_icon, size):
        self.is_tower_button = True
        self.tower_icon = pygame.transform.scale(tower_icon, (size, size))
        
    def setup_pause_button(self):
        self.is_pause_button = True
        
    def draw(self, screen):
        if self.is_pause_button:
            # Clear the surface
            self.image.fill((0, 0, 0, 0))
            
            # Draw white semi-transparent circle
            circle_radius = self.rect.width // 2
            circle_center = (circle_radius, circle_radius)
            
            # Draw white circle with transparency
            pygame.draw.circle(self.image, (255, 255, 255, 128), circle_center, circle_radius)
            pygame.draw.circle(self.image, (255, 255, 255, 255), circle_center, circle_radius, 2)
            
            # Draw pause icon (two rectangles)
            bar_width = circle_radius // 2
            bar_height = circle_radius
            spacing = circle_radius // 3
            
            # Left bar
            pygame.draw.rect(self.image, (255, 255, 255, 255),
                           (circle_radius - spacing - bar_width//2,
                            circle_radius - bar_height//2,
                            bar_width//2, bar_height))
            
            # Right bar
            pygame.draw.rect(self.image, (255, 255, 255, 255),
                           (circle_radius + spacing,
                            circle_radius - bar_height//2,
                            bar_width//2, bar_height))
            
            screen.blit(self.image, self.rect)
            
        elif self.is_tower_button:
            # Clear the surface
            self.image.fill((0, 0, 0, 0))
            
            # Calculate circle center and radius
            circle_radius = self.rect.width // 2 - 5
            circle_center = (self.rect.width // 2, circle_radius + 5)
            
            # Use the text_color if set, otherwise use default colors
            circle_color = GREEN if self.text_color == YELLOW else LIGHT_GREY
            pygame.draw.circle(self.image, circle_color, circle_center, circle_radius, 2)
            
            # Draw tower icon
            if self.tower_icon:
                icon_rect = self.tower_icon.get_rect(center=circle_center)
                self.image.blit(self.tower_icon, icon_rect)
            
            # Draw cost text
            font = pygame.font.Font(None, 30)
            text_color = self.text_color if self.text_color else YELLOW
            cost_text = font.render(self.text, True, text_color)
            text_rect = cost_text.get_rect(centerx=self.rect.width//2, 
                                         top=circle_center[1] + circle_radius + 5)
            self.image.blit(cost_text, text_rect)
            
            # Draw the final surface
            screen.blit(self.image, self.rect)
        else:
            # Regular button drawing
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            font = pygame.font.Font(None, 36)
            text = font.render(self.text, True, BLACK)
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)