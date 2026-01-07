import sys

def main():
    # Usage:
    #   python main.py uci      -> run UCI loop (for GUIs like Arena/CuteChess)
    #   python main.py terminal -> play in terminal vs the bot
    #   python main.py          -> defaults to UCI (recommended)
    mode = (sys.argv[1].lower() if len(sys.argv) > 1 else "uci")

    if mode == "uci":
        from uci import uci_loop
        uci_loop()
        return

    if mode == "terminal":
        import chess
        from engine import choose_move

        board = chess.Board()
        print("Type moves like e2e4, g1f3. Type 'quit' to exit.\n")

        human_is_white = True
        depth = 3

        while not board.is_game_over():
            print(board)
            print()

            if board.turn == (chess.WHITE if human_is_white else chess.BLACK):
                s = input("Your move: ").strip()
                if s.lower() in ("q", "quit", "exit"):
                    return
                try:
                    mv = chess.Move.from_uci(s)
                    if mv not in board.legal_moves:
                        raise ValueError("Illegal move")
                    board.push(mv)
                except Exception:
                    print("Invalid/illegal move. Try again.\n")
            else:
                mv = choose_move(board, depth=depth)
                print(f"Bot plays: {mv.uci()}\n")
                board.push(mv)

        print(board)
        print("\nGame over:", board.result(), board.outcome())
        return

    print("Unknown mode. Use: python main.py [uci|terminal]")

if __name__ == "__main__":
    main()
