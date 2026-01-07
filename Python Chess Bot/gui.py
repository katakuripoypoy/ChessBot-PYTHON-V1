import pygame
import chess
from engine import choose_move

# ---------- Config ----------
WIDTH, HEIGHT = 640, 640
SQ = WIDTH // 8
FPS = 60

# Board colors (light/dark)
LIGHT = (240, 217, 181)
DARK  = (181, 136, 99)

HIGHLIGHT_SEL = (120, 180, 255)   # selected square
HIGHLIGHT_MOV = (120, 255, 160)   # legal move squares

# Unicode chess pieces
UNICODE_PIECES = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
}

def square_from_mouse(pos):
    x, y = pos
    file = x // SQ
    rank = 7 - (y // SQ)   # pygame y=0 is top, chess rank 8 is top
    return chess.square(file, rank)

def draw_board(screen, board, font, selected_sq, legal_targets):
    # Squares
    for r in range(8):
        for f in range(8):
            is_light = (r + f) % 2 == 0
            color = LIGHT if is_light else DARK
            x = f * SQ
            y = r * SQ
            pygame.draw.rect(screen, color, (x, y, SQ, SQ))

    # Highlights
    if selected_sq is not None:
        f = chess.square_file(selected_sq)
        r = chess.square_rank(selected_sq)
        x = f * SQ
        y = (7 - r) * SQ
        pygame.draw.rect(screen, HIGHLIGHT_SEL, (x, y, SQ, SQ), 4)

    for sq in legal_targets:
        f = chess.square_file(sq)
        r = chess.square_rank(sq)
        x = f * SQ
        y = (7 - r) * SQ
        pygame.draw.rect(screen, HIGHLIGHT_MOV, (x, y, SQ, SQ), 4)

    # Pieces
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if not piece:
            continue
        symbol = piece.symbol()  # 'P' 'n' etc.
        text = UNICODE_PIECES[symbol]
        f = chess.square_file(sq)
        r = chess.square_rank(sq)
        x = f * SQ
        y = (7 - r) * SQ

        # Render centered
        surf = font.render(text, True, (10, 10, 10))
        rect = surf.get_rect(center=(x + SQ // 2, y + SQ // 2))
        screen.blit(surf, rect)

def draw_text_panel(screen, text, y=10):
    font = pygame.font.SysFont("arial", 28, bold=True)
    text_surf = font.render(text, True, (255, 255, 255))

    padding = 10
    panel_w = text_surf.get_width() + padding * 2
    panel_h = text_surf.get_height() + padding * 2
    panel_x = (WIDTH - panel_w) // 2

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 180))  # semi-transparent black

    screen.blit(panel, (panel_x, y))
    screen.blit(text_surf, (panel_x + padding, y + padding))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Python Chess Bot (click-to-move)")
    clock = pygame.time.Clock()

    # A font that supports unicode chess symbols (Segoe UI Symbol usually works on Windows)
    font = pygame.font.SysFont("segoeuisymbol", 64)
    if font is None:
        font = pygame.font.SysFont(None, 64)

    board = chess.Board()

    human_is_white = True
    bot_depth = 3

    selected_sq = None
    legal_targets = set()

    

    running = True
    while running:
        clock.tick(FPS)

        # If it's bot turn, make bot move automatically
        if not board.is_game_over():
            human_turn = (board.turn == chess.WHITE) if human_is_white else (board.turn == chess.BLACK)
            if not human_turn:
                bot_move = choose_move(board, depth=bot_depth)
                board.push(bot_move)
                selected_sq = None
                legal_targets = set()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Quick controls
                if event.key == pygame.K_r:
                    board.reset()
                    selected_sq = None
                    legal_targets = set()
                elif event.key == pygame.K_u:
                    # Undo two plies: bot + human (if available)
                    if len(board.move_stack) >= 1:
                        board.pop()
                    if len(board.move_stack) >= 1:
                        board.pop()
                    selected_sq = None
                    legal_targets = set()
                elif event.key == pygame.K_1:
                    bot_depth = 1
                elif event.key == pygame.K_2:
                    bot_depth = 2
                elif event.key == pygame.K_3:
                    bot_depth = 3
                elif event.key == pygame.K_4:
                    bot_depth = 4

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if board.is_game_over():
                    continue

                human_turn = (board.turn == chess.WHITE) if human_is_white else (board.turn == chess.BLACK)
                if not human_turn:
                    continue  # ignore clicks during bot turn

                clicked = square_from_mouse(pygame.mouse.get_pos())

                # If nothing selected yet, select a piece of the side to move
                if selected_sq is None:
                    piece = board.piece_at(clicked)
                    if piece and piece.color == board.turn:
                        selected_sq = clicked
                        # compute legal targets for this piece
                        legal_targets = set()
                        for mv in board.legal_moves:
                            if mv.from_square == selected_sq:
                                legal_targets.add(mv.to_square)
                    else:
                        selected_sq = None
                        legal_targets = set()
                else:
                    # Try to make a move from selected_sq to clicked
                    move = None

                    # Handle promotions: default to queen if pawn reaches last rank
                    piece = board.piece_at(selected_sq)
                    if piece and piece.piece_type == chess.PAWN:
                        to_rank = chess.square_rank(clicked)
                        if (piece.color == chess.WHITE and to_rank == 7) or (piece.color == chess.BLACK and to_rank == 0):
                            move = chess.Move(selected_sq, clicked, promotion=chess.QUEEN)

                    if move is None:
                        move = chess.Move(selected_sq, clicked)

                    if move in board.legal_moves:
                        board.push(move)

                    # reset selection either way
                    selected_sq = None
                    legal_targets = set()

        draw_board(screen, board, font, selected_sq, legal_targets)

        # Game-over overlay (readable)
        if board.is_game_over():
            # Optional: dim the board a bit
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 60))
            screen.blit(overlay, (0, 0))

            draw_text_panel(screen, f"Game Over: {board.result()}   (Press R to reset)", y=10)

        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()