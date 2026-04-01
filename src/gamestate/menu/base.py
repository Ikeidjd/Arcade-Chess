import arcade
import arcade.gui


class MenuView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.ui_manager: arcade.gui.UIManager = arcade.gui.UIManager()

    def on_draw(self) -> None:
        self.ui_manager.draw()

    def on_show_view(self) -> None:
        self.ui_manager.enable()

    def on_hide_view(self) -> None:
        self.ui_manager.disable()

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            from .main import MenuMainView
            self.window.show_view(MenuMainView())