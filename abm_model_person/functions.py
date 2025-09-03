'''
functions.py 

Este arhivo estará manejando todas las listas que se utilizan en el proyecto para manejar tanto los caminos
iniciales de los agentes, finales, puntos de interés y demás.
'''
import numpy as np
import random
import pygame

from simulations_lists import (
    initial_path_waypoints, 
    middle_path_waypoints, 
    final_path_waypoints, 
    exit_waypoints, 
    checkout_map, 
    walls)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255) 
YELLOW = (255, 255, 0)

# DECLARACION DE VARIABLES
RANGO_ALEATORIEDAD = (1, 15) # Aleatoriedad de caminos, cantidad de middle path waypoint que una persona puede tener en un recorrido.

# Number to specify the grid tempalte
GRID_NUMBER = 10

# half of the supermarket, number use to make to generate the random path
midle_value = 975 

# Pegamos toda la lista de puntos para dibujar en el mapa las trayectorias 
path_waypoints = initial_path_waypoints + middle_path_waypoints + final_path_waypoints


# FUNCTIONS

'''
Checkout Function
Se crea un valor para el tiempo de espera que tendrá una persona al momento de realizar el Checkout
'''
# Se definen rangos realistas de tiempo de checkout
CHECKOUT_WAIT_MEAN = 90  # 3 minutes (180 seconds) as a typical (mean) wait
CHECKOUT_WAIT_STD = 60    # 1 minute (60 seconds) of standard deviation
CHECKOUT_WAIT_MIN = 20    # Absolute minimum: 10 seconds
CHECKOUT_WAIT_MAX = 300   # Absolute maximum: 5 minutes

def get_checkout_time(mean = CHECKOUT_WAIT_MEAN, 
                      std = CHECKOUT_WAIT_STD, 
                      min_val = CHECKOUT_WAIT_MIN, 
                      max_val = CHECKOUT_WAIT_MAX):
    """Generates a random value from a normal distribution, truncated between min_val and max_val."""
    while True:
        value = random.normalvariate(mean, std)
        if min_val <= value <= max_val:
            return value
        
# Create function to generate path way 
def generate_random_path():
    """Generate a path with random middle waypoints (3-8) between fixed start/end"""
    # Randomly select 3-8 waypoints from the middle path
    num_waypoints = random.randint(*RANGO_ALEATORIEDAD)
    selected_waypoints = random.sample(middle_path_waypoints, num_waypoints)
    
    # Combine with fixed start and end points, points of interest and exit
    full_path = selected_waypoints + [random.choice(final_path_waypoints)]
    
    # Intialize the whole path way
    final_path = initial_path_waypoints
        
    # Make a loop to make the path way smoother for the agente
    i = 0
    for point in full_path:
        # Select each value of the actual objective
        row = point[0]
        column = point[1]
        
        # We calculate the exit of the person in the hallway
        if final_path[-1][0] > midle_value:
            final_path = final_path +  [np.array([1625, final_path[-1][1]])]
        else:
            final_path = final_path + [np.array([275, final_path[-1][1]])]
        
        # We calcule the entry to the hallway
        # The row value is the last value of the list final_path
        final_path = final_path + [np.array([final_path[-1][0], column])]
        
        # We add the actual objective
        final_path = final_path + [point]
        
        # We iterate to next objective        
        i = i + 1
    
    return final_path

# Generate random path at the exit
def exit_path_creation(x, y):
    path = [
        np.array([x, y + 80]), # Actual position of the person + some distance in Y
        random.choice(exit_waypoints['exit1']), # First random point choice
        random.choice(exit_waypoints['exit2'])  # Second random point choice
    ]
    return path

# To check for the best position in the checkout
def best_slot(checkout_map):
    # Count occupied slots per line
    occupancy = {
        line: sum(1 for x, y, pid in slots if pid != -1)
        for line, slots in checkout_map.items()
    }
    # Pick the least-crowded line
    best_line = min(occupancy, key=occupancy.get)
    # Gather free slot indices
    free_idxs = [
        idx for idx, (_x, _y, pid) in enumerate(checkout_map[best_line])
        if pid == -1
    ]
    if not free_idxs:
        print("All queues are full.")
        return
    # Pick the last free slot
    idx = min(free_idxs)
    x, y, _ = checkout_map[best_line][idx]
    
    return best_line, [x, y]

# To register a person in the position
def register_person(checkout_map, person_id, coords):
    """
    Finds the slot matching coords [x, y] in checkout_map and sets its pid to person_id.
    Returns (line_key, slot_index) if successful, or (None, None) if coords not found.
    """
    x_target, y_target = coords
    for line, slots in checkout_map.items():
        for idx, (x, y, pid) in enumerate(slots):
            if x == x_target and y == y_target:
                checkout_map[line][idx][2] = person_id
                return line, idx
    return None, None

# When a person gets done
def unregister_person(checkout_map, person_id):
    """
    Finds the slot where pid == person_id in checkout_map,
    sets that slot’s pid back to -1, and returns (line_key, slot_index).
    If the person_id is not found, returns (None, None).
    """
    for line, slots in checkout_map.items():
        for idx, (x, y, pid) in enumerate(slots):
            if pid == person_id:
                checkout_map[line][idx][2] = -1
                return line, idx
    return None, None

def find_line_and_idx_by_coords(checkout_map, coords):
    x_t, y_t = coords
    for line, slots in checkout_map.items():
        for i, (x, y, _) in enumerate(slots):
            if x == x_t and y == y_t:
                return line, i
    return None, None

def try_advance_in_line(checkout_map, person_id, coords):
    """
    If the next slot towards the cashier is free, move the person forward.
    Returns the (possibly updated) coords they should target next.
    """
    line, idx = find_line_and_idx_by_coords(checkout_map, coords)
    if line is None:
        return coords  # not found; do nothing

    slots = checkout_map[line]
    last_idx = len(slots) - 1
    if idx < last_idx and slots[idx + 1][2] == -1:
        # Move forward one slot
        unregister_person(checkout_map, person_id)
        next_coords = slots[idx + 1][:2]
        register_person(checkout_map, person_id, next_coords)
        return next_coords
    return coords  # cannot advance yet

# Round coordinates down to the nearest multiple of a number
def round_down(num):
    return (num // GRID_NUMBER) * GRID_NUMBER

def draw_logic(screen):
    # Clear screen
    screen.fill(WHITE)

    # Draw path waypoints and connecting lines
    for i, point in enumerate(path_waypoints):
        pygame.draw.circle(screen, GREEN, point.astype(int), 5)
        if i > 0:
            pygame.draw.line(
                screen, (200, 200, 200),
                path_waypoints[i - 1],
                point,
                2
            )

    # Draw checkout slots
    for line_name, slots in checkout_map.items():
        for slot in slots:
            point = np.array([slot[0], slot[1]])
            pygame.draw.circle(screen, YELLOW, point.astype(int), 8)
            
    # Draw the exit points
    for exit in exit_waypoints:
        for posicion in exit_waypoints[exit]:            
            pygame.draw.circle(screen, BLACK, posicion.astype(int), 5)

    # Draw walls
    for wall in walls:
        pygame.draw.line(screen, BLACK, (wall[0], wall[1]), (wall[2], wall[3]), 5)
        
def reset_checkout_map():
    for fila in checkout_map:
        for posicion in checkout_map[fila]:
            posicion[2] = -1
  

