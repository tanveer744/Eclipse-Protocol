# Eclipse Protocol: Lost in the Void

A 2D space-themed adventure game built with **Pygame** where you navigate through dangerous environments, avoid enemies, and manage your oxygen levels to survive.

## Game Overview

In **"Eclipse Protocol: Lost in the Void,"** you play as an astronaut stranded in deep space. Your mission is to navigate challenging levels, avoid enemies known as **Voidwalkers**, and keep an eye on your depleting oxygen levels. Collect oxygen stations to survive, reach the exits, and progress through increasingly difficult levels.

## Features

- **Multiple Levels:** Progress through various levels with increasing difficulty.
- **Oxygen Management:** Your oxygen depletes over time. Collect oxygen stations to replenish it.
- **Enemies:** Avoid and outsmart Voidwalkers patrolling the levels.
- **Dynamic Difficulty:** Difficulty increases as you advance through levels.
- **Retro Graphics:** 2D sprites and pixel art style.
- **Engaging Soundtrack and Effects:** Background music and sound effects for an immersive experience.

## Controls

- **WASD or Arrow Keys:** Move your character.
- **SPACE:** Start the game or proceed to the next level.
- **R:** Restart the game after a game over.
- **ESC:** Pause/Unpause the game.

## Installation

### Prerequisites

- **Python 3.x** (https://www.python.org/downloads/)
- **Pygame** library

### Install Pygame

Run the following command to install Pygame:

```bash
pip install pygame
```

### Download the Game

Clone the repository from GitHub:

```bash
git clone https://github.com/yourusername/eclipse-protocol.git
cd eclipse-protocol
```

### Game Assets

Ensure the following assets are placed in the `assets` folder:

- `player_sprite.png` (Player sprite)
- `voidwalker_sprite.png` (Voidwalker enemy sprite)
- `oxygen_station_sprite.png` (Oxygen station sprite)
- `levels.json` (Level data)
- `background_music.mp3` (Background music)
- `collect.wav` (Sound effect for collecting items)
- `damage.wav` (Sound effect for taking damage)

### Running the Game

Execute the `main.py` script:

```bash
python main.py
```

## How to Play

1. **Start the Game:**
   - Press **SPACE** to begin from the main menu.
2. **Survive:**
   - Navigate through levels while avoiding enemies and managing your oxygen.
   - Collect oxygen stations to replenish your oxygen levels.
3. **Advance Levels:**
   - Reach the exit to complete the level.
   - The difficulty increases with each new level.
4. **Game Over:**
   - If your oxygen runs out or you collide with a Voidwalker, the game ends.
   - Press **R** to restart.

## Game States

- **Menu:** Start screen.
- **Playing:** Active gameplay.
- **Paused:** Game paused (press **ESC** to toggle).
- **Game Over:** Displayed when the player dies.
- **Level Complete:** Shown when the player reaches the exit.

## Future Enhancements

- Add more levels and enemies.
- Implement additional power-ups.
- Improve graphics and animations.
- Add more sound effects and background music.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

## Credits

- **Developer:** Shaik Tanveer Lohare, Mohammed Maaz , Nithin S , Mohammed Razi

## Contact

For feedback or contributions, reach out via:

- **GitHub:** [Tanveer744](https://github.com/tanveer744)
- **Email:** shaiktanver07404@gmail.com

---

Enjoy surviving in space! 🚀
