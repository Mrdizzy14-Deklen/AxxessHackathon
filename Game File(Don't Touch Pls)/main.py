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
thirst = 50  # Starts at 50, max 100
thirst_increase_rate = 1  # How fast thirst increases
last_thirst_update = time.time()

def water_tree(amount=10):
    """Waters the tree 'int amount'"""
    global thirst
    thirst = max(0, thirst - amount)
    print(f"Tree watered, thirst: {thirst}")

def thirst_tree(amount=10):
    pass

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
            global thirst 
            thirst = int(tree_data[0])
        print("Game loaded:", tree_data)
    else:
        save_game()

load_game()
print(thirst)
running = True
while running:

    screen.fill(WHITE)
    w, h = pygame.display.get_surface().get_size()

    # Handle Inputs
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("Spacebar pressed")
                save_game()
            if event.key == pygame.K_ESCAPE:
                save_game()
                running = False
                
        if event.type == pygame.QUIT:
            running = False

    # Increase thirst over time
    if time.time() - last_thirst_update > 1:
        print(thirst)
        thirst = min(100, thirst + thirst_increase_rate)
        last_thirst_update = time.time()

    # Draw tree
    screen.blit(tree_image, (w/2 - 350, h/2 - 200))

    # Draw thirst bar
    pygame.draw.rect(screen, RED, (50, 350, 500, 20))
    pygame.draw.rect(screen, BLUE, (50, 350, 500 * (1 - thirst/100), 20))

    pygame.display.update()
    pygame.time.delay(100)

pygame.quit()
