# Tower Defense Game

A Python-based tower defense game where you defend against waves of enemies using different types of towers.

## Features

- Three different tower types: Archer, Mage, and Catapult
- Dynamic path generation for enemy waves
- Multiple enemy waves with increasing difficulty
- Tower upgrading system
- Interactive menu system
- Visual effects for projectiles and splash damage

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Ensure you have Python installed on your system. You can download it from [python.org](https://python.org)

2. Install the required Pygame library using pip:
```bash
pip install pygame
```

3. Clone or download this repository to your local machine

## How to Play

1. Run the game:
```bash
python main.py
```

2. Game Controls:
- Click "Start Game" in the main menu to begin
- Click on tower buttons to select a tower for placement
- Click anywhere on the map to place the selected tower (avoid paths)
- Click on placed towers to:
  - Upgrade them (up arrow button)
  - Sell them ($ button)
- Use the pause button in the top-right corner to pause the game

## Game Elements

### Towers
- **Archer Tower** ($100): Basic tower with balanced stats
- **Mage Tower** ($125): Fast-firing tower with higher damage
- **Catapult Tower** ($150): Slow but powerful tower with splash damage

### Upgrading
- Each tower can be upgraded up to level 4
- Upgrades increase damage and range (except for Catapult)
- Higher levels cost more gold

### Waves
- 5 increasingly difficult waves
- Later waves spawn enemies in groups
- Survive all waves to win!

## Tips
- Place towers strategically to cover multiple paths
- Upgrade towers to deal with stronger waves
- Balance between building new towers and upgrading existing ones
- Keep an eye on your gold and lives!