from typing import Any
from PodSixNet.Channel import Channel # type: ignore
from PodSixNet.Server import Server # type: ignore
from PodSixNet.Connection import ConnectionListener, connection # type: ignore
from constants import SCREEN_SIZE
from .main import NormalChessMainView
from .move_packet import MovePacket
from piece.type import PieceType, PieceColor
from piece.piece import Piece


class ClientChannel(Channel):
    def __init__(self, *args, **kwargs): # type: ignore
        super().__init__(*args, **kwargs) # type: ignore

    def Network_move(self, data: dict[str, Any]) -> None:
        print(f"Server received {data}")
        self._server.move(data) # type: ignore


class ServerChannel(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs) -> None: # type: ignore
        super().__init__(*args, **kwargs) # type: ignore

        self.white: ClientChannel | None = None
        self.black: ClientChannel | None = None
    
    def Connected(self, channel: ClientChannel, addr: Any):
        print(f"{channel} connected")
        if self.white is None:
            self.white = channel
        else:
            self.black = channel

    def move(self, data: dict[str, Any]) -> None:
        assert(self.white and self.black)

        if data["move"]["src_color"] == PieceColor.BLACK.value:
            self.white.Send(data) # type: ignore
        else:
            self.black.Send(data) # type: ignore


class NormalChessOnlineView(NormalChessMainView, ConnectionListener):
    def __init__(self, my_turn_color: PieceColor, is_host: bool, host, port) -> None: # type: ignore
        NormalChessMainView.__init__(self)
        self.board.inverted = my_turn_color == PieceColor.BLACK

        self.server: ServerChannel | None = ServerChannel(localaddr=(host, port)) if is_host else None
        self.Connect((host, port)) # type: ignore

        self.my_turn_color: PieceColor = my_turn_color
        self.move_packet: MovePacket | None = None

        self.enemy_pieces_moving: list[Piece] = []
        self.enemy_promotion_piece: tuple[PieceType, PieceColor] | None = None

    def is_my_turn(self):
        return self.cur_turn_color == self.my_turn_color

    def on_update(self, delta_time: float) -> None:
        connection.Pump()
        self.Pump()

        if self.server:
            self.server.Pump()

        if self.is_my_turn():
            if self.selected and self.selected.just_finished_moving:
                connection.Send({ # type: ignore
                    "action": "move",
                    "move": self.selected.move_packet.to_dict()
                })
            NormalChessMainView.on_update(self, delta_time)
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
            if self.move_packet.capture:
                self.board.kill_piece(self.move_packet.capture)

            for start, end in zip(self.move_packet.start, self.move_packet.end):
                assert(piece := self.board[start])
                piece.move(end)
                self.enemy_pieces_moving.append(piece)

            self.future_en_passant_pos = self.move_packet.future_en_passant_pos
            self.enemy_promotion_piece = self.move_packet.promotion_piece
            self.last_move = self.move_packet.start[0], self.move_packet.end[0]
            self.move_packet = None

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.is_my_turn():
            super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.is_my_turn():
            super().on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        super().on_mouse_motion(x, y, dx, dy)

        if self.board.inverted:
            self.mouse_x, self.mouse_y = SCREEN_SIZE - self.mouse_x, SCREEN_SIZE - self.mouse_y

    def Network_move(self, data: dict[str, Any]):
        print(f"Client received {data}")
        self.move_packet = MovePacket.from_dict(data["move"])