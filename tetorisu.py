# tetris_game.py
import pygame, random

# --- 設定 ---
CELL_SIZE = 30
COLS, ROWS = 10, 20
MARGIN = CELL_SIZE
FIELD_WIDTH = COLS * CELL_SIZE
FIELD_HEIGHT = ROWS * CELL_SIZE
WIDTH = FIELD_WIDTH + MARGIN * 2
HEIGHT = FIELD_HEIGHT + MARGIN * 2
FPS = 60

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
}
SHAPE_COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0),
}

# --- 関数 ---
def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def create_piece():
    t = random.choice(list(SHAPES.keys()))
    return {'type': t, 'shape': SHAPES[t], 'x': COLS // 2 - len(SHAPES[t][0]) // 2, 'y': 0}

def check_collision(board, shape, offset):
    ox, oy = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                px, py = x + ox, y + oy
                if px < 0 or px >= COLS or py >= ROWS:
                    return True
                if py >= 0 and board[py][px]:
                    return True
    return False

def freeze_piece(board, shape, offset, color):
    ox, oy = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                board[y + oy][x + ox] = color

def clear_lines(board):
    cleared = 0
    new_board = []
    for row in board:
        if all(cell != 0 for cell in row):
            cleared += 1
        else:
            new_board.append(row)
    while len(new_board) < ROWS:
        new_board.insert(0, [0 for _ in range(COLS)])
    return new_board, cleared

def draw_block(screen, x, y, color):
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (30, 30, 30), rect, 1)

def draw_piece(screen, piece):
    color = SHAPE_COLORS[piece['type']]
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                px = MARGIN + (piece['x'] + x) * CELL_SIZE
                py = MARGIN + (piece['y'] + y) * CELL_SIZE
                draw_block(screen, px, py, color)

def draw_board(screen, board):
    for y in range(ROWS):
        for x in range(COLS):
            cell = board[y][x]
            if cell:
                px = MARGIN + x * CELL_SIZE
                py = MARGIN + y * CELL_SIZE
                draw_block(screen, px, py, cell)

def draw_grid(screen):
    for x in range(COLS + 1):
        xpos = MARGIN + x * CELL_SIZE
        pygame.draw.line(screen, (200,200,200), (xpos, MARGIN), (xpos, HEIGHT - MARGIN))
    for y in range(ROWS + 1):
        ypos = MARGIN + y * CELL_SIZE
        pygame.draw.line(screen, (200,200,200), (MARGIN, ypos), (WIDTH - MARGIN, ypos))

def draw_frame(screen):
    pygame.draw.rect(screen, (160, 160, 160), (MARGIN - 1, MARGIN - 1, FIELD_WIDTH + 2, FIELD_HEIGHT + 2), 2)

def show_text_center(text, size, color, y_offset=0):
    font = pygame.font.SysFont(None, size)
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(surface, rect)

def draw_score(screen, score):
    font = pygame.font.SysFont(None, 28)
    surface = font.render(f"LINES: {score}", True, (50, 50, 50))
    screen.blit(surface, (MARGIN, 5))

# --- 初期化 ---
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TETRIS")
clock = pygame.time.Clock()

board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
current = create_piece()
fall_time = 0
fall_speed = 0.5
score = 0
game_state = "start"

# --- メインループ ---
running = True
while running:
    dt = clock.tick(FPS) / 1000
    fall_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "start":
                game_state = "playing"
                board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
                current = create_piece()
                score = 0
                if check_collision(board, current['shape'], (current['x'], current['y'])):
                    game_state = "gameover"
            elif game_state == "gameover":
                game_state = "start"
            elif game_state == "playing":
                if event.button == 1:
                    r = rotate(current['shape'])
                    if not check_collision(board, r, (current['x'], current['y'])):
                        current['shape'] = r
                elif event.button == 3:
                    r = rotate(rotate(rotate(current['shape'])))
                    if not check_collision(board, r, (current['x'], current['y'])):
                        current['shape'] = r

        elif event.type == pygame.KEYDOWN and game_state == "playing":
            if event.key == pygame.K_LEFT:
                current['x'] -= 1
                if check_collision(board, current['shape'], (current['x'], current['y'])):
                    current['x'] += 1
            elif event.key == pygame.K_RIGHT:
                current['x'] += 1
                if check_collision(board, current['shape'], (current['x'], current['y'])):
                    current['x'] -= 1
            elif event.key == pygame.K_DOWN:
                current['y'] += 1
                if check_collision(board, current['shape'], (current['x'], current['y'])):
                    current['y'] -= 1
            elif event.key == pygame.K_UP:
                while not check_collision(board, current['shape'], (current['x'], current['y'] + 1)):
                    current['y'] += 1

    if game_state == "playing":
        if fall_time > fall_speed:
            fall_time = 0
            current['y'] += 1
            if check_collision(board, current['shape'], (current['x'], current['y'])):
                current['y'] -= 1
                color = SHAPE_COLORS[current['type']]
                freeze_piece(board, current['shape'], (current['x'], current['y']), color)
                board, cleared = clear_lines(board)
                score += cleared
                current = create_piece()
                if check_collision(board, current['shape'], (current['x'], current['y'])):
                    game_state = "gameover"

    # --- 描画 ---
    screen.fill((255, 255, 255))
    draw_grid(screen)
    draw_frame(screen)

    if game_state == "start":
        show_text_center("TETRIS", 60, (0, 0, 0))
        show_text_center("クリックでスタート", 30, (100, 100, 100), y_offset=80)
    elif game_state == "playing":
        draw_board(screen, board)
        draw_piece(screen, current)
        draw_score(screen, score)
    elif game_state == "gameover":
        show_text_center("GAME OVER", 60, (200, 0, 0))
        show_text_center(f"LINES: {score}", 30, (50, 50, 50), y_offset=60)
        show_text_center("クリックでリスタート", 30, (100, 100, 100), y_offset=100)

    pygame.display.flip()

pygame.quit()