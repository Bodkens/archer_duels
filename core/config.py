"""Central tunable constants for Archer Duels."""

import os

# --- Assets ---
# assets/ lives next to the core/ package (one level up from this file).
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
BACKGROUND_IMAGE = "background.png"

# Optional spritesheets / tilesets. Leave as None to use the built-in vector /
# colour fallback. Drop a PNG into assets/ and point these at it to switch on
# real artwork without touching any other code.
PLAYER_SHEET = "player_sheet.png"
PLAYER_FRAME = (40, 62)    # nominal cell size in the sheet; grid is derived by rounding
ENEMY_SHEET = "enemy_sheet.png"
ENEMY_FRAME = (40, 62)
# Spritesheet rows are animation states (10 fps). Each row is one full animation:
#   0 = idle + bow, 1 = idle + bomb, 2 = aiming + bow, 3 = aiming + bomb, 4 = moving
SPRITE_ANIM_FPS = 10
ARROW_IMAGE = "arrow.png"         # single sprite, rotated to the flight angle
BOMB_IMAGE = "bomb.png"
TILES_IMAGE = None         # one row of TILE-sized cells: [EMPTY, DIRT, STONE]

# On-screen sizes for projectile artwork (only used when the *_IMAGE is set).
# The archer body is 24x40 px; these boxes are deliberately smaller so the
# bomb/arrow read as held items rather than dwarfing the players.
BOMB_DRAW_SIZE = 18        # bomb image scaled to fit this box (px)
ARROW_DRAW_SIZE = 34       # arrow image scaled to fit this box (px)
HUD_ICON_SIZE = 26         # weapon icon shown next to the HUD turn label

# --- Display ---
SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
TITLE = "Archer Duels"
SPLASH_TIME = 2.0  # seconds

# --- Tiles / terrain ---
TILE = 8
COLS = SCREEN_W // TILE
ROWS = SCREEN_H // TILE

EMPTY = 0
DIRT = 1
STONE = 2

# Vertical band (in tiles) where the surface line is allowed to wander.
SURFACE_MIN_ROW = ROWS // 3
SURFACE_MAX_ROW = ROWS - 4

# --- Physics ---
GRAVITY = 900.0            # px/s^2 for the arrow arc
BOMB_GRAVITY_MULT = 1.6    # bomb is heavier -> falls faster / steeper arc
BOMB_DRAG = 0.6            # horizontal air drag for the bomb (per second)
POWER_TO_SPEED = 6.0       # drag pixels -> launch speed multiplier
MAX_POWER = 180.0          # max drag length considered (pixels)

# --- Gameplay ---
MAX_HP = 100
WALK_SPEED = 160.0         # px/s while walking
WALK_DISTANCE = 160.0      # max pixels an archer may move per turn

ARROW_DAMAGE = 35
BOMB_MAX_DAMAGE = 50       # at the blast center
BOMB_RADIUS_TILES = 9      # crater / blast radius in tiles
BOMB_KNOCKBACK = 70.0      # horizontal displacement at blast center (px)
BOMB_FUSE = 4.0            # seconds before an airborne bomb self-detonates

SAFE_GROUND_ROWS = 8       # permanent bottom layer, never destroyed by bombs
STONE_START_ROW = ROWS - SAFE_GROUND_ROWS - 12

MIN_SPAWN_GAP = 400        # min horizontal distance between the two archers

# AI
AIM_HIT_CHANCE = 0.45      # chance the AI lands the shot while "ranging in"
AIM_MISS_SPREAD = 14.0     # angle/power jitter (deg / power units) on a miss
AI_MOVE_THRESHOLD = 24     # player movement (px) that forces the AI to re-aim

# --- Colors ---
COL_SKY = (135, 170, 210)
COL_DIRT = (110, 78, 48)
COL_DIRT_TOP = (76, 150, 64)   # grassy top edge
COL_STONE = (96, 96, 104)
COL_PLAYER = (70, 130, 220)
COL_ENEMY = (210, 80, 80)
COL_TEXT = (245, 245, 245)
COL_TEXT_DIM = (180, 180, 180)
COL_ARROW = (200, 180, 120)
COL_BOMB = (40, 40, 40)
COL_HP_BG = (60, 60, 60)
COL_HP_GOOD = (80, 200, 90)
COL_HP_LOW = (220, 70, 70)
COL_AIM = (255, 255, 255)
COL_BUTTON = (50, 60, 80)
COL_BUTTON_HOVER = (80, 100, 140)
COL_EXPLOSION = (255, 170, 40)
