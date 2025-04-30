import pygame
import random
from constants import *
from sprites import Enemy, Tower, Button
import math

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tower Defense")
        self.clock = pygame.time.Clock()
        self.placing_tower = False
        self.selected_tower = None
        self.gold = 300
        self.paused = False
        self.last_spawn_time = pygame.time.get_ticks()
        # Load images
        self.tower_preview = pygame.image.load('assets/tower.png').convert_alpha()
        self.tower_preview = pygame.transform.scale(self.tower_preview, (int(TOWER_SIZE), int(TOWER_SIZE)))
        self.mage_preview = pygame.image.load('assets/mage-tower.png').convert_alpha()
        self.mage_preview = pygame.transform.scale(self.mage_preview, (int(TOWER_SIZE), int(TOWER_SIZE)))
        self.catapult_preview = pygame.image.load('assets/catapult.png').convert_alpha()
        self.catapult_preview = pygame.transform.scale(self.catapult_preview, (int(TOWER_SIZE), int(TOWER_SIZE)))
        self.menu_bg = pygame.image.load('assets/menu.png').convert()
        self.menu_bg = pygame.transform.scale(self.menu_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.paths = []  # Store multiple paths
        self.current_path = 0  # Track which path to use for new enemies
        self.reset()

    def reset(self):
        self.running = True
        self.state = "menu"
        self.lives = MAX_LIVES
        self.current_wave = 0
        self.wave_started = False
        self.last_spawn = 0
        self.enemies_spawned = 0
        self.last_spawn_time = pygame.time.get_ticks()  # Reset last_spawn_time
        self.generate_map()
        self.setup_sprites()
        self.selected_tower = None
        self.gold = 300
        self.placing_tower = False
        self.paused = False
        self.current_path = 0

    def generate_control_points(self):
        paths = []
        center_x = WINDOW_WIDTH // 2 
        center_y = WINDOW_HEIGHT // 2
        
        # Add some randomness to the center point
        center_offset_x = random.randint(-50, 50)
        center_offset_y = random.randint(-50, 50)
        center_point = (center_x + center_offset_x, center_y + center_offset_y)
        
        # Add randomness to the end point
        end_x = WINDOW_WIDTH
        end_y = center_y - random.randint(150, 250)  # Random final height
        end_point = (end_x, end_y)
        
        # Random curve control point
        curve_x = center_x - random.randint(150, 250)  # Random left curve
        curve_y = center_y - random.randint(50, 150)  # Random height for curve
        curve_point = (curve_x, curve_y)
        
        # Left to right path through center with left curve
        left_path = [
            (0, WINDOW_HEIGHT // 2 + random.randint(-50, 50)),  # Randomize start height
            (center_x - random.randint(80, 120), center_y + random.randint(-30, 30)),  # Random approach
            center_point,  # Center point
            curve_point,  # Curve point to the left
            end_point  # End point
        ]
        
        # Top to center path with left curve
        top_path = [
            (center_x + random.randint(-50, 50), 0),  # Randomize start position
            (center_x + random.randint(-30, 30), center_y - random.randint(80, 120)),  # Random approach
            center_point,  # Center point
            curve_point,  # Curve point to the left
            end_point  # End point
        ]
        
        # Bottom to center path with left curve
        bottom_path = [
            (center_x + random.randint(-50, 50), WINDOW_HEIGHT),  # Randomize start position
            (center_x + random.randint(-30, 30), center_y + random.randint(80, 120)),  # Random approach
            center_point,  # Center point
            curve_point,  # Curve point to the left
            end_point  # End point
        ]
        
        return [left_path, top_path, bottom_path]

    def calculate_bezier_point(self, points, t):
        n = len(points) - 1
        x = 0
        y = 0
        
        for i in range(n + 1):
            # Calculate binomial coefficient
            coefficient = 1
            for j in range(i):
                coefficient *= (n - j)
                coefficient //= (j + 1)
            
            # Calculate Bernstein polynomial
            term = coefficient * (t ** i) * ((1 - t) ** (n - i))
            x += points[i][0] * term
            y += points[i][1] * term
        
        return (int(x), int(y))

    def generate_map(self):
        control_points = self.generate_control_points()
        self.paths = []
        
        # Generate bezier curves for each path
        for control_path in control_points:
            path_points = []
            num_points = WINDOW_WIDTH // TILE_SIZE
            
            for i in range(num_points + 1):
                t = i / num_points
                point = self.calculate_bezier_point(control_path, t)
                path_points.append(point)
            
            self.paths.append(path_points)

    def setup_sprites(self):
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.selected_tower_type = "archer"  # Track which tower type is selected
        
        # Create menu buttons
        button_width = 200
        button_height = 50
        start_x = WINDOW_WIDTH // 2 - button_width // 2
        
        self.start_button = Button(start_x, 200, button_width, button_height, "Start Game", GREEN)
        self.exit_button = Button(start_x, 300, button_width, button_height, "Exit", RED)
        
        # Create game buttons with improved visibility
        tower_button_size = 100
        
        # Archer tower button
        self.archer_button = Button(20, WINDOW_HEIGHT - tower_button_size - 20, 
                                  tower_button_size, tower_button_size + 30, 
                                  f"${TOWER_COST}", GREEN)
        self.archer_button.setup_tower_button(self.tower_preview, tower_button_size - 20)
        
        # Mage tower button
        self.mage_preview = pygame.image.load('assets/mage-tower.png').convert_alpha()
        self.mage_preview = pygame.transform.scale(self.mage_preview, (int(TOWER_SIZE), int(TOWER_SIZE)))
        self.mage_button = Button(20 + tower_button_size + 20, WINDOW_HEIGHT - tower_button_size - 20,
                                tower_button_size, tower_button_size + 30,
                                f"${MAGE_TOWER_COST}", GREEN)
        self.mage_button.setup_tower_button(self.mage_preview, tower_button_size - 20)
        
        # Catapult tower button
        self.catapult_button = Button(20 + (tower_button_size + 20) * 2, WINDOW_HEIGHT - tower_button_size - 20,
                                    tower_button_size, tower_button_size + 30,
                                    f"${CATAPULT_TOWER_COST}", GREEN)
        self.catapult_button.setup_tower_button(self.catapult_preview, tower_button_size - 20)

        # Create pause button
        pause_button_size = 60
        self.pause_button = Button(WINDOW_WIDTH - pause_button_size - 20, 
                                 WINDOW_HEIGHT - pause_button_size - 20,
                                 pause_button_size, pause_button_size, "", WHITE)
        self.pause_button.setup_pause_button()
        
        # Create pause menu buttons
        self.continue_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 30,
                                    200, 50, "Continue", GREEN)
        self.menu_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 30,
                                200, 50, "Main Menu", RED)
        
        self.start_wave_button = Button(20, 20, 160, 60, "Start Wave", GREEN)

    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()
        if self.current_wave < len(WAVES):
            wave = WAVES[self.current_wave]
            if self.enemies_spawned < wave["count"]:
                if current_time - self.last_spawn_time >= wave["interval"]:
                    group_size = wave.get("group_size", 1)  # Get group size, default to 1
                    for _ in range(group_size):
                        if self.enemies_spawned < wave["count"]:
                            # Rotate through available paths
                            enemy = Enemy(self.paths[self.current_path])
                            self.enemies.add(enemy)
                            self.enemies_spawned += 1
                            # Move to next path for next enemy
                            self.current_path = (self.current_path + 1) % len(self.paths)
                    self.last_spawn_time = current_time
            elif len(self.enemies) == 0:  # Wave completed
                self.current_wave += 1
                self.enemies_spawned = 0
                self.last_spawn_time = current_time

    def handle_menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.rect.collidepoint(event.pos):
                self.state = "game"
            elif self.exit_button.rect.collidepoint(event.pos):
                self.running = False

    def check_tower_proximity(self, x, y):
        """Check if the position is too close to existing towers"""
        for tower in self.towers:
            distance = math.sqrt((tower.rect.centerx - x)**2 + 
                               (tower.rect.centery - y)**2)
            if distance < TOWER_MIN_DISTANCE:
                return False
        return True

    def handle_game_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.paused:
                if self.continue_button.rect.collidepoint(event.pos):
                    self.paused = False
                elif self.menu_button.rect.collidepoint(event.pos):
                    self.state = "menu"
                    self.reset()
                return
            
            if self.pause_button.rect.collidepoint(event.pos):
                self.paused = True
                return
                
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            if self.archer_button.rect.collidepoint(event.pos):
                if self.gold >= TOWER_COST:
                    self.placing_tower = True
                    self.selected_tower_type = "archer"
                    self.selected_tower = None
            elif self.mage_button.rect.collidepoint(event.pos):
                if self.gold >= MAGE_TOWER_COST:
                    self.placing_tower = True
                    self.selected_tower_type = "mage"
                    self.selected_tower = None
            elif self.catapult_button.rect.collidepoint(event.pos):
                if self.gold >= CATAPULT_TOWER_COST:
                    self.placing_tower = True
                    self.selected_tower_type = "catapult"
                    self.selected_tower = None
            elif self.start_wave_button.rect.collidepoint(event.pos) and not self.wave_started:
                self.wave_started = True
                self.enemies_spawned = 0
            elif self.placing_tower:
                # Check if position is valid
                can_build = True
                preview_x = mouse_x - TOWER_SIZE//2
                preview_y = mouse_y - TOWER_SIZE//2
                
                # Check path proximity
                for path in self.paths:
                    for point in path:
                        if (abs(point[0] - mouse_x) < ROAD_WIDTH * 0.8 and
                            abs(point[1] - mouse_y) < ROAD_WIDTH * 0.8):
                            can_build = False
                            break
                
                # Check tower proximity
                if can_build:
                    can_build = self.check_tower_proximity(mouse_x, mouse_y)
                
                if can_build:
                    tower = Tower(preview_x, preview_y, self.selected_tower_type)
                    self.towers.add(tower)
                    if self.selected_tower_type == "archer":
                        cost = TOWER_COST
                    elif self.selected_tower_type == "mage":
                        cost = MAGE_TOWER_COST
                    else:  # catapult
                        cost = CATAPULT_TOWER_COST
                    self.gold -= cost
                self.placing_tower = False
            else:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Check for upgrade or sell button clicks first
                if self.selected_tower:
                    upgrade_rect = self.selected_tower.draw_upgrade_button(self.screen, True)
                    sell_rect = self.selected_tower.draw_sell_button(self.screen, True)
                    
                    if upgrade_rect and upgrade_rect.collidepoint(event.pos):
                        if self.gold >= self.selected_tower.upgrade_cost:
                            self.gold -= self.selected_tower.upgrade_cost
                            self.selected_tower.upgrade()
                        return
                    elif sell_rect and sell_rect.collidepoint(event.pos):
                        self.gold += self.selected_tower.get_sell_value()
                        self.selected_tower.kill()
                        self.selected_tower = None
                        return
                
                # Check if clicked on existing tower
                self.selected_tower = None
                for tower in self.towers:
                    if tower.rect.collidepoint(event.pos):
                        self.selected_tower = tower
                        break

    def update(self):
        if self.state == "game" and not self.paused:
            # Update tower button text based on gold
            self.archer_button.text = f"${TOWER_COST}"
            self.archer_button.text_color = YELLOW if self.gold >= TOWER_COST else LIGHT_GREY
            
            self.mage_button.text = f"${MAGE_TOWER_COST}"
            self.mage_button.text_color = YELLOW if self.gold >= MAGE_TOWER_COST else LIGHT_GREY
            
            self.catapult_button.text = f"${CATAPULT_TOWER_COST}"
            self.catapult_button.text_color = YELLOW if self.gold >= CATAPULT_TOWER_COST else LIGHT_GREY
            
            # Spawn enemies if wave is started
            if self.wave_started:
                self.spawn_enemy()
                
            # Update enemies
            self.enemies.update()
            
            # Check for enemies reaching end
            for enemy in self.enemies:
                if enemy.path_index >= len(enemy.path) - 1:
                    self.lives -= 1
                    enemy.kill()
                    
                if enemy.health <= 0:
                    self.gold += enemy.reward
                    enemy.kill()
            
            # Tower shooting and arrow updates
            for tower in self.towers:
                tower.shoot(self.enemies)
            
            # Check wave completion
            if (self.wave_started and len(self.enemies) == 0 and 
                self.enemies_spawned >= WAVES[self.current_wave]["count"]):
                self.current_wave += 1
                self.wave_started = False
                
            # Check game over conditions
            if self.lives <= 0 or self.current_wave >= len(WAVES):
                self.state = "menu"
                self.reset()

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == "menu":
            # Draw menu background
            self.screen.blit(self.menu_bg, (0, 0))
            self.start_button.draw(self.screen)
            self.exit_button.draw(self.screen)
            
        elif self.state == "game":
            # Draw grass background
            self.screen.fill(MUTED_GREEN)
            
            # Draw paths
            for path in self.paths:
                for i in range(len(path) - 1):
                    start_pos = path[i]
                    end_pos = path[i + 1]
                    pygame.draw.line(self.screen, MUTED_YELLOW, start_pos, end_pos, ROAD_WIDTH)
            
            # Draw spawn point indicators
            for path_index, path in enumerate(self.paths):
                start_x, start_y = path[0]
                next_x, next_y = path[1]  # Second point to determine direction
                
                # Add offset based on spawn location
                if start_x == 0:  # Left spawn
                    start_x += 30
                elif start_y == 0:  # Top spawn
                    start_y += 30
                elif start_y == WINDOW_HEIGHT:  # Bottom spawn
                    start_y -= 30
                
                # Draw white circle outline only
                circle_radius = 15
                pygame.draw.circle(self.screen, (255, 255, 255, 200), (start_x, start_y), circle_radius, 2)
                
                # Calculate arrow direction
                dx = next_x - path[0][0]  # Use original start point for direction
                dy = next_y - path[0][1]
                length = (dx*dx + dy*dy) ** 0.5
                if length > 0:
                    dx, dy = dx/length, dy/length
                
                # Draw arrow with slightly smaller size to fit circle better
                arrow_size = 8
                arrow_thickness = 2
                # Arrow body
                pygame.draw.line(self.screen, (255, 255, 255, 200),
                               (start_x - dx*arrow_size, start_y - dy*arrow_size),
                               (start_x + dx*arrow_size, start_y + dy*arrow_size),
                               arrow_thickness)
                # Arrow head
                head_size = 5
                pygame.draw.line(self.screen, (255, 255, 255, 200),
                               (start_x + dx*arrow_size, start_y + dy*arrow_size),
                               (start_x + dx*arrow_size - dy*head_size - dx*head_size,
                                start_y + dy*arrow_size + dx*head_size - dy*head_size),
                               arrow_thickness)
                pygame.draw.line(self.screen, (255, 255, 255, 200),
                               (start_x + dx*arrow_size, start_y + dy*arrow_size),
                               (start_x + dx*arrow_size + dy*head_size - dx*head_size,
                                start_y + dy*arrow_size - dx*head_size - dy*head_size),
                               arrow_thickness)
            
            # Draw buttons before sprites so they appear under tower preview
            self.archer_button.draw(self.screen)
            self.mage_button.draw(self.screen)
            self.catapult_button.draw(self.screen)
            if not self.wave_started:
                self.start_wave_button.draw(self.screen)
                
            # Draw end point (X in circle)
            end_x, end_y = self.paths[0][-1]
            # Add offset to draw X earlier on the road
            end_x -= 30
            
            # Draw the circle first (keep same size)
            circle_radius = 15
            pygame.draw.circle(self.screen, RED, (end_x, end_y), circle_radius, 3)
            
            # Draw smaller X inside the circle
            size = 7  # Reduced from 10 to make X smaller
            pygame.draw.line(self.screen, RED, 
                           (end_x - size, end_y - size), 
                           (end_x + size, end_y + size), 9)
            pygame.draw.line(self.screen, RED, 
                           (end_x - size, end_y + size), 
                           (end_x + size, end_y - size), 9)
            
            # Draw towers and their levels
            self.towers.draw(self.screen)
            for tower in self.towers:
                if tower != self.selected_tower:  # Only draw level if tower is not selected
                    tower.draw_level(self.screen)
            
            # Draw arrows and their effects
            for tower in self.towers:
                for arrow in tower.arrows:
                    arrow.draw(self.screen)
            
            # Draw selected tower radius and preview
            if self.selected_tower:
                tower_radius = self.selected_tower.radius
                
                # Draw upgraded radius preview first (so it appears below)
                if (self.selected_tower.upgrade_hover and 
                    self.selected_tower.level < TOWER_MAX_LEVEL and 
                    self.selected_tower.tower_type != "catapult"):  # Only show preview for non-catapult towers
                    # Calculate new radius after upgrade using constant
                    preview_radius = int(tower_radius * TOWER_RADIUS_MULTIPLIER)
                    
                    # Draw larger radius with lighter blue underneath
                    preview_surface = pygame.Surface((preview_radius * 2, preview_radius * 2), pygame.SRCALPHA)
                    # Draw filled circle first
                    pygame.draw.circle(preview_surface, (100, 150, 255, 32),
                                    (preview_radius, preview_radius), preview_radius)
                    # Draw outline in dark blue
                    pygame.draw.circle(preview_surface, (0, 0, 180, 128),
                                    (preview_radius, preview_radius), preview_radius, 2)
                    self.screen.blit(preview_surface, 
                                   (self.selected_tower.rect.centerx - preview_radius,
                                    self.selected_tower.rect.centery - preview_radius))
                
                # Draw current radius on top
                radius_color = (0, 0, 255, 64)  # Default blue
                if self.selected_tower.sell_hover:
                    radius_color = (255, 0, 0, 64)  # Red when hovering sell
                
                radius_surface = pygame.Surface((tower_radius * 2, tower_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(radius_surface, radius_color, 
                                (tower_radius, tower_radius), tower_radius)
                self.screen.blit(radius_surface, 
                               (self.selected_tower.rect.centerx - tower_radius,
                                self.selected_tower.rect.centery - tower_radius))
                
                # Draw upgrade and sell buttons after radius
                self.selected_tower.draw_upgrade_button(self.screen, True, self.gold)
                self.selected_tower.draw_sell_button(self.screen, True)
                
            # Draw tower preview when placing
            if self.placing_tower:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                preview_x = mouse_x - TOWER_SIZE//2
                preview_y = mouse_y - TOWER_SIZE//2
                
                # Check if position is valid
                can_build = True
                for path in self.paths:
                    for point in path:
                        if (abs(point[0] - mouse_x) < ROAD_WIDTH * 0.8 and
                            abs(point[1] - mouse_y) < ROAD_WIDTH * 0.8):
                            can_build = False
                            break
                
                # Check tower proximity
                if can_build:
                    can_build = self.check_tower_proximity(mouse_x, mouse_y)
                
                # Draw tower radius (blue if valid, red if invalid)
                if self.selected_tower_type == "archer":
                    preview_radius = TOWER_RADIUS
                elif self.selected_tower_type == "mage":
                    preview_radius = MAGE_TOWER_RADIUS
                else:  # catapult
                    preview_radius = CATAPULT_TOWER_RADIUS
                    
                radius_surface = pygame.Surface((preview_radius * 2, preview_radius * 2), pygame.SRCALPHA)
                radius_color = (0, 0, 255, 64) if can_build else (255, 0, 0, 64)
                pygame.draw.circle(radius_surface, radius_color, 
                                (preview_radius, preview_radius), preview_radius)
                self.screen.blit(radius_surface, 
                               (mouse_x - preview_radius, mouse_y - preview_radius))
                
                # Draw tower preview with semi-transparency
                preview_surface = pygame.Surface((int(TOWER_SIZE), int(TOWER_SIZE)), pygame.SRCALPHA)
                preview_image = self.tower_preview
                if self.selected_tower_type == "mage":
                    preview_image = self.mage_preview
                elif self.selected_tower_type == "catapult":
                    preview_image = self.catapult_preview
                preview_surface.blit(preview_image, (0, 0))
                preview_surface.set_alpha(128)
                self.screen.blit(preview_surface, (preview_x, preview_y))
            
            # Draw enemies and health bars on top of everything except UI
            self.enemies.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw_health(self.screen)
            
            # Draw pause button
            self.pause_button.draw(self.screen)
            
            if self.paused:
                # Draw semi-transparent overlay
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
                self.screen.blit(overlay, (0, 0))
                
                # Draw pause menu
                self.continue_button.draw(self.screen)
                self.menu_button.draw(self.screen)
            
            # Draw stats
            font = pygame.font.Font(None, 36)
            lives_text = font.render(f"Lives: {self.lives}", True, WHITE)
            wave_text = font.render(f"Wave: {self.current_wave + 1}/5", True, WHITE)
            gold_text = font.render(f"Gold: ${self.gold}", True, WHITE)
            self.screen.blit(lives_text, (WINDOW_WIDTH - 150, 10))
            self.screen.blit(wave_text, (WINDOW_WIDTH - 150, 50))
            self.screen.blit(gold_text, (WINDOW_WIDTH - 150, 90))
        
        pygame.display.flip()