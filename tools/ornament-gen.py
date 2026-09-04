#!/usr/bin/env python3
"""Генератор казахского орнамента «қошқар мүйіз» плотным силуэтом.

Рог — лента переменной ширины вдоль логарифмической спирали: широкая у
основания, сужается к центру завитка. Лепесток — линза из двух дуг.
Всё симметрично: правая половина строится зеркалом левой.
"""
import math, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'd')
os.makedirs(OUT, exist_ok=True)


def fmt(p):
    return f'{p[0]:.1f} {p[1]:.1f}'


def poly(points):
    return 'M' + ' L'.join(fmt(p) for p in points) + ' Z'


def spiral_band(cx, cy, r0, r1, th0, turns, w0, w1, steps=90, ccw=False):
    """Лента вдоль логарифмической спирали от радиуса r0 к r1.
    th0 — стартовый угол (рад, y вниз), turns — число оборотов."""
    th1 = th0 + (-1 if ccw else 1) * 2 * math.pi * turns
    k = math.log(r1 / r0)
    outer, inner = [], []
    for i in range(steps + 1):
        t = i / steps
        th = th0 + (th1 - th0) * t
        r = r0 * math.exp(k * t)
        # ширина сужается плавно, с лёгким «мясом» у основания
        w = w1 + (w0 - w1) * (1 - t) ** 1.35
        c, s = math.cos(th), math.sin(th)
        outer.append((cx + (r + w / 2) * c, cy + (r + w / 2) * s))
        inner.append((cx + (r - w / 2) * c, cy + (r - w / 2) * s))
    return outer + inner[::-1]


def leaf(p0, p1, width, bend=0.0, sharp=1.0, steps=40):
    """Заострённый с обоих концов лепесток от p0 к p1.
    width — максимальная ширина, bend — изгиб оси (доля длины)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        ax = p0[0] + dx * t + nx * bend * L * math.sin(math.pi * t)
        ay = p0[1] + dy * t + ny * bend * L * math.sin(math.pi * t)
        hw = width / 2 * math.sin(math.pi * t) ** sharp
        left.append((ax + nx * hw, ay + ny * hw))
        right.append((ax - nx * hw, ay - ny * hw))
    return left + right[::-1]


def diamond(cx, cy, w, h):
    return [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]


def svg(viewbox, paths, mirror_x=None, rotate_center=None):
    body = '\n'.join(f'<path d="{poly(p)}"/>' for p in paths)
    if mirror_x is not None:
        inner = f'<g id="h">{body}</g><use href="#h" transform="matrix(-1 0 0 1 {mirror_x} 0)"/>'
    elif rotate_center is not None:
        cx, cy = rotate_center
        inner = (f'<g id="q">{body}</g>'
                 + ''.join(f'<use href="#q" transform="rotate({a} {cx} {cy})"/>' for a in (90, 180, 270)))
    else:
        inner = body
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" fill="currentColor" '
            f'fill-rule="nonzero">{inner}</svg>')


# ── 1. «Корона»: центральный лепесток, два рога-спирали, крылья ─────────
def crown():
    paths = []
    cx, cy = 72, 66                                # тугой завиток рядом с шипом
    bx, by = 96, 92                                # общее основание
    th0 = math.atan2(by - cy, bx - cx)
    r0 = math.hypot(bx - cx, by - cy)
    paths.append(spiral_band(cx, cy, r0=r0, r1=4, th0=th0, turns=1.3, w0=17, w1=2.5, ccw=True))
    # крыло: широкий заострённый лист от основания наружу-вниз
    paths.append(leaf((84, 98), (16, 130), width=26, bend=0.26, sharp=1.2))
    return paths


def crown_center():
    return [leaf((100, 104), (100, 6), width=17, bend=0.0, sharp=1.1),
            diamond(100, 96, 20, 20)]


# ── 2. Розетка 4-кратной симметрии ──────────────────────────────────────
def rosette_quadrant():
    """Корона, уменьшенная и поставленная шипом вверх, основанием к центру."""
    s = 0.44
    full = crown() + [scale_mirror_p(q) for q in crown()] + crown_center()
    out = []
    for p in full:
        # основание короны (100,104) отодвинуто от центра на 30; шип смотрит вверх
        out.append([(100 + (x - 100) * s, 70 - (104 - y) * s) for x, y in p])
    return out


def rosette_center():
    return [diamond(100, 100, 22, 22)]


# ── 3. Фриз 400×80 ───────────────────────────────────────────────────────
def scale(points, s, dx, dy, flip=False):
    return [(x * s + dx, (-(y) if flip else y) * s + dy) for x, y in points]


def frieze():
    paths = []
    s = 0.42
    # корона вверх на x=100 (центр), низ на y≈72
    for p in crown() + [scale_mirror_p(q) for q in crown()]:
        pass
    return paths


def scale_mirror_p(points):
    return [(200 - x, y) for x, y in points]


def frieze_paths():
    s = 0.5
    up = crown() + [scale_mirror_p(q) for q in crown()] + crown_center()
    out = []
    for p in up:                                   # корона вверх, основание y=76
        out.append([(x * s + 50, 76 - (140 - y) * s) for x, y in p])
    for p in up:                                   # корона вниз, основание y=4
        out.append([(x * s + 250, 4 + (140 - y) * s) for x, y in p])
    out.append([(0, 38.5), (400, 38.5), (400, 41.5), (0, 41.5)])
    return out


def write(name, content):
    path = os.path.join(OUT, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(name, len(content) // 1024, 'КБ')


write('crown.svg', svg('0 0 200 140', crown(), mirror_x=200).replace(
    '</svg>', '\n'.join(f'<path d="{poly(p)}"/>' for p in crown_center()) + '</svg>'))
write('rosette.svg', svg('0 0 200 200', rosette_quadrant(), rotate_center=(100, 100)).replace(
    '</svg>', '\n'.join(f'<path d="{poly(p)}"/>' for p in rosette_center()) + '</svg>'))
write('frieze.svg', svg('0 0 400 80', frieze_paths()))
