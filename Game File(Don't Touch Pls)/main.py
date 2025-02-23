import pygame
import time
import os
import csv
import datetime
import pytz
import random as rand

pygame.init()

# Game settings
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Broken Branches")

# Colors
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
GRAY = (150, 150, 150)


# Get the directory of the current script
game_folder = os.path.dirname(__file__)

# Load tree image from the same folder as this script
tree_image = pygame.image.load(os.path.join(game_folder, "tree.png"))
tree_image = pygame.transform.scale(tree_image, (WIDTH/3, HEIGHT/3))

# Tree properties
thirst = 50

# Backend data
boot_day = datetime.datetime.now(pytz.timezone('America/Chicago')).date()
last_boot = None
daily_test_goal = 5
tests_done_today = 0

running = True

def water_tree(amount=10):
    """Waters the tree 'int amount'"""

    global thirst, tests_done_today, last_boot
    thirst = max(0, thirst - amount)
    tests_done_today += 1
    last_boot = datetime.datetime.now(pytz.timezone('America/Chicago')).date()

def thirst_tree(days=0):
    """Add thirst to meter 'int days'"""

    global thirst
    if thirst <= 50:
        thirst = 50
    thirst = min(100, thirst + (days) * 40 + rand.randint(-9, 9))
    print("thirst: ", thirst)

def get_thirst():
    """Set the thirst on start"""

    global boot_day, last_boot, tests_done_today
    if last_boot:
        if get_day(boot_day) - get_day(last_boot) > 0:
            thirst_tree(get_day(boot_day) - get_day(last_boot))
            tests_done_today = 0
    
def get_day(date=None):
    """Converts yyyy-mm-dd to dd"""

    if date:
        return datetime.datetime.strptime(str(date), "%Y-%m-%d").day
    else:
        return None

def save_game():
    """Saves current game data"""
    
    # Get path
    game_folder = os.path.dirname(__file__)
    save_file = os.path.join(game_folder, "save_data.csv")

    # Get data
    tree_data = [
        thirst, 
        datetime.datetime.now(pytz.timezone('America/Chicago')).date(),
        ]

    # Save to file
    with open(save_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Thirst", "Last Fed"]) # Header
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
            global thirst, last_boot
            thirst = int(tree_data[0])
            last_boot = tree_data[1]
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
    
    load_game()
    get_thirst()

on_start()

while running:

    screen.fill(WHITE)
    w, h = pygame.display.get_surface().get_size()

    # Handle Inputs
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit_game()
                
        if event.type == pygame.QUIT:
            exit_game()

    # Draw tree
    screen.blit(tree_image, (w/2 - w/6, h/2))

    # Draw thirst bar
    pygame.draw.rect(screen, GRAY, (w/2 - 250, 350, 500, 20))
    pygame.draw.rect(screen, (200 - 2 * thirst, 200 - 2 * thirst, 255), (w/2 - 250, 350, 500 * (1 - thirst/100), 20))
    pygame.draw.rect(screen, GREEN, (w/2 - 50, 354, 100, 12))

    pygame.display.update()
    pygame.time.delay(100)

pygame.quit()
