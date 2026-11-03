"""Configurações centrais de Ilha dos Enigmas."""

WIDTH = 1100
HEIGHT = 720
FPS = 60
TITLE = "Ilha dos Enigmas"

# Área navegável aproximada da ilha.
WORLD_BOUNDS = (75, 125, 1025, 650)
PLAYER_SPEED = 255.0
PLAYER_RADIUS = 15
PLAYER_START = (555, 565)

# Geometria da ilha (elipse): retângulo de desenho, centro e raios de caminhada.
ISLAND_RECT = (55, 94, 990, 590)
ISLAND_CENTER = (550, 389)
ISLAND_RADII = (480.0, 282.0)

# Drenagem por segundo. Os valores foram pensados para permitir explorar,
# coletar recursos e resolver os enigmas sem transformar o jogo em uma corrida.
HUNGER_DRAIN = 0.075
THIRST_DRAIN = 0.115
SLEEP_DRAIN = 0.085

# Tempo de recarga (s) dos pontos de recurso.
COOLDOWNS = {"food": 8.0, "water": 8.0, "rest": 10.0}

# Transições e animações.
SOLVE_DELAY = 1.9        # tempo mostrando a celebração ao resolver um enigma
FADE_DURATION = 0.9      # fade ao chegar em uma ilha
BANNER_DURATION = 4.0    # cartão com o nome da ilha

FONT_NAME = "arial"

COLORS = {
    "ocean": (20, 43, 60),
    "ocean_light": (34, 67, 83),
    "panel": (25, 39, 48),
    "panel_light": (38, 57, 66),
    "cream": (246, 239, 218),
    "muted": (184, 195, 184),
    "ink": (26, 39, 42),
    "gold": (235, 188, 93),
    "gold_dark": (176, 134, 60),
    "green": (103, 174, 119),
    "blue": (93, 164, 194),
    "red": (210, 105, 91),
    "shadow": (8, 18, 24),
}