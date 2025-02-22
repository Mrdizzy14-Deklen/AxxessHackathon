import pygame
import time
import os
import csv
import datetime

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


# Get the directory of the current script
game_folder = os.path.dirname(__file__)

# Load tree image from the same folder as this script
tree_image = pygame.image.load(os.path.join(game_folder, "tree.png"))
tree_image = pygame.transform.scale(tree_image, (WIDTH/3, HEIGHT/3))

# Tree properties
thirst = 50
thirst_increase_rate = 1  # How fast thirst increases
last_thirst_update = time.time()

# Backend data
boot_day = datetime.datetime.now(datetime.timezone.utc).date()
last_boot = None

running = True

def water_tree(amount=10):
    """Waters the tree 'int amount'"""
    global thirst
    thirst = max(0, thirst - amount)
    print(f"Tree watered, thirst: {thirst}")

def thirst_tree(days=1):
    global thirst
    thirst += days * days
    print("days: ", days)
    pass

def get_thirst():
    global boot_day, last_boot
    if last_boot:
        thirst_tree(get_day(boot_day) - get_day(last_boot))
    
def get_day(date=None):
    if date:
        return datetime.datetime.strptime(str(date), "%Y-%m-%d").day
    else:
        return None

def save_game():
    
    # Get path
    game_folder = os.path.dirname(__file__)
    save_file = os.path.join(game_folder, "save_data.csv")

    # Get data
    tree_data = [
        thirst, 
        datetime.datetime.now(datetime.timezone.utc).date(),
        ]

    # Save to file
    with open(save_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Thirst", "Last Fed"]) # Header
        writer.writerow(tree_data)
        
    print("==Game saved==")

def load_game():
    
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
            if event.key == pygame.K_SPACE:
                print("Spacebar pressed")
            if event.key == pygame.K_ESCAPE:
                exit_game()
                
        if event.type == pygame.QUIT:
            exit_game()

    # Increase thirst over time
    if time.time() - last_thirst_update > 1:
        print(thirst)
        thirst = min(100, thirst + thirst_increase_rate)
        last_thirst_update = time.time()

    # Draw tree
    screen.blit(tree_image, (w/2 - w/6, h/2))

    # Draw thirst bar
    pygame.draw.rect(screen, RED, (w/2 - 250, 350, 500, 20))
    pygame.draw.rect(screen, BLUE, (w/2 - 250, 350, 500 * (1 - thirst/100), 20))

    pygame.display.update()
    pygame.time.delay(100)

pygame.quit()
