import pygame
import time
import os
import csv
import datetime
import pytz
import random as rand

pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)
secret_font = pygame.font.SysFont('Comic Sans MS', 15)

# Game settings
WIDTH, HEIGHT = 750, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Broken Branches")

# Colors
WHITE = (220, 220, 180)
RED = (200, 50, 50)
GREEN = (25, 255, 25)
BLUE = (50, 50, 200)
GRAY = (50, 50, 50)

# Sprite atlas
game_folder = os.path.dirname(__file__)
tree_atlas = pygame.image.load(os.path.join(game_folder, "tree_atlas_shadow.png"))
SPRITE_SHEETS = {
    "OAK_BARE": [
        {"x": 9, "y": 89 + 112, "width": 16, "height": 8},
        {"x": 41, "y": 81 + 112, "width": 16, "height": 16},
        {"x": 73, "y": 80 + 112, "width": 16, "height": 16},
        {"x": 97, "y": 177, "width": 32, "height": 32},
        {"x": 137, "y": 145, "width": 48, "height": 64},
        {"x": 201, "y": 121, "width": 48, "height": 88}
        
        ],
    "OAK_FULL": [
        {"x": 264, "y": 200, "width": 16, "height": 16},
        {"x": 296, "y": 192, "width": 16, "height": 24},
        {"x": 327, "y": 80 + 104, "width": 16, "height": 32},
        {"x": 352, "y": 176, "width": 32, "height": 40},
        {"x": 392, "y": 144, "width": 48, "height": 72},
        {"x": 452, "y": 120, "width": 56, "height": 96}
        ],
    "BIRCH_BARE": [
        {"x": 9, "y": 89, "width": 16, "height": 8},
        {"x": 41, "y": 81, "width": 16, "height": 16},
        {"x": 73, "y": 80, "width": 16, "height": 16},
        {"x": 97, "y": 177 - 112, "width": 32, "height": 32},
        {"x": 137, "y": 145 - 112, "width": 48, "height": 64},
        {"x": 201, "y": 121 - 112, "width": 48, "height": 88}
        
        ],
    "BIRCH_FULL": [
        {"x": 264, "y": 200 - 112, "width": 16, "height": 8},
        {"x": 296, "y": 192  - 112, "width": 16, "height": 16},
        {"x": 327, "y": 80 + 104  - 112, "width": 16, "height": 24},
        {"x": 352, "y": 176  - 112, "width": 32, "height": 32},
        {"x": 392, "y": 144 - 120, "width": 48, "height": 72},
        {"x": 452, "y": 120 - 112, "width": 56, "height": 88}
        ],
    }

# Motivational text
MOTIVATION = ["Healing takes time"]
current_text = None

# Define background images
wind_speed = 0.1
background1 = pygame.image.load(os.path.join(game_folder, "glacial_mountains.png"))
bg1w, bg1h = background1.get_size()
background1 = pygame.transform.scale(background1, (WIDTH, (WIDTH / bg1w) * bg1h))

background5 = pygame.image.load(os.path.join(game_folder, "cliff.png"))
bg5w, bg5h = background5.get_size()
background5 = pygame.transform.scale(background5, (WIDTH, (WIDTH / bg5w) * bg5h))

background3 = pygame.image.load(os.path.join(game_folder, "sky_lightened.png"))
bg3w, bg3h = background1.get_size()
background3 = pygame.transform.scale(background3, (WIDTH, HEIGHT))

background0 = pygame.image.load(os.path.join(game_folder, "clouds_mg_1_lightened.png"))
bg0w, bg0h = background0.get_size()
background0 = pygame.transform.scale(background0, (WIDTH, (WIDTH / bg0w) * bg0h))
bg0x1 = 0
bg0x2 = 0
background2 = pygame.image.load(os.path.join(game_folder, "clouds_bg.png"))
bg2w, bg2h = background2.get_size()
background2 = pygame.transform.scale(background2, (WIDTH, (WIDTH / bg2w) * bg2h))
bg2x1 = 0
bg2x2 = 0
background4 = pygame.image.load(os.path.join(game_folder, "clouds_mg_2.png"))
bg4w, bg4h = background4.get_size()
background4 = pygame.transform.scale(background4, (WIDTH, (WIDTH / bg4w) * bg4h))
bg4x1 = 0
bg4x2 = 0

# Load tree image from the same folder as this script
tree_image = pygame.image.load(os.path.join(game_folder, "tree.png"))
tree_image = pygame.transform.scale(tree_image, (WIDTH/3, HEIGHT/3))
img_width, img_height = tree_image.get_size()
img_sheet = "OAK_FULL"

# Add fill indicator
indicator = pygame.image.load(os.path.join(game_folder, "indicator.png"))
indicator = pygame.transform.scale(indicator, (80, 80))

# Define buttons
button_color = BLUE
button_hover_color = RED
start_button_clicked = False
start_button = pygame.Rect(500, 750, 200, 50)
start_button_text = my_font.render('Start', True, (255, 255, 255))


# Tree properties
thirst = 100
MAX_SCORE = 60
score = 0

# Backend data
boot_day = datetime.datetime.now(pytz.timezone('America/Chicago')).date()
last_boot = None
daily_test_goal = 5
tests_done_today = 0
increase_amount = 12
show_ui = True

running = True

def get_sprite(atlas, category, index):
    if category in SPRITE_SHEETS:
        if 0 <= index < len(SPRITE_SHEETS[category]):
            data = SPRITE_SHEETS[category][index]
            return get_sprite_from_atlas(atlas, data["x"], data["y"], data["width"], data["height"])
        else:
            print(f"Index {index} out of range for '{category}'")
    else:
        print(f"Category '{category}' not found!")
    return None

def get_sprite_from_atlas(atlas, x, y, width, height):
    """Extracts a sprite from an atlas at the given coordinates."""
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)  # Create a new transparent surface
    sprite.blit(atlas, (0, 0), (x, y, width, height))  # Copy from the atlas
    return sprite

def water_tree():
    """Waters the tree"""

    global thirst, tests_done_today, last_boot
    thirst = max(0, thirst - increase_amount - rand.randint(-3, 3))
    thirst = int(thirst)
    tests_done_today += 1
    last_boot = datetime.datetime.now(pytz.timezone('America/Chicago')).date()
    save_game()

def thirst_tree(days=0):
    """Add thirst to meter 'int days'"""

    global thirst
    if thirst <= 50:
        thirst = 50
    thirst = min(100, thirst + (days) * 40 + rand.randint(-9, 9))
    print("thirst: ", thirst)

def get_thirst():
    """Set the thirst on start"""

    global boot_day, last_boot, thirst, tests_done_today, increase_amount
    if last_boot:
        if get_day(boot_day) - get_day(last_boot) > 0:
            # If new day
            thirst_tree(get_day(boot_day) - get_day(last_boot))
            tests_done_today = 0
            increase_amount = abs(thirst - 50)/5

def set_tree_image():
    global MAX_SCORE, score, tree_image, tree_atlas, img_width, img_height, img_sheet
    match score:
        case x if x >= 50:
            tree_image = get_sprite(tree_atlas, img_sheet, 5)
            img_width, img_height = tree_image.get_size()
            tree_image = pygame.transform.scale(tree_image, (img_width * 10, img_height * 10))
        case x if x >= 40:
            tree_image = get_sprite(tree_atlas, img_sheet, 4)
            img_width, img_height = tree_image.get_size()
            tree_image = pygame.transform.scale(tree_image, (img_width * 10, img_height * 10))
        case x if x >= 30:
            tree_image = get_sprite(tree_atlas, img_sheet, 3)
            img_width, img_height = tree_image.get_size()
            tree_image = pygame.transform.scale(tree_image, (img_width * 10, img_height * 10))
        case x if x >= 20:
            tree_image = get_sprite(tree_atlas, img_sheet, 2)
            img_width, img_height = tree_image.get_size()
            tree_image = pygame.transform.scale(tree_image, (img_width * 10, img_height * 10))
        case x if x >= 10:
            tree_image = get_sprite(tree_atlas, img_sheet, 1)
            img_width, img_height = tree_image.get_size()
            tree_image = pygame.transform.scale(tree_image, (img_width * 10, img_height * 10))
        case _:
            tree_image = get_sprite(tree_atlas, img_sheet, 0)
            img_width, img_height = tree_image.get_size()
            tree_image = pygame.transform.scale(tree_image, (img_width * 10, img_height * 10))

def get_day(date=None):
    """Converts yyyy-mm-dd to dd"""

    if date:
        return datetime.datetime.strptime(str(date), "%Y-%m-%d").day
    else:
        return None

def set_score():
    global score

def save_game():
    """Saves current game data"""
    
    # Get path
    game_folder = os.path.dirname(__file__)
    save_file = os.path.join(game_folder, "save_data.csv")

    # Get data
    tree_data = [
        thirst, 
        datetime.datetime.now(pytz.timezone('America/Chicago')).date(),
        img_sheet,
        tests_done_today,
        ]

    # Save to file
    with open(save_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Thirst", "Last Watered", "Type"]) # Header
        writer.writerow(tree_data)
        
    print("==Game saved==")

def load_game():
    """Loads saved data"""
    
    # Get path
    game_folder = os.path.dirname(__file__)
    save_file = os.path.join(game_folder, "save_data.csv")

    if os.path.exists(save_file):
        with open(save_file, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            tree_data = next(reader)
            global thirst, last_boot, img_sheet, tests_done_today
            thirst = int(tree_data[0])
            last_boot = tree_data[1]
            img_sheet = tree_data[2]
            tests_done_today = int(tree_data[3])
        print("Game loaded:", tree_data)
    else:
        save_game()

def exit_game():
    """Quits game and saves data"""

    global running
    save_game()
    running = False

def on_start():
    """Does all functions required on startup"""

    global current_text
    current_text = MOTIVATION[rand.randint(0, len(MOTIVATION) - 1)]

    load_game()
    get_thirst()
    set_tree_image()

on_start()

while running:
    mouse = pygame.mouse.get_pos() 
    screen.blit(background3, (0, 0))
    w, h = pygame.display.get_surface().get_size()

    # Handle Inputs
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                show_ui = not show_ui
                score += 10
                water_tree()
                print(tests_done_today)
                set_tree_image()
            if event.key == pygame.K_ESCAPE:
                exit_game()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                start_button_clicked = not start_button_clicked
                
        if event.type == pygame.QUIT:
            exit_game()



    # Handle background
    
    bg2x1 -= wind_speed * 0.5
    bg2x2 -= wind_speed * 0.5
    screen.blit(background2, (bg2x1, 0))
    screen.blit(background2, (bg2x2 + w, 0))
    if bg2x1 <= -w:
        bg2x1 = 0
    if bg2x2 <= -w:
        bg2x2 = 0

    screen.blit(background1, (0, 0))

    bg4x1 -= wind_speed * 2
    bg4x2 -= wind_speed * 2
    screen.blit(background4, (bg4x1, 0))
    screen.blit(background4, (bg4x2 + w, 0))
    if bg4x1 <= -w:
        bg4x1 = 0
    if bg4x2 <= -w:
        bg4x2 = 0

    bg0x1 -= wind_speed * 5
    bg0x2 -= wind_speed * 5
    screen.blit(background0, (bg0x1, 0))
    screen.blit(background0, (bg0x2 + w, 0))
    if bg0x1 <= -w:
        bg0x1 = 0
    if bg0x2 <= -w:
        bg0x2 = 0

    screen.blit(background5, (0, 380))

    # Draw tree
    screen.blit(tree_image, (w/2 - img_width * 5, h * 0.95 - img_height * 10))
    if show_ui:

        text = secret_font.render("Press 'SPACE' to hide UI", True, (10, 10, 10))
        text_width, text_height = text.get_size()
        screen.blit(text, (w * 0.75 ,h * 0.98))

        if tests_done_today >= daily_test_goal:
            current_text = "Good work today, don't over do it"

        text = my_font.render(current_text, True, (10, 10, 10))
        text_width, text_height = text.get_size()
        pygame.draw.ellipse(screen, WHITE, (w/2 - text_width/2 - 10, h * 0.93 - 10, text_width + 20, text_height + 20))
        screen.blit(text, (w/2 - text_width/2,h * 0.93))

        # Draw thirst bar
        pygame.draw.rect(screen, GRAY, (47, h * 0.7 - 253, 26, 506))
        pygame.draw.rect(screen, (100 - thirst, 100 - thirst, 255), (50 , (h * 0.7 + 250) - (500 *(1 - thirst/100)), 20, 500 * (1 - thirst/100)))
        pygame.draw.rect(screen, GREEN, (54, h * 0.7 - 50, 12, 100))

        screen.blit(indicator, (-20, (h * 0.7 - 45 + 250) - (500 *(1 - thirst/100))))

        if start_button.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, button_hover_color, start_button)
        else:
            pygame.draw.rect(screen, button_color, start_button)

        text_rect = start_button_text.get_rect(center=start_button.center)
        screen.blit(start_button_text, text_rect)

        if start_button_clicked:
            start_button_clicked = not start_button_clicked

    pygame.display.update()
    pygame.time.delay(1)

pygame.quit()
