
"""
Main Driver file.
"""
import sys
import threading

import math
import pyperclip
import re

from objects import *
from move import *
from game_handler import GameState
from engine_handler import Engine


def main():
    pygame.init()

    screen_size = DEFAULT_SCREEN_SIZE
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

    screen.fill(SCREEN_COLOR)

    pygame.display.set_caption("Chess")

    main_state = GameState()
    new_mode = 0

    while True:
        if new_mode == -1:
            return
        elif new_mode == 0:
            new_mode = main_menu(screen, main_state)
        elif new_mode == 1:
            new_mode = game_options_menu(screen, main_state)
        elif new_mode == 2:
            new_mode = engine_options_menu(screen, main_state)


def main_menu(screen, main_state):

    # Important Variables

    screen_size = screen.get_size()

    mode = 0

    buttons = [
        RectTextButton(BUTTON1_COLOR, (770, 30, 200, 40), False, 0, DEFAULT_RECT_RADIUS, "menu:1", 'Game Options',
                       BUTTON_TEXT_COLOR),
        RectTextButton(BUTTON1_COLOR, (770, 80, 200, 40), False, 0, DEFAULT_RECT_RADIUS, "menu:2", 'Engine Options',
                       BUTTON_TEXT_COLOR),
        RectTextButton(BUTTON1_COLOR, (888, 136, 76, 26), False, 0, DEFAULT_RECT_RADIUS, "toggle:analysis", 'Off',
                       BUTTON_TEXT_COLOR),
        RectTextButton(BUTTON1_COLOR, (828, 488, 18, 18), False, 0, DEFAULT_RECT_RADIUS, "engine:pv:+", '+',
                       BUTTON_TEXT_COLOR),
        RectTextButton(BUTTON1_COLOR, (850, 488, 18, 18), False, 0, DEFAULT_RECT_RADIUS, "engine:pv:-", '-',
                       BUTTON_TEXT_COLOR),
        RectTextButton(BUTTON1_COLOR, (926, 488, 18, 18), False, 0, DEFAULT_RECT_RADIUS, "engine:cpu:+", '+',
                       BUTTON_TEXT_COLOR),
        RectTextButton(BUTTON1_COLOR, (948, 488, 18, 18), False, 0, DEFAULT_RECT_RADIUS, "engine:cpu:-", '-',
                       BUTTON_TEXT_COLOR),
        RectTextButton(BUTTON1_COLOR, (610, 80, 120, 20), False, 0, DEFAULT_RECT_RADIUS, "position:undo", 'Undo',
                       BUTTON_TEXT_COLOR),
        RectTextButton(BUTTON1_COLOR, (610, 110, 120, 20), False, 0, DEFAULT_RECT_RADIUS, "position:flip", 'Flip',
                       BUTTON_TEXT_COLOR)
    ]

    eval_bar = EvalBar(LAYER2_COLOR, (20, 20, 40, 500), 0, DEFAULT_RECT_RADIUS)
    basic_objects = [
        eval_bar,
        RectObject(LAYER2_COLOR, (80, 20, 500, 500), False, 0, DEFAULT_RECT_RADIUS),
        RectObject(LAYER2_COLOR, (600, 20, 140, 500), False, 0, DEFAULT_RECT_RADIUS),
        RectObject(LAYER2_COLOR, (760, 20, 220, 500), False, 0, DEFAULT_RECT_RADIUS),
        RectObject(LAYER1_COLOR, (770, 130, 200, 380), False, 0, DEFAULT_RECT_RADIUS),
        RectObject(LAYER3_COLOR, (774, 134, 192, 30), False, 0, DEFAULT_RECT_RADIUS),
        RectTextObject(LAYER3_COLOR, (774, 134, 116, 30), False, 0, DEFAULT_RECT_RADIUS, "Analysis: ", TEXT_COLOR),
        RectTextObject(LAYER4_COLOR, (774, 488, 50, 18), False, 0, DEFAULT_RECT_RADIUS, "Lines", TEXT_COLOR),
        RectTextObject(LAYER4_COLOR, (872, 488, 50, 18), False, 0, DEFAULT_RECT_RADIUS, "CPU: 0", TEXT_COLOR),
    ]

    board_gui = Board(CHESS_BOARD_COLOR, (STARTING_SQ[0], STARTING_SQ[1], 480, 480))

    # Engine
    engine_side = BLACK_COLOR
    engine_play = False

    engine_files = os.listdir(FILE_PATH + "engines/")

    engine_files = [FILE_PATH + "engines/" + x for x in engine_files]
    engine_file = FILE_PATH + "engines/Altair607"  # engine_files[0]

    if PLATFORM == "Windows":
        engine_file = FILE_PATH + "engines/Altair3.0.0_windows_64.exe"
    elif PLATFORM != "Darwin":
        print(PLATFORM + " NOT SUPPORTED")
        return -1

    analysis = False

    name_panel = RectTextObject(LAYER3_COLOR, (774, 168, 192, 20), False, 0, DEFAULT_RECT_RADIUS, "Engine: 0",
                                TEXT_COLOR)
    author_panel = RectTextObject(LAYER3_COLOR, (774, 192, 192, 20), False, 0, DEFAULT_RECT_RADIUS, "Author: 0",
                                  TEXT_COLOR)
    depth_panel = RectTextObject(LAYER3_COLOR, (774, 216, 192, 20), False, 0, DEFAULT_RECT_RADIUS, "Depth: 0",
                                 TEXT_COLOR)
    score_panel = RectTextObject(LAYER3_COLOR, (774, 240, 192, 20), False, 0, DEFAULT_RECT_RADIUS, "Score: 0",
                                 TEXT_COLOR)
    nodes_panel = RectTextObject(LAYER3_COLOR, (774, 264, 192, 20), False, 0, DEFAULT_RECT_RADIUS, "Nodes: 0",
                                 TEXT_COLOR)

    pv_panel = PVPanel(LAYER3_COLOR, LAYER1_COLOR, (774, 288, 192, 196), 0, DEFAULT_RECT_RADIUS, TEXT_COLOR, 26)

    basic_objects.append(name_panel)
    basic_objects.append(author_panel)
    basic_objects.append(depth_panel)
    basic_objects.append(score_panel)
    basic_objects.append(nodes_panel)
    basic_objects.append(pv_panel)

    engine = Engine(main_state, engine_file)
    engine_connection_thread = None

    # Chess
    current_moves = main_state.position.get_legal_moves()

    white_clock = Clock(LAYER1_COLOR, (610, 470, 120, 40), False, 0, DEFAULT_RECT_RADIUS, '00:00', TEXT_COLOR)
    black_clock = Clock(LAYER1_COLOR, (610, 30, 120, 40), False, 0, DEFAULT_RECT_RADIUS, '00:00', TEXT_COLOR)

    promotions_panel = RectObject(LAYER1_COLOR, (610, 300, 120, 160), False, 0, DEFAULT_RECT_RADIUS)
    promotions_title = RectTextObject(LAYER3_COLOR, (612, 302, 116, 38), False, 0, DEFAULT_RECT_RADIUS, "Promotion:",
                                      TEXT_COLOR)

    promotions_buttons = [
        PromotionButton(BUTTON1_COLOR, (612, 342, 56, 56), 0, DEFAULT_RECT_RADIUS, "promotion_piece:1", "n",
                        main_state.piece_images),
        PromotionButton(BUTTON1_COLOR, (671, 342, 56, 56), 0, DEFAULT_RECT_RADIUS, "promotion_piece:2", "b",
                        main_state.piece_images),
        PromotionButton(BUTTON1_COLOR, (612, 401, 56, 56), 0, DEFAULT_RECT_RADIUS, "promotion_piece:3", "r",
                        main_state.piece_images),
        PromotionButton(BUTTON1_COLOR, (671, 401, 56, 56), 0, DEFAULT_RECT_RADIUS, "promotion_piece:4", "q",
                        main_state.piece_images),
    ]

    promotion_piece = 4
    promotions_buttons[promotion_piece - 1].chosen = True

    basic_objects.append(white_clock)
    basic_objects.append(black_clock)
    basic_objects.append(promotions_panel)
    basic_objects.append(promotions_title)

    buttons += promotions_buttons

    main_state.initialize_pieces()

    sprite_group = pygame.sprite.Group()
    sprite_group.add(main_state.pieces)

    selected_piece = None
    released = True

    # Pygame Setup

    notification_object = None

    scale_objects(screen_size, basic_objects, buttons, [board_gui], main_state.pieces)

    clock = pygame.time.Clock()
    last_ticks = 0

    # Main Game Loop

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                engine.stop()

            if event.type == pygame.VIDEORESIZE:
                # screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                screen_size = screen.get_size()
                scale_objects(screen_size, basic_objects, buttons, [board_gui], main_state.pieces)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    selected_sprites = [s for s in main_state.pieces if s.rect.collidepoint(mouse_pos)]

                    if len(selected_sprites) == 1 and selected_sprites[0].side == main_state.position.side:
                        selected_piece = selected_sprites[0]
                        released = False
                    else:
                        if selected_piece is not None:
                            attempt = attempt_selection_move(main_state, current_moves, mouse_pos, selected_piece,
                                                   promotion_piece, sprite_group)

                            if attempt and analysis:
                                engine.stop()
                                engine.start_analysis()

                            if attempt and engine_play and main_state.position.side == engine_side:
                                engine.think(5000)

                            released = True

                        selected_piece = None

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left Button
                    mouse_pos = pygame.mouse.get_pos()

                    if selected_piece is not None and not released:
                        attempt = attempt_selection_move(main_state, current_moves, mouse_pos, selected_piece,
                                               promotion_piece, sprite_group)

                        if attempt and analysis:
                            engine.stop()
                            engine.start_analysis()

                        if attempt and engine_play and main_state.position.side == engine_side:
                            engine.think(5000)

                        released = True

                    selected_object = get_selected_object(mouse_pos, buttons)

                    if selected_object is None:
                        continue

                    action = selected_object.get_action().split(":")

                    if action[0] == "menu":
                        engine.stop()
                        mode = int(action[1])
                        return mode

                    elif action[0] == "promotion_piece":
                        promotions_buttons[promotion_piece - 1].chosen = False

                        promotion_piece = int(action[1])
                        selected_object.chosen = True

                    elif action[0] == "toggle":
                        if action[1] == "analysis":
                            analysis = not analysis

                            if analysis:
                                selected_object.text = "On"
                                engine_connection_thread = threading.Thread(target=engine.connect, args=())
                                engine_connection_thread.start()
                            else:
                                selected_object.text = "Off"

                                engine.stop()
                                if engine_connection_thread is not None:
                                    engine_connection_thread.join()

                            selected_object.update_text()

                    elif action[0] == "engine":
                        if action[1] == "pv":
                            if action[2] == "+":
                                engine.set_multi_pv(engine.options["multi_pv"] + 1)
                            elif action[2] == "-":
                                engine.set_multi_pv(engine.options["multi_pv"] - 1)
                        if action[2] == "cpu":
                            pass

                    elif action[0] == "position":
                        if action[1] == "undo":

                            move_uci = get_uci_from_move(main_state.move_archive[-1])

                            main_state.undo_move()

                            sprite_group = pygame.sprite.Group()
                            sprite_group.add(main_state.pieces)

                            scale_objects(screen_size, basic_objects, buttons, [board_gui], main_state.pieces)
                            current_moves = main_state.position.get_legal_moves()

                            if analysis:
                                engine.stop()
                                engine.start_analysis()

                            notification_object = NotificationMessage(LAYER4_COLOR, (400, 50, 200, 50), False,
                                                                      "Undid move: " + move_uci, TEXT_COLOR)

                        elif action[1] == "flip":
                            main_state.perspective ^= 1
                            main_state.set_perspectives()

        mouse_pos = pygame.mouse.get_pos()

        if analysis:
            if engine_connection_thread is not None and engine.connection_successful:
                engine_connection_thread.join()
                engine_connection_thread = None

                engine.start_analysis()

            if engine.info["depth"] >= 1:
                name_panel.text = "Engine: " + str(engine.info["name"])
                author_panel.text = "Author: " + str(engine.info["author"])
                depth_panel.text = "Depth: " + str(engine.info["depth"])

                score_info = engine.info["scores"][0] * (-1 if main_state.position.side == 1 else 1)
                if engine.info["score_types"][0] == "cp":
                    score_info = str(score_info / 100.0)
                else:
                    score_info = ("M" if score_info >= 0 else "-M") + str(abs(score_info))

                score_panel.text = "Score: " + score_info
                nodes_panel.text = "Nodes: " + str(engine.info["nodes"])

                pv_panel.update_pvs(engine, main_state.position.side)

                name_panel.update_text()
                author_panel.update_text()
                depth_panel.update_text()
                score_panel.update_text()
                nodes_panel.update_text()
                pv_panel.update_text()

                eval_bar.update_evaluation(engine.info["scores"][0] * (-1 if main_state.position.side == 1 else 1),
                                           engine.info["score_types"][0])

        if len(current_moves) == 0:
            print("PLAYER LOST")

            main_state.in_play = False
            running = False
            engine.stop()

        if selected_piece is not None and not released:
            selected_piece.rect.center = mouse_pos

        # print(clock.get_time(), clock.get_fps())
        if pygame.time.get_ticks() >= last_ticks + 1000:
            last_ticks = pygame.time.get_ticks()
            if main_state.in_play:

                main_state.times[main_state.position.side] -= 1000

                if main_state.times[main_state.position.side] <= 0:
                    main_state.times[main_state.position.side] = 0
                    main_state.in_play = False

        white_clock.time = main_state.times[WHITE_COLOR]
        black_clock.time = main_state.times[BLACK_COLOR]

        screen.fill(SCREEN_COLOR)

        selected_object = get_selected_object(mouse_pos, buttons)
        draw_main_objects(screen, screen_size, selected_object, basic_objects, buttons, board_gui)
        sprite_group.draw(screen)
        draw_legal_moves(screen, main_state, selected_piece, current_moves)
        draw_notification_object(screen, notification_object)

        if analysis and len(engine.info["pvs"][0]) >= 1:
            analysis_moves = []
            for multi_pv_index in range(engine.options["multi_pv"]):
                if len(engine.info["pvs"][multi_pv_index].split()) == 0:
                    break

                analysis_moves.append((
                    get_move_from_uci(main_state.position,
                                      engine.info["pvs"][multi_pv_index].split()[0].strip()),
                    engine.info["scores"][multi_pv_index]
                ))

            draw_analysis_moves(screen, main_state, board_gui, analysis_moves)

        clock.tick(60)
        pygame.display.update()

    pygame.display.quit()
    pygame.quit()
    sys.exit()


def game_options_menu(screen, main_state):

    # Important Variables

    screen_size = screen.get_size()

    buttons = [
        RectTextButton(BUTTON1_COLOR, (770, 30, 200, 40), False, 0, DEFAULT_RECT_RADIUS, "menu:0", 'Exit',
                       BUTTON_TEXT_COLOR),
        RectTextButton(BUTTON1_COLOR, (770, 80, 200, 40), False, 0, DEFAULT_RECT_RADIUS, "import:fen", 'Import FEN',
                       BUTTON_TEXT_COLOR),
        RectTextButton(BUTTON1_COLOR, (770, 130, 200, 40), False, 0, DEFAULT_RECT_RADIUS, "import:pgn", 'Import PGN',
                       BUTTON_TEXT_COLOR),
        RectTextButton(BUTTON1_COLOR, (770, 180, 200, 40), False, 0, DEFAULT_RECT_RADIUS, "copy:fen", 'Copy FEN',
                       BUTTON_TEXT_COLOR),
    ]

    basic_objects = [
        RectObject(LAYER2_COLOR, (20, 20, 720, 500), False, 0, DEFAULT_RECT_RADIUS),
        RectObject(LAYER2_COLOR, (760, 20, 220, 500), False, 0, DEFAULT_RECT_RADIUS)
    ]

    scale_objects(screen_size, basic_objects, buttons)

    clock = pygame.time.Clock()

    notification_object = None

    # Menu Game Loop

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                # screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                screen_size = screen.get_size()
                scale_objects(screen_size, basic_objects, buttons)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left Button
                    mouse_pos = pygame.mouse.get_pos()
                    selected_object = get_selected_object(mouse_pos, buttons)

                    if selected_object is None:
                        continue

                    action = selected_object.get_action().split(":")

                    if action[0] == "menu":
                        mode = int(action[1])
                        return mode

                    if action[0] == "import":
                        clipboard = pyperclip.paste()
                        if action[1] == "fen":
                            fen = clipboard.strip()
                            re.sub(r'[^\w]', ' ', fen)
                            success = main_state.position.parse_fen(fen)

                            if len(fen.split()) < 5:
                                fen += " 0"

                            if len(fen.split()) < 6:
                                fen += " 1"

                            if success:
                                main_state.fen = fen
                                main_state.move_archive.clear()

                            text = "Fen Successfully Imported" if success else "Fen Import Failed"
                            notification_object = NotificationMessage(LAYER4_COLOR, (400, 50, 200, 50), False,
                                                                      text, TEXT_COLOR)

                    if action[0] == "copy":
                        fen = main_state.position.get_fen()
                        print(fen)
                        pyperclip.copy(fen)

                        notification_object = NotificationMessage(LAYER4_COLOR, (400, 50, 200, 50), False,
                                                                  "FEN copied to clipboard", TEXT_COLOR)

        mouse_pos = pygame.mouse.get_pos()

        screen.fill(SCREEN_COLOR)

        selected_object = get_selected_object(mouse_pos, buttons)
        draw_menu_objects(screen, screen_size, selected_object, basic_objects, buttons)
        draw_notification_object(screen, notification_object)

        clock.tick(60)
        pygame.display.update()

    pygame.display.quit()
    pygame.quit()
    sys.exit()


def engine_options_menu(screen, main_state):

    # Important Variables

    screen_size = screen.get_size()

    buttons = [
        RectTextButton(BUTTON1_COLOR, (780, 200, 180, 40), False, 0, DEFAULT_RECT_RADIUS, "menu:0", 'Exit',
                       BUTTON_TEXT_COLOR)
    ]

    basic_objects = [
        RectObject(LAYER2_COLOR, (20, 20, 720, 500), False, 0, DEFAULT_RECT_RADIUS),
        RectObject(LAYER2_COLOR, (760, 20, 220, 500), False, 0, DEFAULT_RECT_RADIUS)
    ]

    scale_objects(screen_size, basic_objects, buttons)

    clock = pygame.time.Clock()

    notification_object = None

    # Menu Game Loop

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                # screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                screen_size = screen.get_size()
                scale_objects(screen_size, basic_objects, buttons)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left Button
                    mouse_pos = pygame.mouse.get_pos()
                    selected_object = get_selected_object(mouse_pos, buttons)

                    if selected_object is None:
                        continue

                    action = selected_object.get_action().split(":")

                    if action[0] == "menu":
                        mode = int(action[1])
                        return mode

        mouse_pos = pygame.mouse.get_pos()

        screen.fill(SCREEN_COLOR)

        selected_object = get_selected_object(mouse_pos, buttons)
        draw_menu_objects(screen, screen_size, selected_object, basic_objects, buttons)

        clock.tick(60)
        pygame.display.update()

    pygame.display.quit()
    pygame.quit()
    sys.exit()


def attempt_selection_move(main_state, current_moves, mouse_pos, selected_piece, promotion_piece, sprite_group):
    new_col = int((mouse_pos[0] - selected_piece.new_starting_square_location[0])
                  // selected_piece.width)
    new_row = int((mouse_pos[1] - selected_piece.new_starting_square_location[1])
                  // selected_piece.height)

    new_col = abs(new_col - 7 * main_state.perspective)
    new_row = abs(new_row - 7 * main_state.perspective)

    if new_col < 0 or new_col > 7 or new_row < 0 or new_row > 7:
        return

    from_col = selected_piece.col
    from_row = selected_piece.row

    array_move = [from_col, from_row, new_col, new_row, promotion_piece + main_state.position.side * BLACK_PAWN]
    move = get_move_from_array_move(main_state.position, array_move)

    if move in current_moves:

        removed_piece = main_state.get_piece(new_col, new_row)

        if get_move_type(move) == MOVE_TYPE_EP:
            removed_piece = main_state.get_piece(new_col, new_row + (1 if main_state.position.side == 0 else -1))

        if removed_piece is not None:
            main_state.pieces.remove(removed_piece)
            sprite_group.remove(removed_piece)

        main_state.make_move(move)
        selected_piece.move(new_col, new_row)

        if get_move_type(move) == MOVE_TYPE_PROMOTION:
            selected_piece.piece = PIECE_MATCHER[promotion_piece]
            selected_piece.image = pygame.Surface((selected_piece.width, selected_piece.height),
                                                  pygame.SRCALPHA).convert_alpha()
            selected_piece.unedited_sprite = pygame.image.load(
                FILE_PATH + "images/{}.png".format(selected_piece.color + selected_piece.piece)).convert_alpha()

            selected_piece.sprite = pygame.transform.smoothscale(
                selected_piece.unedited_sprite,
                (selected_piece.width, selected_piece.height))

            selected_piece.image.blit(selected_piece.sprite, (0, 0))

        if get_move_type(move) == MOVE_TYPE_CASTLE:
            rook_col = 0 if selected_piece.col == 2 else 7
            rook_row = new_row

            new_rook_col = 3 if rook_col == 0 else 5

            rook = main_state.get_piece(rook_col, rook_row)
            rook.move(new_rook_col, rook_row)

        current_moves.clear()
        for new_move in main_state.position.get_legal_moves():
            current_moves.append(new_move)

        return True
    else:
        selected_piece.rect.topleft = [selected_piece.x, selected_piece.y]
        return False


def get_selected_object(mouse_pos, buttons):
    for button in buttons:
        if button.is_selecting(mouse_pos):
            return button
    return None


def draw_main_objects(screen, screen_size, selected_object, basic_objects, buttons, board):

    surface1 = pygame.Surface(screen_size, pygame.SRCALPHA)
    draw_basic_objects(surface1, basic_objects)
    board.draw(surface1)

    surface2 = pygame.Surface(screen_size, pygame.SRCALPHA)
    draw_buttons(surface2, selected_object, buttons)

    surface1.blit(surface2, (0, 0))
    screen.blit(surface1, (0, 0))


def draw_menu_objects(screen, screen_size, selected_object, basic_objects, buttons):

    surface1 = pygame.Surface(screen_size, pygame.SRCALPHA)
    draw_basic_objects(surface1, basic_objects)

    surface2 = pygame.Surface(screen_size, pygame.SRCALPHA)
    draw_buttons(surface2, selected_object, buttons)

    surface1.blit(surface2, (0, 0))
    screen.blit(surface1, (0, 0))


def draw_basic_objects(surface, objects):
    for basic_object in objects:
        basic_object.draw(surface, False)


def draw_buttons(surface, selected_object, buttons):
    for button in buttons:
        if button == selected_object:
            button.draw(surface, True)
        else:
            button.draw(surface, False)


def draw_notification_object(surface, notification_object):
    if notification_object is None:
        return

    if notification_object.life <= 0:
        notification_object = None
        return

    notification_object.draw(surface, False)


def scale_objects(screen_size, *objects):
    for object_list in objects:
        for basic_object in object_list:
            basic_object.scale(screen_size)


def draw_legal_moves(screen, main_state, selected_piece, legal_moves):
    if selected_piece is None:
        return

    for move in legal_moves:
        from_square = get_from_square(move)
        from_row = int(MAILBOX_TO_STANDARD[from_square] // 8)
        from_col = int(MAILBOX_TO_STANDARD[from_square] % 8)

        if selected_piece.row != from_row or selected_piece.col != from_col:
            continue

        to_square = get_to_square(move)
        row = abs(int(MAILBOX_TO_STANDARD[to_square] // 8) - 7 * main_state.perspective)
        col = abs(int(MAILBOX_TO_STANDARD[to_square] % 8)  - 7 * main_state.perspective)

        dot_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        pygame.draw.circle(dot_surface, (30, 30, 30, 80),
            (int(selected_piece.new_starting_square_location[0]) + col * selected_piece.width +
                 selected_piece.width // 2,
             int(selected_piece.new_starting_square_location[1]) + row * selected_piece.height +
                 selected_piece.height // 2),
             selected_piece.width / 5)

        screen.blit(dot_surface, (0, 0))


def draw_arrow(screen, start, end, color, thickness, sq_size):

    y_length = end[1] - start[1]
    x_length = end[0] - start[0]

    length_ratio = math.sqrt(x_length ** 2 + y_length ** 2) / sq_size

    error = 1000000
    line_slope = error if x_length == 0 else y_length / x_length
    perpendicular = error if line_slope == 0 else -(1 / line_slope)

    triangle_ratio = 0.3

    # Ensure nice looking triangle proportional
    side_ratio = triangle_ratio * (2 ** 0.5) / length_ratio

    optimal_size = sq_size * triangle_ratio

    # Calculate the intersection of a line (y = mx) and circle (x^2 + y^2 = optimal_size)
    # where center is assumed at (0, 0) for simplicity of calculations
    triangle_side_x = optimal_size if line_slope == error else math.sqrt(
        abs((optimal_size ** 2) / (perpendicular ** 2 + 1))
    )

    # Get the Y length based on X length
    triangle_side_y = optimal_size if perpendicular == error else triangle_side_x * perpendicular

    # Calculate the point which will be the midpoint of the base of the triangle
    point = (end[0] - int(end[0] - start[0]) * side_ratio,
             end[1] - int(end[1] - start[1]) * side_ratio)

    triangle = (end,

                # Vertices from midpoint of the base of the triangle
                (point[0] + triangle_side_x, point[1] + triangle_side_y),
                (point[0] - triangle_side_x, point[1] - triangle_side_y))

    pygame.draw.line(screen, color, start, point, thickness)  # Draw line
    pygame.draw.polygon(screen, color, triangle, 0)  # Draw triangle


def draw_analysis_moves(screen, main_state, board, analysis_moves):
    new_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)

    best_evaluation = analysis_moves[0][1]

    for move, evaluation in analysis_moves:
        origin_square = MAILBOX_TO_STANDARD[get_from_square(move)] ^ (63 * main_state.perspective)
        target_square = MAILBOX_TO_STANDARD[get_to_square(move)] ^ (63 * main_state.perspective)

        origin = (board.x + (origin_square % 8) * board.sq_size + board.sq_size // 2,
                  board.y + (origin_square // 8) * board.sq_size + board.sq_size // 2)
        target = (board.x + (target_square % 8) * board.sq_size + board.sq_size // 2,
                  board.y + (target_square // 8) * board.sq_size + board.sq_size // 2)

        eval_diff = abs(best_evaluation - evaluation)

        if eval_diff <= 4 or evaluation >= 800:
            rank = 0
        elif eval_diff <= 15 or evaluation >= 500:
            rank = 1
        elif eval_diff <= 45 or evaluation >= 300:
            rank = 2
        elif eval_diff <= 95 or evaluation >= 175:
            rank = 3
        elif eval_diff <= 180 or evaluation >= 50:
            rank = 4
        else:
            rank = 5

        draw_arrow(new_surface, origin, target, ARROW_COLORS[rank], board.sq_size // 5, board.sq_size)

    screen.blit(new_surface, (0, 0))


if __name__ == "__main__":
    main()
