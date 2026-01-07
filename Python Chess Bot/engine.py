import chess
import math
import time

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

def evaluate(board: chess.Board) -> int:
    """Positive = good for White, Negative = good for Black."""
    if board.is_checkmate():
        # If it's checkmate and it's your turn, you are mated.
        return -10_000 if board.turn else 10_000
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0

    score = 0
    for piece_type, val in PIECE_VALUES.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * val
        score -= len(board.pieces(piece_type, chess.BLACK)) * val

    # Tiny mobility bonus (keeps it from being totally sleepy)
    score += 2 * board.legal_moves.count() if board.turn == chess.WHITE else -2 * board.legal_moves.count()

    return score

def order_moves(board: chess.Board, moves):
    """Basic move ordering: captures first (MVV-LVA-ish)."""
    scored = []
    for m in moves:
        score = 0
        if board.is_capture(m):
            captured = board.piece_at(m.to_square)
            attacker = board.piece_at(m.from_square)
            if captured:
                score += 10 * PIECE_VALUES[captured.piece_type]
            if attacker:
                score -= PIECE_VALUES[attacker.piece_type]
        if board.gives_check(m):
            score += 50
        scored.append((score, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored]

def negamax(board: chess.Board, depth: int, alpha: int, beta: int) -> int:
    if depth == 0 or board.is_game_over():
        # Negamax returns score from side-to-move perspective
        base = evaluate(board)
        return base if board.turn == chess.WHITE else -base

    best = -10_000_000
    moves = order_moves(board, list(board.legal_moves))
    for move in moves:
        board.push(move)
        val = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()

        if val > best:
            best = val
        if best > alpha:
            alpha = best
        if alpha >= beta:
            break
    return best

def choose_move(board: chess.Board, depth: int = 3) -> chess.Move:
    best_move = None
    best_val = -math.inf

    moves = order_moves(board, list(board.legal_moves))
    for move in moves:
        board.push(move)
        val = -negamax(board, depth - 1, -10_000_000, 10_000_000)
        board.pop()

        if val > best_val:
            best_val = val
            best_move = move

    return best_move if best_move else list(board.legal_moves)[0]

def main():
    board = chess.Board()
    print("Type moves in UCI like e2e4, g1f3. Type 'quit' to exit.\n")

    human_is_white = True  # flip this if you want
    depth = 5

    while not board.is_game_over():
        print(board)
        print("FEN:", board.fen())
        print()

        if board.turn == (chess.WHITE if human_is_white else chess.BLACK):
            # Human move
            move_str = input("Your move: ").strip()
            if move_str.lower() in ("q", "quit", "exit"):
                return
            try:
                move = chess.Move.from_uci(move_str)
                if move not in board.legal_moves:
                    raise ValueError("Illegal move")
                board.push(move)
            except Exception:
                print("Invalid/illegal move. Try again.\n")
                continue
        else:
            # Bot move
            t0 = time.time()
            move = choose_move(board, depth=depth)
            dt = time.time() - t0
            print(f"Bot plays: {move.uci()} (depth {depth}, {dt:.2f}s)\n")
            board.push(move)

    print(board)
    print("\nGame over:", board.result(), board.outcome())


