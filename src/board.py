import arcade
from typing import TypeVar, Generic
from constants import PIECE_SCALE, PIECE_SIZE, BOARD_SIZE, SCREEN_SIZE
from piece.type import PieceType, PieceColor, MarkerPieceType, PiecePos, piece_type_from_str, piece_color_from_str, marker_sprite_paths


# T should only ever be Piece. Making it generic is a workaround to get static type checking without circular imports
T = TypeVar('T')
class Board(Generic[T]):
    tile_colors = [arcade.color.DARK_MOSS_GREEN, arcade.color.FLORAL_WHITE]

    def __init__(self, initial_board: list[list[str]], *, inverted: bool = False) -> None:
        from piece.piece import Piece

        self.data: list[list[T | None]] = []
        self.pieces: arcade.SpriteList[Piece] = arcade.SpriteList()
        self.inverted = inverted
        self.fill(initial_board)

        self.old_markers: dict[PiecePos, MarkerPieceType] = {}
        self.new_markers: dict[PiecePos, MarkerPieceType] = {}
        self.markers_to_draw: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()

        self.captured_pieces: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self.captured_pieces_camera: arcade.Camera2D = arcade.Camera2D(arcade.LBWH(0, 0, SCREEN_SIZE, SCREEN_SIZE))

    def fill(self, initial_board: list[list[str]]) -> None:
        self.data.clear()
        self.pieces.clear()

        for rank, row in enumerate(reversed(initial_board)):
            self.data.append([])
            for file, name in enumerate(row):
                if name == "":
                    self.data[-1].append(None)
                else:
                    self.data[-1].append(self.new_piece_of_name(name, PiecePos(rank, file), add_to_board=False))

    def new_piece_of_name(self, name: str, piece_pos: PiecePos, *, add_to_board: bool = True, append_to_sprite_list: bool = True) -> T:
        piece_type = piece_type_from_str[name[0]]
        piece_color = piece_color_from_str[name[1]]
        return self.new_piece_of_type(piece_type, piece_color, piece_pos, add_to_board=add_to_board, append_to_sprite_list=append_to_sprite_list)

    def new_piece_of_type(self, piece_type: PieceType, piece_color: PieceColor, piece_pos: PiecePos, *, add_to_board: bool = True, append_to_sprite_list: bool = True) -> T:
        from piece.pawn import Pawn
        from piece.single_move_piece import SingleMovePiece
        from piece.looping_move_piece import LoopingMovePiece
        from piece.rook import Rook
        from piece.king import King

        match piece_type:
            case PieceType.PAWN:
                piece = Pawn(piece_color, piece_pos, self) # pyright: ignore[reportArgumentType]
            case PieceType.KNIGHT:
                piece = SingleMovePiece(piece_type, piece_color, piece_pos, self, {PiecePos(1, 2)}) # pyright: ignore[reportArgumentType]
            case PieceType.BISHOP:
                piece = LoopingMovePiece(piece_type, piece_color, piece_pos, self, {PiecePos(1, 1)}) # pyright: ignore[reportArgumentType]
            case PieceType.ROOK:
                piece = Rook(piece_color, piece_pos, self) # pyright: ignore[reportArgumentType]
            case PieceType.QUEEN:
                piece = LoopingMovePiece(piece_type, piece_color, piece_pos, self, {PiecePos(0, 1), PiecePos(1, 1)}) # pyright: ignore[reportArgumentType]
            case PieceType.KING:
                piece = King(piece_color, piece_pos, self) # pyright: ignore[reportArgumentType]

        if add_to_board:
            self[piece.piece_pos] = piece # pyright: ignore[reportArgumentType]

        if append_to_sprite_list:
            self.pieces.append(piece)

        return piece # pyright: ignore[reportReturnType]

    def add_piece(self, piece: T) -> None:
        from piece.piece import Piece
        assert(isinstance(piece, Piece))

        piece.reset_pos()
        self[piece.piece_pos] = piece
        self.pieces.append(piece)

    def kill_piece(self, pos: PiecePos) -> None:
        from piece.piece import Piece

        assert(victim := self[pos])
        assert(isinstance(victim, Piece))

        self[pos] = None
        victim.remove_from_sprite_lists()

        """
        victim.piece_pos = PiecePos.out_of_bounds()
        victim.position = 0, 0
        victim.multiply_scale(0.5)
        self.captured_pieces.append(victim)
        """

    def add_marker(self, pos: PiecePos, type: MarkerPieceType) -> None:
        self.new_markers[pos] = type

    def has_marker(self, pos: PiecePos, type: MarkerPieceType) -> bool:
        return pos in self.old_markers and self.old_markers[pos] == type

    def advance_markers(self) -> None:
        self.old_markers = self.new_markers
        self.new_markers = {}

        self.markers_to_draw.clear()
        for pos, marker_type in self.old_markers.items():
            self.markers_to_draw.append(arcade.Sprite(marker_sprite_paths[marker_type], PIECE_SCALE, int((pos.file + 0.5) * PIECE_SIZE), int((pos.rank + 0.5) * PIECE_SIZE)))

    def get_enemy_king_pos(self, color: PieceColor) -> PiecePos:
        for piece in self.pieces:
            if piece.has_type(PieceType.KING) and not piece.has_color(color):
                return piece.piece_pos

        assert(False)

    def draw_everything(self) -> None:
        self.draw_background()
        self.draw_pieces()
        self.draw_captured_pieces()

    def draw_background(self) -> None:
        for rank in range(BOARD_SIZE):
            for file in range(BOARD_SIZE):
                arcade.draw_lbwh_rectangle_filled(file * PIECE_SIZE, rank * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE, self.tile_colors[(rank + file) % 2])

    def draw_pieces(self) -> None:
        if self.inverted:
            for piece in self.pieces:
                piece.center_x, piece.center_y = SCREEN_SIZE - piece.center_x, SCREEN_SIZE - piece.center_y

        self.pieces.draw(pixelated=True)

        if self.inverted:
            for piece in self.pieces:
                piece.center_x, piece.center_y = SCREEN_SIZE - piece.center_x, SCREEN_SIZE - piece.center_y

    def draw_markers(self) -> None:
        if self.inverted:
            for marker in self.markers_to_draw:
                marker.center_x, marker.center_y = SCREEN_SIZE - marker.center_x, SCREEN_SIZE - marker.center_y

        self.markers_to_draw.draw(pixelated=True)

        if self.inverted:
            for marker in self.markers_to_draw:
                marker.center_x, marker.center_y = SCREEN_SIZE - marker.center_x, SCREEN_SIZE - marker.center_y

    def draw_captured_pieces(self) -> None:
        self.captured_pieces_camera.use()

        if self.inverted:
            for piece in self.captured_pieces:
                piece.center_x, piece.center_y = SCREEN_SIZE - piece.center_x, SCREEN_SIZE - piece.center_y

        self.captured_pieces.draw(pixelated=True)

        if self.inverted:
            for piece in self.captured_pieces:
                piece.center_x, piece.center_y = SCREEN_SIZE - piece.center_x, SCREEN_SIZE - piece.center_y

    def to_piece_pos(self, x: int, y: int) -> PiecePos:
        if self.inverted:
            x, y = SCREEN_SIZE - x, SCREEN_SIZE - y

        return PiecePos(int(y // PIECE_SIZE), int(x // PIECE_SIZE))

    def color_tile(self, pos: PiecePos, color: arcade.types.Color) -> None:
        if self.inverted:
            pos = PiecePos(BOARD_SIZE - 1, BOARD_SIZE - 1) - pos

        arcade.draw_lbwh_rectangle_filled(pos.file * PIECE_SIZE, pos.rank * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE, color)

    def __getitem__(self, pos: PiecePos) -> T | None:
        if not self.is_in_bounds(pos):
            raise IndexError(f"PiecePos {pos} out of range for board")

        return self.data[pos.rank][pos.file]

    def __setitem__(self, pos: PiecePos, value: T | None):
        if not self.is_in_bounds(pos):
            raise IndexError(f"PiecePos {pos} out of range for board")

        self.data[pos.rank][pos.file] = value

    def __repr__(self) -> str:
        out = "Board("

        for rank in reversed(self.data):
            out += f"\n    {rank}"

        return out + "\n)"

    @staticmethod
    def is_in_bounds(pos: PiecePos) -> bool:
        return 0 <= pos.rank < BOARD_SIZE and 0 <= pos.file < BOARD_SIZE