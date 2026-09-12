# -*- coding: utf-8 -*-
"""Extrai o contorno do Paraná do mapa de cobertura da operadora e gera um path SVG."""
import sys, json, math
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image

SRC = r'C:\Users\Dalla\OneDrive\Desktop\NOSSA SAÚDE\WhatsApp Image 2026-08-17 at 13.56.29.jpeg'

im = Image.open(SRC).convert('RGB')
a = np.asarray(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
# a mancha do estado é laranja saturado
mask = (R > 150) & (R - B > 70) & (R - G > 40)

# maior componente conexo (flood fill iterativo simples via rotulagem por varredura)
from collections import deque
lab = np.zeros(mask.shape, int)
atual, tam = 0, {}
H, W = mask.shape
for y in range(H):
    for x in range(W):
        if mask[y, x] and not lab[y, x]:
            atual += 1
            q = deque([(y, x)]); lab[y, x] = atual; n = 0
            while q:
                cy, cx = q.popleft(); n += 1
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = atual; q.append((ny, nx))
            tam[atual] = n
maior = max(tam, key=tam.get)
m = (lab == maior)
print('componentes:', len(tam), '| maior:', tam[maior], 'px')

# preenche buracos internos (inunda o fundo a partir das bordas)
fundo = np.zeros_like(m)
q = deque()
for x in range(W):
    for y in (0, H - 1):
        if not m[y, x] and not fundo[y, x]:
            fundo[y, x] = True; q.append((y, x))
for y in range(H):
    for x in (0, W - 1):
        if not m[y, x] and not fundo[y, x]:
            fundo[y, x] = True; q.append((y, x))
while q:
    cy, cx = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = cy + dy, cx + dx
        if 0 <= ny < H and 0 <= nx < W and not m[ny, nx] and not fundo[ny, nx]:
            fundo[ny, nx] = True; q.append((ny, nx))
m = ~fundo

ys, xs = np.where(m)
print('bbox px: x %d..%d  y %d..%d' % (xs.min(), xs.max(), ys.min(), ys.max()))

# ---- contorno por moore-neighborhood tracing
viz = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
inicio = None
for y in range(H):
    for x in range(W):
        if m[y, x]:
            inicio = (y, x); break
    if inicio:
        break

contorno = [inicio]
atual = inicio
antes = (inicio[0], inicio[1] - 1)
while True:
    i0 = viz.index((antes[0] - atual[0], antes[1] - atual[1]))
    prox = None
    for k in range(1, 9):
        dy, dx = viz[(i0 + k) % 8]
        ny, nx = atual[0] + dy, atual[1] + dx
        if 0 <= ny < H and 0 <= nx < W and m[ny, nx]:
            prox = (ny, nx)
            antes = (atual[0] + viz[(i0 + k - 1) % 8][0], atual[1] + viz[(i0 + k - 1) % 8][1])
            break
    if prox is None:
        break
    atual = prox
    if atual == inicio and len(contorno) > 3:
        break
    contorno.append(atual)
    if len(contorno) > 60000:
        break
print('pontos do contorno:', len(contorno))

pts = [(x, y) for y, x in contorno]


def rdp(pontos, eps):
    if len(pontos) < 3:
        return pontos
    x0, y0 = pontos[0]; x1, y1 = pontos[-1]
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1e-9
    pior, idx = 0.0, 0
    for i in range(1, len(pontos) - 1):
        px, py = pontos[i]
        d = abs(dy * px - dx * py + x1 * y0 - y1 * x0) / n
        if d > pior:
            pior, idx = d, i
    if pior > eps:
        return rdp(pontos[:idx + 1], eps)[:-1] + rdp(pontos[idx:], eps)
    return [pontos[0], pontos[-1]]


sys.setrecursionlimit(20000)
simples = rdp(pts, 1.6)
print('após simplificar:', len(simples))

# ---- normaliza para um viewBox 1000 x H
x0, x1 = xs.min(), xs.max()
y0, y1 = ys.min(), ys.max()
larg, alt = x1 - x0, y1 - y0
VB_W = 1000.0
esc = VB_W / larg
VB_H = round(alt * esc, 1)


def proj_px(x, y):
    return (round((x - x0) * esc, 1), round((y - y0) * esc, 1))


d = 'M' + ' L'.join('%g %g' % proj_px(x, y) for x, y in simples) + ' Z'

# ---- cidades: coordenadas reais projetadas pela caixa geográfica do Paraná
# (a imagem é um mapa simples do estado; usamos os limites do PR para posicionar)
PR = {'lat_n': -22.516, 'lat_s': -26.717, 'lon_o': -54.619, 'lon_l': -48.023}
CIDADES = {
    'Ponta Grossa':   (-25.095, -50.162),
    'Telêmaco Borba': (-24.324, -50.617),
    'Jaguariaíva':    (-24.251, -49.706),
    'Castro':         (-24.791, -50.012),
    'Irati':          (-25.468, -50.651),
    'Palmeira':       (-25.429, -50.007),
    'Carambeí':       (-24.915, -50.098),
    'Prudentópolis':  (-25.213, -50.978),
    'Piraí do Sul':   (-24.526, -49.945),
}


def proj_geo(lat, lon):
    fx = (lon - PR['lon_o']) / (PR['lon_l'] - PR['lon_o'])
    fy = (PR['lat_n'] - lat) / (PR['lat_n'] - PR['lat_s'])
    return (round(fx * VB_W, 1), round(fy * VB_H, 1))


cidades = {k: proj_geo(*v) for k, v in CIDADES.items()}
saida = {'viewBox': '0 0 %g %g' % (VB_W, VB_H), 'path': d, 'cidades': cidades}
json.dump(saida, open('mapa_pr.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('viewBox', saida['viewBox'], '| path %d chars' % len(d))
for k, v in cidades.items():
    print('  %-16s %s' % (k, v))
