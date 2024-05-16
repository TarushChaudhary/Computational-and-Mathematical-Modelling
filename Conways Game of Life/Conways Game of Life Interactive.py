import pygame
import numpy as np

GRID_SIZE = (50, 50)
CELL_SIZE = 10
BUTTON_AREA_HEIGHT = 70

pygame.init()

window = pygame.display.set_mode((GRID_SIZE[0]*CELL_SIZE, GRID_SIZE[1]*CELL_SIZE + BUTTON_AREA_HEIGHT))

grid = np.zeros(GRID_SIZE)

def draw_grid():
    for x in range(GRID_SIZE[0]):
        for y in range(GRID_SIZE[1]):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(window, (255, 255, 255), rect, 1 if grid[x, y] == 0 else 0)

def update():
    global grid
    new_grid = grid.copy()
    for x in range(GRID_SIZE[0]):
        for y in range(GRID_SIZE[1]):
            #Count the number of alive neighbors
            n_alive = np.sum(grid[max(x-1, 0):min(x+2, GRID_SIZE[0]), max(y-1, 0):min(y+2, GRID_SIZE[1])]) - grid[x, y]
            #Any live cell with fewer than two live neighbors dies, as if by underpopulation
            #Any live cell with more than three live neighbors dies, as if by overpopulation.
            if grid[x, y] == 1 and not 2 <= n_alive <= 3:
                new_grid[x, y] = 0
            #Any dead cell with exactly three live neighbors becomes a live cell, as if by reproduction.
            elif grid[x, y] == 0 and n_alive == 3:
                new_grid[x, y] = 1
    grid = new_grid

#Defining the pause button
BUTTON_COLOR = (0, 200, 0)
BUTTON_COLOR_HOVER = (0, 255, 0)
BUTTON_RECT = pygame.Rect(10, GRID_SIZE[1]*CELL_SIZE + 10, 100, 50)
BUTTON_BORDER_COLOR = (255, 255, 255)
BUTTON_BORDER_WIDTH = 2

#Defining the speed buttons
SPEED_BUTTON_RECTS = [pygame.Rect(120, GRID_SIZE[1]*CELL_SIZE + 10, 50, 50),
                      pygame.Rect(180, GRID_SIZE[1]*CELL_SIZE + 10, 50, 50)]
SPEED_BUTTON_COLORS = [(0, 0, 200), (200, 0, 0)]
SPEED_BUTTON_COLORS_HOVER = [(0, 0, 255), (255, 0, 0)]

FONT = pygame.font.Font(None, 24)

speed = 10

def draw_button(paused):
    color = BUTTON_COLOR_HOVER if BUTTON_RECT.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(window, color, BUTTON_RECT)
    pygame.draw.rect(window, BUTTON_BORDER_COLOR, BUTTON_RECT, BUTTON_BORDER_WIDTH)
    text = FONT.render("Pause" if not paused else "Unpause", True, (0, 0, 0))
    window.blit(text, (BUTTON_RECT.x + 5, BUTTON_RECT.y + 5))

def draw_speed_buttons():
    for i, rect in enumerate(SPEED_BUTTON_RECTS):
        color = SPEED_BUTTON_COLORS_HOVER[i] if rect.collidepoint(pygame.mouse.get_pos()) else SPEED_BUTTON_COLORS[i]
        pygame.draw.rect(window, color, rect)
        pygame.draw.rect(window, BUTTON_BORDER_COLOR, rect, BUTTON_BORDER_WIDTH)
        text = FONT.render("+" if i == 1 else "-", True, (0, 0, 0))
        window.blit(text, (rect.x + 20, rect.y + 10))

def check_pause_button_click(pos):
    return BUTTON_RECT.collidepoint(pos)

def check_speed_button_click(pos):
    for i, rect in enumerate(SPEED_BUTTON_RECTS):
        if rect.collidepoint(pos):
            return i
    return -1

def main():
    global speed
    clock = pygame.time.Clock()
    paused = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if check_pause_button_click(event.pos):
                    paused = not paused
                else:
                    speed_button = check_speed_button_click(event.pos)
                    if speed_button == 0:
                        speed = max(1, speed - 1)
                    elif speed_button == 1:
                        speed += 1
                    else:
                        x, y = event.pos
                        grid[x//CELL_SIZE, y//CELL_SIZE] = 1 if event.button == 1 else 0
        window.fill((0, 0, 0))
        draw_grid()
        draw_button(paused)
        draw_speed_buttons()
        if not paused:
            update()
        pygame.display.flip()
        clock.tick(speed)

if __name__ == "__main__":
    main()