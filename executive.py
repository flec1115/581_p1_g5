
# from pygame_widgets.slider import Slider
# from pygame_widgets.textbox import TextBox
from cell import Cell
import random
import pygame

NUMBER_OF_MINES = 10
MIN_MINES = 10
MAX_MINES = 20
GRID_SIZE = 10
CELL_SIZE = 40
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
safe_cells = GRID_SIZE * GRID_SIZE - NUMBER_OF_MINES
revealed_safe_cells = 0

button_rect = pygame.Rect(100, 150, 200, 60)
slider_rect = pygame.Rect(100, 220, 200, 20)
handle_rect = pygame.Rect(100, 210, 20, 40)
handle_color = (255,0,0)
slider_color = (200, 200, 200)

grid = [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def recursive_sweep(r, c):
    global revealed_safe_cells

    if grid[r][c].is_revealed:
        return

    grid[r][c].is_revealed = True
    revealed_safe_cells += 1
    if grid[r][c].adjacent_mines > 0:
        return
    else:
        for row_offset in [-1, 0, 1]:
            for col_offset in [-1, 0, 1]:
                if row_offset == 0 and col_offset == 0:
                    continue
                if 0 <= r + row_offset < GRID_SIZE and 0 <= c + col_offset < GRID_SIZE:
                    recursive_sweep(r+row_offset, c+col_offset)


def first_click(input_row, input_col):
    protected = set()
    for row_offset in [-1, 0, 1]:
        for col_offset in [-1, 0, 1]:
            if 0 <= input_row + row_offset < GRID_SIZE and 0 <= input_col + col_offset < GRID_SIZE:
                protected.add((input_row+row_offset, input_col+col_offset)) 

    possible = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if (i, j) not in protected:
                possible.append((i, j))

    mine_locations = random.sample(possible, NUMBER_OF_MINES)
    for i, j in mine_locations:
        grid[i][j].has_mine = True

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            for row_offset in [-1, 0, 1]:
                for col_offset in [-1, 0, 1]:
                    if row_offset == 0 and col_offset == 0:
                        continue
                    if 0 <= i + row_offset < GRID_SIZE and 0 <= j + col_offset < GRID_SIZE:
                        if grid[i+row_offset][j+col_offset].has_mine:
                            grid[i][j].adjacent_mines += 1

    recursive_sweep(input_row, input_col)


def reveal(input_row, input_col):
    if grid[input_row][input_col].has_mine:
        return False

    recursive_sweep(input_row, input_col)

    if revealed_safe_cells == safe_cells:
        return "win"

    return True

def draw_cell(screen, row, col):
    x = col * CELL_SIZE
    y = row * CELL_SIZE
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    #This block of code was adapted from GitHub CoPilot when asking how to setup a gameboard in pygame
    #All code was subesequently written manually, but it was adapted from the AI
    if grid[row][col].is_revealed:
        if grid[row][col].has_mine:
            pygame.draw.rect(screen, (255, 80, 80), rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            font = pygame.font.Font(None, 28)
            text = font.render("*", True, (0, 0, 0))
            screen.blit(text, (x + 12, y + 6))
        else:
            pygame.draw.rect(screen, (207, 194, 154), rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            if grid[row][col].adjacent_mines > 0:
                font = pygame.font.Font(None, 28)
                text = font.render(str(grid[row][col].adjacent_mines), True, (0, 0, 0))
                screen.blit(text, (x + 14, y + 6))
    else:
        pygame.draw.rect(screen, (76, 175, 80), rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        if grid[row][col].is_flagged:
            font = pygame.font.Font(None, 28)
            text = font.render("F", True, (255, 0, 0))
            screen.blit(text, (x + 10, y + 6))


def draw_board(screen):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            draw_cell(screen, row, col)


def run_game():
    global NUMBER_OF_MINES
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Minesweeper")
    first_move_done = False
    game_over = False
    dragging=False
    slider_value_picked = False
    slider_value = 10

    #Game loop set up with reference from Geeks to Geeks PyGame tutorial
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if not slider_value_picked:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if handle_rect.collidepoint(event.pos):
                        dragging = True
                    elif button_rect.collidepoint(event.pos):
                        slider_value_picked = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False
                elif event.type == pygame.MOUSEMOTION and dragging:
                    mouse_x, _ = event.pos
                    #This line was generated by AI when asking how to get the slider handle to stay on the track and centered
                    #It was then edited to use mouse_x as it was initially event.pos[0] but mouse_x is used multiple times
                    handle_rect.x = max(slider_rect.x, min(mouse_x - handle_rect.width//2, slider_rect.right - handle_rect.width))

                    slider_percent = (mouse_x - slider_rect.x) / slider_rect.width
                    slider_percent = max(0, min(1, slider_percent))
                    slider_value = round(MIN_MINES + slider_percent * (MAX_MINES - MIN_MINES))

                if slider_value_picked:
                    NUMBER_OF_MINES = slider_value
                    

            
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                col = event.pos[0]//CELL_SIZE
                row = event.pos[1]//CELL_SIZE

                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    if event.button == 1:
                        if not first_move_done:
                            first_click(row, col)
                            first_move_done = True
                        else:
                            result = reveal(row, col)
                            if not result:
                                game_over = True
                                print("Boom.")
                            elif result == "win":
                                game_over = True
                                print("You win!")
                    elif event.button == 3:
                        if grid[row][col].is_flagged:
                            grid[row][col].is_flagged = False
                        else:
                            grid[row][col].is_flagged = True
        if not slider_value_picked:
            #draw the slider
            screen.fill((255,255,255))
            pygame.draw.rect(screen, slider_color, slider_rect)
            pygame.draw.rect(screen, handle_color, handle_rect)
            font = pygame.font.SysFont(None, 36)
            text = font.render(f"Mine Count: {slider_value}", True, (0, 0, 0))
            screen.blit(text, (slider_rect.x, slider_rect.y + 40))

            #draw the start button
            pygame.draw.rect(screen, (73,204,3), button_rect)
            font = pygame.font.SysFont(None, 32)
            text = font.render("Start", True, (255,255,255))
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
        else:
            draw_board(screen)
        pygame.display.flip()
