# -*- coding: utf-8 -*-
"""Baixa e monta a imagem de satélite dos Campos Gerais (Esri World Imagery).

Gera site/img/campos-gerais-satelite.jpg e satelite.json com a caixa exata da imagem,
para o overlay de pontos casar com a projeção.
"""
import os, sys, math, json, io, time
sys.stdout.reconfigure(encoding='utf-8')
import requests
from PIL import Image, ImageEnhance

AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(AQUI, 'site', 'img')
os.makedirs(IMG, exist_ok=True)

Z = 10
TILE = 256
URL = ('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
       '/tile/{z}/{y}/{x}')
ATRIB = 'Esri, Maxar, Earthstar Geographics'

# recorte dos Campos Gerais com folga para caber os rótulos
NORTE, SUL = -23.98, -25.78
OESTE, LESTE = -51.42, -49.34


def px(lat, lon, z=Z):
    n = 2.0 ** z * TILE
    x = (lon + 180.0) / 360.0 * n
    s = math.radians(lat)
    y = (1.0 - math.log(math.tan(s) + 1.0 / math.cos(s)) / math.pi) / 2.0 * n
    return x, y


def main():
    x0, y0 = px(NORTE, OESTE)
    x1, y1 = px(SUL, LESTE)
    tx0, ty0 = int(x0 // TILE), int(y0 // TILE)
    tx1, ty1 = int(x1 // TILE), int(y1 // TILE)
    nx, ny = tx1 - tx0 + 1, ty1 - ty0 + 1
    print('zoom %d · %d x %d tiles (%d requisições)' % (Z, nx, ny, nx * ny))

    mosaico = Image.new('RGB', (nx * TILE, ny * TILE))
    s = requests.Session()
    s.headers.update({'User-Agent': 'MazzaBroker-RedeCredenciada/1.0 (mapa estatico regional)'})
    baixados = 0
    for i, tx in enumerate(range(tx0, tx1 + 1)):
        for j, ty in enumerate(range(ty0, ty1 + 1)):
            u = URL.format(z=Z, x=tx, y=ty)
            for tent in range(3):
                try:
                    r = s.get(u, timeout=40)
                    r.raise_for_status()
                    mosaico.paste(Image.open(io.BytesIO(r.content)).convert('RGB'),
                                  (i * TILE, j * TILE))
                    baixados += 1
                    break
                except Exception as e:
                    print('   retry', tx, ty, e)
                    time.sleep(1.5)
    print('tiles baixados:', baixados)

    # recorta exatamente na caixa pedida
    cx0, cy0 = int(round(x0 - tx0 * TILE)), int(round(y0 - ty0 * TILE))
    cx1, cy1 = int(round(x1 - tx0 * TILE)), int(round(y1 - ty0 * TILE))
    corte = mosaico.crop((cx0, cy0, cx1, cy1))
    print('imagem final:', corte.size)

    # leve tratamento para o mapa não brigar com a tipografia
    corte = ImageEnhance.Color(corte).enhance(0.72)
    corte = ImageEnhance.Brightness(corte).enhance(1.02)
    corte = ImageEnhance.Contrast(corte).enhance(1.05)

    destino = os.path.join(IMG, 'campos-gerais-satelite.jpg')
    corte.save(destino, 'JPEG', quality=78, optimize=True, progressive=True)
    print('salvo %s · %d KB' % (destino, os.path.getsize(destino) // 1024))

    json.dump({'norte': NORTE, 'sul': SUL, 'oeste': OESTE, 'leste': LESTE,
               'largura': corte.size[0], 'altura': corte.size[1], 'zoom': Z,
               'atribuicao': ATRIB, 'arquivo': 'img/campos-gerais-satelite.jpg'},
              open(os.path.join(AQUI, 'satelite.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
