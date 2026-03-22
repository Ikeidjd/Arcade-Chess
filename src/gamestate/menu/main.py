import arcade
import arcade.gui
from constants import SCREEN_SIZE
from gamestate.chess_normal.main import ChessNormalMainView
from .ask_online_info import MenuAskOnlineInfoView


class MenuMainView(arcade.View):
    def __init__(self) -> None:
        super().__init__()

        self.ui_manager: arcade.gui.UIManager = arcade.gui.UIManager()
        self.ui_manager.enable()

        box_layout: arcade.gui.UIBoxLayout = arcade.gui.UIBoxLayout(space_between=SCREEN_SIZE // 40)
        anchor_layout: arcade.gui.UIAnchorLayout = arcade.gui.UIAnchorLayout(children=[box_layout], anchor_x="center_x", anchor_y="center_y")
        self.ui_manager.add(anchor_layout)

        button_play_offline = arcade.gui.UIFlatButton(text="Play offline", width=SCREEN_SIZE // 2, height=SCREEN_SIZE // 8)
        button_play_online = arcade.gui.UIFlatButton(text="Play online", width=SCREEN_SIZE // 2, height=SCREEN_SIZE // 8)

        box_layout.add(button_play_offline)
        box_layout.add(button_play_online)

        @button_play_offline.event("on_click")
        def on_click_offline(event: arcade.gui.UIOnClickEvent):
            self.ui_manager.disable()
            self.window.show_view(ChessNormalMainView())

        @button_play_online.event("on_click")
        def on_click_online(event: arcade.gui.UIOnClickEvent):
            self.ui_manager.disable()
            self.window.show_view(MenuAskOnlineInfoView())

    def on_draw(self) -> bool | None:
        self.clear()
        self.ui_manager.draw()