import numpy as np
import random
import math
import pygame

# Se exportan las funciones creadas
from functions import (
    best_slot, 
    register_person, 
    find_line_and_idx_by_coords, 
    exit_path_creation,
    unregister_person,
    get_checkout_time
    )

# Se importan las funciones necesarias 
from simulations_lists import (checkout_map, )

# Se importan las constantes
from constants import (
    WIDTH, 
    HEIGHT, 
    FINAL_Y, 
    # Colors
    YELLOW,
    RED, 
    BLUE
    )

# Person Features
PERSON_RADIUS = 5
SEPARATION_RADIUS = 15
WALL_MARGIN = 15 # Separación entre las paredes, separación de pixeles con las paredes

# Wait times
WALK_WAIT_RANGE = (1, 5)      # seconds

#CHECKOUT_WAIT_RANGE = (30, 300) # seconds
#CHECKOUT_WAIT_RANGE = (4, 7) # seconds

class Person():
    _id_counter = 1  # class‐level counter
    # Variables iniciales de la clase Person
    def __init__(self, x, y, path, infected=False, asymptomatic = False, speed = 0, infection_radius = 0):
        # assign unique ID and increment counter
        self.id = Person._id_counter
        Person._id_counter += 1
        # Position variables
        self.max_speed = speed * 20
        self.acceleration_factor = 200
        self.position = np.array([x, y], dtype=float) # Actual position of the person
        self.velocity = np.random.rand(2) * self.max_speed # actual velocity of the person
        self.radius = PERSON_RADIUS  
        self.path_index = 0 # Index of the path that is actually following
        self.path_threshold = 35  # Distance to consider waypoint reached
        self.active = True # True before checkout process
        self.path = path  # Each person gets its own path
        self.pulse_phase = 0  # Para el efecto de pulso
        # Checkout logic
        self.checkout = False # True in checkout process
        self.checkout_coords = [0, 0] # Position in the checkout logic
        # Exit logic
        self.exit = False # True in the exit process of the agent
        # Logic infection
        self.infected = infected
        self.asymptomatic = asymptomatic
        if self.asymptomatic:
            self.base_color = YELLOW
        elif self.infected:
            self.base_color = RED
        else:
            self.base_color = BLUE
        self.infection_radius = infection_radius
        # Add waiting-related attributes
        self.waiting = False
        self.wait_time = random.uniform(*WALK_WAIT_RANGE)  # Wait between 0.5-2 seconds        
        self.checkout_wait_time = get_checkout_time()
        self.wait_start_time = 0
            
    def follow_path(self, sim_time, dt):
        # Normal path process
        if self.active:
            target = self.path[self.path_index]
            direction = target - self.position
            distance = np.linalg.norm(direction)
            
            # Definir los puntos donde NO debe esperar
            x_value = self.path[self.path_index][0]
            is_special_point = x_value in [275, 1625]

            if distance < self.path_threshold:
                # Solo espera en waypoints intermedios, que NO son especiales
                if (
                    2 < self.path_index < len(self.path) - 1 and  # waypoints intermedios
                    not self.waiting and
                    not is_special_point
                ):
                    # Iniciar espera
                    self.waiting = True
                    self.wait_start_time = sim_time
                    self.velocity = np.zeros(2)  # Detenerse
                elif self.waiting:
                    # Checar si terminó de esperar
                    if sim_time - self.wait_start_time > self.wait_time:
                        self.waiting = False
                        self.path_index += 1
                else:
                    # Para los puntos especiales, los dos primeros y el último: avanzar sin esperar
                    self.path_index += 1

                # Si llegó al final, desactiva el camino normal y activa checkout process
                if self.path_index >= len(self.path):
                    self.active = False
                    self.checkout = True
                    # Calculate the best new position for the person
                    line, self.checkout_coords = best_slot(checkout_map)
                    # Register in the chekout map the position of the person
                    line, idx = register_person(checkout_map, person_id=self.id, coords=self.checkout_coords )
            elif distance > 0 and not self.waiting:
                direction_normalized = direction / distance
                # Scale acceleration by dt and our acceleration factor
                self.velocity += direction_normalized * (self.acceleration_factor * dt)
                # Limit speed
                speed = np.linalg.norm(self.velocity)
                if speed > self.max_speed:
                    self.velocity = (self.velocity / speed) * self.max_speed
        # Checkout process
        elif self.checkout == True:
            target = np.array(self.checkout_coords)
            direction = target - self.position
            distance = np.linalg.norm(direction)

            if distance < self.path_threshold:
                line, idx = find_line_and_idx_by_coords(checkout_map, self.checkout_coords)
                if line is None:
                    # safety: re-acquire a spot
                    line, self.checkout_coords = best_slot(checkout_map)
                    register_person(checkout_map, self.id, self.checkout_coords)
                    return

                slots = checkout_map[line]
                last_idx = len(slots) - 1
                at_final_slot = (idx == last_idx) or (self.checkout_coords[1] == FINAL_Y)

                if at_final_slot:
                    # Wait only at the final slot for checkout duration
                    if not self.waiting:
                        self.waiting = True
                        self.wait_start_time = sim_time
                        self.velocity = np.zeros(2)
                    else:
                        if sim_time - self.wait_start_time > self.checkout_wait_time:
                            # Done paying; leave queue
                            self.waiting = False
                            self.checkout = False
                            # Activate the exit process
                            self.exit = True # Activate exit process
                            self.path_index = 0 # reset the path index
                            self.path = exit_path_creation(self.position[0], self.position[1]) # Create exit path
                            unregister_person(checkout_map, self.id)
                else:
                    # INTERMEDIATE SLOTS: stand still here, do not roam
                    self.velocity = np.zeros(2)
                    self.waiting = True  # freeze at current slot

                    # If the next slot toward cashier is free, advance
                    if slots[idx + 1][2] == -1:
                        self.waiting = False  # allow movement toward the next slot
                        unregister_person(checkout_map, self.id)
                        next_coords = slots[idx + 1][:2]
                        register_person(checkout_map, self.id, next_coords)
                        self.checkout_coords = next_coords
                        # (movement vector will be set below on the next tick)
            elif distance > 0 and not self.waiting:
                direction_normalized = direction / distance
                # Scale acceleration by dt and our acceleration factor
                self.velocity += direction_normalized * (self.acceleration_factor * dt)
                # Limit speed
                speed = np.linalg.norm(self.velocity)
                if speed > self.max_speed:
                    self.velocity = (self.velocity / speed) * self.max_speed
        # Final path process
        if self.exit:
            target = self.path[self.path_index]
            direction = target - self.position
            distance = np.linalg.norm(direction)
            
            # Definir los puntos donde NO debe esperar
            x_value = self.path[self.path_index][0]
            is_special_point = x_value in [275, 1625]

            if distance < self.path_threshold:
                # Para los puntos especiales, los dos primeros y el último: avanzar sin esperar
                self.path_index += 1

                # Si llegó al final, desactiva el camino normal y activa checkout process
                if self.path_index >= len(self.path):
                    self.exit = False
            elif distance > 0 and not self.waiting:
                direction_normalized = direction / distance
                # Scale acceleration by dt and our acceleration factor
                self.velocity += direction_normalized * (self.acceleration_factor * dt)
                # Limit speed
                speed = np.linalg.norm(self.velocity)
                if speed > self.max_speed:
                    self.velocity = (self.velocity / speed) * self.max_speed

    def update(self, people, walls, sim_time, dt):
        if not self.active and not self.checkout and not self.exit:
            return

        # Always update intent/targets first
        self.follow_path(sim_time, dt)

        # If in checkout:
        if self.checkout:
            # If waiting at a slot, don't move
            if self.waiting:
                return
            # Only basic movement (no separation/wall forces)
            speed = np.linalg.norm(self.velocity)
            if speed > self.max_speed:
                self.velocity = (self.velocity / speed) * self.max_speed
            # Multiply by dt to make frame-rate independent
            self.position += self.velocity * dt
            self.position = np.clip(self.position, [0, 0], [WIDTH, HEIGHT])
            return

        # Normal world movement (not in checkout)
        if self.waiting:
            return
            
        # Separation forces with proper scaling
        separation = np.zeros(2)
        for other in people:
            if other != self and other.active:
                dist = np.linalg.norm(self.position - other.position)
                if dist < SEPARATION_RADIUS:
                    separation += (self.position - other.position) / (dist + 0.0001)
        
        for wall in walls:
            dist_to_wall = self.distance_to_wall(wall)
            if dist_to_wall < WALL_MARGIN:
                separation += (self.position - wall[:2]) / (dist_to_wall + 0.0001)
        
        # Apply separation forces with proper scaling
        self.velocity += separation * (self.acceleration_factor * dt)
        
        # Limit speed
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity = (self.velocity / speed) * self.max_speed
        
        # Apply movement
        self.position += self.velocity * dt
        self.position = np.clip(self.position, [0, 0], [WIDTH, HEIGHT])
    
    def distance_to_wall(self, wall):
        x1, y1, x2, y2 = wall
        px, py = self.position
        line_length = np.linalg.norm(np.array([x2 - x1, y2 - y1]))
        if line_length == 0:
            return np.linalg.norm(self.position - np.array([x1, y1]))
        t = max(0, min(1, np.dot([px - x1, py - y1], [x2 - x1, y2 - y1]) / line_length**2))
        closest_point = np.array([x1 + t * (x2 - x1), y1 + t * (y2 - y1)])
        return np.linalg.norm(self.position - closest_point)
    
    def draw(self, screen, sim_time):
        if not self.active and not self.checkout and not self.exit:
            return

        if self.infected or self.asymptomatic:
            # Tiempo animado en segundos
            time = sim_time # más suave que *0.005

            # Pulso de tamaño usando seno (entre 2.5x y 3.5x del radio)
            pulse_scale = self.infection_radius * (1 + math.sin(time)) / 2

            outer_radius = max(1, int(pulse_scale))

            # Color pulsante (entre rosa claro y rojo intenso)
            pulse_color = (
                255,
                int(100 + 50 * math.sin(time)),  # valor entre 50 y 150
                int(100 + 50 * math.sin(time))
            )

            # Dibuja círculo externo
            pygame.draw.circle(screen, pulse_color, self.position, outer_radius, width=2)

        # Dibuja la persona (círculo base)
        pygame.draw.circle(screen, self.base_color, self.position, self.radius)
