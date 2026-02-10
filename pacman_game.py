import arcade
import random

# --- Load config ---
def load_config(filename):
    config = {}
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=")
            key = key.strip()
            value = value.strip()

            # Convert numeric values
            if value.isdigit():
                value = int(value)
            elif value.replace(".", "", 1).isdigit():
                value = float(value)
            config[key] = value
    return config

config = load_config("config.txt")

# --- Global variables from config ---
WINDOW_WIDTH = config.get("WINDOW_WIDTH", 800)
WINDOW_HEIGHT = config.get("WINDOW_HEIGHT", 600)
WINDOW_TITLE = config.get("WINDOW_TITLE", "Pacman Game")
TILE_SIZE = config.get("TILE_SIZE", 32)

PLAYER_SPEED = config.get("PLAYER_SPEED", 150)
PLAYER_COLOR = getattr(arcade.color, config.get("PLAYER_COLOR", "YELLOW").upper())
PLAYER_RADIUS = config.get("PLAYER_RADIUS", TILE_SIZE // 2 - 2)

GHOST_SPEED = config.get("GHOST_SPEED", 120)
GHOST_COLOR = getattr(arcade.color, config.get("GHOST_COLOR", "RED").upper())
GHOST_RADIUS = config.get("GHOST_RADIUS", TILE_SIZE // 2 - 2)

COIN_COLOR = getattr(arcade.color, config.get("COIN_COLOR", "YELLOW").upper())
COIN_SIZE = config.get("COIN_SIZE", 8)

BACKGROUND_COLOR = getattr(arcade.color, config.get("BACKGROUND_COLOR", "BLACK").upper())
POINTS_PER_COIN = config.get("POINTS_PER_COIN", 10)
PLAYER_LIVES = config.get("PLAYER_LIVES", 3)

# --- Level Map ---
LEVEL_MAP = [
    "WWWWWWWWWWWWWWWWWWWWWWW",
    "W.........W.........W.W",
    "W.WWW.WWW.W.WWW.WWW.W.W",
    "W.W...W...W.W...W...W.W",
    "W.W.W.W.WWW.W.W.W.W.W.W",
    "W...W.....P.....W...W.W",
    "WWW.W.WWW.WWW.W.W.WWW.W",
    "W.....W...G...W.....W.W",
    "W.WWW.W.WWW.W.W.WWW.W.W",
    "W.W...W.....W.W...W...W",
    "W.W.W.WWWWWWW.W.W.W.W.W",
    "W...G.....W.....G.....W",
    "WWWWWWWWWWWWWWWWWWWWWWW"
]

# --- Character Class ---
class Character(arcade.Sprite):
    def __init__(self, x, y, color, radius=None):
        super().__init__()
        if radius is None:
            radius = TILE_SIZE // 2 - 2
        self.texture = arcade.make_circle_texture(radius * 2, color)
        self.width = radius * 2
        self.height = radius * 2
        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.next_direction = (0, 0)  # כיוון הבא (לפקמן)
        self.target = (0, 0)          # מיקום יעד (לרוחות)

# --- Game View ---
class PacmanGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.ghost_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.player = None
        self.score = 0
        self.lives = PLAYER_LIVES
        self.game_over = False
        self.background_color = BACKGROUND_COLOR

        # Text objects לשיפור ביצועים
        self.score_text = arcade.Text("", 10, WINDOW_HEIGHT - 30, arcade.color.WHITE, 24)
        self.lives_text = arcade.Text("", 10, WINDOW_HEIGHT - 55, arcade.color.WHITE, 24)
        self.game_over_text = arcade.Text("GAME OVER",
                                          WINDOW_WIDTH // 2,
                                          WINDOW_HEIGHT // 2,
                                          arcade.color.RED,
                                          50,
                                          anchor_x="center",
                                          anchor_y="center")

    def setup(self):
        """ אתחול המשחק לפי המפה """
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.ghost_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.game_over = False
        self.score = 0
        self.lives = PLAYER_LIVES

        rows = len(LEVEL_MAP)
        for row_idx, row in enumerate(LEVEL_MAP):
            for col_idx, cell in enumerate(row):
                x = col_idx * TILE_SIZE + TILE_SIZE / 2
                y = (rows - row_idx - 1) * TILE_SIZE + TILE_SIZE / 2

                if cell == "W":
                    wall = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE, arcade.color.BLUE)
                    wall.center_x = x
                    wall.center_y = y
                    self.wall_list.append(wall)
                elif cell == "." or cell == " ":
                    coin = arcade.SpriteSolidColor(COIN_SIZE, COIN_SIZE, COIN_COLOR)
                    coin.center_x = x
                    coin.center_y = y
                    self.coin_list.append(coin)
                elif cell == "P":
                    self.player = Character(x, y, PLAYER_COLOR, radius=PLAYER_RADIUS)
                    self.player_list.append(self.player)
                elif cell == "G":
                    ghost = Character(x, y, GHOST_COLOR, radius=GHOST_RADIUS)
                    self.ghost_list.append(ghost)

    # --- Draw ---
    def on_draw(self):
        self.clear()  # הכנה לציור
        self.wall_list.draw()
        self.coin_list.draw()
        self.ghost_list.draw()
        self.player_list.draw()

        # עדכון טקסט
        self.score_text.text = f"SCORE: {self.score}"
        self.lives_text.text = f"LIVES: {self.lives}"
        self.score_text.draw()
        self.lives_text.draw()

        if self.game_over:
            self.game_over_text.draw()

    # --- Player Input ---
    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.next_direction = (0, 1)
        elif key == arcade.key.DOWN:
            self.player.next_direction = (0, -1)
        elif key == arcade.key.LEFT:
            self.player.next_direction = (-1, 0)
        elif key == arcade.key.RIGHT:
            self.player.next_direction = (1, 0)

    def on_key_release(self, key, modifiers):
        pass

    # --- Movement ---
    def move_player(self, delta_time):
        if self.player is None:
            return

        grid_x = round(self.player.center_x / TILE_SIZE) * TILE_SIZE
        grid_y = round(self.player.center_y / TILE_SIZE) * TILE_SIZE

        # שינוי כיוון לפי next_direction
        if self.player.next_direction != (0, 0):
            dx, dy = self.player.next_direction
            future_x = self.player.center_x + dx * PLAYER_SPEED * delta_time
            future_y = self.player.center_y + dy * PLAYER_SPEED * delta_time
            self.player.change_x = dx * PLAYER_SPEED
            self.player.change_y = dy * PLAYER_SPEED
            self.player.center_x = future_x
            self.player.center_y = future_y
            if arcade.check_for_collision_with_list(self.player, self.wall_list):
                self.player.center_x = grid_x
                self.player.center_y = grid_y
                self.player.change_x = 0
                self.player.change_y = 0
            self.player.next_direction = (0, 0)

        # תנועה נוכחית
        self.player.center_x += self.player.change_x * delta_time
        self.player.center_y += self.player.change_y * delta_time
        if arcade.check_for_collision_with_list(self.player, self.wall_list):
            self.player.center_x -= self.player.change_x * delta_time
            self.player.center_y -= self.player.change_y * delta_time
            self.player.change_x = 0
            self.player.change_y = 0
            self.player.center_x = grid_x
            self.player.center_y = grid_y

    def move_ghosts(self, delta_time):
        for ghost in self.ghost_list:
            dx = self.player.center_x - ghost.center_x
            dy = self.player.center_y - ghost.center_y

            if abs(dx) > abs(dy):
                ghost.change_x = GHOST_SPEED if dx > 0 else -GHOST_SPEED
                ghost.change_y = 0
            else:
                ghost.change_x = 0
                ghost.change_y = GHOST_SPEED if dy > 0 else -GHOST_SPEED

            ghost.center_x += ghost.change_x * delta_time
            ghost.center_y += ghost.change_y * delta_time

            if arcade.check_for_collision_with_list(ghost, self.wall_list):
                ghost.center_x -= ghost.change_x * delta_time
                ghost.center_y -= ghost.change_y * delta_time
                ghost.change_x, ghost.change_y = random.choice([
                    (GHOST_SPEED, 0), (-GHOST_SPEED, 0),
                    (0, GHOST_SPEED), (0, -GHOST_SPEED)
                ])

    # --- Update ---
    def on_update(self, delta_time):
        if self.game_over:
            return

        self.move_player(delta_time)
        self.move_ghosts(delta_time)

        # איסוף מטבעות
        coins_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.score += POINTS_PER_COIN

        # התנגשות עם רוחות
        ghosts_hit = arcade.check_for_collision_with_list(self.player, self.ghost_list)
        if ghosts_hit:
            self.lives -= 1
            # החזרת השחקן לנקודת ההתחלה
            for row_idx, row in enumerate(LEVEL_MAP):
                for col_idx, cell in enumerate(row):
                    if cell == "P":
                        self.player.center_x = col_idx * TILE_SIZE + TILE_SIZE / 2
                        self.player.center_y = (len(LEVEL_MAP) - row_idx - 1) * TILE_SIZE + TILE_SIZE / 2
                        self.player.change_x = 0
                        self.player.change_y = 0
                        self.player.next_direction = (0, 0)
                        break
                else:
                    continue
                break
            if self.lives <= 0:
                self.game_over = True
                self.player.change_x = 0
                self.player.change_y = 0
                for ghost in self.ghost_list:
                    ghost.change_x = 0
                    ghost.change_y = 0

# --- Main ---
def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = PacmanGame()
    game.setup()
    window.show_view(game)
    arcade.run()

if __name__ == "__main__":
    main()
