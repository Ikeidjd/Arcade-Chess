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
        self._server.close_all(data)


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

            self.white.Send({"action": "start_game"})
            self.black.Send({"action": "start_game"})

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

    def close_all(self, data: dict[str, Any]) -> None:
        assert(self.white)
        assert(self.black)

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
        self.move_packet: MovePacket | None = None

        self.enemy_pieces_moving: list[Piece] = []
        self.enemy_promotion_piece: tuple[PieceType, PieceColor] | None = None

        self.start_game = False

        self.data: dict[str, Any] | None = None

    def is_my_turn(self):
        return self.cur_turn_color == self.my_turn_color

    def on_update(self, delta_time: float) -> None:
        connection.Pump()
        self.Pump()

        if self.server:
            self.server.Pump()

        if not self.start_game:
            return

        if self.is_my_turn():
            if self.selected and self.selected.just_finished_moving:
                connection.Send({
                    "action": "move",
                    "move": self.selected.move_packet.to_dict()
                })
            ChessNormalMainView.on_update(self, delta_time)
        elif len(self.enemy_pieces_moving) > 0:
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
                self.swap_turn()
                self.gen_moves()
        elif self.move_packet:
            if self.move_packet.captures:
                for capture in self.move_packet.captures:
                    self.board.kill_piece(capture)

            for start, end in zip(self.move_packet.start, self.move_packet.end):
                assert(piece := self.board[start])
                piece.move(end)
                self.enemy_pieces_moving.append(piece)

            self.future_en_passant_pos = self.move_packet.future_en_passant_pos
            self.enemy_promotion_piece = self.move_packet.promotion_piece
            self.last_move = self.move_packet.start[0], self.move_packet.end[0]
            self.move_packet = None

    def on_draw(self) -> None:
        if self.start_game:
            super().on_draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.is_my_turn():
            super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.is_my_turn():
            super().on_mouse_release(x, y, button, modifiers)

    def on_hide_view(self) -> None:
        connection.Send({"action": "close"})
        connection.close()

    def Network(self, data: dict[str, Any]) -> None:
        print(f"Client received {data}")

    def Network_move(self, data: dict[str, Any]) -> None:
        self.move_packet = MovePacket.from_dict(data["move"])

    def Network_start_game(self, data: dict[str, Any]) -> None:
        self.start_game = True