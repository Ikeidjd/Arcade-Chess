from piece.type import PieceType, PiecePos
from gamestate.chess_normal.main import ChessNormalMainView


class ChessAtomicMainView(ChessNormalMainView):
    def __init__(self) -> None:
        ChessNormalMainView.__init__(self)

    def on_update(self, delta_time: float) -> None:
        if self.selected and self.selected.just_finished_moving and self.selected.move_packet.captures:
            captures = self.selected.move_packet.captures.copy()

            for capture in captures:
                for rank in range(-1, 2):
                    for file in range(-1, 2):
                        pos = capture + PiecePos(rank, file)

                        if not self.board.is_in_bounds(pos) or pos == capture or not (piece := self.board[pos]) or piece.piece_type == PieceType.PAWN:
                            continue

                        self.selected.move_packet.captures.append(pos)
                        self.board.kill_piece(pos)

        super().on_update(delta_time)