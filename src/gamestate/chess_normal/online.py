import arcade
from typing import Any
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from PodSixNet.Connection import ConnectionListener, connection
from .main import ChessNormalMainView
from .move_packet import MovePacket
from piece.type import PieceType, PieceColor
from piece.piece import Piece


class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._server: ServerChannel

    def Network(self, data: dict[str, Any]) -> None:
        print(f"Server received {data}")

        if data["action"] != "move":
            self._server.send_all(data)

    def Network_move(self, data: dict[str, Any]) -> None:
        self._server.move(data)

    def Network_close(self, data: dict[str, Any]) -> None:
        self._server.close_all()


class ServerChannel(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.white: ClientChannel | None = None
        self.black: ClientChannel | None = None
    
    def Connected(self, channel: ClientChannel, addr: Any):
        print(f"{channel} connected")

        if self.white is None:
            self.white = channel
        else:
            self.black = channel
            self.send_all({"action": "start_game"})

    def send_all(self, data: dict[str, Any]) -> None:
        assert(self.white)
        assert(self.black)

        self.white.Send(data)
        self.black.Send(data)

    def move(self, data: dict[str, Any]) -> None:
        assert(self.white and self.black)

        if data["move"]["src_color"] == PieceColor.BLACK.value:
            self.white.Send(data)
        else:
            self.black.Send(data)

    def close_all(self) -> None:
        if not self.white or not self.black:
            return

        self.send_all({"action": "close"})

        self.white.close()
        self.black.close()

        self.white = None
        self.black = None

        self.close()


class ChessNormalOnlineView(ChessNormalMainView, ConnectionListener):
    def __init__(self, my_turn_color: PieceColor, is_host: bool, host: str, port: int) -> None:
        super().__init__(flip_perspective_on_turn_swap=False)
        self.board.inverted = my_turn_color == PieceColor.BLACK

        self.server: ServerChannel | None = ServerChannel(localaddr=(host, port)) if is_host else None
        self.Connect((host, port))
        self.host = host
        self.port = port

        self.my_turn_color: PieceColor = my_turn_color

        self.enemy_pieces_moving: list[Piece] = []
        self.enemy_promotion_piece: tuple[PieceType, PieceColor] | None = None

        self.start_game = False

    def is_my_turn(self):
        return self.cur_turn_color == self.my_turn_color

    def on_update(self, delta_time: float) -> None:
        self.do_pumps()

        if not self.start_game:
            return

        if self.is_my_turn():
            ChessNormalMainView.on_update(self, delta_time)
        elif self.enemy_pieces_moving:
            done = True

            for piece in self.enemy_pieces_moving:
                if piece.moving:
                    piece.advance_move_transition(delta_time, self.window)
                    done = False
                elif piece.just_finished_moving:
                    piece.fully_end_move_transition()

            if done:
                if self.enemy_promotion_piece:
                    self.board.kill_piece(self.enemy_pieces_moving[0].piece_pos)
                    self.board.new_piece_of_type(*self.enemy_promotion_piece, self.enemy_pieces_moving[0].piece_pos)

                self.enemy_pieces_moving = []

                self.board.advance_markers()
                self.swap_turn()
                self.gen_moves()

    def on_fully_ended_move(self) -> None:
        assert(self.selected)

        connection.Send({
            "action": "move",
            "move": self.selected.move_packet.to_dict()
        })

        ChessNormalMainView.on_fully_ended_move(self)

    def on_draw(self) -> None:
        if self.start_game:
            super().on_draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.is_my_turn():
            super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.is_my_turn():
            super().on_mouse_release(x, y, button, modifiers)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        super().on_key_release(symbol, modifiers)

        if symbol == arcade.key.ESCAPE:
            if self.server:
                self.server.close_all()
            else:
                connection.Send({"action": "close"})

            self.do_pumps()

    def do_pumps(self) -> None:
        connection.Pump()
        self.Pump()

        if self.server:
            self.server.Pump()

    def Network(self, data: dict[str, Any]) -> None:
        print(f"Client received {data}")

    def Network_move(self, data: dict[str, Any]) -> None:
        move_packet = MovePacket.from_dict(data["move"])

        for marker in move_packet.added_markers:
            self.board.add_marker(*marker)

        for capture in move_packet.captures:
            self.board.kill_piece(capture)

        for start, end in zip(move_packet.start, move_packet.end):
            assert(piece := self.board[start])
            piece.move(end)
            self.enemy_pieces_moving.append(piece)

        self.enemy_promotion_piece = move_packet.promotion_piece
        self.last_move = move_packet.start[0], move_packet.end[0]

    def Network_start_game(self, data: dict[str, Any]) -> None:
        self.start_game = True

    def Network_close(self, data: dict[str, Any]) -> None:
        connection.close()