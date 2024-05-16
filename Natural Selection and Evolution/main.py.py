import pygame
import random
import sys
import math
import numpy as np
# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Natural Selection Simulation')

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)

# Clock to control game speed
clock = pygame.time.Clock()
FPS = 30

def run_simulation():
    running = True
    paused = False 
    selected_creature = None
    
    simulation_speed = 1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Get the position of the mouse click
                pos = pygame.mouse.get_pos()
                # Check for creature click
                for creature in creatures:
                    if creature.rect.collidepoint(pos):
                        selected_creature = creature
                        paused = not paused  # Toggle pause on click
                        break
                for predator in predators:
                    if predator.rect.collidepoint(pos):
                        selected_creature = predator
                        paused = not paused  # Toggle pause on click
                        break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused  # Toggle pause
                if event.key == pygame.K_UP:
                    simulation_speed += 1  # Increase speed
                if event.key == pygame.K_DOWN:
                    simulation_speed = max(1, simulation_speed - 1)

        if selected_creature:
            font = pygame.font.Font(None, 24)
            details = [
                f"Energy: {selected_creature.energy}",
                f"Size: {selected_creature.size}",
                f"Speed: {selected_creature.speed}",
                f"Color: {selected_creature.color}",
                f"Age: {selected_creature.age}",
                f"Generation: {selected_creature.generation}",
                f"Vision: {selected_creature.vision}"
                f"Camouflaged: {selected_creature.is_camouflaged}"
            ]
            for index, detail in enumerate(details):
                text = font.render(detail, True, (0, 0, 0))
                screen.blit(text, (10, 10 + 30 * index))
        
        
        if not paused:
            # Update simulation
            creatures.update(foods, predators, terrains)
            predators.update(creatures)

            
            creatures.update(foods, predators, terrains)  # Move the creatures
            predators.update(creatures)
            for creature in creatures:
                food_collided = pygame.sprite.spritecollide(creature, foods, True)
                if food_collided:
                    creature.energy += 50  # Increase energy for each food eaten


            # Repopulate food randomly
            if len(foods) < 10:
                x, y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)
                foods.add(Food(x, y))
            
            screen.fill(WHITE)
            terrains.draw(screen)
            creatures.draw(screen)
            predators.draw(screen)
            foods.draw(screen)
            pygame.display.flip()
            clock.tick(FPS + simulation_speed)  # Adjust simulation speed
        
    pygame.quit()
    sys.exit()


def mutate_value(value, mutation_rate=0.1, max_change=0.1):
    """ Randomly mutate a value by a percentage of its current value. """
    if random.random() < mutation_rate:
        change = value * max_change
        value += random.uniform(-change, change)
    return max(1, value)  # Ensure values do not drop below 1

def clamp_color(value):
    """Clamp the color value to be within the valid RGB range and ensure it's an integer."""
    return max(0, min(int(value), 255))

class Creature(pygame.sprite.Sprite):
    def __init__(self, x, y, size, speed, color, vision, generation=1):
        super().__init__()
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.size = size
        self.speed = speed
        self.color = color
        self.vision = vision
        self.energy = 50 * size
        self.age = 0
        self.is_camouflaged = False
        self.generation = generation
        self.direction = random.choice([(self.speed, 0), (-self.speed, 0), (0, self.speed), (0, -self.speed)])
        self.direction_timer = 0
        self.direction_change_frequency = 180  # Change direction every 3 seconds (60 FPS * 3)
    
    def update(self, food_group, predator_group, terrain_group):
        self.age += 1
        if self.age > 200:
            self.reproduce()
        
        self.check_terrain_effects(terrain_group)

        nearest_food = self.get_nearest(food_group)
        if nearest_food and self.can_see(nearest_food):
            self.move_towards(nearest_food)
        else:
            self.search_for_food()
        
        nearest_predator = self.get_nearest(predator_group)
        if nearest_predator and self.can_see(nearest_predator):
            self.run_from(nearest_predator)
        
        self.energy -= self.size * 0.1
        if self.energy <= 0:
            self.kill()

    def search_for_food(self):
        if self.direction_timer == 0:
            self.direction = random.choice([(self.speed, 0), (-self.speed, 0), (0, self.speed), (0, -self.speed)])
            self.direction_timer = self.direction_change_frequency
        else:
            self.rect.x += self.direction[0]
            self.rect.y += self.direction[1]
            self.direction_timer -= 1

    def get_nearest(self, group):
        nearest = None
        min_distance = float('inf')
        for obj in group:
            distance = self.distance_to(obj)
            if distance < min_distance:
                min_distance = distance
                nearest = obj
        return nearest

    def distance_to(self, other):
        return math.hypot(self.rect.x - other.rect.x, self.rect.y - other.rect.y)

    def can_see(self, other):
        return self.distance_to(other) <= self.vision

    def check_terrain_effects(self, terrain_group):

        for terrain in terrain_group:
            if self.rect.colliderect(terrain.rect):

                if self.color_distance(self.color, terrain.color) < 50:  # Threshold for color similarity
                    self.is_camouflaged = True
                    break

                else:
                    self.is_camouflaged = False

    def color_distance(self, color1, color2):
        # Calculate the Euclidean distance between two colors
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(color1, color2)))


    def move_towards(self, target):
        vector_x = target.rect.centerx - self.rect.centerx
        vector_y = target.rect.centery - self.rect.centery
        distance = math.sqrt(vector_x ** 2 + vector_y ** 2)
        if distance > 0:
            vector_x /= distance
            vector_y /= distance
        self.rect.x += vector_x * self.speed
        self.rect.y += vector_y * self.speed

    def run_from(self, predator):
        vector_x = predator.rect.centerx - self.rect.centerx
        vector_y = predator.rect.centery - self.rect.centery
        distance = math.sqrt(vector_x ** 2 + vector_y ** 2)
        if distance > 0:
            vector_x /= distance
            vector_y /= distance
        self.rect.x -= vector_x * self.speed
        self.rect.y -= vector_y * self.speed

    def reproduce(self):
        predator_mutation_chance = 0.01
        new_size = mutate_value(self.size)
        new_speed = mutate_value(self.speed, max_change=0.05)  # Smaller mutation range for speed
        new_color = tuple(clamp_color(mutate_value(c)) for c in self.color)
        new_vision = mutate_value(self.vision, max_change=0.1)
        if self.age > 200:
            # Create 2 new creatures at the same location with similar traits
            self.age = 0  # Reset age after reproduction
            for _ in range(np.random.randint(1, 3)):
                if random.random() < predator_mutation_chance:
                    new_predator = Predator(self.rect.x, self.rect.y, new_size, new_speed, new_color, new_vision, self.generation + 1)
                    predators.add(new_predator)
                else:
                    new_creature = Creature(self.rect.x, self.rect.y, new_size, new_speed, new_color, new_vision, self.generation + 1)
                    creatures.add(new_creature)

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))


class Predator(Creature):
    def __init__(self, x, y, size, speed, color, vision, generation=1):
        super().__init__(x, y, size, speed, color, vision)
        self.vision = vision  # Ensure vision is defined and used
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, self.image.get_rect())  # Draw a square
        self.prey_consumed = 0
    def update(self, prey_group):
        
        # Find the nearest prey within vision
        nearest_prey = None
        min_distance = float('inf')
        smaller_prey_list = [prey for prey in prey_group if prey.size < self.size]

        for prey in smaller_prey_list:
            distance = self.distance_to(prey)
            if distance < min_distance and distance <= self.vision:
                min_distance = distance
                nearest_prey = prey
        
        # Move towards the nearest prey if it exists
        if nearest_prey:
            self.move_towards(nearest_prey)
            if self.rect.colliderect(nearest_prey.rect):
                prey_group.remove(nearest_prey)
                self.prey_consumed += 1
                self.energy += 50  # Increase energy for each prey eaten

                if self.prey_consumed >= 5:
                    self.reproduce()
                    self.prey_consumed = 0

        # Energy and age update (if using)
        self.energy -= self.size * 0.2  # Example: adjust energy decrement based on activity
        if self.energy <= 0:
            self.kill()  # Predator dies of starvation

        if self.age > 200:
            self.reproduce()
            self.age = 0  # Reset age after reproduction

    def distance_to(self, other_sprite):
        # Calculate Euclidean distance to another sprite
        return math.hypot(self.rect.centerx - other_sprite.rect.centerx, self.rect.centery - other_sprite.rect.centery)

    def move_towards(self, prey):
        # Calculate vector towards the prey and move in that direction
        prey_x, prey_y = prey.rect.center
        vector_x = prey_x - self.rect.centerx
        vector_y = prey_y - self.rect.centery
        distance = math.hypot(vector_x, vector_y)
        if distance > 0:  # Avoid division by zero
            vector_x /= distance
            vector_y /= distance
        
        # Move towards the prey
        self.rect.x += vector_x * self.speed
        self.rect.y += vector_y * self.speed

        def reproduce(self):
            mutation_chance = 0.05
            new_size = mutate_value(self.size)
            new_speed = mutate_value(self.speed, max_change=0.05)  # Smaller mutation range for speed
            new_color = tuple(clamp_color(mutate_value(c)) for c in self.color)
            new_vision = mutate_value(self.vision, max_change=0.1)
            if random.random() < mutation_chance:
                new_herbivore = Creature(self.rect.x, self.rect.y, new_size, new_speed, new_color, new_vision, self.generation + 1)
                creatures.add(new_herbivore)
            else:
                new_predator = Predator(self.rect.x, self.rect.y, new_size, new_speed, new_color, new_vision, self.generation + 1)
                predators.add(new_predator)
            # Create 2 new predators at the same location with similar traits
            


class Terrain(pygame.sprite.Sprite):
    def __init__(self, terrain_type, color, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.terrain_type = terrain_type
        self.color = color

    def affect_creature(self, creature):
        # Modify creature's speed and visibility based on the terrain
        if creature.color == self.color:  # Simple camouflage check
            creature.is_camouflaged = True
        else:
            creature.is_camouflaged = False



# Sprite groups
creatures = pygame.sprite.Group()
foods = pygame.sprite.Group()
predators = pygame.sprite.Group()
terrains = pygame.sprite.Group()

# Create some terrain
terrains.add(Terrain('forest', GREEN, 200, 200, 200, 200))
terrains.add(Terrain('water', BLUE, 500, 300, 100, 100))
terrains.add(Terrain('desert', (255, 255, 0), 600, 100, 100, 100))
terrains.add(Terrain('snow', WHITE, 100, 500, 100, 100))
terrains.add(Terrain('mountain',BROWN, 400, 500, 200, 100))

# Initialize creatures
for _ in range(20):  # Adjust number as needed
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    size = random.randint(5, 20)
    speed = max(1, 30 - size)  # Larger creatures are slower
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    vision = random.randint(100, 200)
    creatures.add(Creature(x, y, size, speed, color, vision))

# Initialize predators
for _ in range(5):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    size = random.randint(10, 20)
    speed = max(1, 35 - size)
    color = (random.randint(0, 255), 0, 0)  # Predators are variations of red
    vision = random.randint(150, 250)
    predators.add(Predator(x, y, size, speed, color, vision))

# Initialize food
for _ in range(50):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    foods.add(Food(x, y))

# Initialize terrain
for _ in range(10):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    width = random.randint(50, 100)
    height = random.randint(50, 100)

running = True
while running:
    run_simulation()