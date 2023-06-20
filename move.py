
from constants import *

"""
           Binary move bits                Meaning          Hexadecimal

    0000 0000 0000 0000 0000 0000 0111 1111    from   square       0x7f
    0000 0000 0000 0000 0011 1111 1000 0000    to     square       0x3f80
    0000 0000 0000 0011 1100 0000 0000 0000    selected            0x3c000
    0000 0000 0011 1100 0000 0000 0000 0000    occupied            0x3c0000
    0000 0001 1100 0000 0000 0000 0000 0000    move type           0x1c00000
    0001 1110 0000 0000 0000 0000 0000 0000    promotion piece     0x1e000000
    0010 0000 0000 0000 0000 0000 0000 0000    is_capture          0x20000000

"""


def encode_move(from_square, to_square, selected, occupied, move_type, promotion_piece, is_capture):
    return from_square | to_square << 7 | selected << 14 | occupied << 18 | move_type << 22 | \
        promotion_piece << 25 | is_capture << 29


def get_from_square(move):
    return move & 0x7f


def get_to_square(move):
    return (move & 0x3f80) >> 7


def get_selected(move):
    return (move & 0x3c000) >> 14


def get_occupied(move):
    return (move & 0x3c0000) >> 18


def get_move_type(move):
    return (move & 0x1c00000) >> 22


def get_promotion_piece(move):
    return (move & 0x1e000000) >> 25


def get_is_capture(move):
    return (move & 0x20000000) >> 29


def get_uci_from_move(move):

    uci_move = ""

    from_square = get_from_square(move)
    to_square = get_to_square(move)

    move_type = get_move_type(move)

    from_pos = MAILBOX_TO_STANDARD[from_square]
    to_pos = MAILBOX_TO_STANDARD[to_square]

    num_from_pos = [from_pos // 8, from_pos % 8]
    num_to_pos = [to_pos // 8, to_pos % 8]

    uci_move += chr(num_from_pos[1] + 97) + str(8 - num_from_pos[0])
    uci_move += chr(num_to_pos[1] + 97) + str(8 - num_to_pos[0])

    if move_type == 3:
        promotion_piece = get_promotion_piece(move)
        if promotion_piece == WHITE_QUEEN or promotion_piece == BLACK_QUEEN:
            uci_move += "q"
        elif promotion_piece == WHITE_ROOK or promotion_piece == BLACK_ROOK:
            uci_move += "r"
        elif promotion_piece == WHITE_BISHOP or promotion_piece == BLACK_BISHOP:
            uci_move += "b"
        elif promotion_piece == WHITE_KNIGHT or promotion_piece == BLACK_KNIGHT:
            uci_move += "n"

    return uci_move


def get_move_from_uci(position, uci):
    promotion_piece = 0
    if len(uci) == 5:
        if uci[4] == "q":
            promotion_piece = 4
        elif uci[4] == "r":
            promotion_piece = 3
        elif uci[4] == "b":
            promotion_piece = 2
        elif uci[4] == "n":
            promotion_piece = 1

        promotion_piece += position.side * BLACK_PAWN
        uci = uci[:4]

    num_from_pos = [8 - ord(uci[1]) + 48, ord(uci[0]) - 97]
    num_to_pos = [8 - ord(uci[3]) + 48, ord(uci[2]) - 97]

    from_pos = num_from_pos[0] * 8 + num_from_pos[1]
    to_pos = num_to_pos[0] * 8 + num_to_pos[1]

    from_square = STANDARD_TO_MAILBOX[from_pos]
    to_square = STANDARD_TO_MAILBOX[to_pos]

    selected = position.board[from_square]
    occupied = position.board[to_square]

    move_type = 0

    if selected == WHITE_PAWN or selected == BLACK_PAWN:
        if 21 <= to_square <= 28:
            move_type = 3
        elif 91 <= to_square <= 98:
            move_type = 3
        elif to_square == position.ep_square:
            move_type = 1

    elif selected == WHITE_KING or selected == BLACK_KING:
        if abs(to_square - from_square) == 2:
            move_type = 2

    is_capture = 1 if occupied < EMPTY else 0
    move = encode_move(from_square, to_square, selected, occupied, move_type, promotion_piece, is_capture)

    return move


def get_move_from_array_move(position, array_move):
    from_square = STANDARD_TO_MAILBOX[array_move[1] * 8 + array_move[0]]
    to_square = STANDARD_TO_MAILBOX[array_move[3] * 8 + array_move[2]]

    move_type = 0

    selected = position.board[from_square]
    occupied = position.board[to_square]

    if selected == WHITE_PAWN or selected == BLACK_PAWN:
        if 21 <= to_square <= 28:
            move_type = 3
        elif 91 <= to_square <= 98:
            move_type = 3
        elif to_square == position.ep_square:
            move_type = 1

    elif selected == WHITE_KING or selected == BLACK_KING:
        if abs(to_square - from_square) == 2:
            move_type = 2

    promotion_piece = array_move[4] if move_type == 3 else 0

    is_capture = 1 if occupied < EMPTY else 0
    move = encode_move(from_square, to_square, selected, occupied, move_type, promotion_piece, is_capture)

    return move

