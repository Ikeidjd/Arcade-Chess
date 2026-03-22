import arcade
import arcade.gui
from constants import SCREEN_SIZE
from gamestate.chess_960.online import Chess960OnlineView
from piece.type import PieceColor


class MenuAskOnlineInfoView(arcade.View):
    def __init__(self) -> None:
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
        self.text_box_host = arcade.gui.UIInputText(text="localhost", width=SCREEN_SIZE // 3, height=SCREEN_SIZE // 16)

        left_box_layout.add(button_play_white)
        left_box_layout.add(self.text_box_host)

        @button_play_white.event("on_click")
        def on_click_play_white(event: arcade.gui.UIOnClickEvent):
            self.try_connect(True)

        button_play_black = arcade.gui.UIFlatButton(text="Play as black", width=SCREEN_SIZE // 3, height=SCREEN_SIZE // 8)
        self.text_box_port = arcade.gui.UIInputText(text="1234", width=SCREEN_SIZE // 3, height=SCREEN_SIZE // 16)

        right_box_layout.add(button_play_black)
        right_box_layout.add(self.text_box_port)

        @button_play_black.event("on_click")
        def on_click_play_black(event: arcade.gui.UIOnClickEvent):
            self.try_connect(False)

    def try_connect(self, is_host: bool) -> None:
        host = self.text_box_host.text
        try:
            port = int(self.text_box_port.text)
        except:
            pass
        else:
            self.ui_manager.disable()
            self.window.show_view(Chess960OnlineView(PieceColor.WHITE if is_host else PieceColor.BLACK, is_host, host, port))

    def on_draw(self) -> bool | None:
        self.clear()
        self.ui_manager.draw()