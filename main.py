TITLE = "Roguelike Game"
WIDTH = 800
HEIGHT = 600

import random
from pygame import Rect

# --- Música e Sons ---
music_loaded = False
music_on = True

# Sistema de pontuação e timers
score = 0
alive_time = 0
score_timer = 0
score_interval = 3
spawn_enemy_timer = 0
spawn_enemy_interval = 10

# Sistema de vidas
lives = 3
survival_timer = 0
survival_reward_time = 30  # segundos para ganhar 1 vida extra

def play_step():
    if music_on:
        sounds.step.play()

def play_hit():
    if music_on:
        sounds.hit.play()

def play_powerup():
    if music_on:
        sounds.powerup.play()

def start_music():
    global music_loaded
    if music_on and not music_loaded:
        music.play("bgm")
        music_loaded = True
    elif not music_on:
        music.stop()
        music_loaded = False

def toggle_music():
    global music_on, music_loaded
    music_on = not music_on
    if music_on:
        music.play("bgm")
        music_loaded = True
    else:
        music.stop()
        music_loaded = False

# --- Menu State ---
menu_items = [
    {"label": "Start Game", "rect": Rect((300, 200), (200, 60)), "action": "start"},
    {"label": "Music: ON", "rect": Rect((300, 280), (200, 60)), "action": "toggle_music"},
    {"label": "Exit", "rect": Rect((300, 360), (200, 60)), "action": "exit"},
]

menu_active = True

# --- Game State ---
game_map = [
    "############",
    "#..........#",
    "#..........#",
    "#..........#",
    "#..........#",
    "#..........#",
    "#..........#",
    "############",
]
TILE_SIZE = 48

class Hero:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.pos_x = x * TILE_SIZE
        self.pos_y = y * TILE_SIZE
        self.speed = 6
        self.sprites = ["hero_idle", "hero_walk1", "hero_walk2"]
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.2
        self.moving = False

    def draw_at(self, offset_x, offset_y):
        sprite = self.sprites[self.anim_index]
        screen.blit(sprite, (offset_x + self.pos_x, offset_y + self.pos_y))

    def update(self):
        if self.moving:
            dx = self.target_x * TILE_SIZE - self.pos_x
            dy = self.target_y * TILE_SIZE - self.pos_y
            distance = (dx**2 + dy**2)**0.5
            if distance <= self.speed:
                self.pos_x = self.target_x * TILE_SIZE
                self.pos_y = self.target_y * TILE_SIZE
                self.moving = False
                self.anim_index = 0
            else:
                self.pos_x += dx * (self.speed / distance)
                self.pos_y += dy * (self.speed / distance)
                self.anim_timer += self.anim_speed
                if self.anim_timer >= 1:
                    self.anim_timer = 0
                    self.anim_index = 1 if self.anim_index == 2 else 2

class Enemy:
    def __init__(self, x, y, patrol_min, patrol_max):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.pos_x = x * TILE_SIZE
        self.pos_y = y * TILE_SIZE
        self.speed = 4
        self.sprites = ["enemy_idle", "enemy_walk1", "enemy_walk2"]
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.18
        self.moving = False
        self.direction = 1
        self.patrol_min = patrol_min
        self.patrol_max = patrol_max

    def draw_at(self, offset_x, offset_y):
        sprite = self.sprites[self.anim_index]
        screen.blit(sprite, (offset_x + self.pos_x, offset_y + self.pos_y))

    def update(self):
        if not self.moving:
            next_x = self.x + self.direction
            if next_x < self.patrol_min or next_x > self.patrol_max or game_map[self.y][next_x] != ".":
                self.direction *= -1
                next_x = self.x + self.direction
            if game_map[self.y][next_x] == ".":
                self.x = next_x
                self.target_x = next_x
                self.moving = True
        if self.moving:
            dx = self.target_x * TILE_SIZE - self.pos_x
            dy = self.target_y * TILE_SIZE - self.pos_y
            distance = (dx**2 + dy**2)**0.5
            if distance <= self.speed:
                self.pos_x = self.target_x * TILE_SIZE
                self.pos_y = self.target_y * TILE_SIZE
                self.moving = False
                self.anim_index = 0
            else:
                self.pos_x += dx * (self.speed / distance)
                self.pos_y += dy * (self.speed / distance)
                self.anim_timer += self.anim_speed
                if self.anim_timer >= 1:
                    self.anim_timer = 0
                    self.anim_index = 1 if self.anim_index == 2 else 2

def create_initial_enemies():
    return [
        Enemy(5, 2, 2, 9),
        Enemy(7, 5, 4, 9),
    ]

hero = Hero(1, 1)
enemies = create_initial_enemies()

def draw_score():
    screen.draw.text(f"Score: {score}", (10, 10), fontsize=40, color="white")

def draw_lives():
    screen.draw.text(f"Lives: {lives}", (10, 50), fontsize=40, color="white")

def draw():
    screen.clear()
    if menu_active:
        draw_menu()
    else:
        draw_game()
        draw_score()
        draw_lives()

def draw_menu():
    screen.draw.text("Roguelike Game", center=(WIDTH//2, 120), fontsize=70, color="white")
    for item in menu_items:
        screen.draw.filled_rect(item["rect"], (60, 60, 60))
        screen.draw.rect(item["rect"], (200, 200, 200))
        screen.draw.text(
            item["label"],
            center=item["rect"].center,
            fontsize=40,
            color="white"
        )

def draw_game():
    map_width = len(game_map[0]) * TILE_SIZE
    map_height = len(game_map) * TILE_SIZE
    map_x = (WIDTH - map_width) // 2
    map_y = (HEIGHT - map_height) // 2

    screen.draw.filled_rect(Rect((0, 0), (WIDTH, HEIGHT)), (60, 60, 60))
    screen.blit("background", (map_x, map_y))

    for y, row in enumerate(game_map):
        for x, cell in enumerate(row):
            if cell == "#":
                color = (80, 80, 80)
                screen.draw.filled_rect(
                    Rect((map_x + x*TILE_SIZE, map_y + y*TILE_SIZE), (TILE_SIZE, TILE_SIZE)), color)
    hero.draw_at(map_x, map_y)
    for enemy in enemies:
        enemy.draw_at(map_x, map_y)

def on_mouse_down(pos):
    global menu_active
    if not menu_active:
        return
    for item in menu_items:
        if item["rect"].collidepoint(pos):
            if item["action"] == "start":
                menu_active = False
                start_music()
            elif item["action"] == "toggle_music":
                toggle_music()
                item["label"] = f"Music: {'ON' if music_on else 'OFF'}"
            elif item["action"] == "exit":
                quit()

def on_key_down(key):
    if menu_active or hero.moving:
        return

    dx, dy = 0, 0
    if key == keys.LEFT or key == keys.A:
        dx = -1
    elif key == keys.RIGHT or key == keys.D:
        dx = 1
    elif key == keys.UP or key == keys.W:
        dy = -1
    elif key == keys.DOWN or key == keys.S:
        dy = 1

    new_x = hero.x + dx
    new_y = hero.y + dy

    if game_map[new_y][new_x] == ".":
        hero.x = new_x
        hero.y = new_y
        hero.target_x = new_x
        hero.target_y = new_y
        hero.moving = True
        play_step()

def spawn_enemy():
    valid_positions = []
    for y in range(1, len(game_map)-1):
        for x in range(1, len(game_map[0])-1):
            if (
                game_map[y][x] == "." 
                and not any(e.x == x and e.y == y for e in enemies) 
                and not (hero.x == x and hero.y == y)
            ):
                valid_positions.append((x, y))
    if valid_positions:
        x, y = random.choice(valid_positions)
        enemies.append(Enemy(x, y, max(1, x-3), min(len(game_map[0])-2, x+3)))

def reset_game():
    global hero, enemies, score, alive_time, spawn_enemy_timer, score_timer, lives, survival_timer
    lives -= 1
    survival_timer = 0
    if lives <= 0:
        # Game Over - reinicia tudo
        hero = Hero(1, 1)
        enemies = create_initial_enemies()
        score = 0
        alive_time = 0
        spawn_enemy_timer = 0
        score_timer = 0
        lives = 3
    else:
        # Continua com menos uma vida
        hero = Hero(1, 1)
        enemies = create_initial_enemies()

def update(dt):
    global alive_time, score, spawn_enemy_timer, score_timer, survival_timer, lives
    if not menu_active:
        alive_time += dt
        spawn_enemy_timer += dt
        score_timer += dt
        survival_timer += dt
        
        if score_timer >= score_interval:
            score += 1
            score_timer = 0
            
        if spawn_enemy_timer >= spawn_enemy_interval:
            spawn_enemy()
            spawn_enemy_timer = 0
            
        if survival_timer >= survival_reward_time:
            lives += 1
            survival_timer = 0
            play_powerup()
            
        hero.update()
        for enemy in enemies:
            enemy.update()
            
        for enemy in enemies:
            if int(hero.x) == int(enemy.x) and int(hero.y) == int(enemy.y):
                play_hit()
                reset_game()