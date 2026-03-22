import arcade.gui
from constants import SCREEN_SIZE
from .base import MenuView
from piece.type import PieceColor


class MenuAskOnlineInfoView(MenuView):
    def __init__(self, game_online: type) -> None:
        super().__init__()

        self.ui_manager: arcade.gui.UIManager = arcade.gui.UIManager()
        self.ui_manager.enable()

        box_layout: arcade.gui.UIBoxLayout = arcade.gui.UIBoxLayout(space_between=SCREEN_SIZE // 40, vertical=False)
        anchor_layout: arcade.gui.UIAnchorLayout = arcade.gui.UIAnchorLayout(children=[box_layout], anchor_x="center_x", anchor_y="center_y")
        self.ui_manager.add(anchor_layout)

        left_box_layout: arcade.gui.UIBoxLayout = arcade.gui.UIBoxLayout(space_between=SCREEN_SIZE // 40)
        right_box_layout: arcade.gui.UIBoxLayout = arcade.gui.UIBoxLayout(space_between=SCREEN_SIZE // 40)

        box_layout.add(left_box_layout)
        box_layout.add(right_box_layout)

        button_play_white = arcade.gui.UIFlatButton(text="Play as white", width=SCREEN_SIZE // 3, height=SCREEN_SIZE // 8)
        text_box_host = arcade.gui.UIInputText(text="localhost", width=SCREEN_SIZE // 3, height=SCREEN_SIZE // 16)

        left_box_layout.add(button_play_white)
        left_box_layout.add(text_box_host)

        button_play_black = arcade.gui.UIFlatButton(text="Play as black", width=SCREEN_SIZE // 3, height=SCREEN_SIZE // 8)
        text_box_port = arcade.gui.UIInputText(text="1234", width=SCREEN_SIZE // 3, height=SCREEN_SIZE // 16)

        right_box_layout.add(button_play_black)
        right_box_layout.add(text_box_port)

        def try_connect(*, is_host: bool) -> None:
            host = text_box_host.text
            try:
                port = int(text_box_port.text)
            except:
                pass
            else:
                self.window.show_view(game_online(PieceColor.WHITE if is_host else PieceColor.BLACK, is_host, host, port))

        @button_play_white.event("on_click")
        def on_click_play_white(event: arcade.gui.UIOnClickEvent):
            try_connect(is_host=True)

        @button_play_black.event("on_click")
        def on_click_play_black(event: arcade.gui.UIOnClickEvent):
            try_connect(is_host=False)