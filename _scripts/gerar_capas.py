# -*- coding: utf-8 -*-
"""Rasteriza a capa de cada guia em PDF para usar como miniatura no site."""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
import pymupdf
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(AQUI, 'site', 'img', 'capas')
BASE = r'C:\Users\Dalla\OneDrive\Desktop\NOSSA SAÚDE\ESTUDO CAMPOS GERAIS'
P_CID = os.path.join(BASE, '02 - COMPARATIVOS DE REDE', 'Rede por cidade')
P02 = os.path.join(BASE, '02 - COMPARATIVOS DE REDE')

os.makedirs(IMG, exist_ok=True)
IND = json.load(open(os.path.join(AQUI, 'indice_cidades.json'), encoding='utf-8'))


def capa(pdf, destino, largura=760):
    d = pymupdf.open(pdf)
    pg = d[0]
    esc = largura / pg.rect.width
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(esc, esc))
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    im.save(destino, 'JPEG', quality=82, optimize=True, progressive=True)
    d.close()
    return os.path.getsize(destino)


total = 0
for it in IND:
    src = os.path.join(P_CID, 'Rede Nossa Saude - %s.pdf' % it['cidade'])
    dst = os.path.join(IMG, 'capa-%s.jpg' % it['slug'])
    n = capa(src, dst)
    total += n
    print('%-16s %5d KB' % (it['cidade'], n // 1024))

reg = os.path.join(P02, 'Rede Nossa Saude - Campos Gerais (9 cidades).pdf')
n = capa(reg, os.path.join(IMG, 'capa-regiao.jpg'))
total += n
print('%-16s %5d KB' % ('REGIÃO', n // 1024))
print('total %d KB em %d capas' % (total // 1024, len(IND) + 1))
