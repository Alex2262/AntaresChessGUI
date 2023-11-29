
import pygame

from constants import *
from position import Position
from objects import Piece


class GameState:
    def __init__(self):
        self.position = Position()
        self.pieces = []
        self.piece_images = []
        self.fen = START_FEN

        self.in_play = True

        self.setting_white_time = 60000
        self.setting_black_time = 60000
        self.setting_white_increment = 1000
        self.setting_black_increment = 1000

        self.times = [60000, 60000]

        self.old_ep_square = 0
        self.old_castle_ability_bits = 0

        self.move_archive = []

        self.initialize_piece_images()

    def initialize_piece_images(self):
        color_names = ["w", "b"]
        for color in range(2):
            new_arr = []
            for piece in range(6):
                new_arr.append(pygame.image.load(
                    FILE_PATH + "images/{}.png".format(color_names[color] + PIECE_MATCHER[piece])).convert_alpha())
            self.piece_images.append(new_arr)

    def initialize_pieces(self):
        self.pieces = []

        for i in range(64):

            pos = STANDARD_TO_MAILBOX[i]
            row = i // 8
            col = i % 8
            piece = self.position.board[pos]
            if piece < EMPTY:
                self.pieces.append(Piece((STARTING_SQ[0] + DEFAULT_SQ_SIZE * col,
                                                STARTING_SQ[1] + DEFAULT_SQ_SIZE * row,
                                                DEFAULT_SQ_SIZE,
                                                DEFAULT_SQ_SIZE),
                                        row, col, piece >= 6,
                                        PIECE_MATCHER[self.position.board[pos] % 6].lower(),
                                        self.piece_images))

    def get_piece(self, col, row):
        for piece in self.pieces:
            if piece.col == col and piece.row == row:
                return piece

        return None

    def make_move(self, move):
        self.old_ep_square = self.position.ep_square
        self.old_castle_ability_bits = self.position.castle_ability_bits

        self.position.make_move(move)
        self.position.side ^= 1

        self.move_archive.append(move)

    def undo_move(self):
        if len(self.move_archive) == 0 or self.move_archive[-1] == 0:
            print("INVALID LAST MOVE")
            return

        self.position.undo_move(self.move_archive[-1], self.old_ep_square, self.old_castle_ability_bits)
        self.position.side ^= 1

        self.old_ep_square = 0
        self.old_castle_ability_bits = 0
        self.move_archive.pop(-1)
