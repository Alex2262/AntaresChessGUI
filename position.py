
from move import *


class Position:
    def __init__(self):
        self.board = np.zeros(120, dtype=np.uint8)
        self.white_pieces = []
        self.black_pieces = []
        self.king_positions = np.zeros(2, dtype=np.uint8)
        self.castle_ability_bits = 0
        self.ep_square = 0
        self.side = 0

        self.parse_fen(START_FEN)

    def reset_position(self):
        self.board = np.zeros(120, dtype=np.uint8)
        self.white_pieces = []
        self.black_pieces = []
        self.king_positions = np.zeros(2, dtype=np.uint8)
        self.castle_ability_bits = 0
        self.ep_square = 0
        self.side = 0

    def parse_fen(self, fen_string):

        fen_list = fen_string.strip().split()

        if len(fen_list) < 4:
            return False

        self.reset_position()

        fen_board = fen_list[0]
        turn = fen_list[1]

        # -- boundaries for 12x10 mailbox --
        pos = 21
        for i in range(21):
            self.board[i] = PADDING

        # -- parse board --
        for i in fen_board:
            if i == "/":
                self.board[pos] = PADDING
                self.board[pos + 1] = PADDING
                pos += 2
            elif i.isdigit():
                for j in range(ord(i) - 48):
                    self.board[pos] = EMPTY
                    pos += 1
            elif i.isalpha():
                idx = 0
                if i.islower():
                    idx = 6
                piece = i.upper()
                for j, p in enumerate(PIECE_MATCHER):
                    if piece == p:
                        idx += j
                self.board[pos] = idx

                if idx < BLACK_PAWN:
                    self.white_pieces.append(pos)
                else:
                    self.black_pieces.append(pos)

                if i == 'K':
                    self.king_positions[0] = pos
                elif i == 'k':
                    self.king_positions[1] = pos
                pos += 1

        # -- boundaries for 12x10 mailbox --
        for i in range(21):
            self.board[pos + i] = PADDING

        self.castle_ability_bits = 0
        for i in fen_list[2]:
            if i == "K":
                self.castle_ability_bits |= 1
            elif i == "Q":
                self.castle_ability_bits |= 2
            elif i == "k":
                self.castle_ability_bits |= 4
            elif i == "q":
                self.castle_ability_bits |= 8

        # -- en passant square --
        if len(fen_list[3]) > 1:
            square = [8 - (ord(fen_list[3][1]) - 48), ord(fen_list[3][0]) - 97]

            square = square[0] * 8 + square[1]

            self.ep_square = STANDARD_TO_MAILBOX[square]
        else:
            self.ep_square = 0

        self.side = 0
        if turn == "b":
            self.side = 1

        return True

    def get_pseudo_legal_moves(self):
        moves = []

        if self.side == 0:  # white
            for pos in self.white_pieces:
                piece = self.board[pos]

                for increment in WHITE_INCREMENTS[piece]:
                    if increment == 0:
                        break

                    new_pos = pos
                    while True:
                        new_pos += increment
                        occupied = self.board[new_pos]
                        if occupied == PADDING or occupied < BLACK_PAWN:  # standing on own piece or outside of board
                            break
                        elif piece == WHITE_PAWN and increment in (-10, -20) and self.board[pos - 10] != EMPTY:
                            break
                        elif piece == WHITE_PAWN and increment == -20 and (pos < 81 or occupied != EMPTY):
                            break

                        # En passant
                        if piece == WHITE_PAWN and increment in (-11, -9) and occupied == EMPTY:
                            if new_pos == self.ep_square:
                                moves.append(encode_move(pos, new_pos,
                                                         WHITE_PAWN, EMPTY,
                                                         MOVE_TYPE_EP, 0, 0))
                            break

                        # Promotion
                        elif piece == WHITE_PAWN and new_pos < 31:
                            for j in range(WHITE_KNIGHT, WHITE_KING):
                                moves.append(encode_move(pos, new_pos,
                                                         WHITE_PAWN, occupied,
                                                         MOVE_TYPE_PROMOTION, j, 1 if occupied < EMPTY else 0))
                            break

                        # Normal capture move
                        if occupied < EMPTY:
                            moves.append(encode_move(pos, new_pos,
                                                     piece, occupied,
                                                     MOVE_TYPE_NORMAL, 0, 1))
                            break

                        # Normal non-capture move
                        moves.append(encode_move(pos, new_pos,
                                                 piece, occupied,
                                                 MOVE_TYPE_NORMAL, 0, 0))

                        # if we are a non-sliding piece, or we have captured an opposing piece then stop
                        if piece in (WHITE_PAWN, WHITE_KNIGHT, WHITE_KING):
                            break

                        # King side castle
                        if self.castle_ability_bits & 1 == 1 and pos == H1 and self.board[new_pos - 1]\
                                == WHITE_KING:
                            moves.append(encode_move(E1, G1, WHITE_KING,
                                                     EMPTY, MOVE_TYPE_CASTLE, 0, 0))
                        # Queen side castle
                        elif self.castle_ability_bits & 2 == 2 and pos == A1 and self.board[new_pos + 1]\
                                == WHITE_KING:
                            moves.append(encode_move(E1, C1, WHITE_KING,
                                                     EMPTY, MOVE_TYPE_CASTLE, 0, 0))

        else:
            for pos in self.black_pieces:
                piece = self.board[pos]

                for increment in BLACK_INCREMENTS[piece - BLACK_PAWN]:
                    if increment == 0:
                        break

                    new_pos = pos

                    while True:
                        new_pos += increment
                        occupied = self.board[new_pos]
                        if occupied != EMPTY and occupied > WHITE_KING:  # standing on own piece or outside of board
                            break
                        elif piece == BLACK_PAWN and increment in (10, 20) and self.board[pos + 10] != EMPTY:
                            break
                        elif piece == BLACK_PAWN and increment == 20 and (pos > 38 or occupied != EMPTY):
                            break

                        # En passant
                        if piece == BLACK_PAWN and increment in (11, 9) and occupied == EMPTY:
                            if new_pos == self.ep_square:
                                moves.append(encode_move(pos, new_pos,
                                                         BLACK_PAWN, EMPTY,
                                                         MOVE_TYPE_EP, 0, 0))
                            break

                        # Promotion
                        elif piece == BLACK_PAWN and new_pos > 88:
                            for j in range(BLACK_KNIGHT, BLACK_KING):
                                moves.append(encode_move(pos, new_pos,
                                                         BLACK_PAWN, occupied,
                                                         MOVE_TYPE_PROMOTION, j, 1 if occupied < BLACK_PAWN else 0))
                            break

                        # Normal capture move
                        if occupied < BLACK_PAWN:
                            moves.append(encode_move(pos, new_pos,
                                                     piece, occupied,
                                                     MOVE_TYPE_NORMAL, 0, 1))
                            break
                        # Normal non-capture move
                        moves.append(encode_move(pos, new_pos,
                                                 piece, occupied,
                                                 MOVE_TYPE_NORMAL, 0, 0))

                        # if we are a non-sliding piece, or we have captured an opposing piece then stop
                        if piece in (BLACK_PAWN, BLACK_KNIGHT, BLACK_KING):
                            break

                        # King side castle
                        if self.castle_ability_bits & 4 == 4 and pos == H8 and self.board[new_pos - 1]\
                                == BLACK_KING:
                            moves.append(encode_move(E8, G8, BLACK_KING,
                                                     EMPTY, MOVE_TYPE_CASTLE, 0, 0))
                        # Queen side castle
                        elif self.castle_ability_bits & 8 == 8 and pos == A8 and self.board[new_pos + 1]\
                                == BLACK_KING:
                            moves.append(encode_move(E8, C8, BLACK_KING,
                                                     EMPTY, MOVE_TYPE_CASTLE, 0, 0))

        return moves

    def is_attacked(self, pos):
        if self.side == 0:
            for piece in (WHITE_QUEEN, WHITE_KNIGHT):
                for increment in ATK_INCREMENTS[piece]:
                    if increment == 0:
                        break
                    new_pos = pos
                    while True:
                        new_pos += increment
                        occupied = self.board[new_pos]
                        if occupied == PADDING or occupied < BLACK_PAWN:  # standing on own piece or outside of board
                            break

                        if occupied < EMPTY:
                            if piece == occupied - BLACK_PAWN:
                                return True

                            if piece == WHITE_KNIGHT:
                                break

                            if occupied == BLACK_KNIGHT:
                                break

                            if occupied == BLACK_KING:  # king
                                if new_pos == pos + increment:
                                    return True
                                break

                            if occupied == BLACK_PAWN:  # pawn
                                if new_pos == pos - 11 or \
                                        new_pos == pos - 9:
                                    return True
                                break

                            if occupied == BLACK_BISHOP:  # bishop
                                if increment in (-11, 11, 9, -9):
                                    return True
                                break
                            if occupied == BLACK_ROOK:  # rook
                                if increment in (-10, 1, 10, -1):
                                    return True
                                break

                        if piece == WHITE_KNIGHT:  # if checking with knight
                            break

        else:
            for piece in (BLACK_QUEEN, BLACK_KNIGHT):
                for increment in ATK_INCREMENTS[piece - BLACK_PAWN]:
                    if increment == 0:
                        break
                    new_pos = pos
                    while True:
                        new_pos += increment
                        occupied = self.board[new_pos]
                        if occupied != EMPTY and occupied > WHITE_KING:  # standing on own piece or outside of board
                            break

                        if occupied < BLACK_PAWN:
                            if piece == occupied + BLACK_PAWN:
                                return True

                            if piece == BLACK_KNIGHT:
                                break
                            if occupied == WHITE_KNIGHT:
                                break
                            if occupied == WHITE_KING:  # king
                                if new_pos == pos + increment:
                                    return True
                                break

                            if occupied == WHITE_PAWN:  # pawn
                                if new_pos == pos + 11 or \
                                        new_pos == pos + 9:
                                    return True
                                break

                            if occupied == WHITE_BISHOP:  # bishop
                                if increment in (-11, 11, 9, -9):
                                    return True
                                break
                            if occupied == WHITE_ROOK:  # rook
                                if increment in (-10, 1, 10, -1):
                                    return True
                                break

                        if piece == BLACK_KNIGHT:  # if checking with knight
                            break

        return False

    def make_move(self, move):

        # Get move info
        castled_pos = np.array([0, 0], dtype=np.int8)
        from_square = get_from_square(move)
        to_square = get_to_square(move)
        selected = get_selected(move)
        move_type = get_move_type(move)

        # Normal move
        if move_type == MOVE_TYPE_NORMAL:
            # Set the piece to the target square and hash it
            self.board[to_square] = selected

        # En passant move
        elif move_type == MOVE_TYPE_EP:
            # Set the piece to the target square and hash it
            self.board[to_square] = selected

            # Remove the en passant captured pawn and hash it
            if self.side == 0:
                self.board[to_square + 10] = EMPTY
                self.black_pieces.remove(to_square + 10)
            else:
                self.board[to_square - 10] = EMPTY
                self.white_pieces.remove(to_square - 10)

        # Castling move
        elif move_type == MOVE_TYPE_CASTLE:
            # Set the piece to the target square and hash it
            self.board[to_square] = selected

            # Queen side castling
            if to_square < from_square:
                castled_pos[0], castled_pos[1] = to_square - 2, to_square + 1  # A1/A8, D1/D8
            # King side castling
            else:
                castled_pos[0], castled_pos[1] = to_square + 1, to_square - 1  # H1/H8, F1/F8

            # Move the rook and hash it
            if self.side == 0:
                self.board[castled_pos[1]] = WHITE_ROOK

                # Remove the rook from the source square and hash it
                self.board[castled_pos[0]] = EMPTY

                self.white_pieces[self.white_pieces.index(castled_pos[0])] = castled_pos[1]
            else:
                self.board[castled_pos[1]] = BLACK_ROOK

                # Remove the rook from the source square and hash it
                self.board[castled_pos[0]] = EMPTY

                self.black_pieces[self.black_pieces.index(castled_pos[0])] = castled_pos[1]

        # Promotion move
        elif move_type == MOVE_TYPE_PROMOTION:
            # Get the promoted piece, set it in the new location, and hash it
            promoted_piece = get_promotion_piece(move)
            self.board[to_square] = promoted_piece

        # Remove the piece from the source square
        self.board[from_square] = EMPTY

        if self.side == 0:
            self.white_pieces[self.white_pieces.index(from_square)] = to_square
            if get_is_capture(move):
                self.black_pieces.remove(to_square)
        else:
            self.black_pieces[self.black_pieces.index(from_square)] = to_square
            if get_is_capture(move):
                self.white_pieces.remove(to_square)

        # Change the king position for check detection
        if selected == WHITE_KING or selected == BLACK_KING:
            self.king_positions[self.side] = to_square

        # Legal move checking.
        # Return False if we are in check after our move or castling isn't legal.
        if self.is_attacked(self.king_positions[self.side]):
            return False
        elif castled_pos[0]:
            # If we have castled, then we already checked to_square with is_attacked since the king moved.
            # We then check the position of where the rook would be, and also where the king originally was
            if self.is_attacked(castled_pos[1]):
                return False
            elif self.is_attacked(from_square):
                return False

        # --- The move is legal ---

        # Double pawn push
        if (selected == WHITE_PAWN or selected == BLACK_PAWN) and abs(to_square - from_square) == 20:
            self.ep_square = to_square - self.side * 20 + 10  # 119 - (to_square + 10)

        # Reset ep square since it is not a double pawn push
        else:
            self.ep_square = 0

        if selected == WHITE_KING:
            self.castle_ability_bits &= ~(1 << 0)
            self.castle_ability_bits &= ~(1 << 1)
        elif selected == BLACK_KING:
            self.castle_ability_bits &= ~(1 << 2)
            self.castle_ability_bits &= ~(1 << 3)

        # Update the castling rights if necessary
        if from_square == H1:
            self.castle_ability_bits &= ~(1 << 0)
        elif from_square == A1:
            self.castle_ability_bits &= ~(1 << 1)
        if to_square == H8:
            self.castle_ability_bits &= ~(1 << 2)
        elif to_square == A8:
            self.castle_ability_bits &= ~(1 << 3)

        return True

    def undo_move(self, move, current_ep, current_castle_ability_bits):

        # Get move info
        from_square = get_from_square(move)
        to_square = get_to_square(move)
        selected = get_selected(move)
        occupied = get_occupied(move)
        move_type = get_move_type(move)

        # En Passant move
        if move_type == MOVE_TYPE_EP:
            # Place the en passant captured pawn back and hash it
            if self.side == 0:
                self.board[to_square + 10] = BLACK_PAWN
                self.black_pieces.append(to_square + 10)
            else:
                self.board[to_square - 10] = WHITE_PAWN
                self.white_pieces.append(to_square - 10)

        # Castling move
        if move_type == MOVE_TYPE_CASTLE:
            # Queen side castle
            if to_square < from_square:
                # Remove the rook from the destination square
                self.board[from_square - 1] = EMPTY
                if self.side == 0:
                    # Move the rook back
                    self.board[to_square - 2] = WHITE_ROOK
                    self.white_pieces[self.white_pieces.index(from_square - 1)] = to_square - 2
                else:
                    # Move the rook back
                    self.board[to_square - 2] = BLACK_ROOK
                    self.black_pieces[self.black_pieces.index(from_square - 1)] = to_square - 2
            # King side castle
            else:
                # Remove the rook from the destination square
                self.board[from_square + 1] = EMPTY
                if self.side == 0:
                    # Move the rook back
                    self.board[to_square + 1] = WHITE_ROOK
                    self.white_pieces[self.white_pieces.index(from_square + 1)] = to_square + 1
                else:
                    # Move the rook back
                    self.board[to_square + 1] = BLACK_ROOK
                    self.black_pieces[self.black_pieces.index(from_square + 1)] = to_square + 1

        if self.side == 0:
            self.white_pieces[self.white_pieces.index(to_square)] = from_square
            if get_is_capture(move):
                self.black_pieces.append(to_square)
        else:
            self.black_pieces[self.black_pieces.index(to_square)] = from_square
            if get_is_capture(move):
                self.white_pieces.append(to_square)

        # Place occupied piece/value back in the destination square
        # Set the source square back to the selected piece
        self.board[to_square] = occupied
        self.board[from_square] = selected

        # The en passant square has changed
        if self.ep_square != current_ep:
            self.ep_square = current_ep

        # Revert the castling rights
        self.castle_ability_bits = current_castle_ability_bits

        # Reset the king position if it has moved
        if selected == WHITE_KING or selected == BLACK_KING:
            self.king_positions[self.side] = from_square

    def get_legal_moves(self):
        moves = self.get_pseudo_legal_moves()
        new_moves = []

        current_ep = self.ep_square
        current_castle_ability_bits = self.castle_ability_bits
        for move in moves:
            attempt = self.make_move(move)
            if attempt:
                new_moves.append(move)
            self.undo_move(move, current_ep, current_castle_ability_bits)

        return new_moves

