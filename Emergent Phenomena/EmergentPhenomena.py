import pygame
import random
import numpy as np

atoms=[]
window_size = 600
pygame.init()
window = pygame.display.set_mode((window_size, window_size))


def draw(surface, x, y, color, size):
    for i in range(0, size):
        pygame.draw.line(surface, color, (x, y-1), (x, y+2), abs(size))

def rules_window():
    pass

def atom(x, y, c):
    return {"x": x, "y": y, "vx": 0, "vy": 0, "color": c}

def randomxy():
    return round(random.random()*window_size + 1)

def create(number, color):
    group = []
    for i in range(number):
        group.append(atom(randomxy(), randomxy(), color))
        atoms.append((group[i]))
    return group

def rule(atoms1, atoms2, g):
    # Loop over all atoms in the first group
    for i in range(len(atoms1)):
        # Initialize force components
        fx = 0
        fy = 0
        # Determine the starting index for the second loop
        start_index = i+1 if atoms1 is atoms2 else 0
        # Loop over all atoms in the second group, starting from the determined index
        for j in range(start_index, len(atoms2)):
            # Get the current atom from the first group and the other atom from the second group
            a = atoms1[i]
            b = atoms2[j]
            # Calculate the distance in x and y directions
            dx = a["x"] - b["x"]
            dy = a["y"] - b["y"]
            # Calculate the actual distance using Pythagorean theorem
            d = (dx*dx + dy*dy)**0.5
            # If the distance is within a certain range (greater than 0 and less than 80 in this case)
            if( d > 0 and d < 80):
                # Calculate the force using the given constant g and the distance
                F = g/d
                # Add the force components to the total force
                fx += F*dx
                fy += F*dy
        # Update the velocity of the atom by adding the force (divided by 2 for some damping effect)
        a["vx"] = (a["vx"] + fx)*0.5
        a["vy"] = (a["vy"] + fy)*0.5
        # Update the position of the atom by adding the velocity
        a["x"] += a["vx"]
        a["y"] += a["vy"]
        # If the atom hits the edge of the window, reverse its velocity to make it bounce back
        if(a["x"] <= 0 or a["x"] >= window_size):
            a["vx"] *=-1
        if(a["y"] <= 0 or a["y"] >= window_size):
            a["vy"] *=-1


def generate_interaction_rules(atom_types, num_rules):
    rules = []
    for _ in range(num_rules):
        atom_type1, atom_type2 = random.sample(atom_types, 2)
        weight = np.random.uniform(-1, 1)
        rules.append((atom_type1, atom_type2, weight))
    return rules

colors = ["yellow", "red", "blue", "green"]
      
yellow = create(200, colors[0])
red = create(200, colors[1])
blue = create(200, colors[2])
green = create(200, colors[3])

colours = [yellow, red, blue, green]
interaction_rules = generate_interaction_rules(colours, 4)

print(interaction_rules)
run = True
while run:
    window.fill(0)
    """for i in interaction_rules:
        item1, item2, wt = i
        rule(item1, item2, wt)  """
    rule(yellow, red, 0.5)
    rule(green, blue, -0.7)
    rule(red, blue, 0.5)
    rule(green, yellow, -0.7)
    rule(blue, yellow, 0.5)    
    
    for i in range(len(atoms)):
        draw(window,  atoms[i]["x"], atoms[i]["y"], atoms[i]["color"], 3)
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.flip()
pygame.quit()
exit()