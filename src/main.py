import arcade
from gamestate.menu.main import MenuMainView
from constants import SCREEN_SIZE


class ViewManager(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_SIZE, SCREEN_SIZE, "Chess")

        view = MenuMainView()
        self.show_view(view)

        arcade.run()

    def draw(self, dt: float) -> None:
        self.clear()
        super().draw(dt)


if __name__ == "__main__":
    ViewManager()