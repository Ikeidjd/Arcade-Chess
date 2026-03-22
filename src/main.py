import arcade
from gamestate.menu.main import MenuMainView
from constants import SCREEN_SIZE


class ViewManager(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_SIZE, SCREEN_SIZE)

        view = MenuMainView()
        self.show_view(view)

        arcade.run()

    def on_update(self, delta_time: float) -> bool | None:
        return super().on_update(delta_time)


def main():
    ViewManager()


if __name__ == "__main__":
    main()