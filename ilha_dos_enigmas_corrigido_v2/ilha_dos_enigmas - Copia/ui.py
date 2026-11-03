"""Recursos visuais reutilizáveis: textos, formas, runas, botões e painéis.

Tudo é desenhado com primitivas do Pygame (sem imagens ou fontes externas).
"""

import math

import pygame

from settings import COLORS, FONT_NAME, HEIGHT, WIDTH

_FONTS = {}
_GLOWS = {}
_PANELS = {}
_OVERLAYS = {}


# ---------------------------------------------------------------------------
# Cores, fontes e brilhos
# ---------------------------------------------------------------------------

def shade(color, amount):
    """Clareia (positivo) ou escurece (negativo) uma cor RGB."""
    return tuple(max(0, min(255, int(c + amount))) for c in color[:3])


def mix(a, b, t):
    """Interpolação linear entre duas cores."""
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def now():
    """Tempo em segundos desde o início do Pygame."""
    return pygame.time.get_ticks() / 1000.0


def get_font(size, bold=False):
    key = (size, bold)
    if key not in _FONTS:
        _FONTS[key] = pygame.font.SysFont(FONT_NAME, size, bold=bold)
    return _FONTS[key]


def get_glow(radius, color, max_alpha=150):
    """Círculo luminoso com degradê radial (cacheado)."""
    key = (radius, tuple(color[:3]), max_alpha)
    if key not in _GLOWS:
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -2):
            alpha = int(max_alpha * (1 - r / radius) ** 2)
            pygame.draw.circle(surf, (*color[:3], alpha), (radius, radius), r)
        _GLOWS[key] = surf
    return _GLOWS[key]


def draw_glow(surface, center, radius, color, alpha=1.0, max_alpha=150):
    glow = get_glow(radius, color, max_alpha)
    glow.set_alpha(int(255 * max(0.0, min(1.0, alpha))))
    surface.blit(glow, glow.get_rect(center=(int(center[0]), int(center[1]))))


def dim_overlay(alpha):
    """Camada escura de tela cheia (cacheada por transparência)."""
    alpha = int(max(0, min(255, alpha)))
    if alpha not in _OVERLAYS:
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        surf.fill((5, 13, 18, alpha))
        _OVERLAYS[alpha] = surf
    return _OVERLAYS[alpha]


# ---------------------------------------------------------------------------
# Texto
# ---------------------------------------------------------------------------

def draw_text(surface, font, text, color, pos, max_width=None, align="center"):
    """Desenha uma linha de texto. `pos` é o centro (ou o meio da esquerda/direita).

    Se `max_width` for informado e o texto for maior, ele é reduzido para caber.
    """
    rendered = font.render(str(text), True, color)
    if max_width and rendered.get_width() > max_width:
        scale = max_width / rendered.get_width()
        size = (int(max_width), max(1, int(rendered.get_height() * scale)))
        rendered = pygame.transform.smoothscale(rendered, size)
    if align == "left":
        rect = rendered.get_rect(midleft=pos)
    elif align == "right":
        rect = rendered.get_rect(midright=pos)
    else:
        rect = rendered.get_rect(center=pos)
    surface.blit(rendered, rect)
    return rect


def draw_text_shadow(surface, font, text, color, pos, offset=2, shadow=(8, 18, 24), max_width=None):
    draw_text(surface, font, text, shadow, (pos[0] + offset, pos[1] + offset), max_width)
    return draw_text(surface, font, text, color, pos, max_width)


def wrap_lines(font, text, width):
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(surface, font, text, color, rect, line_gap=7, align="left"):
    """Quebra um parágrafo em linhas dentro de um retângulo. Retorna o y final."""
    y = rect.y
    for line in wrap_lines(font, text, rect.width):
        rendered = font.render(line, True, color)
        if align == "center":
            x = rect.centerx - rendered.get_width() // 2
        else:
            x = rect.x
        surface.blit(rendered, (x, y))
        y += rendered.get_height() + line_gap
    return y


# ---------------------------------------------------------------------------
# Formas e runas
# ---------------------------------------------------------------------------

def draw_shape(surface, shape, center, size, color, outline=None, width=2):
    """Desenha as formas usadas nos enigmas."""
    x, y = center
    outline = outline or COLORS["cream"]
    if shape == "círculo":
        pygame.draw.circle(surface, color, center, size)
        pygame.draw.circle(surface, shade(color, 60), (x - size // 3, y - size // 3), max(2, size // 4))
        pygame.draw.circle(surface, outline, center, size, width)
        return
    if shape == "triângulo":
        points = [(x, y - size), (x - size, y + size * 0.85), (x + size, y + size * 0.85)]
    elif shape == "quadrado":
        rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
        pygame.draw.rect(surface, color, rect, border_radius=4)
        pygame.draw.rect(surface, shade(color, 45), (rect.x + 4, rect.y + 4, size, max(3, size // 4)), border_radius=2)
        pygame.draw.rect(surface, outline, rect, width=width, border_radius=4)
        return
    elif shape == "estrela":
        points = []
        for index in range(10):
            radius = size * 1.12 if index % 2 == 0 else size * 0.46
            angle = -math.pi / 2 + index * math.pi / 5
            points.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
    elif shape == "losango":
        points = [(x, y - size), (x + size, y), (x, y + size), (x - size, y)]
    else:
        return
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, outline, points, width)


def draw_rune(surface, rune, center, color, scale=1.0):
    """Desenha runas com primitivas, com transparência real nos recortes."""
    size = int(84 * scale)
    tmp = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    s = scale
    clear = (0, 0, 0, 0)
    if rune == "sol":
        pygame.draw.circle(tmp, color, (c, c), int(14 * s))
        pygame.draw.circle(tmp, clear, (c, c), int(8 * s))
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            start = (c + math.cos(rad) * 21 * s, c + math.sin(rad) * 21 * s)
            end = (c + math.cos(rad) * 31 * s, c + math.sin(rad) * 31 * s)
            pygame.draw.line(tmp, color, start, end, max(2, int(4 * s)))
    elif rune == "lua":
        pygame.draw.circle(tmp, color, (c - int(3 * s), c), int(26 * s))
        pygame.draw.circle(tmp, clear, (c + int(10 * s), c - int(7 * s)), int(22 * s))
    elif rune == "onda":
        for offset in (-12, 0, 12):
            pts = []
            for i in range(9):
                px = c - 26 * s + i * 6.5 * s
                py = c + offset * s + math.sin(i * 0.95) * 6 * s
                pts.append((px, py))
            pygame.draw.lines(tmp, color, False, pts, max(2, int(4 * s)))
    elif rune == "folha":
        pts = [(c - 24 * s, c + 14 * s), (c - 14 * s, c - 18 * s), (c + 4 * s, c - 28 * s),
               (c + 24 * s, c - 22 * s), (c + 18 * s, c + 8 * s), (c - 2 * s, c + 26 * s)]
        pygame.draw.polygon(tmp, color, pts)
        pygame.draw.line(tmp, clear, (c - 19 * s, c + 18 * s), (c + 16 * s, c - 17 * s), max(2, int(3 * s)))
        pygame.draw.line(tmp, color, (c - 26 * s, c + 22 * s), (c - 19 * s, c + 18 * s), max(2, int(3 * s)))
    surface.blit(tmp, tmp.get_rect(center=(int(center[0]), int(center[1]))))


def draw_check(surface, center, size, color, progress=1.0, width=7):
    """Marca de verificação animada (progress de 0 a 1)."""
    x, y = center
    a = (x - size * 0.45, y + size * 0.02)
    b = (x - size * 0.12, y + size * 0.36)
    c = (x + size * 0.5, y - size * 0.34)
    progress = max(0.0, min(1.0, progress))
    if progress <= 0.4:
        t = progress / 0.4
        pygame.draw.line(surface, color, a, (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), width)
    else:
        t = (progress - 0.4) / 0.6
        pygame.draw.line(surface, color, a, b, width)
        pygame.draw.line(surface, color, b, (b[0] + (c[0] - b[0]) * t, b[1] + (c[1] - b[1]) * t), width)
        pygame.draw.circle(surface, color, (int(b[0]), int(b[1])), width // 2)
    pygame.draw.circle(surface, color, (int(a[0]), int(a[1])), width // 2)


def draw_icon(surface, kind, center, color, bg=(19, 34, 42), size=1.0):
    """Ícones simples de fome, sede, sono, dica e chave."""
    x, y = int(center[0]), int(center[1])
    r = int(9 * size)
    if kind == "food":
        pygame.draw.circle(surface, color, (x - r // 3, y + 1), r - 1)
        pygame.draw.circle(surface, color, (x + r // 3, y + 1), r - 1)
        pygame.draw.line(surface, (92, 70, 48), (x, y - r + 1), (x + 2, y - r - 3), 2)
        pygame.draw.ellipse(surface, (103, 174, 119), (x + 2, y - r - 5, 8, 5))
    elif kind == "water":
        pygame.draw.polygon(surface, color, [(x, y - r - 3), (x - r + 1, y + 2), (x + r - 1, y + 2)])
        pygame.draw.circle(surface, color, (x, y + 3), r - 1)
        pygame.draw.circle(surface, shade(color, 70), (x - 3, y + 2), 2)
    elif kind == "sleep":
        pygame.draw.circle(surface, color, (x, y), r)
        pygame.draw.circle(surface, bg, (x + r // 2 + 1, y - r // 3), r - 1)
    elif kind == "hint":
        pygame.draw.circle(surface, color, (x, y - 2), r - 2)
        pygame.draw.rect(surface, color, (x - 3, y + r - 5, 6, 5), border_radius=2)
        pygame.draw.circle(surface, shade(color, 80), (x - 3, y - 5), 2)


# ---------------------------------------------------------------------------
# Botões e painéis
# ---------------------------------------------------------------------------

def draw_button(surface, rect, label, font, *, fill=None, border=None, text_color=None,
                hover=False, pressed=False):
    fill = fill or COLORS["panel_light"]
    border = border or (105, 133, 133)
    text_color = text_color or COLORS["cream"]
    if hover:
        fill = shade(fill, 14)
        border = shade(border, 45)
    draw_rect = rect.move(0, 2) if pressed else rect
    shadow = rect.move(0, 4)
    pygame.draw.rect(surface, COLORS["shadow"], shadow, border_radius=14)
    pygame.draw.rect(surface, fill, draw_rect, border_radius=14)
    pygame.draw.rect(surface, shade(fill, 22), (draw_rect.x + 4, draw_rect.y + 3, draw_rect.width - 8, 3), border_radius=2)
    pygame.draw.rect(surface, border, draw_rect, width=2, border_radius=14)
    draw_text(surface, font, label, text_color, draw_rect.center, draw_rect.width - 16)


def panel_surface(size, accent):
    """Painel com degradê, borda dupla e ornamentos nos cantos (cacheado)."""
    key = (size, tuple(accent))
    if key in _PANELS:
        return _PANELS[key]
    w, h = size
    panel = pygame.Surface(size, pygame.SRCALPHA)
    top, bottom = (33, 52, 62), (20, 31, 39)
    for y in range(h):
        pygame.draw.line(panel, mix(top, bottom, y / h), (0, y), (w, y))
    # Faixa do cabeçalho.
    header = pygame.Surface((w, 90), pygame.SRCALPHA)
    header.fill((255, 255, 255, 12))
    panel.blit(header, (0, 0))
    pygame.draw.line(panel, shade(accent, -40), (40, 88), (w - 40, 88), 2)
    pygame.draw.line(panel, COLORS["gold_dark"], (w // 2 - 70, 88), (w // 2 + 70, 88), 2)
    pygame.draw.polygon(panel, COLORS["gold"], [(w // 2, 82), (w // 2 + 7, 88), (w // 2, 94), (w // 2 - 7, 88)])
    # Recorte arredondado.
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=22)
    panel.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(panel, accent, (0, 0, w, h), width=3, border_radius=22)
    pygame.draw.rect(panel, shade(accent, -70), (7, 7, w - 14, h - 14), width=1, border_radius=17)
    for cx, cy in ((22, 22), (w - 22, 22), (22, h - 22), (w - 22, h - 22)):
        pygame.draw.polygon(panel, accent, [(cx, cy - 6), (cx + 6, cy), (cx, cy + 6), (cx - 6, cy)])
        pygame.draw.polygon(panel, COLORS["panel"], [(cx, cy - 3), (cx + 3, cy), (cx, cy + 3), (cx - 3, cy)])
    _PANELS[key] = panel
    return panel