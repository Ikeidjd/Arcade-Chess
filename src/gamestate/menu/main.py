import arcade.gui
from constants import SCREEN_SIZE
from .base import MenuView
from .offline_online import MenuOfflineOnlineView


class MenuMainView(MenuView):
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

        button_play_normal = arcade.gui.UIFlatButton(text="Play normal chess", width=SCREEN_SIZE // 3, height=SCREEN_SIZE // 3)
        button_play_duck = arcade.gui.UIFlatButton(text="Play duck chess", width=SCREEN_SIZE // 3, height=SCREEN_SIZE // 3)

        left_box_layout.add(button_play_normal)
        left_box_layout.add(button_play_duck)

        button_play_960 = arcade.gui.UIFlatButton(text="Play 960 chess", width=SCREEN_SIZE // 3, height=SCREEN_SIZE // 3)
        button_play_atomic = arcade.gui.UIFlatButton(text="Play atomic chess", width=SCREEN_SIZE // 3, height=SCREEN_SIZE // 3)

        right_box_layout.add(button_play_960)
        right_box_layout.add(button_play_atomic)

        def on_click_play(game_main: type, game_online):
            return lambda event: self.window.show_view(MenuOfflineOnlineView(game_main, game_online))

        from gamestate.chess_normal.main import ChessNormalMainView
        from gamestate.chess_normal.online import ChessNormalOnlineView
        from gamestate.chess_duck.main import ChessDuckMainView
        from gamestate.chess_duck.online import ChessDuckOnlineView
        from gamestate.chess_960.main import Chess960MainView
        from gamestate.chess_960.online import Chess960OnlineView
        from gamestate.chess_atomic.main import ChessAtomicMainView
        from gamestate.chess_atomic.online import ChessAtomicOnlineView

        button_play_normal.on_click = on_click_play(ChessNormalMainView, ChessNormalOnlineView)
        button_play_duck.on_click = on_click_play(ChessDuckMainView, ChessDuckOnlineView)
        button_play_960.on_click = on_click_play(Chess960MainView, Chess960OnlineView)
        button_play_atomic.on_click = on_click_play(ChessAtomicMainView, ChessAtomicOnlineView)