import sys
import chess
from engine import choose_move

def uci_loop():
    board = chess.Board()

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()

        if line == "uci":
            print("id name MyPythonBot")
            print("id author you")
            print("uciok")
            sys.stdout.flush()

        elif line == "isready":
            print("readyok")
            sys.stdout.flush()

        elif line == "ucinewgame":
            board.reset()

        elif line.startswith("position"):
            parts = line.split()
            i = 1

            if parts[i] == "startpos":
                board.set_fen(chess.STARTING_FEN)
                i += 1
            elif parts[i] == "fen":
                fen = " ".join(parts[i + 1:i + 7])
                board.set_fen(fen)
                i += 7

            if i < len(parts) and parts[i] == "moves":
                i += 1
                while i < len(parts):
                    mv = chess.Move.from_uci(parts[i])
                    if mv in board.legal_moves:
                        board.push(mv)
                    i += 1

        elif line.startswith("go"):
            # minimal: support "go depth N"
            depth = 3
            parts = line.split()
            if "depth" in parts:
                depth = int(parts[parts.index("depth") + 1])

            best = choose_move(board, depth=depth)
            print(f"bestmove {best.uci()}")
            sys.stdout.flush()

        elif line == "quit":
            break

if __name__ == "__main__":
    uci_loop()
