# Version 1.7

# In this version the time in the simulation is change, now runs as fast as the cpu allows it
import pygame
import numpy as np
import sys
import random
from pygame.locals import *
from collections import defaultdict

# Se exportan las constantes
from constants import (
    WIDTH, 
    HEIGHT, 
    GROUP_SIZE, 
    ASYMPTOMATIC_RATE, 
    BLACK,
    MASK_REDUCE,
    MASK_USE
)

# Se exporta la clase Person
from person_class import Person

# Se exportan las funciones
from functions import (reset_checkout_map, generate_random_path, draw_logic, round_down)

# Se exporta la función para guardar los datos en la base de datos
from database_configuration import save_simulation_run

# Se exportan las listas de dimensiones
from simulations_lists import walls

# Parameters of the person
MAX_SPEED = (1.2, 1.8) # Speed of the person in m/s

# Parameters of the simulation
NUM_PEOPLE = 10

SPAWN_AREA = (20, 40, 200, 930)  # x_min, x_max, y_min, y_max, zona donde aparecen inicialmente l34eos agentes
#SPAWN_AREA = (100, 101, 900, 901)  
SPAWN_TIME = (2000, 10000)

#  Main simulation loop: run the simulation NUM_RUNS times
# ---------------------------------------------------------------------#
NUM_RUNS = 20
FAST_MODE = True
TARGET_FPS = 5
DT = 1.0 / TARGET_FPS  # fixed sim step (seconds)
MAX_RUN_TIME = 30.0  # seconds
SIMULATION_NAME = "prueba"
INFECTION_RADIUS = 2 # The simulation radius is in meters
INFECTION_RATE = 15
# Pygame setup
pygame.init()

if FAST_MODE:
    # draw into an off-screen surface
    screen = pygame.Surface((WIDTH, HEIGHT))
    #os.environ["SDL_VIDEODRIVER"] = "dummy"  # or use pygame.HIDDEN flag alternative
else:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20)

def run_simulation(
    NUM_RUNS = NUM_RUNS, # Cantidad de corridas 
    INFECTION_RADIUS = INFECTION_RADIUS, # Radio de infección, la entrada es en pixeles
    NUM_PEOPLE = NUM_PEOPLE,
    SIMULATION_NAME = SIMULATION_NAME,
    INFECTION_RATE = INFECTION_RATE,
    ):    
    INFECTION_RADIUS = INFECTION_RADIUS*20
    
    for sim_run in range(NUM_RUNS):
        # Initial setup
        current_spawn_interval = random.uniform(*SPAWN_TIME)  # Random interval for this run
        last_spawn_time = 0.0
        sim_time = 0.0
        running = True
        reset_checkout_map()
        people = []
        people.clear()            # drop references to all Person objects
        Person._id_counter = 1    # Restart IDs next run
        # Print an action time to time, to debug
        ID_DUMP_INTERVAL = 20.0  # seconds    
        # --- per-run analytics variable  ---
        exposure_time_s = defaultdict(float)  # {susceptible_id: seconds near any infectious}
        exposure_time_per_location = defaultdict(float)  # {(x, y): total_seconds}
        exposure_time_grid = defaultdict(float) # Group exposure times into GRID_NUMBERxGRID_NUMBER pixel buckets
        # We define the type of people that are in the simulation
        susceptibles_amount = 0
        infectious_amount = 0
        asymptomatic_amount = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                    
            # --- time step ---
            if FAST_MODE:
                dt = DT                 # run as fast as the CPU allows
            else:
                dt = DT                 # run as fast as the CPU allows
                #dt = clock.tick(TARGET_FPS) / 1000.0  # real-time pacing
            sim_time += dt
                    
            # --- spawns based on SIM time, not wall time ---
            if (sim_time - last_spawn_time) > (current_spawn_interval / 1000.0) and len(people) < NUM_PEOPLE:
                group_path = generate_random_path()
                spawn_count = min(GROUP_SIZE, NUM_PEOPLE - len(people))
                for _ in range(spawn_count):
                    # Infection logic
                    infected = random.random() < INFECTION_RATE
                    asymptomatic = infected and random.random() < ASYMPTOMATIC_RATE
                    # Mask use logic
                    mask = random.random() < MASK_USE # Only 85% of the people use it
                    if mask:
                        mask_reduction = random.uniform(*MASK_REDUCE)
                    else:
                        mask_reduction = 0
                    infection_radius_mask = INFECTION_RADIUS * (1 - mask_reduction)
                    print("distancia reducida", infection_radius_mask/20)
                    # Velocity and position of the person
                    speed = random.uniform(*MAX_SPEED)
                    x = random.randint(SPAWN_AREA[0], SPAWN_AREA[1])
                    y = random.randint(SPAWN_AREA[2], SPAWN_AREA[3])
                    p = Person(x, y, group_path, infected, asymptomatic, speed, infection_radius_mask)
                    people.append(p)
                    # We add the person in the variable
                    if infected:
                        infectious_amount += 1 
                    elif asymptomatic:
                        asymptomatic_amount += 1
                    else:
                        susceptibles_amount += 1
                last_spawn_time = sim_time
                current_spawn_interval = random.uniform(*SPAWN_TIME)

            # --- update ---
            active_count = 0
            for person in people:
                person.update(people, walls, sim_time, dt)
                if person.active or person.checkout or person.exit:
                    active_count += 1
                    
            # >>> INSERT ANALYTICS HERE <<<
            infectious = [p for p in people if ((p.infected or p.asymptomatic) and p.active)] # La persona debe encontrarse activa
            susceptibles = [p for p in people if ((not p.infected and not p.asymptomatic) and p.active)]

            if infectious and susceptibles:
                for s in susceptibles:
                    s_pos = s.position
                    # Early exit as soon as we find one infector in range
                    for inf in infectious:
                        dist = np.linalg.norm(s_pos - inf.position)
                        if dist <= inf.infection_radius: # Use the infection distance of the person using the mask
                            # Save exposure time by ID
                            exposure_time_s[s.id] += dt   # <- uses the dt of this frame
                            # Save Round coordinates to avoid floating-point precision issues
                            x, y = round(s_pos[0]), round(s_pos[1])
                            exposure_time_per_location[(x, y)] += dt  # Accumulate time
                            break  # count once per frame

            # --- draw only if NOT fast mode ---
            if not FAST_MODE:
                draw_logic(screen)
                for person in people:
                    person.draw(screen, sim_time)
                status_text = (f"Run {sim_run+1}/{NUM_RUNS}  "
                            f"Active: {active_count}/{NUM_PEOPLE}  "
                            f"t={sim_time:.1f}s")
                screen.blit(font.render(status_text, True, BLACK), (10, 10))
                pygame.display.flip()   

            # --- finish condition ---
            if active_count == 0 and len(people) == NUM_PEOPLE:
                print(f"Simulation {sim_run+1} finished in {sim_time:.2f} s")
                print(f"Exposure time (s) near infectious, by person id: {dict(exposure_time_s)}")
                # Round the positions by 10
                for (x, y), time in exposure_time_per_location.items():
                    x_bucket = round_down(x)  # e.g., 104 → 100, 107 → 100, 111 → 110
                    y_bucket = round_down(y)  # e.g., 904 → 900, 905 → 900, 902 → 900
                    exposure_time_grid[(x_bucket, y_bucket)] += time
                # Only saves the cases in which the time is bigger than 0.5 seconds
                filtered_grid = {
                    (x, y): time 
                    for (x, y), time in exposure_time_grid.items() 
                    if time > 1.0
                }
                print("Exposure time (s) per location:", dict(filtered_grid))
                print("\n")
                
                # Save the data of the simulation in the database
                save_simulation_run(
                    simulation_name=SIMULATION_NAME,  # Optional name
                    duration=sim_time,
                    person_exposures=exposure_time_s,
                    location_exposures=filtered_grid,
                    num_people=len(people),
                    susceptible=susceptibles_amount,
                    infectious=infectious_amount,
                    asymptomatic=asymptomatic_amount,
                    infection_radius = INFECTION_RADIUS/20,
                    infected_percentage = INFECTION_RATE*100,
                )
                running = False
                
# Crear diferentes simulaciones y se guardan en la base de datos
personas = [10, 20, 30, 40] # Cantidad de personas que se van a simular
distancias = [2, 3, 5] # Diametro en metros de la infección
porcentajes = [0.15, 0.1, 0.05] # Porcentajes de infección
# Se crean las diferentes simulaciones según los diferentes parametros creados
for porcentaje in porcentajes:
    for persona in personas:
        for distancia in distancias:
            simulation_name = "mask_simulation_p" + str(persona) + "_d" + str(distancia) + "_ir" + str(porcentaje)
            print("Corriendo simulacion" + simulation_name)
            run_simulation(
             20,
             distancia,
             persona,
             simulation_name,
             porcentaje 
         )
            
pygame.quit()
sys.exit()