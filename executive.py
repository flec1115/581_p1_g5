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
#Layout for the retro style: beveled header panel above the board
BORDER = 12
HEADER_HEIGHT = 56
LABEL_SIZE = 24
BOARD_X = BORDER + LABEL_SIZE
BOARD_Y = BORDER + HEADER_HEIGHT + BORDER + LABEL_SIZE
WINDOW_WIDTH = BOARD_X + WINDOW_SIZE + BORDER
WINDOW_HEIGHT = BOARD_Y + WINDOW_SIZE + BORDER
SAFE_CELLS = GRID_SIZE * GRID_SIZE - NUMBER_OF_MINES
revealed_safe_cells = 0

button_rect = pygame.Rect(132, 300, 160, 50)
slider_rect = pygame.Rect(112, 236, 200, 12)
handle_rect = pygame.Rect(112, 226, 16, 32)
handle_color = (196, 194, 188)
slider_color = (150, 148, 142)

#Retro color palette
FACE = (196, 194, 188)
REVEALED = (212, 210, 204)
HIGHLIGHT = (250, 250, 246)
SHADOW = (122, 120, 114)
TEXT_COLOR = (40, 40, 40)
LED_ON = (255, 170, 30)
LED_OFF = (70, 40, 10)
LED_BG = (22, 16, 10)
NUMBER_COLORS = {1: (30, 60, 200), 2: (20, 125, 40), 3: (200, 30, 30), 4: (30, 30, 120),
                 5: (120, 30, 30), 6: (20, 120, 120), 7: (20, 20, 20), 8: (110, 110, 110)}

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

    if revealed_safe_cells == SAFE_CELLS:
        return "win"

    return True

_fonts = {}


def get_font(size, bold=False):
    #Cache fonts so they aren't recreated for every cell every frame
    if (size, bold) not in _fonts:
        font = pygame.font.Font(None, size)
        font.set_bold(bold)
        _fonts[(size, bold)] = font
    return _fonts[(size, bold)]


def draw_bevel(screen, rect, raised=True, width=3):
    #Light edge top/left and dark edge bottom/right gives the raised 3D look
    light, dark = (HIGHLIGHT, SHADOW) if raised else (SHADOW, HIGHLIGHT)
    for i in range(width):
        left, top = rect.left + i, rect.top + i
        right, bottom = rect.right - 1 - i, rect.bottom - 1 - i
        pygame.draw.line(screen, dark, (left, bottom), (right, bottom))
        pygame.draw.line(screen, dark, (right, top), (right, bottom))
        pygame.draw.line(screen, light, (left, top), (right, top))
        pygame.draw.line(screen, light, (left, top), (left, bottom))


def draw_mine(screen, cx, cy):
    r = CELL_SIZE // 5
    spike = r + 6
    for dx, dy in [(1, 0), (0, 1), (0.7, 0.7), (0.7, -0.7)]:
        pygame.draw.line(screen, (20, 20, 20), (cx - dx * spike, cy - dy * spike),
                         (cx + dx * spike, cy + dy * spike), 3)
    pygame.draw.circle(screen, (20, 20, 20), (cx, cy), r)
    pygame.draw.circle(screen, (235, 235, 235), (cx - r // 3, cy - r // 3), max(2, r // 3))


def draw_flag(screen, cx, cy):
    pygame.draw.rect(screen, (20, 20, 20), (cx - 9, cy + 9, 18, 3))
    pygame.draw.rect(screen, (20, 20, 20), (cx - 5, cy + 6, 10, 3))
    pygame.draw.line(screen, (20, 20, 20), (cx + 1, cy - 11), (cx + 1, cy + 7), 2)
    pygame.draw.polygon(screen, (205, 25, 25), [(cx + 2, cy - 12), (cx + 2, cy - 1), (cx - 10, cy - 6)])


SEGMENTS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
            "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g"}


def draw_counter(screen, value, x, y):
    #Three digit seven-segment readout in a sunken box
    text = "-" + f"{min(-value, 99):02d}" if value < 0 else f"{min(value, 999):03d}"
    box = pygame.Rect(x, y, 70, 38)
    pygame.draw.rect(screen, LED_BG, box)
    draw_bevel(screen, box, raised=False, width=2)
    w, h, t = 15, 28, 3
    for i, ch in enumerate(text):
        sx, sy = x + 7 + i * 20, y + 5
        segs = {
            "a": (sx + t, sy, w - 2 * t, t),
            "b": (sx + w - t, sy + t, t, h // 2 - t),
            "c": (sx + w - t, sy + h // 2, t, h // 2 - t),
            "d": (sx + t, sy + h - t, w - 2 * t, t),
            "e": (sx, sy + h // 2, t, h // 2 - t),
            "f": (sx, sy + t, t, h // 2 - t),
            "g": (sx + t, sy + h // 2 - 1, w - 2 * t, t),
        }
        for name, r in segs.items():
            pygame.draw.rect(screen, LED_ON if name in SEGMENTS[ch] else LED_OFF, r)


def draw_plate(screen, rect, label, color):
    pygame.draw.rect(screen, FACE, rect)
    draw_bevel(screen, rect, raised=True, width=3)
    text = get_font(26, bold=True).render(label, True, color)
    screen.blit(text, text.get_rect(center=rect.center))


def draw_cell(screen, row, col, outcome=None, exploded=None):
    x = BOARD_X + col * CELL_SIZE
    y = BOARD_Y + row * CELL_SIZE
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    cx, cy = rect.center
    #This block of code was adapted from GitHub CoPilot when asking how to setup a gameboard in pygame
    #All code was subesequently written manually, but it was adapted from the AI
    #The cell visuals were later restyled (bevels, drawn mines and flags) with help from Claude
    #After a loss, mines are drawn face up here without changing any cell state
    show_mine = outcome == "lost" and grid[row][col].has_mine and not grid[row][col].is_flagged
    if grid[row][col].is_revealed or show_mine:
        bg = (220, 40, 40) if (row, col) == exploded else REVEALED
        pygame.draw.rect(screen, bg, rect)
        pygame.draw.rect(screen, SHADOW, rect, 1)
        if grid[row][col].has_mine:
            draw_mine(screen, cx, cy)
        elif grid[row][col].adjacent_mines > 0:
            n = grid[row][col].adjacent_mines
            text = get_font(34, bold=True).render(str(n), True, NUMBER_COLORS[n])
            screen.blit(text, text.get_rect(center=(cx, cy + 1)))
    else:
        pygame.draw.rect(screen, FACE, rect)
        draw_bevel(screen, rect, raised=True, width=3)
        if grid[row][col].is_flagged:
            if outcome == "lost" and not grid[row][col].has_mine:
                #Wrong flag: crossed-out mine
                draw_mine(screen, cx, cy)
                pygame.draw.line(screen, (200, 20, 20), (x + 8, y + 8), (x + CELL_SIZE - 9, y + CELL_SIZE - 9), 3)
                pygame.draw.line(screen, (200, 20, 20), (x + CELL_SIZE - 9, y + 8), (x + 8, y + CELL_SIZE - 9), 3)
            else:
                draw_flag(screen, cx, cy)


def draw_board(screen, outcome=None, exploded=None):
    board = pygame.Rect(BOARD_X - 3, BOARD_Y - 3, WINDOW_SIZE + 6, WINDOW_SIZE + 6)
    draw_bevel(screen, board, raised=False, width=3)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            draw_cell(screen, row, col, outcome, exploded)

def draw_labels(screen):
    #Column letters (A-J) above the board, row numbers (1-10) to the left
    font = get_font(20, bold=True)
    for col in range(GRID_SIZE):
        letter = chr(ord('A') + col)
        text = font.render(letter, True, TEXT_COLOR)
        x = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_Y - LABEL_SIZE // 2 - 2
        screen.blit(text, text.get_rect(center=(x, y)))

    for row in range(GRID_SIZE):
        number = str(row + 1)
        text = font.render(number, True, TEXT_COLOR)
        x = BOARD_X - LABEL_SIZE // 2 - 2
        y = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2
        screen.blit(text, text.get_rect(center=(x, y)))


def draw_header(screen, outcome, seconds):
    #Mines left on the left, status plate in the middle, timer on the right
    panel = pygame.Rect(BORDER - 3, BORDER - 3, WINDOW_WIDTH - 2 * BORDER + 6, HEADER_HEIGHT + 6)
    draw_bevel(screen, panel, raised=False, width=3)
    flags = sum(cell.is_flagged for grid_row in grid for cell in grid_row)
    draw_counter(screen, NUMBER_OF_MINES - flags, BORDER + 8, BORDER + 9)
    draw_counter(screen, seconds, WINDOW_WIDTH - BORDER - 78, BORDER + 9)
    plate = pygame.Rect((WINDOW_WIDTH - 150) // 2, BORDER + 11, 150, 34)
    if outcome == "won":
        draw_plate(screen, plate, "You Win!", (20, 125, 40))
    elif outcome == "lost":
        draw_plate(screen, plate, "Boom!", (180, 30, 30))
    else:
        draw_plate(screen, plate, "Minesweeper", TEXT_COLOR)


def run_game():
    global NUMBER_OF_MINES
    global SAFE_CELLS
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Minesweeper")
    first_move_done = False
    game_over = False
    dragging=False
    slider_value_picked = False
    slider_value = 10
    #Display-only state for the header and loss screen
    outcome = None
    exploded = None
    start_ticks = 0
    seconds = 0

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
                    SAFE_CELLS=GRID_SIZE * GRID_SIZE - NUMBER_OF_MINES

                    

            
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                col = (event.pos[0] - BOARD_X)//CELL_SIZE
                row = (event.pos[1] - BOARD_Y)//CELL_SIZE

                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    if event.button == 1:
                        if not grid[row][col].is_flagged:
                            if not first_move_done:
                                first_click(row, col)
                                first_move_done = True
                                start_ticks = pygame.time.get_ticks()
                            else:
                                result = reveal(row, col)
                                if not result:
                                    game_over = True
                                    print("Boom.")
                                    outcome = "lost"
                                    exploded = (row, col)
                                elif result == "win":
                                    game_over = True
                                    print("You win!")
                                    outcome = "won"
                    elif event.button == 3:
                        if not grid[row][col].is_revealed:
                            if grid[row][col].is_flagged:
                                grid[row][col].is_flagged = False
                            else:
                                grid[row][col].is_flagged = True
        if not slider_value_picked:
            #draw the slider
            screen.fill(FACE)
            draw_bevel(screen, pygame.Rect(BORDER, BORDER, WINDOW_WIDTH - 2 * BORDER, WINDOW_HEIGHT - 2 * BORDER), raised=False)
            title = get_font(64).render("MINESWEEPER", True, TEXT_COLOR)
            screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 80)))
            draw_mine(screen, WINDOW_WIDTH // 2, 132)
            label = get_font(28, bold=True).render("Mines:", True, TEXT_COLOR)
            screen.blit(label, label.get_rect(midright=(WINDOW_WIDTH // 2 - 6, 190)))
            draw_counter(screen, slider_value, WINDOW_WIDTH // 2 + 4, 171)
            pygame.draw.rect(screen, slider_color, slider_rect)
            draw_bevel(screen, slider_rect, raised=False, width=2)
            pygame.draw.rect(screen, handle_color, handle_rect)
            draw_bevel(screen, handle_rect)

            #draw the start button
            draw_plate(screen, button_rect, "Start", TEXT_COLOR)
            hint = get_font(22).render("Left click: reveal    Right click: flag", True, (80, 80, 80))
            screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40)))
        else:
            if first_move_done and not game_over:
                seconds = min(999, (pygame.time.get_ticks() - start_ticks) // 1000)
            screen.fill(FACE)
            draw_header(screen, outcome, seconds)
            draw_labels(screen)
            draw_board(screen, outcome, exploded)
        pygame.display.flip()