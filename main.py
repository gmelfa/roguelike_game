TITLE = "Roguelike Game"
WIDTH = 800
HEIGHT = 600

import random
import math
from pygame import Rect

# --- Configurações de Áudio ---
music_loaded = False
music_on = True

# --- Sistema do Jogo ---
score = 0
alive_time = 0
score_timer = 0
score_interval = 2
spawn_enemy_timer = 0
spawn_enemy_interval = 8
lives = 1
survival_timer = 0
survival_reward_time = 25

# --- Parâmetros de Animação ---
IDLE_ANIM_SPEED = 0.1
WALK_ANIM_SPEED = 0.15
BOB_HEIGHT = 3

# --- Funções de Áudio ---
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

def toggle_music():
    global music_on, music_loaded
    music_on = not music_on
    if music_on:
        music.play("bgm")
    else:
        music.stop()

# --- Menu Principal ---
menu_items = [
    {"label": "Iniciar Jogo", "rect": Rect(300, 200, 200, 60), "action": "start"},
    {"label": "Music: ON", "rect": Rect(300, 280, 200, 60), "action": "toggle_music"},
    {"label": "Sair", "rect": Rect(300, 360, 200, 60), "action": "exit"},
]
menu_active = True

# --- Mapa do Jogo ---
game_map = [
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
]
TILE_SIZE = 64

class Hero:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.pos_x = x * TILE_SIZE
        self.pos_y = y * TILE_SIZE
        self.speed = 5.5
        self.sprites = {
            "idle": ["hero_idle1", "hero_idle2", "hero_idle3"],
            "walk": ["hero_walk1", "hero_walk2", "hero_walk3"],
            "idle_left": ["hero_idle1left", "hero_idle2left", "hero_idle3left"],
            "walk_left": ["hero_walk1left", "hero_walk2left", "hero_walk3left"]
        }
        self.anim_state = "idle"
        self.anim_frame = 0
        self.anim_timer = 0
        self.idle_offset = 0
        self.moving = False
        self.facing_left = False

    def draw_at(self, offset_x, offset_y):
        y_offset = self.idle_offset if "idle" in self.anim_state else 0
        direction = "_left" if self.facing_left else ""
        state = self.anim_state.replace("_left", "")
        sprite_list = self.sprites[f"{state}{direction}"]
        sprite = sprite_list[self.anim_frame]
        screen.blit(sprite, (offset_x + self.pos_x, offset_y + self.pos_y + y_offset))

    def update(self):
        new_state = "walk" if self.moving else "idle"
        if new_state != self.anim_state:
            self.anim_state = new_state
            self.anim_frame = 0
        
        anim_speed = WALK_ANIM_SPEED if self.moving else IDLE_ANIM_SPEED
        self.anim_timer += anim_speed
        
        if self.anim_timer >= 1:
            self.anim_timer = 0
            max_frames = len(self.sprites["idle"])  
            self.anim_frame = (self.anim_frame + 1) % max_frames
        
        if self.anim_state == "idle":
            self.idle_offset = int(math.sin(self.anim_timer * 2.2) * BOB_HEIGHT)
        
        if self.moving:
            dx = (self.x * TILE_SIZE - self.pos_x)
            dy = (self.y * TILE_SIZE - self.pos_y)
            dist = math.hypot(dx, dy)
            
            if dist <= self.speed:
                self.pos_x = self.x * TILE_SIZE
                self.pos_y = self.y * TILE_SIZE
                self.moving = False
            else:
                self.pos_x += dx * (self.speed / dist)
                self.pos_y += dy * (self.speed / dist)

class Enemy:
    def __init__(self, x, y, patrol_min, patrol_max):
        self.x, self.y = x, y
        self.pos_x = x * TILE_SIZE
        self.pos_y = y * TILE_SIZE
        self.speed = 3.8
        self.sprites = {
            "idle": ["enemy_idle1", "enemy_idle2"],
            "walk": ["enemy_walk1", "enemy_walk2", "enemy_walk3"],
            "idle_left": ["enemy_idle1left", "enemy_idle2left"],
            "walk_left": ["enemy_walk1left", "enemy_walk2left", "enemy_walk3left"]
        }
        self.anim_state = "idle"
        self.anim_frame = 0
        self.anim_timer = 0
        self.idle_offset = 0
        self.moving = False
        self.direction = 1
        self.patrol_min = patrol_min
        self.patrol_max = patrol_max
        self.facing_left = False

    def draw_at(self, offset_x, offset_y):
        y_offset = self.idle_offset if "idle" in self.anim_state else 0
        direction = "_left" if self.facing_left else ""
        state = self.anim_state.replace("_left", "")
        sprite_list = self.sprites[f"{state}{direction}"]
        sprite = sprite_list[self.anim_frame]
        screen.blit(sprite, (offset_x + self.pos_x, offset_y + self.pos_y + y_offset))

    def update(self):
        new_state = "walk" if self.moving else "idle"
        if new_state != self.anim_state:
            self.anim_state = new_state
            self.anim_frame = 0
        
        anim_speed = WALK_ANIM_SPEED if self.moving else IDLE_ANIM_SPEED * 1.5
        self.anim_timer += anim_speed
        
        if self.anim_timer >= 1:
            self.anim_timer = 0
            max_frames = len(self.sprites["idle"])  
            self.anim_frame = (self.anim_frame + 1) % max_frames
        
        if self.anim_state == "idle":
            self.idle_offset = int(math.sin(self.anim_timer * 3) * (BOB_HEIGHT-1))
        
        if not self.moving:
            next_x = self.x + self.direction
            if next_x < self.patrol_min or next_x > self.patrol_max or game_map[self.y][next_x] != ".":
                self.direction *= -1
                next_x = self.x + self.direction
                self.facing_left = self.direction < 0
            if game_map[self.y][next_x] == ".":
                self.x = next_x
                self.moving = True
                self.facing_left = self.direction < 0
        
        if self.moving:
            dx = (self.x * TILE_SIZE - self.pos_x)
            dist = abs(dx)
            
            if dist <= self.speed:
                self.pos_x = self.x * TILE_SIZE
                self.moving = False
            else:
                self.pos_x += dx * (self.speed / dist)

# --- Inicialização do Jogo ---
hero = Hero(0, 0)
enemies = [Enemy(5, 1, 1, 11), Enemy(7, 5, 4, 11)]

def draw():
    screen.clear()
    if menu_active:
        draw_menu()
    else:
        render_game()
        draw_ui()

def draw_menu():
    screen.draw.text("Roguelike", center=(400, 120), fontsize=90, color="#7FDBFF")
    for item in menu_items:
        color = "#2ECC40" if item["action"] == "toggle_music" and music_on else "#FFFFFF"
        screen.draw.filled_rect(item["rect"], "#1F2F3F")
        screen.draw.textbox(item["label"], item["rect"], color=color)

def render_game():
    screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (60, 100, 60))
    
    bg = images.background
    bg_width = bg.get_width()
    bg_height = bg.get_height()
    for x in range(0, WIDTH, bg_width):
        for y in range(0, HEIGHT, bg_height):
            screen.blit("background", (x, y))
    
    map_w = len(game_map[0]) * TILE_SIZE
    map_h = len(game_map) * TILE_SIZE
    offset_x = (WIDTH - map_w) // 2
    offset_y = (HEIGHT - map_h) // 2

    hero.draw_at(offset_x, offset_y)
    for enemy in enemies:
        enemy.draw_at(offset_x, offset_y)

def draw_ui():
    screen.draw.text(f"SCORE: {score}", (15, 15), fontsize=42, color="#FFD700")
    screen.draw.text(f"LIVES: {'O ' * lives}", (15, 65), fontsize=42, color="#FF4136")

def on_mouse_down(pos):
    global menu_active
    if menu_active:
        for item in menu_items:
            if item["rect"].collidepoint(pos):
                handle_menu_action(item["action"])

def handle_menu_action(action):
    global menu_active
    if action == "start":
        menu_active = False
        start_music()
    elif action == "toggle_music":
        toggle_music()
        menu_items[1]["label"] = f"Music: {'ON' if music_on else 'OFF'}"
    elif action == "exit":
        quit()

def on_key_down(key):
    if menu_active or hero.moving:
        return
    
    move = {
        keys.LEFT: (-1, 0),
        keys.RIGHT: (1, 0),
        keys.UP: (0, -1),
        keys.DOWN: (0, 1),
        keys.A: (-1, 0),
        keys.D: (1, 0),
        keys.W: (0, -1),
        keys.S: (0, 1)
    }.get(key, (0, 0))
    
    new_x = hero.x + move[0]
    new_y = hero.y + move[1]
    
    if 0 <= new_x < len(game_map[0]) and 0 <= new_y < len(game_map):
        if game_map[new_y][new_x] == ".":
            hero.x, hero.y = new_x, new_y
            hero.moving = True
            if move[0] < 0:
                hero.facing_left = True
            elif move[0] > 0:
                hero.facing_left = False
            play_step()

def update(dt):
    global score, spawn_enemy_timer, score_timer, survival_timer, lives
    
    if not menu_active:
        score_timer += dt
        spawn_enemy_timer += dt
        survival_timer += dt        
        if score_timer >= score_interval:
            score += 10
            score_timer = 0
        
        if spawn_enemy_timer >= spawn_enemy_interval:
            spawn_enemy()
            spawn_enemy_timer = 0
        
        if survival_timer >= survival_reward_time:
            lives = min(5, lives + 1)
            survival_timer = 0
            play_powerup()
        
        hero.update()
        for enemy in enemies[:]:
            enemy.update()
            if int(hero.x) == enemy.x and int(hero.y) == enemy.y:
                play_hit()
                reset_game()

def spawn_enemy():
    valid_pos = [(x, y) for y in range(1, len(game_map)-1) 
                for x in range(1, len(game_map[0])-1) 
                if game_map[y][x] == "." 
                and not any(e.x == x and e.y == y for e in enemies)
                and (x, y) != (hero.x, hero.y)]
    
    if valid_pos:
        x, y = random.choice(valid_pos)
        enemies.append(Enemy(x, y, 0, len(game_map[0])-1))

def reset_game():
    global hero, enemies, score, lives, score_timer, spawn_enemy_timer, survival_timer, menu_active  # ALTERAÇÃO
    lives -= 1
    if lives <= 0:
        
        menu_active = True
        
        lives = 1
        score = 0
        score_timer = 0
        spawn_enemy_timer = 0
        survival_timer = 0
        hero = Hero(1, 1)
        enemies = [Enemy(5, 1, 1, 11), Enemy(7, 5, 4, 11)]
        return
    
    hero = Hero(1, 1)
    enemies = [Enemy(5, 1, 1, 11), Enemy(7, 5, 4, 11)]
