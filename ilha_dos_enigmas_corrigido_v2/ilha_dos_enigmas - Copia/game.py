"""Lógica principal, exploração e interface de Ilha dos Enigmas."""

import math
import random
import pygame

from settings import (
    COLORS,
    HEIGHT,
    HUNGER_DRAIN,
    PLAYER_RADIUS,
    PLAYER_SPEED,
    SLEEP_DRAIN,
    THIRST_DRAIN,
    WIDTH,
    WORLD_BOUNDS,
)
from puzzles import create_puzzle, draw_shape, draw_text, draw_wrapped


ISLANDS = [
    {
        "name": "Floresta dos Sussurros",
        "description": "Entre árvores antigas, uma voz espera ser compreendida.",
        "ground": (87, 133, 100),
        "path": (183, 157, 111),
        "accent": (133, 197, 132),
        "food": (210, 230),
        "water": (865, 230),
        "rest": (815, 530),
        "altar": (555, 345),
        "dock": (555, 615),
        "seed": 11,
    },
    {
        "name": "Praia das Relíquias",
        "description": "A maré esconde objetos que precisam encontrar seu lugar.",
        "ground": (204, 177, 117),
        "path": (235, 211, 155),
        "accent": (107, 184, 207),
        "food": (190, 240),
        "water": (875, 225),
        "rest": (820, 525),
        "altar": (555, 345),
        "dock": (555, 615),
        "seed": 22,
    },
    {
        "name": "Pântano das Formas",
        "description": "Símbolos antigos se repetem nas pedras cobertas de musgo.",
        "ground": (92, 133, 112),
        "path": (151, 157, 119),
        "accent": (190, 169, 112),
        "food": (205, 225),
        "water": (875, 225),
        "rest": (815, 530),
        "altar": (555, 345),
        "dock": (555, 615),
        "seed": 33,
    },
    {
        "name": "Templo das Marés",
        "description": "No coração das ruínas, quatro runas guardam o último segredo.",
        "ground": (130, 133, 133),
        "path": (179, 164, 132),
        "accent": (198, 172, 105),
        "food": (190, 235),
        "water": (885, 225),
        "rest": (815, 530),
        "altar": (555, 345),
        "dock": (555, 615),
        "seed": 44,
    },
]


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"
        self.island_index = 0
        self.completed = [False, False, False, False]
        self.puzzles = [create_puzzle(i) for i in range(4)]

        self.player = pygame.Vector2(555, 565)
        self.facing = pygame.Vector2(0, -1)
        self.hunger = 100.0
        self.thirst = 100.0
        self.sleep = 100.0

        self.message = ""
        self.message_timer = 0.0
        self.interact_cooldowns = {"food": 0.0, "water": 0.0, "rest": 0.0}
        self.decorations = []
        self.particles = []
        self.fonts = {
            "title": pygame.font.SysFont("arial", 64, bold=True),
            "heading": pygame.font.SysFont("arial", 30, bold=True),
            "body": pygame.font.SysFont("arial", 22),
            "small": pygame.font.SysFont("arial", 16),
            "tiny": pygame.font.SysFont("arial", 13),
        }
        self._make_decorations()

    @property
    def island(self):
        return ISLANDS[self.island_index]

    def _make_decorations(self):
        """Gera decoração determinística para cada ilha."""
        self.decorations = []
        for island in ISLANDS:
            rng = random.Random(island["seed"])
            items = []
            for _ in range(35):
                x = rng.randint(105, 995)
                y = rng.randint(155, 590)
                # Mantém o caminho central e os pontos de interação mais livres.
                if abs(x - 555) < 100 and 270 < y < 640:
                    continue
                if math.dist((x, y), island["food"]) < 70:
                    continue
                if math.dist((x, y), island["water"]) < 75:
                    continue
                if math.dist((x, y), island["rest"]) < 75:
                    continue
                items.append((x, y, rng.randint(12, 25), rng.random()))
            self.decorations.append(items)

    def set_message(self, text, duration=3.5):
        self.message = text
        self.message_timer = duration

    def reset_game(self):
        self.island_index = 0
        self.completed = [False, False, False, False]
        self.puzzles = [create_puzzle(i) for i in range(4)]
        self.player.update(555, 565)
        self.hunger = self.thirst = self.sleep = 100.0
        self.interact_cooldowns = {"food": 0.0, "water": 0.0, "rest": 0.0}
        self.state = "world"
        self.set_message("Explore a ilha e procure o altar no centro.", 5)

    def run(self):
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.05)
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if self.state == "menu":
                self.handle_menu_event(event)
            elif self.state == "world":
                self.handle_world_event(event)
            elif self.state == "puzzle":
                self.handle_puzzle_event(event)
            elif self.state == "recovery":
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.recover()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if pygame.Rect(390, 470, 320, 58).collidepoint(event.pos):
                        self.recover()
            elif self.state == "victory":
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.state = "menu"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if pygame.Rect(390, 500, 320, 58).collidepoint(event.pos):
                        self.state = "menu"

    def handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.reset_game()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(395, 440, 310, 64).collidepoint(event.pos):
                self.reset_game()

    def handle_world_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "menu"
            elif event.key in (pygame.K_e, pygame.K_SPACE):
                self.interact()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Clique no mundo também pode ativar o objeto mais próximo do jogador.
            if pygame.Rect(925, 620, 145, 55).collidepoint(event.pos):
                self.interact()

    def handle_puzzle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "world"
            self.set_message("Enigma pausado. Volte ao altar quando estiver pronto.", 2.8)
            return
        puzzle = self.puzzles[self.island_index]
        was_solved = puzzle.solved
        puzzle.handle_event(event)
        if puzzle.solved and not was_solved:
            self.completed[self.island_index] = True
            if self.island_index == 3:
                self.state = "victory"
            else:
                self.state = "world"
                self.set_message("Enigma resolvido! O caminho até o barco foi liberado.", 5)

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)
        for key in self.interact_cooldowns:
            self.interact_cooldowns[key] = max(0.0, self.interact_cooldowns[key] - dt)

        if self.state not in ("world", "puzzle"):
            return

        self.hunger = max(0.0, self.hunger - HUNGER_DRAIN * dt)
        self.thirst = max(0.0, self.thirst - THIRST_DRAIN * dt)
        self.sleep = max(0.0, self.sleep - SLEEP_DRAIN * dt)

        if min(self.hunger, self.thirst, self.sleep) <= 0:
            self.state = "recovery"
            return

        if self.state == "world":
            keys = pygame.key.get_pressed()
            movement = pygame.Vector2(0, 0)
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                movement.x -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                movement.x += 1
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                movement.y -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                movement.y += 1
            if movement.length_squared() > 0:
                movement = movement.normalize()
                self.facing = movement
                speed = PLAYER_SPEED
                if min(self.hunger, self.thirst, self.sleep) < 20:
                    speed *= 0.78
                self.player += movement * speed * dt
                left, top, right, bottom = WORLD_BOUNDS
                self.player.x = max(left, min(right, self.player.x))
                self.player.y = max(top, min(bottom, self.player.y))

                # Mantém o personagem dentro do contorno elíptico da ilha.
                center = pygame.Vector2(550, 389)
                rx, ry = 480.0, 282.0
                dx = (self.player.x - center.x) / rx
                dy = (self.player.y - center.y) / ry
                ellipse_distance = dx * dx + dy * dy
                if ellipse_distance > 0.96:
                    scale = math.sqrt(0.96 / ellipse_distance)
                    self.player.x = center.x + (self.player.x - center.x) * scale
                    self.player.y = center.y + (self.player.y - center.y) * scale

    def nearest_interactable(self):
        island = self.island
        targets = [
            ("altar", pygame.Vector2(island["altar"]), 64),
            ("food", pygame.Vector2(island["food"]), 58),
            ("water", pygame.Vector2(island["water"]), 58),
            ("rest", pygame.Vector2(island["rest"]), 62),
            ("dock", pygame.Vector2(island["dock"]), 70),
        ]
        candidates = []
        for name, pos, radius in targets:
            if name == "dock" and not self.completed[self.island_index]:
                continue
            distance = self.player.distance_to(pos)
            if distance <= radius:
                candidates.append((distance, name))
        return min(candidates)[1] if candidates else None

    def interact(self):
        target = self.nearest_interactable()
        if target is None:
            self.set_message("Chegue mais perto de um ponto de interesse para interagir.", 2.5)
            return

        if target == "altar":
            if self.completed[self.island_index]:
                self.set_message("Este enigma já foi resolvido. Siga até o barco.", 3)
            else:
                self.state = "puzzle"
            return

        if target == "food":
            if self.interact_cooldowns["food"] > 0:
                self.set_message("As plantas precisam de um tempo para crescer novamente.", 2.5)
            elif self.hunger >= 96:
                self.set_message("Você não precisa comer agora.", 2)
            else:
                self.hunger = min(100, self.hunger + 34)
                self.interact_cooldowns["food"] = 8
                self.set_message("Frutas coletadas: fome recuperada.", 2.8)
        elif target == "water":
            if self.interact_cooldowns["water"] > 0:
                self.set_message("A nascente está se recompondo. Tente novamente em instantes.", 2.5)
            elif self.thirst >= 96:
                self.set_message("Você já está bem hidratado.", 2)
            else:
                self.thirst = min(100, self.thirst + 39)
                self.interact_cooldowns["water"] = 8
                self.set_message("Água fresca: sede recuperada.", 2.8)
        elif target == "rest":
            if self.interact_cooldowns["rest"] > 0:
                self.set_message("Descanse um pouco antes de usar este abrigo novamente.", 2.5)
            elif self.sleep >= 96:
                self.set_message("Você está descansado o suficiente.", 2)
            else:
                self.sleep = min(100, self.sleep + 43)
                self.interact_cooldowns["rest"] = 10
                self.set_message("Uma pausa tranquila recuperou seu sono.", 2.8)
        elif target == "dock":
            if self.island_index < 3:
                self.island_index += 1
                self.player.update(555, 565)
                self.interact_cooldowns = {"food": 0, "water": 0, "rest": 0}
                self.set_message(f"Você chegou à {self.island['name']}.", 4)

    def recover(self):
        self.hunger = max(self.hunger, 55)
        self.thirst = max(self.thirst, 55)
        self.sleep = max(self.sleep, 55)
        self.player.update(815, 530)
        self.state = "world"
        self.set_message("Você se recompôs no abrigo. Seu progresso foi mantido.", 4)

    # ------------------------------------------------------------------
    # Desenho do mundo
    # ------------------------------------------------------------------

    def draw(self):
        self.screen.fill(COLORS["ocean"])
        if self.state == "menu":
            self.draw_menu()
        elif self.state in ("world", "puzzle"):
            self.draw_world()
            if self.state == "puzzle":
                self.puzzles[self.island_index].draw(self.screen, self.fonts, self.island["accent"])
        elif self.state == "recovery":
            self.draw_world()
            self.draw_recovery()
        elif self.state == "victory":
            self.draw_victory()

    def draw_ocean(self):
        for y in range(110, HEIGHT, 68):
            for x in range(18 + (y % 2) * 35, WIDTH, 115):
                pygame.draw.arc(self.screen, COLORS["ocean_light"], (x, y, 50, 18), 0.2, 2.8, 2)

    def draw_world(self):
        self.draw_ocean()
        island = self.island
        land = pygame.Rect(55, 94, 990, 590)
        pygame.draw.ellipse(self.screen, (12, 27, 34), land.inflate(15, 14))
        pygame.draw.ellipse(self.screen, island["ground"], land)
        pygame.draw.ellipse(self.screen, tuple(max(0, c - 18) for c in island["ground"]), land, 5)

        # Caminho principal entre o cais e o altar.
        pygame.draw.line(self.screen, island["path"], (555, 615), (555, 345), 42)
        pygame.draw.line(self.screen, tuple(min(255, c + 18) for c in island["path"]), (555, 615), (555, 345), 3)
        pygame.draw.ellipse(self.screen, island["path"], (470, 290, 170, 105))

        self.draw_decorations(island)
        self.draw_resource_spots(island)
        self.draw_altar(island)
        self.draw_dock(island)
        self.draw_player()
        self.draw_hud()
        self.draw_interaction_hint()
        self.draw_message()

    def draw_decorations(self, island):
        for x, y, size, variant in self.decorations[self.island_index]:
            if self.island_index == 1:
                rock = (x - size, y - size // 2, size * 2, size)
                pygame.draw.ellipse(self.screen, (168, 157, 125), rock)
                pygame.draw.ellipse(self.screen, (205, 190, 151), (x - size // 2, y - size // 2, size, size // 2))
            elif self.island_index == 3:
                pygame.draw.rect(self.screen, (101, 108, 102), (x - 7, y - 14, 14, 28), border_radius=3)
                pygame.draw.circle(self.screen, (153, 158, 143), (x, y - 16), size)
            else:
                trunk_color = (92, 76, 53)
                leaf_color = (48, 91, 65) if variant < 0.5 else (58, 110, 72)
                pygame.draw.rect(self.screen, trunk_color, (x - 4, y, 8, 17), border_radius=3)
                pygame.draw.circle(self.screen, leaf_color, (x, y - 8), size)
                pygame.draw.circle(self.screen, tuple(min(255, c + 18) for c in leaf_color), (x - 5, y - 13), max(5, size // 2))

    def draw_resource_spots(self, island):
        self.draw_spot(island["food"], (209, 123, 105), "F", "Frutas", self.interact_cooldowns["food"])
        self.draw_spot(island["water"], (93, 171, 206), "A", "Água", self.interact_cooldowns["water"])
        self.draw_spot(island["rest"], (226, 189, 112), "Z", "Abrigo", self.interact_cooldowns["rest"])

    def draw_spot(self, pos, color, letter, label, cooldown):
        center = tuple(pos)
        pygame.draw.circle(self.screen, (31, 53, 51), center, 28)
        pygame.draw.circle(self.screen, color if cooldown <= 0 else (108, 119, 111), center, 22)
        pygame.draw.circle(self.screen, (245, 238, 214), center, 22, 2)
        font = pygame.font.SysFont("arial", 18, bold=True)
        draw_text(self.screen, font, letter, COLORS["ink"], center)
        small = self.fonts["tiny"]
        draw_text(self.screen, small, label, COLORS["cream"], (center[0], center[1] + 39))

    def draw_altar(self, island):
        x, y = island["altar"]
        accent = island["accent"]
        pygame.draw.circle(self.screen, (63, 69, 62), (x, y + 8), 54)
        pygame.draw.circle(self.screen, (139, 133, 106), (x, y), 48)
        pygame.draw.circle(self.screen, accent, (x, y), 37, 4)
        pygame.draw.circle(self.screen, (39, 54, 54), (x, y), 27)
        draw_shape(self.screen, ["círculo", "triângulo", "quadrado", "estrela"][self.island_index], (x, y), 19, accent)
        label = "Enigma resolvido" if self.completed[self.island_index] else "Enigma"
        draw_text(self.screen, self.fonts["small"], label, COLORS["cream"], (x, y + 68))
        if self.completed[self.island_index]:
            pygame.draw.circle(self.screen, COLORS["green"], (x + 40, y - 40), 10)

    def draw_dock(self, island):
        x, y = island["dock"]
        pygame.draw.ellipse(self.screen, (42, 54, 54), (x - 57, y - 20, 114, 43))
        pygame.draw.polygon(self.screen, (123, 83, 56), [(x - 44, y - 14), (x + 44, y - 14), (x + 29, y + 12), (x - 29, y + 12)])
        pygame.draw.line(self.screen, (230, 215, 177), (x, y - 10), (x, y - 48), 3)
        pygame.draw.polygon(self.screen, (228, 219, 185), [(x + 2, y - 45), (x + 2, y - 14), (x + 28, y - 14)])
        label = "Viajar" if self.completed[self.island_index] and self.island_index < 3 else "Barco"
        if self.island_index == 3:
            label = "Jornada final"
        draw_text(self.screen, self.fonts["tiny"], label, COLORS["cream"], (x, y + 29))

    def draw_player(self):
        x, y = int(self.player.x), int(self.player.y)
        pygame.draw.ellipse(self.screen, (22, 32, 34), (x - 13, y + 10, 26, 10))
        pygame.draw.circle(self.screen, (43, 56, 60), (x, y), PLAYER_RADIUS + 3)
        pygame.draw.circle(self.screen, (226, 183, 127), (x, y), PLAYER_RADIUS)
        pygame.draw.circle(self.screen, (245, 224, 186), (x - 4, y - 5), 5)
        pygame.draw.line(self.screen, (75, 67, 54), (x, y + 4), (x + int(self.facing.x * 7), y + int(self.facing.y * 7)), 3)

    def draw_hud(self):
        pygame.draw.rect(self.screen, (19, 34, 42), (0, 0, WIDTH, 100))
        pygame.draw.line(self.screen, (77, 103, 104), (0, 98), (WIDTH, 98), 2)
        island_font = pygame.font.SysFont("arial", 21, bold=True)
        small = self.fonts["tiny"]
        draw_text(self.screen, island_font, f"ILHA {self.island_index + 1}/4", COLORS["gold"], (106, 31))
        draw_text(self.screen, self.fonts["small"], self.island["name"], COLORS["cream"], (165, 68), 300)

        for index, done in enumerate(self.completed):
            center = (350 + index * 39, 46)
            pygame.draw.circle(self.screen, COLORS["green"] if done else (71, 89, 91), center, 12)
            pygame.draw.circle(self.screen, COLORS["cream"] if done else (116, 134, 132), center, 12, 2)
            draw_text(self.screen, small, str(index + 1), COLORS["ink"] if done else COLORS["cream"], center)

        self.draw_meter(555, "FOME", self.hunger, (215, 155, 92))
        self.draw_meter(735, "SEDE", self.thirst, (92, 169, 207))
        self.draw_meter(915, "SONO", self.sleep, (166, 151, 204))

    def draw_meter(self, x, label, value, color):
        font = self.fonts["tiny"]
        draw_text(self.screen, font, label, COLORS["muted"], (x, 24))
        bar = pygame.Rect(x - 51, 39, 102, 13)
        pygame.draw.rect(self.screen, (57, 72, 77), bar, border_radius=7)
        fill = bar.copy()
        fill.width = int(bar.width * max(0, min(100, value)) / 100)
        if fill.width > 0:
            bar_color = COLORS["red"] if value < 25 else color
            pygame.draw.rect(self.screen, bar_color, fill, border_radius=7)
        draw_text(self.screen, font, f"{int(value)}%", COLORS["cream"], (x, 68))

    def draw_interaction_hint(self):
        target = self.nearest_interactable() if self.state == "world" else None
        if target:
            hints = {
                "altar": "E  •  Examinar enigma",
                "food": "E  •  Coletar frutas",
                "water": "E  •  Beber água",
                "rest": "E  •  Descansar",
                "dock": "E  •  Viajar para a próxima ilha",
            }
            label = hints[target]
        else:
            label = "WASD / Setas: mover   •   E: interagir   •   Esc: menu"
        pygame.draw.rect(self.screen, (19, 34, 42), (300, 674, 500, 34), border_radius=10)
        draw_text(self.screen, self.fonts["tiny"], label, COLORS["cream"], (550, 691), 475)
        pygame.draw.rect(self.screen, (19, 34, 42), (925, 620, 145, 55), border_radius=10)
        pygame.draw.rect(self.screen, (97, 123, 122), (925, 620, 145, 55), width=1, border_radius=10)
        draw_text(self.screen, self.fonts["small"], "INTERAGIR  [E]", COLORS["gold"], (997, 647))

    def draw_message(self):
        if self.message_timer <= 0 or not self.message:
            return
        rect = pygame.Rect(250, 112, 600, 43)
        pygame.draw.rect(self.screen, (24, 42, 47), rect, border_radius=12)
        pygame.draw.rect(self.screen, (116, 146, 130), rect, width=1, border_radius=12)
        draw_text(self.screen, self.fonts["small"], self.message, COLORS["cream"], rect.center, 570)

    # ------------------------------------------------------------------
    # Telas especiais
    # ------------------------------------------------------------------

    def draw_menu(self):
        self.draw_ocean()
        for index, (x, y, color) in enumerate([
            (220, 250, (83, 132, 99)),
            (850, 220, (192, 167, 109)),
            (275, 550, (87, 128, 111)),
            (825, 535, (127, 133, 125)),
        ]):
            pygame.draw.ellipse(self.screen, (12, 27, 34), (x - 120, y - 70, 240, 140))
            pygame.draw.ellipse(self.screen, color, (x - 116, y - 74, 232, 140))
            for j in range(5):
                cx = x - 75 + j * 37
                cy = y - 8 + (j % 2) * 13
                pygame.draw.circle(self.screen, tuple(min(255, c + 20) for c in color), (cx, cy), 14 + (j % 3) * 3)

        title = self.fonts["title"]
        draw_text(self.screen, title, "ILHA DOS ENIGMAS", COLORS["cream"], (550, 190))
        draw_text(self.screen, self.fonts["body"], "Quatro ilhas. Quatro segredos. Uma jornada de lógica e sobrevivência.", COLORS["muted"], (550, 255), 900)
        pygame.draw.rect(self.screen, (31, 54, 61), (395, 440, 310, 64), border_radius=16)
        pygame.draw.rect(self.screen, COLORS["gold"], (395, 440, 310, 64), width=2, border_radius=16)
        draw_text(self.screen, self.fonts["heading"], "COMEÇAR JORNADA", COLORS["cream"], (550, 472))
        draw_text(self.screen, self.fonts["small"], "WASD / Setas para mover  •  E para interagir  •  Mouse nos enigmas", COLORS["cream"], (550, 555))
        draw_text(self.screen, self.fonts["tiny"], "Sobreviva: encontre comida, água e abrigo em cada ilha.", COLORS["muted"], (550, 590))

    def draw_recovery(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 13, 18, 205))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Rect(280, 175, 540, 370)
        pygame.draw.rect(self.screen, COLORS["panel"], panel, border_radius=22)
        pygame.draw.rect(self.screen, COLORS["gold"], panel, width=2, border_radius=22)
        draw_text(self.screen, self.fonts["heading"], "Hora de se recompor", COLORS["cream"], (550, 245))
        draw_wrapped(
            self.screen,
            self.fonts["body"],
            "Suas reservas acabaram. Volte ao abrigo para recuperar as forças. "
            "Os enigmas já resolvidos continuam completos.",
            COLORS["muted"],
            pygame.Rect(355, 290, 390, 100),
            10,
        )
        button = pygame.Rect(390, 470, 320, 58)
        pygame.draw.rect(self.screen, (46, 75, 69), button, border_radius=14)
        pygame.draw.rect(self.screen, COLORS["green"], button, width=2, border_radius=14)
        draw_text(self.screen, self.fonts["body"], "RECUPERAR E CONTINUAR", COLORS["cream"], button.center)

    def draw_victory(self):
        self.draw_ocean()
        panel = pygame.Rect(210, 135, 680, 450)
        pygame.draw.rect(self.screen, COLORS["panel"], panel, border_radius=24)
        pygame.draw.rect(self.screen, COLORS["gold"], panel, width=3, border_radius=24)
        draw_text(self.screen, self.fonts["title"], "JORNADA CONCLUÍDA", COLORS["gold"], (550, 235))
        draw_text(self.screen, self.fonts["heading"], "O segredo das quatro ilhas foi revelado!", COLORS["cream"], (550, 330), 620)
        draw_wrapped(
            self.screen,
            self.fonts["body"],
            "Você combinou observação, lógica e cuidado com seus recursos para atravessar o arquipélago. "
            "A Ilha dos Enigmas agora está em paz.",
            COLORS["muted"],
            pygame.Rect(305, 375, 490, 75),
            8,
        )
        button = pygame.Rect(390, 500, 320, 58)
        pygame.draw.rect(self.screen, (46, 75, 69), button, border_radius=14)
        pygame.draw.rect(self.screen, COLORS["green"], button, width=2, border_radius=14)
        draw_text(self.screen, self.fonts["body"], "VOLTAR AO MENU", COLORS["cream"], button.center)
