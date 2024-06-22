import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# random.seed(40)

# Set up display
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Airplane Simulation")

# Colors
SKY_BLUE = (145, 255, 255)  # Light blue color for sky
WHITE = (255, 255, 255)
CLOUD_GRAY = (140, 140, 140)  # Gray color for clouds
GREEN = (0, 128, 0)  # Green color for airplane
RED = (255, 0, 0)

# Load airplane image
airplane_img = pygame.image.load("airplane.png")
airplane_img = pygame.transform.scale(airplane_img, (60, 40))

# Airplane class
class Airplane:
    def __init__(self, start, destination):
        self.x = start[0]
        self.y = start[1]
        self.destination = destination
        self.speed = 2
        self.direction = random.uniform(0, 2 * math.pi)
        self.reached_destination = False

    def update(self):
        if not self.reached_destination:
            dx = self.speed * math.cos(self.direction)
            dy = self.speed * math.sin(self.direction)
            self.x += dx
            self.y += dy

            # Check if airplane reached destination
            if math.sqrt((self.x - self.destination[0]) ** 2 + (self.y - self.destination[1]) ** 2) < 10:
                self.reached_destination = True

    def draw(self):
        rotated_image = pygame.transform.rotate(airplane_img, math.degrees(-self.direction))
        screen.blit(rotated_image, (self.x - rotated_image.get_width() / 2, self.y - rotated_image.get_height() / 2))

    def avoid_obstacle(self, obstacles):
        # No obstacle avoidance if destination is reached
        if not self.reached_destination:
            # Calculate angle to destination
            angle_to_destination = math.atan2(self.destination[1] - self.y, self.destination[0] - self.x)

            # Determine neighboring directions
            num_directions = 36  # Number of directions to consider
            direction_step = 2 * math.pi / num_directions
            directions = [angle_to_destination + direction_step * i for i in range(num_directions)]

            # Find the best direction that avoids obstacles using potential fields
            min_distance = float('inf')
            best_direction = None

            buffer_zone = 30

            for direction in directions:
                dx = self.speed * math.cos(direction)
                dy = self.speed * math.sin(direction)
                new_x, new_y = self.x + dx, self.y + dy

                # Calculate the repulsive force from each obstacle
                repulsive_force_x, repulsive_force_y = 0, 0
                for obstacle in obstacles:
                    cloud_points = [(obstacle.x + 5, obstacle.y + 2), (obstacle.x + 15, obstacle.y + 2),
                                    (obstacle.x + 20, obstacle.y + 8), (obstacle.x + 30, obstacle.y + 8),
                                    (obstacle.x + 35, obstacle.y + 15), (obstacle.x + 45, obstacle.y + 15),
                                    (obstacle.x + 50, obstacle.y + 20), (obstacle.x + 55, obstacle.y + 15),
                                    (obstacle.x + 65, obstacle.y + 15), (obstacle.x + 70, obstacle.y + 8),
                                    (obstacle.x + 80, obstacle.y + 8), (obstacle.x + 85, obstacle.y + 2),
                                    (obstacle.x + 95, obstacle.y + 2), (obstacle.x + 85, obstacle.y - 8),
                                    (obstacle.x + 75, obstacle.y - 15), (obstacle.x + 65, obstacle.y - 8),
                                    (obstacle.x + 55, obstacle.y - 15), (obstacle.x + 50, obstacle.y - 8),
                                    (obstacle.x + 40, obstacle.y - 15), (obstacle.x + 35, obstacle.y - 8),
                                    (obstacle.x + 25, obstacle.y - 8), (obstacle.x + 20, obstacle.y - 15),
                                    (obstacle.x + 10, obstacle.y - 8), (obstacle.x + 5, obstacle.y - 8)]

                    for point in cloud_points:
                        distance = math.sqrt((new_x - point[0]) ** 2 + (new_y - point[1]) ** 2)
                        if distance < buffer_zone:
                            # Calculate the vector from the obstacle to the airplane
                            obstacle_vector_x = self.x - point[0]
                            obstacle_vector_y = self.y - point[1]

                            # Calculate the angle between the obstacle vector and the airplane's direction
                            angle_difference = abs(math.atan2(obstacle_vector_y, obstacle_vector_x) - direction)

                            # Adjust the avoidance direction based on the relative direction to the obstacle
                            avoidance_direction = direction + math.pi / 2 if angle_difference < math.pi / 2 else direction - math.pi / 2

                            # Calculate the repulsive force using the adjusted avoidance direction
                            force_magnitude = 1 / distance  # Inverse proportionality to distance
                            repulsive_force_x += force_magnitude * math.cos(avoidance_direction)
                            repulsive_force_y += force_magnitude * math.sin(avoidance_direction)

                # Calculate the resulting direction considering obstacle avoidance
                resultant_direction = math.atan2(dy + repulsive_force_y, dx + repulsive_force_x)

                # Update best direction if closer to the destination
                distance_to_destination = math.sqrt((new_x - self.destination[0]) ** 2 + (new_y - self.destination[1]) ** 2)
                if distance_to_destination < min_distance:
                    min_distance = distance_to_destination
                    best_direction = resultant_direction

            # Update airplane direction
            if best_direction is not None:
                self.direction = best_direction

# Obstacle class
class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        cloud_points = [(self.x + 5, self.y + 2), (self.x + 15, self.y + 2),
                        (self.x + 20, self.y + 8), (self.x + 30, self.y + 8),
                        (self.x + 35, self.y + 15), (self.x + 45, self.y + 15),
                        (self.x + 50, self.y + 20), (self.x + 55, self.y + 15),
                        (self.x + 65, self.y + 15), (self.x + 70, self.y + 8),
                        (self.x + 80, self.y + 8), (self.x + 85, self.y + 2),
                        (self.x + 95, self.y + 2), (self.x + 85, self.y - 8),
                        (self.x + 75, self.y - 15), (self.x + 65, self.y - 8),
                        (self.x + 55, self.y - 15), (self.x + 50, self.y - 8),
                        (self.x + 40, self.y - 15), (self.x + 35, self.y - 8),
                        (self.x + 25, self.y - 8), (self.x + 20, self.y - 15),
                        (self.x + 10, self.y - 8), (self.x + 5, self.y - 8)]
        pygame.draw.polygon(screen, CLOUD_GRAY, cloud_points)

# Main loop
def main():
    clock = pygame.time.Clock()

    # Generate random source and destination
    start_x = random.choice([50, WIDTH - 50])  # Either at left or right edge
    start_y = random.randint(50, HEIGHT - 50)  # Random y-coordinate within window height
    start = (start_x, start_y)

    dest_x = WIDTH - 50 if start_x == 50 else 50  # Opposite edge of the source
    destination_y = random.randint(50, HEIGHT - 50)  # Random y-coordinate within window height
    destination = (dest_x, destination_y)

    # Ensure the destination is farther than the specified distance
    while math.sqrt((start[0] - destination[0]) ** 2 + (start[1] - destination[1]) ** 2) <= 350:
        destination_y = random.randint(50, HEIGHT - 50)
        destination = (dest_x, destination_y)

    print("Source:", start)
    print("Destination:", destination)

    # Generate random obstacles
    num_obstacles = 30
    obstacles = [Obstacle(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)) for _ in range(num_obstacles)]

    airplane = Airplane(start, destination)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update airplane
        airplane.update()

        # Clear screen
        screen.fill(SKY_BLUE)

        # Draw obstacles
        for obstacle in obstacles:
            obstacle.draw()

        # Draw source and destination
        pygame.draw.circle(screen, GREEN, start, 10)
        pygame.draw.circle(screen, RED, destination, 10)

        # Check for collision with obstacles and avoid them
        airplane.avoid_obstacle(obstacles)

        # Draw airplane
        airplane.draw()

        # Update display
        pygame.display.flip()

        # Cap FPS
        clock.tick(60)

if __name__ == "__main__":
    main()
