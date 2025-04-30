import pygame

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (34, 177, 76)
YELLOW = (255, 255, 0)
MUTED_GREEN = (100, 140, 100)  # New muted green color
MUTED_YELLOW = (204, 153, 51)  # New muted yellow-orange color
LIGHT_GREY = (180, 180, 180)  # New light grey color for insufficient funds

# Game settings
TILE_SIZE = 40
TOWER_SIZE = TILE_SIZE * 2.25  # Increased from 1.5 to 2.25 (1.5x bigger than before)
ROAD_WIDTH = int(TILE_SIZE * 1.5)  # Converted to integer
MAX_LIVES = 20

# Enemy settings
ENEMY_SPEED = 2
ENEMY_SIZE = 50  # Increased from 30 to 60 (2x bigger)
ENEMY_HP = 100

# Tower settings
TOWER_COST = 100
TOWER_RADIUS = 150
TOWER_DAMAGE = 20
TOWER_COOLDOWN = 1000  # milliseconds
TOWER_MIN_DISTANCE = TOWER_SIZE * 1.2  # Minimum distance between towers
TOWER_MAX_LEVEL = 4
TOWER_UPGRADE_MULTIPLIER = 1.5  # Cost and damage multiplier per level
TOWER_SPEED_MULTIPLIER = 1.25   # Speed multiplier per level
TOWER_RADIUS_MULTIPLIER = 1.1   # Radius multiplier per level (10% increase)

# Mage tower settings
MAGE_TOWER_COST = 125
MAGE_TOWER_RADIUS = int(TOWER_RADIUS * 0.75)
MAGE_TOWER_DAMAGE = int(TOWER_DAMAGE * 2.5)
MAGE_TOWER_COOLDOWN = int(TOWER_COOLDOWN / 0.5)  # 0.5 means twice as fast

# Catapult tower settings
CATAPULT_TOWER_COST = 150
CATAPULT_TOWER_RADIUS = int(TOWER_RADIUS * 1.5)  # 1.5x regular tower radius
CATAPULT_TOWER_DAMAGE = int(TOWER_DAMAGE * 1.75)  # 1.75x regular tower damage
CATAPULT_TOWER_COOLDOWN = int(TOWER_COOLDOWN * 2)  # Half speed of regular tower
CATAPULT_SPLASH_RADIUS = 75  # Radius of the explosion effect
CATAPULT_SPLASH_DURATION = 2000  # Duration of splash effect in milliseconds

# Wave settings
WAVES = [
    {"count": 10, "interval": 2000},  # Wave 1: Same as before
    {"count": 15, "interval": 1800},  # Wave 2: Increased from 10 to 15
    {"count": 20, "interval": 1600, "group_size": 3},  # Wave 3: Increased count, spawns in groups of 3
    {"count": 25, "interval": 1400, "group_size": 4},  # Wave 4: Increased count, spawns in groups of 4
    {"count": 30, "interval": 1200, "group_size": 5}   # Wave 5: Increased count, spawns in groups of 5
]