"""Ponto de entrada de Ilha dos Enigmas."""

import sys
import pygame

from settings import FPS, HEIGHT, TITLE, WIDTH
from game import Game


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"{TITLE} • Survival Puzzle")

    try:
        Game(screen).run()
    finally:
        pygame.quit()

    return 0


if __name__ == "__main__":
    sys.exit(main())
