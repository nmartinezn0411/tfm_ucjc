import pygame
import numpy as np
import sys

# Parameters
WIDTH, HEIGHT = 1800, 1000 # Size of the screen
NUM_PEOPLE = 50 # Number of people
PERSON_RADIUS = 5 # Size of the person
MAX_SPEED = 2 # Speed of the movement
SEPARATION_RADIUS = 10 # Separation between a person and another
WALL_MARGIN = 10 # Space between the person and the center box

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Clase que define el movimiento
class Person:
    def __init__(self, x, y):
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.random.rand(2) * MAX_SPEED
        self.radius = PERSON_RADIUS
        # To follow a certain path
        self.path_index = 0
        self.path_threshold = 20  # Distance to consider waypoint reached
        
    def follow_path(self, path_waypoints):
        if self.path_index < len(path_waypoints):
            target = path_waypoints[self.path_index]
            direction = target - self.position
            distance = np.linalg.norm(direction)
            
            if distance < self.path_threshold:
                self.path_index += 1
            else:
                self.velocity += direction / distance * 0.1


    def update(self, people, walls):
        self.follow_path(path_waypoints)
        # Separation: Avoid crowding local flockmates
        separation = np.zeros(2)
        for other in people:
            if other != self:
                dist = np.linalg.norm(self.position - other.position)
                if dist < SEPARATION_RADIUS:
                    separation += (self.position - other.position) / dist

        # Wall avoidance
        for wall in walls:
            dist_to_wall = self.distance_to_wall(wall)
            if dist_to_wall < WALL_MARGIN:
                separation += (self.position - wall[:2]) / dist_to_wall

        # Update velocity and position
        self.velocity += separation * 0.1
        self.velocity = self.velocity / np.linalg.norm(self.velocity) * MAX_SPEED
        self.position += self.velocity

        # Keep within screen bounds
        self.position = np.clip(self.position, [0, 0], [WIDTH, HEIGHT])

    def distance_to_wall(self, wall):
        # Calculate distance to a wall (line segment)
        x1, y1, x2, y2 = wall
        px, py = self.position
        line_length = np.linalg.norm(np.array([x2 - x1, y2 - y1]))
        if line_length == 0:
            return np.linalg.norm(self.position - np.array([x1, y1]))
        t = max(0, min(1, np.dot([px - x1, py - y1], [x2 - x1, y2 - y1]) / line_length**2))
        closest_point = np.array([x1 + t * (x2 - x1), y1 + t * (y2 - y1)])
        return np.linalg.norm(self.position - closest_point)

    def draw(self, screen):
        pygame.draw.circle(screen, RED, self.position.astype(int), self.radius)

# Follow path
path_waypoints = [
    np.array([100, 100]),
    np.array([1700, 100]),
    np.array([1700, 900]),
    np.array([100, 900]),
    np.array([100, 100])  # Loop back to start
]
# Create people
people = [Person(np.random.randint(0, WIDTH), np.random.randint(0, HEIGHT)) for _ in range(NUM_PEOPLE)]

# Define walls (as line segments: [x1, y1, x2, y2])
walls = [
    # Screen boundaries
    [0, 0, WIDTH, 0],  # Top wall
    [WIDTH, 0, WIDTH, HEIGHT],  # Right wall
    [WIDTH, HEIGHT, 0, HEIGHT],  # Bottom wall
    [0, HEIGHT, 0, 0],  # Left wall
    

    # Middle walls (black walls)
    [WIDTH // 2 - 50, HEIGHT // 2 - 50, WIDTH // 2 + 50, HEIGHT // 2 - 50],  # Top horizontal wall
    [WIDTH // 2 - 50, HEIGHT // 2 + 50, WIDTH // 2 + 50, HEIGHT // 2 + 50],  # Bottom horizontal wall
    [WIDTH // 2 - 50, HEIGHT // 2 - 50, WIDTH // 2 - 50, HEIGHT // 2 + 50],  # Left vertical wall
    [WIDTH // 2 + 50, HEIGHT // 2 - 50, WIDTH // 2 + 50, HEIGHT // 2 + 50],  # Right vertical wall
]

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    # Update and draw people
    for person in people:
        person.update(people, walls)
        person.draw(screen)

    # Draw walls
    for wall in walls:
        pygame.draw.line(screen, BLACK, (wall[0], wall[1]), (wall[2], wall[3]), 2)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()