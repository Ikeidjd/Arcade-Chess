import arcade
from board import Board
from constants import *


class Juego(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_SIZE, SCREEN_SIZE)

        self.board = Board()
        self.mouse_x = self.mouse_y = 0

    def on_update(self, delta_time: float) -> None:
        self.board.update(delta_time, self.mouse_x, self.mouse_y)

    def on_draw(self) -> None:
        self.board.draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.board.on_left_click_press(x, y)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.board.on_left_click_release(x, y)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.mouse_x = x + dx
        self.mouse_y = y + dy


def main():
    juego = Juego()
    juego.run()


if __name__ == "__main__":
    main()