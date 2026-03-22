import arcade
import sys
from gamestate.normal_chess.online import NormalChessOnlineView
from constants import *
from piece.type import PieceColor


class ViewManager(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_SIZE, SCREEN_SIZE)

        if len(sys.argv) == 1:
            color = PieceColor.WHITE
            is_host = True
        else:
            color = PieceColor.BLACK
            is_host = False
        view = NormalChessOnlineView(color, is_host, "localhost", 1234)
        self.show_view(view)

        arcade.run()

    def on_update(self, delta_time: float) -> bool | None:
        return super().on_update(delta_time)


def main():
    ViewManager()


if __name__ == "__main__":
    main()