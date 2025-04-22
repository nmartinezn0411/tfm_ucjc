import pygame
import random
import numpy as np

# Constants
WIDTH, HEIGHT = 800, 600
NUM_AGENTS = 50
MAX_SPEED = 4
NEIGHBOR_RADIUS = 50
SEPARATION_DISTANCE = 20  # Minimum distance between agents
MARGIN = 20  # Distance from screen edges
BORDER_WIDTH = 20  # Width of middle barriers
AVOID_FORCE = 1 # Strength of obstacle avoidance force

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Define obstacle positions (Two vertical walls in the middle)
OBSTACLES = [
    pygame.Rect(WIDTH // 3 - BORDER_WIDTH // 2, HEIGHT // 4, BORDER_WIDTH, HEIGHT // 2),
    pygame.Rect(2 * WIDTH // 3 - BORDER_WIDTH // 2, HEIGHT // 4, BORDER_WIDTH, HEIGHT // 2)
]

class Agent:
    def __init__(self):
        self.position = np.array([random.uniform(MARGIN, WIDTH - MARGIN), random.uniform(MARGIN, HEIGHT - MARGIN)])
        self.velocity = np.array([random.uniform(-MAX_SPEED, MAX_SPEED), random.uniform(-MAX_SPEED, MAX_SPEED)])

    def update(self, agents, mouse_pos):
        acceleration = self.flock(agents, mouse_pos)
        acceleration += self.avoid_obstacles()  # Avoid obstacles

        self.velocity += acceleration
        speed = np.linalg.norm(self.velocity)
        if speed > MAX_SPEED:
            self.velocity = (self.velocity / speed) * MAX_SPEED
        self.position += self.velocity

        # Ensure agents stay within screen bounds
        self.avoid_walls()

    def flock(self, agents, mouse_pos):
        separation, alignment, cohesion = np.zeros(2), np.zeros(2), np.zeros(2)
        count = 0
        
        for agent in agents:
            if agent == self:
                continue
            distance = np.linalg.norm(self.position - agent.position)
            if distance < NEIGHBOR_RADIUS:
                if distance < SEPARATION_DISTANCE:
                    separation += (self.position - agent.position) / (distance + 1e-5)
                alignment += agent.velocity
                cohesion += agent.position
                count += 1
        
        if count > 0:
            separation /= count
            alignment /= count
            cohesion = (cohesion / count) - self.position

        # Mouse attraction
        if mouse_pos:
            mouse_vector = np.array(mouse_pos)
            direction_to_mouse = mouse_vector - self.position
            attraction_force = direction_to_mouse / (np.linalg.norm(direction_to_mouse) + 1e-5)
        else:
            attraction_force = np.zeros(2)

        return (separation * 2.0) + (alignment * 0.1) + (cohesion * 0.05) + (attraction_force * 0.5)

    def avoid_walls(self):
        """ Prevent agents from touching screen edges """
        if self.position[0] < MARGIN:
            self.velocity[0] = abs(self.velocity[0])
        if self.position[0] > WIDTH - MARGIN:
            self.velocity[0] = -abs(self.velocity[0])
        if self.position[1] < MARGIN:
            self.velocity[1] = abs(self.velocity[1])
        if self.position[1] > HEIGHT - MARGIN:
            self.velocity[1] = -abs(self.velocity[1])

    def avoid_obstacles(self):
        """ Steer agents away from obstacles before they hit them. """
        avoidance = np.zeros(2)
        for obstacle in OBSTACLES:
            closest_x = np.clip(self.position[0], obstacle.left, obstacle.right)
            closest_y = np.clip(self.position[1], obstacle.top, obstacle.bottom)
            closest_point = np.array([closest_x, closest_y])
            distance = np.linalg.norm(self.position - closest_point)

            if distance < NEIGHBOR_RADIUS:
                avoidance += (self.position - closest_point) / (distance + 1e-5) * AVOID_FORCE

        return avoidance

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, self.position.astype(int), 4)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    agents = [Agent() for _ in range(NUM_AGENTS)]
    
    running = True
    while running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Draw obstacles
        for obstacle in OBSTACLES:
            pygame.draw.rect(screen, GRAY, obstacle)

        for agent in agents:
            agent.update(agents, mouse_pos)
            agent.draw(screen)
        
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
