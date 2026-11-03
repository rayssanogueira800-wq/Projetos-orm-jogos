"""Minijogos de lógica de Ilha dos Enigmas.

Cada puzzle implementa draw(surface, fonts, accent) e handle_event(event).
handle_event retorna True quando o enigma é resolvido.
"""

import pygame

from settings import COLORS, WIDTH, HEIGHT


# ---------------------------------------------------------------------------
# Utilitários visuais
# ---------------------------------------------------------------------------

def draw_text(surface, font, text, color, center, max_width=None):
    """Desenha uma linha de texto centralizada, reduzindo a fonte se necessário."""
    rendered = font.render(str(text), True, color)
    if max_width and rendered.get_width() > max_width:
        scale = max_width / rendered.get_width()
        new_size = max(12, int(font.get_height() * scale))
        smaller = pygame.font.Font(None, new_size)
        rendered = smaller.render(str(text), True, color)
    surface.blit(rendered, rendered.get_rect(center=center))


def draw_wrapped(surface, font, text, color, rect, line_gap=7):
    """Quebra um parágrafo em linhas dentro de um retângulo."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= rect.width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    y = rect.y
    for line in lines:
        rendered = font.render(line, True, color)
        surface.blit(rendered, (rect.x, y))
        y += rendered.get_height() + line_gap
    return y


def draw_rune(surface, rune, center, color):
    """Desenha runas com primitivas, sem depender de glifos especiais da fonte."""
    x, y = center
    if rune == "sol":
        pygame.draw.circle(surface, color, center, 15, 3)
        for angle in range(0, 360, 45):
            import math
            radians = math.radians(angle)
            start = (x + math.cos(radians) * 21, y + math.sin(radians) * 21)
            end = (x + math.cos(radians) * 29, y + math.sin(radians) * 29)
            pygame.draw.line(surface, color, start, end, 3)
    elif rune == "lua":
        pygame.draw.circle(surface, color, center, 25)
        pygame.draw.circle(surface, (31, 48, 56), (x + 12, y - 8), 22)
    elif rune == "onda":
        for offset in (-9, 2, 13):
            points = [(x - 23, y + offset), (x - 12, y + offset - 7),
                      (x, y + offset), (x + 12, y + offset + 7), (x + 23, y + offset)]
            pygame.draw.lines(surface, color, False, points, 4)
    elif rune == "folha":
        points = [(x - 23, y + 12), (x - 13, y - 18), (x + 22, y - 22),
                  (x + 16, y + 10), (x - 4, y + 23)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.line(surface, (31, 48, 56), (x - 17, y + 14), (x + 15, y - 13), 3)


def puzzle_panel(surface, title, subtitle, accent):
    """Fundo comum dos enigmas."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 13, 18, 190))
    surface.blit(overlay, (0, 0))

    panel = pygame.Rect(105, 92, 890, 536)
    pygame.draw.rect(surface, COLORS["panel"], panel, border_radius=22)
    pygame.draw.rect(surface, accent, panel, width=3, border_radius=22)
    pygame.draw.line(surface, COLORS["panel_light"], (145, 180), (955, 180), 2)

    title_font = pygame.font.SysFont("arial", 31, bold=True)
    subtitle_font = pygame.font.SysFont("arial", 17)
    draw_text(surface, title_font, title, COLORS["cream"], (WIDTH // 2, 132))
    draw_text(surface, subtitle_font, subtitle, COLORS["muted"], (WIDTH // 2, 160), 790)
    return panel


def draw_button(surface, rect, label, font, *, fill=None, border=None, text_color=None):
    fill = fill or COLORS["panel_light"]
    border = border or (105, 133, 133)
    text_color = text_color or COLORS["cream"]
    pygame.draw.rect(surface, fill, rect, border_radius=13)
    pygame.draw.rect(surface, border, rect, width=2, border_radius=13)
    draw_text(surface, font, label, text_color, rect.center, rect.width - 14)


def draw_shape(surface, shape, center, size, color, outline=None):
    """Desenha formas simples usadas nos enigmas."""
    x, y = center
    outline = outline or COLORS["cream"]
    if shape == "círculo":
        pygame.draw.circle(surface, color, center, size)
        pygame.draw.circle(surface, outline, center, size, 2)
    elif shape == "triângulo":
        points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, outline, points, 2)
    elif shape == "quadrado":
        rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
        pygame.draw.rect(surface, color, rect, border_radius=4)
        pygame.draw.rect(surface, outline, rect, width=2, border_radius=4)
    elif shape == "estrela":
        points = []
        import math
        for index in range(10):
            radius = size if index % 2 == 0 else size * 0.43
            angle = -math.pi / 2 + index * math.pi / 5
            points.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, outline, points, 2)
    elif shape == "losango":
        points = [(x, y - size), (x + size, y), (x, y + size), (x - size, y)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, outline, points, 2)


# ---------------------------------------------------------------------------
# Ilha 1 — enigma textual
# ---------------------------------------------------------------------------

class RiddlePuzzle:
    def __init__(self):
        self.title = "O Sussurro da Floresta"
        self.answer = ""
        self.feedback = "Digite sua resposta e pressione Enter."
        self.solved = False
        self.input_rect = pygame.Rect(335, 390, 430, 58)

    def handle_event(self, event):
        if self.solved or event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_BACKSPACE:
            self.answer = self.answer[:-1]
        elif event.key == pygame.K_RETURN:
            normalized = " ".join(self.answer.lower().strip().split())
            if normalized in {"eco", "o eco"}:
                self.solved = True
                self.feedback = "Correto! A floresta devolveu sua própria voz."
            else:
                self.feedback = "Ainda não. Pense em algo que responde sem falar."
        elif event.unicode and event.unicode.isprintable() and len(self.answer) < 32:
            if event.unicode.isalpha() or event.unicode.isspace():
                self.answer += event.unicode
        return self.solved

    def draw(self, surface, fonts, accent):
        puzzle_panel(surface, self.title, "Enigma 1 de 4 • Texto e interpretação", accent)
        heading, body, small = fonts["heading"], fonts["body"], fonts["small"]
        draw_text(surface, heading, "A voz que volta", COLORS["gold"], (550, 235))
        riddle = (
            "Não tenho boca, mas posso responder. Não tenho corpo, mas moro entre as pedras. "
            "Quanto mais alto você chama, mais forte eu volto. Quem sou eu?"
        )
        draw_wrapped(surface, body, riddle, COLORS["cream"], pygame.Rect(235, 275, 630, 80), 10)

        pygame.draw.rect(surface, (15, 26, 33), self.input_rect, border_radius=12)
        pygame.draw.rect(surface, accent, self.input_rect, width=2, border_radius=12)
        shown = self.answer if self.answer else "Sua resposta..."
        color = COLORS["cream"] if self.answer else (126, 145, 145)
        draw_text(surface, body, shown, color, self.input_rect.center, 390)
        draw_text(surface, small, self.feedback, COLORS["green"] if self.solved else COLORS["muted"], (550, 485), 750)
        draw_text(surface, small, "Esc: voltar ao mundo", COLORS["muted"], (550, 565))


# ---------------------------------------------------------------------------
# Ilha 2 — clicar e arrastar
# ---------------------------------------------------------------------------

class DragDropPuzzle:
    """Arraste cada relíquia para o pedestal com o mesmo símbolo."""

    ITEMS = [
        {"shape": "triângulo", "color": (224, 119, 91), "name": "Brasa"},
        {"shape": "círculo", "color": (105, 176, 207), "name": "Maré"},
        {"shape": "quadrado", "color": (232, 190, 99), "name": "Raiz"},
    ]

    TARGETS = [
        {"shape": "círculo", "color": (105, 176, 207), "name": "Maré"},
        {"shape": "quadrado", "color": (232, 190, 99), "name": "Raiz"},
        {"shape": "triângulo", "color": (224, 119, 91), "name": "Brasa"},
    ]

    def __init__(self):
        self.title = "O Altar das Relíquias"
        self.feedback = "Arraste cada relíquia até o pedestal correspondente."
        self.solved = False
        self.tray_centers = [(350, 475), (550, 475), (750, 475)]
        self.target_centers = [(350, 310), (550, 310), (750, 310)]
        self.placements = [None, None, None]  # item em cada pedestal
        self.dragging = None
        self.drag_pos = None
        self.drag_offset = (0, 0)

    def _item_center(self, item_index):
        for slot, placed_item in enumerate(self.placements):
            if placed_item == item_index:
                return self.target_centers[slot]
        return self.tray_centers[item_index]

    def handle_event(self, event):
        if self.solved:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse = pygame.Vector2(event.pos)
            for item_index in range(len(self.ITEMS)):
                center = self._item_center(item_index)
                if mouse.distance_to(center) <= 47:
                    for slot, placed_item in enumerate(self.placements):
                        if placed_item == item_index:
                            self.placements[slot] = None
                    self.dragging = item_index
                    self.drag_pos = event.pos
                    self.drag_offset = (center[0] - event.pos[0], center[1] - event.pos[1])
                    break

        elif event.type == pygame.MOUSEMOTION and self.dragging is not None:
            self.drag_pos = (event.pos[0] + self.drag_offset[0], event.pos[1] + self.drag_offset[1])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging is not None:
            item_index = self.dragging
            mouse = pygame.Vector2(event.pos)
            landed = False
            for slot, center in enumerate(self.target_centers):
                if mouse.distance_to(center) <= 68:
                    item = self.ITEMS[item_index]
                    target = self.TARGETS[slot]
                    if item["shape"] == target["shape"] and item["name"] == target["name"]:
                        self.placements[slot] = item_index
                        self.feedback = f"{item['name']} encaixada no pedestal correto."
                    else:
                        self.feedback = "Esse pedestal não reconhece a relíquia. Tente outro."
                    landed = True
                    break
            if not landed:
                self.feedback = "Solte a relíquia sobre um dos pedestais."
            self.dragging = None
            self.drag_pos = None
            if all(item is not None for item in self.placements):
                self.solved = True
                self.feedback = "As três relíquias despertaram o altar!"

        return self.solved

    def draw(self, surface, fonts, accent):
        puzzle_panel(surface, self.title, "Enigma 2 de 4 • Clique e arraste", accent)
        body, small = fonts["body"], fonts["small"]
        draw_text(surface, body, "Pedestais", COLORS["gold"], (550, 225))

        for slot, center in enumerate(self.target_centers):
            x, y = center
            rect = pygame.Rect(x - 62, y - 54, 124, 108)
            pygame.draw.rect(surface, (36, 53, 59), rect, border_radius=14)
            pygame.draw.rect(surface, accent, rect, width=2, border_radius=14)
            target = self.TARGETS[slot]
            draw_shape(surface, target["shape"], (x, y - 5), 23, target["color"])
            draw_text(surface, small, target["name"], COLORS["cream"], (x, y + 37))
            placed = self.placements[slot]
            if placed is not None:
                draw_text(surface, small, "OK", COLORS["green"], (x + 45, y - 38))

        draw_text(surface, body, "Relíquias", COLORS["gold"], (550, 395))
        for item_index, item in enumerate(self.ITEMS):
            if self.dragging == item_index and self.drag_pos:
                center = self.drag_pos
            else:
                center = self._item_center(item_index)
            rect = pygame.Rect(center[0] - 57, center[1] - 48, 114, 96)
            pygame.draw.rect(surface, (20, 33, 40), rect, border_radius=13)
            pygame.draw.rect(surface, (111, 132, 130), rect, width=2, border_radius=13)
            draw_shape(surface, item["shape"], (center[0], center[1] - 7), 21, item["color"])
            draw_text(surface, small, item["name"], COLORS["cream"], (center[0], center[1] + 30))

        feedback_color = COLORS["green"] if self.solved else COLORS["muted"]
        draw_text(surface, small, self.feedback, feedback_color, (550, 565), 760)
        draw_text(surface, small, "Esc: voltar ao mundo", COLORS["muted"], (550, 600))


# ---------------------------------------------------------------------------
# Ilha 3 — sequência de formas
# ---------------------------------------------------------------------------

class ShapeSequencePuzzle:
    def __init__(self):
        self.title = "O Código das Formas"
        self.feedback = "Observe o padrão e escolha a próxima forma."
        self.solved = False
        self.option_rects = [pygame.Rect(280 + i * 145, 435, 112, 104) for i in range(4)]
        self.options = ["círculo", "triângulo", "quadrado", "estrela"]
        self.option_colors = [(106, 178, 207), (223, 128, 95), (232, 190, 99), (166, 144, 203)]
        self.pattern = ["círculo", "triângulo", "quadrado", "círculo", "triângulo", "?"]

    def handle_event(self, event):
        if self.solved or event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        for index, rect in enumerate(self.option_rects):
            if rect.collidepoint(event.pos):
                if self.options[index] == "quadrado":
                    self.solved = True
                    self.feedback = "Padrão completo! O mecanismo se abriu."
                else:
                    self.feedback = "Essa forma não continua a sequência. Observe os três primeiros símbolos."
                break
        return self.solved

    def draw(self, surface, fonts, accent):
        puzzle_panel(surface, self.title, "Enigma 3 de 4 • Formas e padrões", accent)
        body, small = fonts["body"], fonts["small"]
        draw_text(surface, body, "Qual forma completa a sequência?", COLORS["cream"], (550, 225))

        start_x = 300
        for index, shape in enumerate(self.pattern):
            center = (start_x + index * 100, 325)
            if shape == "?":
                rect = pygame.Rect(center[0] - 35, center[1] - 35, 70, 70)
                pygame.draw.rect(surface, (35, 54, 62), rect, border_radius=10)
                pygame.draw.rect(surface, accent, rect, width=2, border_radius=10)
                draw_text(surface, fonts["heading"], "?", COLORS["gold"], center)
            else:
                shape_index = self.options.index(shape)
                draw_shape(surface, shape, center, 25, self.option_colors[shape_index])

        for index, rect in enumerate(self.option_rects):
            pygame.draw.rect(surface, (31, 48, 56), rect, border_radius=13)
            pygame.draw.rect(surface, accent, rect, width=2, border_radius=13)
            draw_shape(surface, self.options[index], (rect.centerx, rect.centery - 7), 23, self.option_colors[index])
            draw_text(surface, small, self.options[index].capitalize(), COLORS["cream"], (rect.centerx, rect.bottom - 15))

        feedback_color = COLORS["green"] if self.solved else COLORS["muted"]
        draw_text(surface, small, self.feedback, feedback_color, (550, 575), 780)
        draw_text(surface, small, "Esc: voltar ao mundo", COLORS["muted"], (550, 602))


# ---------------------------------------------------------------------------
# Ilha 4 — sequência lógica de runas
# ---------------------------------------------------------------------------

class RuneSequencePuzzle:
    def __init__(self):
        self.title = "O Último Chamado"
        self.feedback = "Toque nas runas na ordem indicada pela pista."
        self.solved = False
        self.runes = ["sol", "lua", "onda", "folha"]
        self.colors = [(235, 187, 86), (153, 157, 208), (91, 169, 198), (111, 176, 118)]
        self.centers = [(355, 390), (485, 390), (615, 390), (745, 390)]
        self.expected = ["sol", "onda", "lua"]
        self.progress = []

    def handle_event(self, event):
        if self.solved or event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        mouse = pygame.Vector2(event.pos)
        for index, center in enumerate(self.centers):
            if mouse.distance_to(center) <= 45:
                rune = self.runes[index]
                expected_index = len(self.progress)
                if rune == self.expected[expected_index]:
                    self.progress.append(rune)
                    if len(self.progress) == len(self.expected):
                        self.solved = True
                        self.feedback = "As runas responderam. A saída da ilha foi revelada!"
                    else:
                        self.feedback = "Boa escolha. Continue a sequência."
                else:
                    self.progress.clear()
                    self.feedback = "A ordem se desfez. A sequência recomeçou."
                break
        return self.solved

    def draw(self, surface, fonts, accent):
        puzzle_panel(surface, self.title, "Enigma 4 de 4 • Lógica e sequência", accent)
        body, small = fonts["body"], fonts["small"]
        draw_text(surface, body, "A inscrição diz:", COLORS["gold"], (550, 220))
        clue = "O dia abre o caminho. A água vem depois. A noite encerra o chamado."
        draw_wrapped(surface, body, clue, COLORS["cream"], pygame.Rect(250, 255, 600, 42), 8)

        for index, center in enumerate(self.centers):
            rect = pygame.Rect(center[0] - 48, center[1] - 49, 96, 98)
            pygame.draw.rect(surface, (31, 48, 56), rect, border_radius=15)
            pygame.draw.rect(surface, accent, rect, width=2, border_radius=15)
            draw_rune(surface, self.runes[index], (center[0], center[1] - 5), self.colors[index])
            draw_text(surface, small, self.runes[index].capitalize(), COLORS["cream"], (center[0], center[1] + 29))

        progress_text = "Passos: " + "  •  ".join(item.capitalize() for item in self.progress)
        if not self.progress:
            progress_text = "Passos: nenhum"
        draw_text(surface, small, progress_text, COLORS["gold"], (550, 500), 740)
        feedback_color = COLORS["green"] if self.solved else COLORS["muted"]
        draw_text(surface, small, self.feedback, feedback_color, (550, 548), 770)
        draw_text(surface, small, "Esc: voltar ao mundo", COLORS["muted"], (550, 590))


def create_puzzle(index):
    """Cria o enigma correspondente à ilha (índice entre 0 e 3)."""
    puzzles = [RiddlePuzzle, DragDropPuzzle, ShapeSequencePuzzle, RuneSequencePuzzle]
    return puzzles[index]()
