import arcade
from constants import PIECE_SIZE, BOARD_SIZE, SCREEN_SIZE
from gamestate.normal_chess.main import NormalChessMainView
from gamestate.normal_chess.move_packet import MovePacket
from piece.piece import Piece
from piece.type import PieceType, PieceColor, PiecePos


class NormalChessPromotionView(arcade.View):
    def __init__(self, main_view: NormalChessMainView, piece_color: PieceColor, piece_pos: PiecePos, forward_dir: PiecePos, move_packet: MovePacket) -> None:
        super().__init__()

        self.prev_view: NormalChessMainView = main_view
        self.board = self.prev_view.board
        self.piece_pos: PiecePos = piece_pos
        self.forward_dir: PiecePos = forward_dir
        self.move_packet: MovePacket = move_packet

        self.options: arcade.SpriteList[Piece] = arcade.SpriteList()
        self.options.append(self.board.new_piece_of_type(PieceType.QUEEN, piece_color, piece_pos, append_to_sprite_list=False))
        self.options.append(self.board.new_piece_of_type(PieceType.ROOK, piece_color, piece_pos - forward_dir, append_to_sprite_list=False))
        self.options.append(self.board.new_piece_of_type(PieceType.BISHOP, piece_color, piece_pos - forward_dir * 2, append_to_sprite_list=False))
        self.options.append(self.board.new_piece_of_type(PieceType.KNIGHT, piece_color, piece_pos - forward_dir * 3, append_to_sprite_list=False))

    def on_draw(self) -> None:
        self.clear()
        self.board.draw_everything()

        piece_pos = self.piece_pos
        forward_dir = self.forward_dir

        if self.board.inverted:
            piece_pos = PiecePos(BOARD_SIZE - 1, BOARD_SIZE - 1) - piece_pos
            forward_dir = -forward_dir

        pos = piece_pos - forward_dir * (len(self.options) - 1)

        if piece_pos.rank < pos.rank:
            pos = piece_pos

        arcade.draw_lbwh_rectangle_filled(pos.file * PIECE_SIZE, pos.rank * PIECE_SIZE, PIECE_SIZE, len(self.options) * PIECE_SIZE, arcade.color.BLACK)
        arcade.draw_lbwh_rectangle_filled((pos.file + 0.05) * PIECE_SIZE, (pos.rank + 0.05) * PIECE_SIZE, 0.9 * PIECE_SIZE, (len(self.options) - 0.1) * PIECE_SIZE, arcade.color.WHITE)

        if self.board.inverted:
            for option in self.options:
                option.center_x, option.center_y = SCREEN_SIZE - option.center_x, SCREEN_SIZE - option.center_y

        self.options.draw(pixelated=True)

        if self.board.inverted:
            for option in self.options:
                option.center_x, option.center_y = SCREEN_SIZE - option.center_x, SCREEN_SIZE - option.center_y

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if not button == arcade.MOUSE_BUTTON_LEFT:
            return

        pos = self.board.to_piece_pos(x, y)

        for piece in self.options:
            if pos == piece.piece_pos:
                self.move_packet.promotion_piece = piece.piece_type, piece.piece_color

                piece.piece_pos = self.piece_pos
                self.board.add_piece(piece)

                self.window.show_view(self.prev_view)
                break