"""Minijogos de lógica de Ilha dos Enigmas.

Contrato de cada puzzle (veja Agents.md):
    solved: bool
    draw(surface, fonts, accent)
    handle_event(event) -> bool   # True quando o enigma é resolvido

Os helpers visuais ficam em ui.py; aqui há apenas a lógica e o layout dos enigmas.
"""

import math
import unicodedata

import pygame

from settings import COLORS, HEIGHT, WIDTH
from ui import (
    dim_overlay,
    draw_button,
    draw_check,
    draw_glow,
    draw_icon,
    draw_rune,
    draw_shape,
    draw_text,
    draw_wrapped,
    ease_out,
    get_font,
    mix,
    now,
    panel_surface,
    shade,
)

PANEL = pygame.Rect(105, 92, 890, 536)
HINT_BUTTON = pygame.Rect(842, 572, 128, 36)


class Puzzle:
    """Base comum: moldura, dica, tremor de erro e celebração de vitória."""

    number = 1
    title = ""
    subtitle = ""
    hints = ()

    def __init__(self):
        self.solved = False
        self.solved_at = None
        self.feedback = ""
        self.feedback_kind = "info"  # info | good | bad
        self.fails = 0
        self.hint_level = 0
        self._last_tick = None
        self._opened_at = now()
        self._shakes = {}

    # -- estado compartilhado ------------------------------------------------

    def set_feedback(self, text, kind="info"):
        self.feedback = text
        self.feedback_kind = kind

    def register_fail(self, text):
        """Conta um erro, mostra a mensagem e libera uma dica a cada dois erros."""
        self.fails += 1
        self.set_feedback(text, "bad")
        if self.fails % 2 == 0:
            self.reveal_hint()

    def reveal_hint(self):
        if self.hint_level < len(self.hints):
            self.hint_level += 1

    def mark_solved(self, text):
        self.solved = True
        self.solved_at = now()
        self.set_feedback(text, "good")

    def shake(self, key, duration=0.45):
        self._shakes[key] = now() + duration

    def shake_offset(self, key, amplitude=7):
        end = self._shakes.get(key)
        if not end:
            return 0
        remaining = end - now()
        if remaining <= 0:
            del self._shakes[key]
            return 0
        return int(math.sin(remaining * 55) * amplitude * min(1.0, remaining / 0.45))

    def is_shaking(self, key):
        return self._shakes.get(key, 0) > now()

    def tick(self):
        """Retorna o dt desde o último desenho; reinicia a animação ao reabrir."""
        t = now()
        if self._last_tick is None or t - self._last_tick > 0.3:
            self._opened_at = t
            dt = 0.0
        else:
            dt = min(0.05, t - self._last_tick)
        self._last_tick = t
        return dt

    def handle_common_event(self, event):
        """Dica por F1 ou clique no botão. Retorna True se o evento foi consumido."""
        if self.solved:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.reveal_hint()
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and HINT_BUTTON.collidepoint(event.pos):
            self.reveal_hint()
            return True
        return False

    # -- desenho -------------------------------------------------------------

    def draw_frame(self, surface, fonts, accent):
        opening = ease_out((now() - self._opened_at) / 0.28)
        surface.blit(dim_overlay(190 * opening), (0, 0))
        lift = int((1 - opening) * 22)
        surface.blit(panel_surface(PANEL.size, accent), (PANEL.x, PANEL.y + lift))

        draw_text(surface, fonts["heading"], self.title, COLORS["cream"], (WIDTH // 2, 126 + lift))
        draw_text(surface, fonts["small"], self.subtitle, COLORS["muted"], (WIDTH // 2, 160 + lift), 700)
        draw_text(surface, fonts["tiny"], "Esc  •  voltar ao mundo", COLORS["muted"], (140, 120 + lift), align="left")
        self.draw_pips(surface, accent, lift)

    def draw_pips(self, surface, accent, lift):
        """Quatro pontos no canto superior direito indicando o enigma atual."""
        for i in range(4):
            center = (PANEL.right - 150 + i * 26, 120 + lift)
            active = i + 1 == self.number
            pygame.draw.circle(surface, accent if active else (61, 80, 85), center, 7)
            pygame.draw.circle(surface, COLORS["cream"] if active else (96, 116, 116), center, 7, 2)

    def draw_footer(self, surface, fonts, accent):
        """Feedback, dica e botão de dica na parte de baixo do painel."""
        if self.feedback:
            colors = {"good": COLORS["green"], "bad": (236, 150, 130), "info": COLORS["muted"]}
            draw_text(surface, fonts["small"], self.feedback, colors[self.feedback_kind], (550, 556), 780)
        if self.hint_level:
            text = self.hints[self.hint_level - 1]
            box = pygame.Rect(0, 0, 640, 34)
            box.center = (495, 590)
            pygame.draw.rect(surface, (44, 40, 28), box, border_radius=10)
            pygame.draw.rect(surface, COLORS["gold_dark"], box, width=1, border_radius=10)
            draw_icon(surface, "hint", (box.x + 20, box.centery), COLORS["gold"], bg=(44, 40, 28), size=0.8)
            draw_text(surface, fonts["tiny"], text, COLORS["cream"], (box.x + 38, box.centery), box.width - 52, align="left")
        if not self.solved:
            more = self.hint_level < len(self.hints)
            label = "DICA  [F1]" if more else "SEM MAIS DICAS"
            hover = more and HINT_BUTTON.collidepoint(pygame.mouse.get_pos())
            draw_button(surface, HINT_BUTTON, label, fonts["tiny"], fill=(58, 52, 34) if more else (40, 50, 54),
                        border=COLORS["gold_dark"] if more else (70, 88, 90),
                        text_color=COLORS["gold"] if more else COLORS["muted"], hover=hover)

    def draw_success(self, surface, fonts, accent):
        """Celebração mostrada enquanto o jogo aguarda para fechar o enigma."""
        if not self.solved or self.solved_at is None:
            return
        elapsed = now() - self.solved_at
        veil = pygame.Surface((PANEL.width - 16, PANEL.height - 110), pygame.SRCALPHA)
        veil.fill((8, 20, 24, int(150 * min(1.0, elapsed / 0.3))))
        surface.blit(veil, (PANEL.x + 8, PANEL.y + 98))

        center = (WIDTH // 2, 345)
        grow = ease_out(elapsed / 0.45)
        draw_glow(surface, center, 120, COLORS["green"], grow * (0.75 + 0.25 * math.sin(elapsed * 6)), 170)
        pygame.draw.circle(surface, (30, 66, 52), center, int(58 * grow))
        pygame.draw.circle(surface, COLORS["green"], center, int(58 * grow), 5)
        draw_check(surface, center, 64, COLORS["cream"], (elapsed - 0.2) / 0.5)
        for i in range(12):
            angle = i * math.tau / 12 + elapsed * 1.6
            dist = 78 + ease_out(elapsed / 0.9) * 54 + math.sin(elapsed * 5 + i) * 4
            pos = (center[0] + math.cos(angle) * dist, center[1] + math.sin(angle) * dist * 0.7)
            fade = max(0.0, 1.0 - elapsed / 2.0)
            draw_shape(surface, "estrela", (int(pos[0]), int(pos[1])), 6, mix(COLORS["gold"], COLORS["cream"], fade * 0.5), width=1)
        if elapsed > 0.35:
            draw_text(surface, fonts["heading"], "Enigma resolvido!", COLORS["gold"], (WIDTH // 2, 440))
            draw_text(surface, fonts["small"], self.feedback, COLORS["cream"], (WIDTH // 2, 478), 700)

    # -- interface exigida pelo contrato ------------------------------------

    def handle_event(self, event):  # pragma: no cover - implementado nas subclasses
        raise NotImplementedError

    def draw(self, surface, fonts, accent):  # pragma: no cover
        raise NotImplementedError


def _normalize(text):
    """Minúsculas, sem acentos e sem espaços duplicados."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    plain = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return " ".join(plain.split())


# ---------------------------------------------------------------------------
# Ilha 1 — enigma textual
# ---------------------------------------------------------------------------

class RiddlePuzzle(Puzzle):
    number = 1
    title = "O Sussurro da Floresta"
    subtitle = "Enigma 1 de 4  •  Texto e interpretação"
    hints = (
        "Pense em lugares vazios e grandes: cavernas, vales e montanhas.",
        "A resposta tem três letras e começa com a letra E.",
    )
    ANSWERS = {"eco", "ecos", "o eco", "um eco"}
    RIDDLE = (
        "Não tenho boca, mas posso responder. Não tenho corpo, mas moro entre as pedras. "
        "Quanto mais alto você chama, mais forte eu volto. Quem sou eu?"
    )
    WRONG = (
        "Ainda não. Pense em algo que responde sem falar.",
        "Quase lá… onde você ouve a própria voz voltar?",
    )

    def __init__(self):
        super().__init__()
        self.answer = ""
        self.set_feedback("Digite sua resposta e pressione Enter.")
        self.input_rect = pygame.Rect(285, 398, 400, 58)
        self.send_rect = pygame.Rect(700, 398, 115, 58)

    def submit(self):
        if not self.answer.strip():
            self.set_feedback("Digite algo antes de enviar.", "info")
            return
        if _normalize(self.answer) in self.ANSWERS:
            self.mark_solved("A floresta devolveu sua própria voz.")
        else:
            self.shake("input")
            self.register_fail(self.WRONG[(self.fails) % len(self.WRONG)])

    def handle_event(self, event):
        if self.solved:
            return False
        if self.handle_common_event(event):
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.send_rect.collidepoint(event.pos):
                self.submit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.answer = self.answer[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.submit()
            elif event.unicode and event.unicode.isprintable() and len(self.answer) < 28:
                if event.unicode.isalpha() or event.unicode == " ":
                    self.answer += event.unicode
        return self.solved

    def draw_echo(self, surface, accent):
        """Ondas de eco expandindo ao fundo, recortadas dentro do painel."""
        t = now()
        layer = pygame.Surface(PANEL.size, pygame.SRCALPHA)
        center = (PANEL.width // 2, 215)
        for k in range(4):
            phase = (t * 0.32 + k / 4) % 1.0
            radius = 40 + phase * 330
            alpha = int(60 * (1 - phase))
            pygame.draw.circle(layer, (*accent, alpha), center, int(radius), 3)
        surface.blit(layer, PANEL.topleft)

    def draw(self, surface, fonts, accent):
        self.tick()
        self.draw_frame(surface, fonts, accent)
        self.draw_echo(surface, accent)
        draw_text(surface, fonts["heading"], "A voz que volta", COLORS["gold"], (550, 222))
        draw_wrapped(surface, fonts["body"], self.RIDDLE, COLORS["cream"], pygame.Rect(235, 262, 630, 110), 10, "center")

        offset = self.shake_offset("input")
        box = self.input_rect.move(offset, 0)
        if self.solved:
            border = COLORS["green"]
        elif self.is_shaking("input"):
            border = COLORS["red"]
        else:
            border = accent
        pygame.draw.rect(surface, (12, 22, 28), box, border_radius=13)
        pygame.draw.rect(surface, border, box, width=2, border_radius=13)
        if self.answer:
            rect = draw_text(surface, fonts["body"], self.answer, COLORS["cream"], (box.x + 18, box.centery), box.width - 36, align="left")
            cursor_x = rect.right + 3
        else:
            draw_text(surface, fonts["body"], "Sua resposta...", (110, 130, 130), (box.x + 18, box.centery), align="left")
            cursor_x = box.x + 18
        if not self.solved and int(now() * 2) % 2 == 0:
            pygame.draw.line(surface, COLORS["gold"], (cursor_x, box.centery - 15), (cursor_x, box.centery + 15), 2)

        hover = self.send_rect.collidepoint(pygame.mouse.get_pos())
        draw_button(surface, self.send_rect, "ENVIAR", fonts["small"], fill=(46, 75, 69),
                    border=COLORS["green"], hover=hover)
        draw_text(surface, fonts["tiny"], "Enter para enviar  •  acentos não importam", COLORS["muted"], (550, 478))
        self.draw_footer(surface, fonts, accent)
        self.draw_success(surface, fonts, accent)


# ---------------------------------------------------------------------------
# Ilha 2 — clicar e arrastar
# ---------------------------------------------------------------------------

class DragDropPuzzle(Puzzle):
    """Arraste cada relíquia para o pedestal com o mesmo símbolo."""

    number = 2
    title = "O Altar das Relíquias"
    subtitle = "Enigma 2 de 4  •  Clique e arraste"
    hints = (
        "Cada pedestal mostra o símbolo e o nome da relíquia que ele aceita.",
        "A Maré é o círculo azul, a Raiz é o quadrado dourado e a Brasa é o triângulo vermelho.",
    )

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
        super().__init__()
        self.set_feedback("Arraste cada relíquia até o pedestal correspondente.")
        self.tray_centers = [(350, 470), (550, 470), (750, 470)]
        self.target_centers = [(350, 305), (550, 305), (750, 305)]
        self.placements = [None, None, None]  # item em cada pedestal
        self.positions = [pygame.Vector2(c) for c in self.tray_centers]
        self.dragging = None
        self.drag_offset = pygame.Vector2(0, 0)

    def _goal(self, item_index):
        for slot, placed in enumerate(self.placements):
            if placed == item_index:
                return pygame.Vector2(self.target_centers[slot])
        return pygame.Vector2(self.tray_centers[item_index])

    def _slot_at(self, point):
        for slot, center in enumerate(self.target_centers):
            if pygame.Vector2(center).distance_to(point) <= 72:
                return slot
        return None

    def handle_event(self, event):
        if self.solved:
            return False
        if self.handle_common_event(event):
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse = pygame.Vector2(event.pos)
            for item_index in reversed(range(len(self.ITEMS))):
                if mouse.distance_to(self.positions[item_index]) <= 50:
                    for slot, placed in enumerate(self.placements):
                        if placed == item_index:
                            self.placements[slot] = None
                    self.dragging = item_index
                    self.drag_offset = self.positions[item_index] - mouse
                    break

        elif event.type == pygame.MOUSEMOTION and self.dragging is not None:
            self.positions[self.dragging] = pygame.Vector2(event.pos) + self.drag_offset

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging is not None:
            item_index = self.dragging
            self.dragging = None
            item = self.ITEMS[item_index]
            slot = self._slot_at(self.positions[item_index])
            if slot is None:
                self.set_feedback("Solte a relíquia sobre um dos pedestais.", "info")
            else:
                target = self.TARGETS[slot]
                if item["shape"] == target["shape"] and item["name"] == target["name"]:
                    self.placements[slot] = item_index
                    left = self.placements.count(None)
                    if left == 0:
                        self.mark_solved("As três relíquias despertaram o altar!")
                    else:
                        self.set_feedback(f"{item['name']} encaixada! Faltam {left}.", "good")
                else:
                    self.shake(("slot", slot))
                    self.register_fail("Esse pedestal não reconhece a relíquia. Tente outro.")
        return self.solved

    def advance(self, dt):
        """Anima cada relíquia em direção ao seu destino (bandeja ou pedestal)."""
        for index, pos in enumerate(self.positions):
            if index == self.dragging:
                continue
            goal = self._goal(index)
            pos += (goal - pos) * min(1.0, dt * 14)

    def draw_pedestal(self, surface, fonts, accent, slot, hot):
        x, y = self.target_centers[slot]
        x += self.shake_offset(("slot", slot))
        rect = pygame.Rect(x - 66, y - 62, 132, 124)
        target = self.TARGETS[slot]
        filled = self.placements[slot] is not None
        if filled:
            draw_glow(surface, (x, y), 92, target["color"], 0.55 + 0.2 * math.sin(now() * 3), 140)
        pygame.draw.rect(surface, COLORS["shadow"], rect.move(0, 5), border_radius=16)
        pygame.draw.rect(surface, (40, 58, 64), rect, border_radius=16)
        pygame.draw.rect(surface, (52, 74, 80), (rect.x + 6, rect.y + 5, rect.width - 12, 8), border_radius=4)
        if self.is_shaking(("slot", slot)):
            border = COLORS["red"]
        elif hot:
            border = COLORS["gold"]
        elif filled:
            border = COLORS["green"]
        else:
            border = accent
        pygame.draw.rect(surface, border, rect, width=3 if hot else 2, border_radius=16)
        if not filled:
            # "Fantasma" do símbolo esperado.
            draw_shape(surface, target["shape"], (x, y - 6), 24, shade(target["color"], -105), outline=shade(target["color"], -50))
        draw_text(surface, fonts["small"], target["name"], COLORS["cream"], (x, y + 42))
        if filled:
            pygame.draw.circle(surface, COLORS["green"], (x + 48, y - 46), 13)
            draw_check(surface, (x + 48, y - 46), 16, COLORS["cream"], 1.0, 3)

    def draw_item(self, surface, fonts, index, hover):
        item = self.ITEMS[index]
        center = self.positions[index]
        lifted = index == self.dragging
        grow = 10 if lifted else (5 if hover else 0)
        rect = pygame.Rect(0, 0, 114 + grow, 96 + grow)
        rect.center = (int(center.x), int(center.y - (6 if lifted else 0)))
        if lifted:
            pygame.draw.rect(surface, COLORS["shadow"], rect.move(6, 12), border_radius=14)
        else:
            pygame.draw.rect(surface, COLORS["shadow"], rect.move(0, 4), border_radius=14)
        pygame.draw.rect(surface, (22, 36, 43), rect, border_radius=14)
        border = item["color"] if (lifted or hover) else (111, 132, 130)
        pygame.draw.rect(surface, border, rect, width=2, border_radius=14)
        draw_shape(surface, item["shape"], (rect.centerx, rect.centery - 8), 21, item["color"])
        draw_text(surface, fonts["small"], item["name"], COLORS["cream"], (rect.centerx, rect.bottom - 17))

    def draw(self, surface, fonts, accent):
        self.advance(self.tick())
        self.draw_frame(surface, fonts, accent)
        mouse = pygame.mouse.get_pos()
        hot_slot = self._slot_at(self.positions[self.dragging]) if self.dragging is not None else None

        draw_text(surface, fonts["body"], "Pedestais", COLORS["gold"], (550, 214))
        for slot in range(3):
            self.draw_pedestal(surface, fonts, accent, slot, slot == hot_slot)

        draw_text(surface, fonts["body"], "Relíquias", COLORS["gold"], (550, 400))
        pygame.draw.line(surface, (52, 74, 80), (190, 424), (910, 424), 1) if False else None
        order = [i for i in range(3) if i != self.dragging]
        if self.dragging is not None:
            order.append(self.dragging)
        for index in order:
            hover = self.dragging is None and pygame.Vector2(mouse).distance_to(self.positions[index]) <= 50
            self.draw_item(surface, fonts, index, hover)

        self.draw_footer(surface, fonts, accent)
        self.draw_success(surface, fonts, accent)


# ---------------------------------------------------------------------------
# Ilha 3 — sequência de formas (3 rodadas)
# ---------------------------------------------------------------------------

class ShapeSequencePuzzle(Puzzle):
    number = 3
    title = "O Código das Formas"
    subtitle = "Enigma 3 de 4  •  Formas e padrões"
    hints = (
        "Procure um grupo de formas que se repete do começo ao fim.",
        "Se o grupo não se repete, tente ler a sequência de trás para frente.",
    )

    OPTIONS = ["círculo", "triângulo", "quadrado", "estrela"]
    COLORS_BY_SHAPE = {
        "círculo": (106, 178, 207),
        "triângulo": (223, 128, 95),
        "quadrado": (232, 190, 99),
        "estrela": (166, 144, 203),
    }
    ROUNDS = [
        {"pattern": ["círculo", "triângulo", "quadrado", "círculo", "triângulo"], "answer": "quadrado",
         "wrong": "Observe os três primeiros símbolos: eles voltam a aparecer."},
        {"pattern": ["estrela", "círculo", "círculo", "estrela", "círculo", "círculo", "estrela"], "answer": "círculo",
         "wrong": "Uma estrela sempre é seguida por dois círculos."},
        {"pattern": ["círculo", "triângulo", "quadrado", "estrela", "quadrado", "triângulo"], "answer": "círculo",
         "wrong": "Esta sequência é um espelho: depois do centro, ela volta ao começo."},
    ]
    ADVANCE_DELAY = 1.0

    def __init__(self):
        super().__init__()
        self.round = 0
        self.advance_at = None
        self.revealed = False
        self.chosen = None
        self.set_feedback("Observe o padrão e escolha a próxima forma.")
        self.option_rects = [pygame.Rect(278 + i * 147, 428, 116, 106) for i in range(4)]

    def _advance_if_ready(self):
        if self.advance_at is not None and now() >= self.advance_at:
            self.advance_at = None
            self.revealed = False
            self.chosen = None
            self.round += 1
            self.set_feedback(f"Rodada {self.round + 1} de {len(self.ROUNDS)}: continue o padrão.")

    def choose(self, index):
        if self.advance_at is not None:
            return
        current = self.ROUNDS[self.round]
        shape = self.OPTIONS[index]
        if shape == current["answer"]:
            self.chosen = index
            self.revealed = True
            if self.round == len(self.ROUNDS) - 1:
                self.mark_solved("Padrão completo! O mecanismo se abriu.")
            else:
                self.advance_at = now() + self.ADVANCE_DELAY
                self.set_feedback(f"Correto! Rodada {self.round + 1} de {len(self.ROUNDS)} concluída.", "good")
        else:
            self.shake(("option", index))
            self.register_fail(f"Essa forma não continua a sequência. {current['wrong']}")

    def handle_event(self, event):
        self._advance_if_ready()
        if self.solved:
            return False
        if self.handle_common_event(event):
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    self.choose(index)
                    break
        elif event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_4:
            self.choose(event.key - pygame.K_1)
        return self.solved

    def draw_pattern(self, surface, fonts, accent):
        current = self.ROUNDS[self.round]
        slots = current["pattern"] + ["?"]
        spacing = min(96, 700 // len(slots))
        start_x = 550 - spacing * (len(slots) - 1) / 2
        t = now()
        for index, shape in enumerate(slots):
            center = (int(start_x + index * spacing), 322)
            card = pygame.Rect(0, 0, spacing - 12, 74)
            card.center = center
            pygame.draw.rect(surface, (24, 38, 45), card, border_radius=12)
            pygame.draw.rect(surface, (52, 74, 80), card, width=1, border_radius=12)
            if shape == "?":
                if self.revealed:
                    answer = current["answer"]
                    draw_glow(surface, center, 56, COLORS["green"], 0.8, 150)
                    draw_shape(surface, answer, center, 24, self.COLORS_BY_SHAPE[answer])
                    pygame.draw.rect(surface, COLORS["green"], card, width=2, border_radius=12)
                else:
                    pulse = 0.5 + 0.5 * math.sin(t * 4)
                    pygame.draw.rect(surface, mix((60, 60, 40), accent, pulse * 0.6 + 0.2), card, width=2, border_radius=12)
                    draw_text(surface, fonts["heading"], "?", COLORS["gold"], center)
            else:
                draw_shape(surface, shape, center, 22, self.COLORS_BY_SHAPE[shape])

    def draw(self, surface, fonts, accent):
        self.tick()
        self._advance_if_ready()
        self.draw_frame(surface, fonts, accent)
        draw_text(surface, fonts["body"], "Qual forma completa a sequência?", COLORS["cream"], (550, 220))
        for i in range(len(self.ROUNDS)):
            done = i < self.round or (i == self.round and self.revealed)
            center = (550 + (i - 1) * 24, 250)
            pygame.draw.circle(surface, COLORS["green"] if done else (61, 80, 85), center, 6)
            pygame.draw.circle(surface, COLORS["gold"] if i == self.round and not done else (96, 116, 116), center, 6, 2)
        self.draw_pattern(surface, fonts, accent)

        mouse = pygame.mouse.get_pos()
        for index, base in enumerate(self.option_rects):
            rect = base.move(self.shake_offset(("option", index)), 0)
            shape = self.OPTIONS[index]
            hover = base.collidepoint(mouse) and not self.solved
            if self.revealed and index == self.chosen:
                border = COLORS["green"]
            elif self.is_shaking(("option", index)):
                border = COLORS["red"]
            else:
                border = COLORS["gold"] if hover else accent
            pygame.draw.rect(surface, COLORS["shadow"], rect.move(0, 4), border_radius=14)
            pygame.draw.rect(surface, (34, 52, 60) if hover else (28, 44, 52), rect, border_radius=14)
            pygame.draw.rect(surface, border, rect, width=2, border_radius=14)
            draw_shape(surface, shape, (rect.centerx, rect.centery - 11), 23, self.COLORS_BY_SHAPE[shape])
            draw_text(surface, fonts["small"], shape.capitalize(), COLORS["cream"], (rect.centerx, rect.bottom - 17))
            draw_text(surface, fonts["tiny"], str(index + 1), COLORS["muted"], (rect.x + 12, rect.y + 12))

        self.draw_footer(surface, fonts, accent)
        self.draw_success(surface, fonts, accent)


# ---------------------------------------------------------------------------
# Ilha 4 — sequência lógica de runas
# ---------------------------------------------------------------------------

class RuneSequencePuzzle(Puzzle):
    number = 4
    title = "O Último Chamado"
    subtitle = "Enigma 4 de 4  •  Lógica e sequência"
    hints = (
        "A inscrição tem quatro versos. Cada um descreve uma runa.",
        "Dia = Sol, água = Onda, vida que floresce = Folha, noite = Lua.",
    )
    CLUE = "O dia abre o caminho. A água vem depois. A vida floresce. A noite encerra o chamado."
    FLIGHT_TIME = 0.35

    def __init__(self):
        super().__init__()
        self.runes = ["sol", "lua", "onda", "folha"]
        self.colors = {"sol": (235, 187, 86), "lua": (170, 174, 224), "onda": (91, 169, 198), "folha": (111, 176, 118)}
        self.centers = [(355, 462), (485, 462), (615, 462), (745, 462)]
        self.expected = ["sol", "onda", "folha", "lua"]
        self.socket_centers = [(415 + i * 90, 352) for i in range(4)]
        self.progress = []
        self.progress_times = []
        self.set_feedback("Toque nas runas na ordem indicada pela inscrição.")

    def click_rune(self, index):
        rune = self.runes[index]
        step = len(self.progress)
        if rune == self.expected[step]:
            self.progress.append(rune)
            self.progress_times.append(now())
            if len(self.progress) == len(self.expected):
                self.mark_solved("As runas responderam. A saída da ilha foi revelada!")
            else:
                self.set_feedback(f"Boa escolha. Faltam {len(self.expected) - len(self.progress)}.", "good")
        else:
            self.shake(("rune", index))
            self.shake("sockets", 0.5)
            self.progress.clear()
            self.progress_times.clear()
            self.register_fail("A ordem se desfez. Releia a inscrição e recomece.")

    def handle_event(self, event):
        if self.solved:
            return False
        if self.handle_common_event(event):
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse = pygame.Vector2(event.pos)
            for index, center in enumerate(self.centers):
                if mouse.distance_to(center) <= 50:
                    self.click_rune(index)
                    break
        return self.solved

    def draw_sockets(self, surface, accent):
        t = now()
        offset = self.shake_offset("sockets")
        wrong = self.is_shaking("sockets")
        for i, base in enumerate(self.socket_centers):
            center = (base[0] + offset, base[1])
            filled = i < len(self.progress)
            pygame.draw.circle(surface, (14, 24, 30), center, 38)
            if wrong:
                ring = COLORS["red"]
            elif filled:
                ring = COLORS["green"]
            elif i == len(self.progress) and not self.solved:
                ring = mix(accent, COLORS["gold"], 0.5 + 0.5 * math.sin(t * 4))
            else:
                ring = (70, 92, 94)
            pygame.draw.circle(surface, ring, center, 38, 3)
            draw_text(surface, get_font(13), str(i + 1), (110, 130, 130), (center[0], center[1] + 52))
            if filled:
                age = t - self.progress_times[i]
                p = ease_out(age / self.FLIGHT_TIME)
                start = self.centers[self.runes.index(self.progress[i])]
                pos = (start[0] + (center[0] - start[0]) * p, start[1] + (center[1] - start[1]) * p)
                if p >= 1:
                    draw_glow(surface, center, 54, self.colors[self.progress[i]], 0.6, 130)
                draw_rune(surface, self.progress[i], pos, self.colors[self.progress[i]], 0.62 + 0.0 * p)

    def draw(self, surface, fonts, accent):
        self.tick()
        self.draw_frame(surface, fonts, accent)
        draw_text(surface, fonts["body"], "A inscrição diz:", COLORS["gold"], (550, 214))
        draw_wrapped(surface, fonts["small"], self.CLUE, COLORS["cream"], pygame.Rect(230, 238, 640, 50), 6, "center")
        self.draw_sockets(surface, accent)

        mouse = pygame.mouse.get_pos()
        for index, center in enumerate(self.centers):
            rune = self.runes[index]
            hover = pygame.Vector2(mouse).distance_to(center) <= 50 and not self.solved
            rect = pygame.Rect(0, 0, 100, 104)
            rect.center = (center[0] + self.shake_offset(("rune", index)), center[1] - (4 if hover else 0))
            used = rune in self.progress
            if hover:
                draw_glow(surface, rect.center, 70, self.colors[rune], 0.5, 120)
            pygame.draw.rect(surface, COLORS["shadow"], rect.move(0, 4), border_radius=16)
            pygame.draw.rect(surface, (24, 38, 45) if not used else (20, 30, 34), rect, border_radius=16)
            if self.is_shaking(("rune", index)):
                border = COLORS["red"]
            elif used:
                border = (60, 100, 78)
            else:
                border = self.colors[rune] if hover else accent
            pygame.draw.rect(surface, border, rect, width=2, border_radius=16)
            color = self.colors[rune] if not used else shade(self.colors[rune], -90)
            draw_rune(surface, rune, (rect.centerx, rect.centery - 8), color, 0.86)
            draw_text(surface, fonts["small"], rune.capitalize(), COLORS["cream"] if not used else COLORS["muted"],
                      (rect.centerx, rect.bottom - 15))

        self.draw_footer(surface, fonts, accent)
        self.draw_success(surface, fonts, accent)


def create_puzzle(index):
    """Cria o enigma correspondente à ilha (índice entre 0 e 3)."""
    puzzles = [RiddlePuzzle, DragDropPuzzle, ShapeSequencePuzzle, RuneSequencePuzzle]
    return puzzles[index]()