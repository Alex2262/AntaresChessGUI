
import pygame
from constants import *


class Object:
    def __init__(self, rect, square):
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.square = square

        self.ratios = (0 if self.x == 0 else DEFAULT_SCREEN_SIZE[0] / self.x,
                       0 if self.y == 0 else DEFAULT_SCREEN_SIZE[1] / self.y,
                       DEFAULT_SCREEN_SIZE[0] / self.width, DEFAULT_SCREEN_SIZE[1] / self.height)

    def scale(self, screen_size):
        if self.square:
            self.width = min(screen_size[0] / self.ratios[2], screen_size[1] / self.ratios[3])
            self.height = min(screen_size[0] / self.ratios[2], screen_size[1] / self.ratios[3])
            self.x = screen_size[0] / self.ratios[0] + (screen_size[0] / self.ratios[2] - self.width) / 2
            self.y = screen_size[1] / self.ratios[1] + (screen_size[1] / self.ratios[3] - self.height) / 2
        else:
            self.x = 0 if self.ratios[0] == 0 else screen_size[0] / self.ratios[0]
            self.y = 0 if self.ratios[1] == 0 else screen_size[1] / self.ratios[1]
            self.width = screen_size[0] / self.ratios[2]
            self.height = screen_size[1] / self.ratios[3]


class RectObject(Object):
    def __init__(self, color, rect, square, border, radius):
        super().__init__(rect, square)
        self.color = color

        self.border = border
        self.radius = radius

    def draw(self, surface, selected):
        pygame.draw.rect(surface, self.color,
                         (self.x, self.y, self.width, self.height), self.border, self.radius)


class RectTextObject(RectObject):
    def __init__(self, color, rect, square, border, radius, text='', text_color=(0, 0, 0)):
        super().__init__(color, rect, square, border, radius)

        self.text = text
        self.text_color = text_color

        self.font = pygame.font.Font('Quicksand-Regular_afda0c4733e67d13c4b46e7985d6a9ce.ttf',
                                     int(min(self.width / (len(self.text) / 2), self.height) * 0.7))

        self.text_surf = self.font.render(self.text, True, self.text_color)

    def update_text(self):
        self.text_surf = self.font.render(self.text, True, self.text_color)

    def scale(self, screen_size):
        super().scale(screen_size)

        self.font = pygame.font.Font('Quicksand-Regular_afda0c4733e67d13c4b46e7985d6a9ce.ttf',
                                     int(min(self.width / (len(self.text) / 2), self.height) * 0.7))
        self.text_surf = self.font.render(self.text, True, self.text_color)

    def draw(self, surface, selected):
        super().draw(surface, selected)
        surface.blit(self.text_surf, (self.x + (self.width / 2 - self.text_surf.get_width() / 2),
                                      self.y + (self.height / 2 - self.text_surf.get_height() / 2)))


class PVPanel(RectTextObject):
    def __init__(self, color, color2, rect, border, radius, text_color, line_height):
        super().__init__(color, rect, False, border, radius, " ", text_color)
        self.color2 = color2

        self.line_height = line_height
        self.line_height_ratio = self.line_height / self.height

        self.font = pygame.font.Font('Quicksand-Regular_afda0c4733e67d13c4b46e7985d6a9ce.ttf',
                                     int(self.line_height * 0.5))

        self.text_surfaces = [self.font.render(" ", True, self.text_color)]
        self.multi_pv = 1
        self.pvs = [""]
        self.scores = [0]
        self.score_types = [""]
        self.side = 0

    def update_pvs(self, engine, side):
        self.multi_pv    = engine.options["multi_pv"]
        self.scores      = engine.info["scores"]
        self.score_types = engine.info["score_types"]
        self.pvs         = engine.info["pvs"]
        self.side        = side

        self.text_surfaces = [self.text_surfaces[0]] * self.multi_pv

    def update_text(self):
        for pv_index in range(self.multi_pv):
            score_info = self.scores[pv_index] * (-1 if self.side == 1 else 1)
            if self.score_types[pv_index] == "cp":
                score_info = str(score_info / 100.0)
            else:
                score_info = ("M" if score_info >= 0 else "-M") + str(abs(score_info))

            x_padding  = self.width // 40
            font_width = int(self.line_height * 0.5) * 0.6
            pv_slice   = int(((self.width - 2 * x_padding) / font_width / 4) - 1)
            pv_text    = score_info + " " + " ".join(self.pvs[pv_index].split()[:pv_slice])

            self.text_surfaces[pv_index] = self.font.render(pv_text, True, self.text_color)

    def scale(self, screen_size):
        super().scale(screen_size)
        self.line_height = self.line_height_ratio * self.height

        self.font = pygame.font.Font('Quicksand-Regular_afda0c4733e67d13c4b46e7985d6a9ce.ttf',
                                     int(self.line_height * 0.5))

        self.update_text()

    def draw(self, surface, selected):
        pygame.draw.rect(surface, self.color,
                         (self.x, self.y, self.width, self.height), self.border, self.radius)

        x_padding = self.width // 40
        y_padding = self.height // 40

        for pv_index in range(self.multi_pv):
            pygame.draw.rect(surface, self.color2,
                             (self.x + x_padding, self.y + pv_index * self.line_height + y_padding,
                              self.width - 2 * x_padding, self.line_height - 2 * y_padding),
                             self.border, self.radius)

            surface.blit(self.text_surfaces[pv_index],
                         (self.x + 2 * x_padding, self.y + pv_index * self.line_height + y_padding))


class RectTextButton(RectTextObject):
    def __init__(self, color, rect, square, border, radius, action, text='', text_color=(0, 0, 0)):

        super().__init__(color, rect, square, border, radius, text, text_color)

        self.action = action

    def update_text(self):
        super().update_text()

    def scale(self, screen_size):
        super().scale(screen_size)

    def draw(self, surface, selected):
        if selected:
            pygame.draw.rect(surface, (self.color[0], self.color[1], self.color[2], 255),
                             (self.x, self.y, self.width, self.height), self.border, self.radius)
        else:
            pygame.draw.rect(surface, (self.color[0], self.color[1], self.color[2], 220),
                             (self.x, self.y, self.width, self.height), self.border, self.radius)

        surface.blit(self.text_surf, (self.x + (self.width / 2 - self.text_surf.get_width() / 2),
                                      self.y + (self.height / 2 - self.text_surf.get_height() / 2)))

    def is_selecting(self, mouse_pos):
        if self.x < mouse_pos[0] < self.x + self.width and \
                self.y < mouse_pos[1] < self.y + self.height:
            return True
        return False

    def get_action(self):
        return self.action


# ----------------- The Image Button -----------------
# (extends RectTextButton)
# A general class for Image Button Objects
class ImageButton(RectTextButton):
    # e.g. sell button. Buttons with images
    def __init__(self, color, rect, square, border, radius, action, image_file, text=' ', text_color=(0, 0, 0)):
        super().__init__(color, rect, square, border, radius, action, text, text_color)
        self.image = pygame.image.load(image_file).convert_alpha() if image_file != "" else None

    def scale(self, screen_size):
        super().scale(screen_size)

    def draw(self, surface, selected):
        surface.blit(self.image, (self.x, self.y))

        self.text_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(self.text_surf, (self.x + (self.width / 2 - self.text_surf.get_width() / 2),
                                      self.y + (self.height / 2 - self.text_surf.get_height() / 2)))

        if selected:
            new_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()
            new_surface.set_alpha(40)
            new_surface.fill((0, 0, 0))
            surface.blit(new_surface, (self.x, self.y))

    def is_selecting(self, mouse_pos):
        if self.x < mouse_pos[0] < self.x + self.width and \
                self.y < mouse_pos[1] < self.y + self.height:
            return True
        return False

    def get_action(self):
        return self.action


class NotificationMessage(RectTextObject):
    def __init__(self, color, rect, square, text, text_color):
        self.border = 0
        self.radius = 8
        super().__init__(color, rect, square, self.border, self.radius, text, text_color)

        self.life = 300

    def scale(self, screen_size):
        super().scale(screen_size)

    def draw(self, surface, selected):
        new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA).convert_alpha()
        alpha = 255

        if self.life >= 280:
            alpha = alpha + (280 - self.life) * 5
        if self.life <= 200:
            alpha = alpha - ((200 - self.life) + (0.008 * (200 - self.life) * (200 - self.life)))
            if alpha <= 0:
                self.life = 0

        new_surface.set_alpha(alpha)

        super().draw(new_surface, selected)

        surface.blit(new_surface, (0, 0))

        self.life -= 1


class PromotionButton(ImageButton):
    def __init__(self, color, rect, border, radius, action, piece, piece_images):
        self.piece_color = "w"
        self.piece = piece
        super().__init__(color, rect, True, border, radius, action, "", ' ', (0, 0, 0, 0))

        self.chosen = False
        self.image = piece_images[0][PIECE_MATCHER.index(self.piece.upper())]

    def scale(self, screen_size):
        super().scale(screen_size)

    def draw(self, surface, selected):
        edited_image = pygame.transform.smoothscale(
            self.image,
            (self.width, self.height))

        surface.blit(edited_image, (self.x, self.y))

        alpha = 20
        if selected:
            alpha += 20
        if self.chosen:
            alpha += 40

        new_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()
        new_surface.set_alpha(alpha)

        pygame.draw.rect(new_surface, (0, 0, 0),
                             (0, 0, self.width, self.height), self.border, self.radius)

        surface.blit(new_surface, (self.x, self.y))

    def is_selecting(self, mouse_pos):
        if self.x < mouse_pos[0] < self.x + self.width and \
                self.y < mouse_pos[1] < self.y + self.height:
            return True
        return False

    def get_action(self):
        return self.action


class Clock(RectTextObject):
    def __init__(self, color, rect, square, border, radius, text='', text_color=(0, 0, 0)):
        super().__init__(color, rect, square, border, radius, text, text_color)
        self.time = 0

    def scale(self, screen_size):
        super().scale(screen_size)

    def draw(self, surface, selected):
        if self.time >= 60000 * 60:
            primary = str(self.time // (60000 * 60))            # hours
            secondary = str(self.time % (60000 * 60) // 60000)  # minutes

            if len(primary) == 1:
                primary = "0" + primary
            if len(secondary) == 1:
                secondary = "0" + secondary

        elif self.time >= 60000:
            primary = str(self.time // 60000)           # minutes
            secondary = str(self.time % 60000 // 1000)  # seconds

            if len(primary) == 1:
                primary = "0" + primary
            if len(secondary) == 1:
                secondary = "0" + secondary
        else:
            primary = str(self.time // 1000)           # seconds
            secondary = str(self.time % 1000 // 10)    # ms

            if len(primary) == 1:
                primary = "0" + primary
            if len(secondary) == 1:
                secondary = "0" + secondary

        self.text = primary + ":" + secondary
        self.text_surf = self.font.render(self.text, True, self.text_color)

        super().draw(surface, selected)


class Board(Object):
    def __init__(self, colors, rect):

        super().__init__(rect, True)

        self.board_colors = colors

        self.sq_size = int(self.width / 8)  # Must be integers for drawing smoothly

    def scale(self, screen_size):
        super().scale(screen_size)
        self.sq_size = int(self.width / 8)

    def draw(self, surface):
        for row in range(8):
            for col in range(8):
                pygame.draw.rect(surface, self.board_colors[(row + col) % 2],
                                 (col * self.sq_size + self.x, row * self.sq_size + self.y,
                                  self.sq_size, self.sq_size))


class Piece(pygame.sprite.Sprite, Object):
    def __init__(self, rect, row, col, side, piece, piece_images):
        Object.__init__(self, rect, True)
        pygame.sprite.Sprite.__init__(self)

        self.width = int(self.width)
        self.height = int(self.height)

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]

        self.row = row
        self.col = col
        self.perspective = WHITE_COLOR

        self.side = side
        self.color = "w" if side == 0 else "b"
        self.piece = piece

        self.unedited_sprite = piece_images[side][PIECE_MATCHER.index(self.piece.upper())]

        self.sprite = pygame.transform.smoothscale(
            self.unedited_sprite,
            (self.width, self.height))

        self.image.blit(self.sprite, (0, 0))

        self.starting_square_ratio = (DEFAULT_SCREEN_SIZE[0] / STARTING_SQ[0],
                                      DEFAULT_SCREEN_SIZE[1] / STARTING_SQ[1],
                                      DEFAULT_SCREEN_SIZE[0] / (DEFAULT_SQ_SIZE * 8),
                                      DEFAULT_SCREEN_SIZE[1] / (DEFAULT_SQ_SIZE * 8))

        self.new_starting_square_location = (0, 0)

    def scale(self, screen_size):
        Object.scale(self, screen_size)

        # Replicate the starting square position to find the new location respective to the board
        new_starting_square_size = (min(screen_size[0] / self.starting_square_ratio[2],
                                        screen_size[1] / self.starting_square_ratio[3]),
                                    min(screen_size[0] / self.starting_square_ratio[2],
                                        screen_size[1] / self.starting_square_ratio[3]))

        self.new_starting_square_location = (screen_size[0] / self.starting_square_ratio[0] +
                                            (screen_size[0] / self.starting_square_ratio[2]
                                             - new_starting_square_size[0]) / 2,
                                            screen_size[1] / self.starting_square_ratio[1] +
                                            (screen_size[1] / self.starting_square_ratio[3]
                                             - new_starting_square_size[1]) / 2)

        # Make width and height integers as the board sq size must be integers
        self.width = int(self.width)
        self.height = int(self.height)

        self.x = self.new_starting_square_location[0] + abs(self.col - 7 * self.perspective) * self.width
        self.y = self.new_starting_square_location[1] + abs(self.row - 7 * self.perspective) * self.height

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]

        self.sprite = pygame.transform.smoothscale(
            self.unedited_sprite,
            (self.width, self.height))

        self.image.blit(self.sprite, (0, 0))

    def set_perspective(self, perspective):
        self.perspective = perspective
        self.x = self.new_starting_square_location[0] + abs(self.col - 7 * self.perspective) * self.width
        self.y = self.new_starting_square_location[1] + abs(self.row - 7 * self.perspective) * self.height

        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]

    def move(self, new_col, new_row):
        self.col = new_col
        self.row = new_row

        self.x = self.new_starting_square_location[0] + abs(self.col - 7 * self.perspective) * self.width
        self.y = self.new_starting_square_location[1] + abs(self.row - 7 * self.perspective) * self.height

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]

        self.sprite = pygame.transform.smoothscale(
            self.unedited_sprite,
            (self.width, self.height))

        self.image.blit(self.sprite, (0, 0))


class EvalBar(RectObject):
    def __init__(self, color, rect, border, radius):
        super().__init__(color, rect, False, border, radius)
        self.evaluation = 0
        self.evaluation_type = "cp"
        self.previous_evaluation = 0
        self.max_scale = 600
        self.flipped = False

        # self.elapsed = 60
        # self.scaling_time = 60

    def update_evaluation(self, new_evaluation, evaluation_type):
        # print(self.elapsed, self.previous_evaluation, self.evaluation, new_evaluation)

        self.evaluation = min(max(new_evaluation, -self.max_scale), self.max_scale)
        self.previous_evaluation = self.evaluation

        self.evaluation_type = evaluation_type

    def draw(self, surface, selected):
        black = (45, 45, 45)
        white = (210, 210, 210)

        middle = self.y + self.height // 2

        if self.evaluation_type != "cp":
            if self.evaluation >= 0:
                black = white
            else:
                white = black

        our = black if self.flipped else white
        opp = white if self.flipped else black

        pygame.draw.rect(surface, opp,
                         (self.x, self.y, self.width, self.height // 2), self.border, self.radius)

        pygame.draw.rect(surface, opp,
                         (self.x, middle - self.height // 8, self.width, self.height // 8), 0, 0)

        pygame.draw.rect(surface, our,
                         (self.x, middle, self.width, self.height // 2), self.border, self.radius)

        pygame.draw.rect(surface, our,
                         (self.x, middle, self.width, self.height // 8), 0, 0)

        if self.evaluation_type != "cp":
            return

        # scale_factor = self.elapsed / self.scaling_time
        # scaled_evaluation = abs(self.evaluation * scale_factor +
        #                         self.previous_evaluation * (1 - scale_factor))

        scaled_evaluation = abs(self.evaluation)

        # print(self.evaluation, self.previous_evaluation, scaled_evaluation, scale_factor)

        evaluation_bar_color = white if self.evaluation >= 0 else black
        evaluation_bar_color_width = int(self.width)
        evaluation_bar_color_height = int((self.height * 0.45 / self.max_scale) * scaled_evaluation)

        evaluation_bar_x = self.x
        evaluation_bar_y = middle - evaluation_bar_color_height if self.evaluation >= 0 else middle

        if self.flipped:
            evaluation_bar_y = middle if self.evaluation >= 0 else middle - evaluation_bar_color_height

        # print((evaluation_bar_x, evaluation_bar_y, evaluation_bar_color_width, evaluation_bar_color_height))
        pygame.draw.rect(surface, evaluation_bar_color,
                         (evaluation_bar_x, evaluation_bar_y, evaluation_bar_color_width, evaluation_bar_color_height),
                         0, 0)

        # if self.elapsed < self.scaling_time:
        #     self.elapsed += 1


class Item(RectTextButton):
    def __init__(self, color, rect, border, radius, action, text='', text_color=(0, 0, 0)):
        super().__init__(color, rect, border, radius, action, text, text_color)



