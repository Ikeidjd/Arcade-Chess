import arcade.gui
from enum import Enum, auto
from constants import SCREEN_SIZE
from board import Board
from gamestate.menu.base import MenuView
from piece.type import PieceColor
from piece.piece import Piece


class GameOverType(Enum):
    CHECKMATE = "{attacker} checkmated {victim}"
    KING_CAPTURE = "{attacker} captured {victim}'s king"
    STALEMATE = "{attacker} stalemated {victim}"


class GameOverView(MenuView):
    def __init__(self, board: Board[Piece], game_over_type: GameOverType, attacker: PieceColor, victim: PieceColor):
        super().__init__()

        self.board = board
        self.game_over_type = game_over_type

        text = f"{self.game_over_type.value.format(attacker=attacker.value.capitalize(), victim=victim.value)}\nF1 to hide\nESC to exit"
        label = arcade.gui.UILabel(text=text, font_size=40, multiline=True, align="center").with_background(color=arcade.types.Color(0, 0, 0, 128))
        anchor_layout: arcade.gui.UIAnchorLayout = arcade.gui.UIAnchorLayout(children=[label], anchor_x="center_x", anchor_y="center_y")
        self.ui_manager.add(anchor_layout)

    def on_draw(self) -> None:
        self.clear()
        self.board.draw_everything()
        super().on_draw()