# -*- coding: utf-8 -*-
"""Motor de layout dos PDFs — padrão visual Mazza Broker (referência: ESTUDO JOINVILLE)."""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.pdfbase.pdfmetrics import stringWidth
import common as C

PW, PH = landscape(A4)          # 842 x 595
ML = MR = 36
MT = 44
MB = 40
CW = PW - ML - MR

NAVY = HexColor(C.NAVY)
NAVY2 = HexColor(C.NAVY2)
LARANJA = HexColor(C.LARANJA)
LARANJA_CL = HexColor(C.LARANJA_CLARO)
DOURADO = HexColor(C.DOURADO)
CINZA = HexColor(C.CINZA)
CINZA_CL = HexColor(C.CINZA_CLARO)
BORDA = HexColor(C.BORDA)
CAT_COR = {k: HexColor(v) for k, v in C.CAT_COR.items()}

SER = 'Times-Roman'
SERB = 'Times-Bold'
SERI = 'Times-Italic'
SAN = 'Helvetica'
SANB = 'Helvetica-Bold'
SANI = 'Helvetica-Oblique'


def wrap(txt, font, size, width):
    """Quebra texto em linhas que cabem em width."""
    txt = (txt or '').strip()
    if not txt:
        return ['']
    out, cur = [], ''
    for w in txt.split(' '):
        t = (cur + ' ' + w).strip()
        if stringWidth(t, font, size) <= width or not cur:
            cur = t
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def elide(txt, font, size, width):
    txt = txt or ''
    if stringWidth(txt, font, size) <= width:
        return txt
    while txt and stringWidth(txt + '…', font, size) > width:
        txt = txt[:-1]
    return txt + '…'


class Doc:
    def __init__(self, path, subtitulo):
        self.c = pdfcanvas.Canvas(path, pagesize=(PW, PH))
        self.c.setTitle('Rede credenciada %s — %s' % (C.OPERADORA, C.REGIAO))
        self.c.setAuthor('Mazza Broker')
        self.subtitulo = subtitulo
        self.pg = 0
        self.y = 0
        self.secao = ''

    # ---------- capa ----------
    def capa(self, titulo1, titulo2, chamada, destaques):
        c = self.c
        c.setFillColor(NAVY); c.rect(0, 0, PW, PH, stroke=0, fill=1)
        c.setFillColor(LARANJA); c.rect(0, PH - 10, PW, 10, stroke=0, fill=1)
        c.setFillColor(DOURADO); c.rect(0, 0, PW, 6, stroke=0, fill=1)

        c.setFillColor(LARANJA); c.rect(ML, PH - 150, 68, 5, stroke=0, fill=1)
        c.setFillColor(DOURADO); c.rect(ML + 74, PH - 150, 26, 5, stroke=0, fill=1)

        c.setFillColor(white); c.setFont(SERB, 40)
        c.drawString(ML, PH - 200, titulo1)
        c.setFillColor(DOURADO); c.setFont(SERI, 30)
        c.drawString(ML, PH - 240, titulo2)

        c.setFillColor(HexColor('#C9D2DE')); c.setFont(SAN, 12)
        yy = PH - 278
        for ln in wrap(chamada, SAN, 12, CW * 0.62):
            c.drawString(ML, yy, ln); yy -= 17

        # cartões de destaque
        x = ML
        for rot, val in destaques:
            w = 132
            c.setFillColor(HexColor('#1B2F4E')); c.roundRect(x, 110, w, 62, 6, stroke=0, fill=1)
            c.setFillColor(LARANJA); c.rect(x, 110, 4, 62, stroke=0, fill=1)
            c.setFillColor(white); c.setFont(SANB, 22)
            c.drawString(x + 16, 140, str(val))
            c.setFillColor(HexColor('#9FB0C6')); c.setFont(SAN, 8)
            for i, ln in enumerate(wrap(rot.upper(), SAN, 8, w - 26)[:2]):
                c.drawString(x + 16, 128 - i * 10, ln)
            x += w + 12

        c.setFillColor(DOURADO); c.setFont(SERB, 15)
        c.drawRightString(PW - MR, 130, 'Mazza Broker')
        c.setFillColor(HexColor('#9FB0C6')); c.setFont(SAN, 8.5)
        c.drawRightString(PW - MR, 116, C.CORRETOR)
        c.drawRightString(PW - MR, 104, C.CORRETOR_TEL + ' · ' + C.CORRETOR_MAIL)

        c.setFillColor(HexColor('#8494A9')); c.setFont(SAN, 7.5)
        c.drawString(ML, 74, C.FONTE)
        for i, ln in enumerate(wrap(C.AVISO, SAN, 7.5, CW * 0.8)):
            c.drawString(ML, 62 - i * 10, ln)
        c.showPage()

    # ---------- moldura ----------
    def _moldura(self):
        c = self.c
        self.pg += 1
        c.setFillColor(NAVY); c.rect(0, PH - 26, PW, 26, stroke=0, fill=1)
        c.setFillColor(LARANJA); c.rect(0, PH - 30, PW, 4, stroke=0, fill=1)
        c.setFillColor(white); c.setFont(SERB, 11)
        c.drawString(ML, PH - 18, 'Rede credenciada Nossa Saúde')
        c.setFillColor(HexColor('#9FB0C6')); c.setFont(SAN, 8.5)
        c.drawString(ML + 178, PH - 18, C.REGIAO)
        if self.secao:
            c.setFillColor(DOURADO); c.setFont(SANB, 9)
            c.drawRightString(PW - MR, PH - 18, self.secao)

        c.setStrokeColor(BORDA); c.setLineWidth(0.6)
        c.line(ML, 30, PW - MR, 30)
        c.setFillColor(CINZA); c.setFont(SAN, 7.5)
        c.drawString(ML, 20, 'Mazza Broker · Rede credenciada %s · %s' % (C.OPERADORA, C.REGIAO))
        c.setFillColor(DOURADO); c.setFont(SANB, 9)
        c.drawRightString(PW - MR, 19, str(self.pg))
        self.y = PH - 56

    def nova_pagina(self):
        if self.pg:
            self.c.showPage()
        self._moldura()

    def espaco(self, h):
        if self.y - h < MB + 8:
            self.nova_pagina()
            return True
        return False

    # ---------- blocos ----------
    def titulo_cidade(self, cidade, resumo, forcar_pagina=True, minimo=300):
        self.secao = cidade
        if forcar_pagina or self.y - minimo < MB:
            self.nova_pagina()
        else:
            self.y -= 12
        c = self.c
        c.setFillColor(NAVY); c.roundRect(ML, self.y - 42, CW, 42, 5, stroke=0, fill=1)
        c.setFillColor(LARANJA); c.rect(ML, self.y - 42, 5, 42, stroke=0, fill=1)
        c.setFillColor(white); c.setFont(SERB, 19)
        c.drawString(ML + 18, self.y - 26, cidade)
        c.setFillColor(HexColor('#9FB0C6')); c.setFont(SAN, 9)
        c.drawString(ML + 18 + stringWidth(cidade, SERB, 19) + 12, self.y - 25, '/ PR')
        c.setFillColor(DOURADO); c.setFont(SANB, 9)
        c.drawRightString(PW - MR - 16, self.y - 25, resumo)
        self.y -= 56

    def titulo_categoria(self, cat, n):
        self.espaco(58)
        c = self.c
        cor = CAT_COR[cat]
        c.setFillColor(cor); c.rect(ML, self.y - 18, 4, 18, stroke=0, fill=1)
        c.setFillColor(cor); c.setFont(SANB, 11)
        c.drawString(ML + 12, self.y - 13, cat.upper())
        c.setFillColor(CINZA); c.setFont(SAN, 8.5)
        c.drawString(ML + 16 + stringWidth(cat.upper(), SANB, 11), self.y - 13,
                     '%d %s' % (n, 'prestador' if n == 1 else 'prestadores'))
        self.y -= 24

    def sub_especialidade(self, esp, n):
        self.espaco(40)
        c = self.c
        c.setFillColor(LARANJA_CL); c.rect(ML, self.y - 15, CW, 15, stroke=0, fill=1)
        c.setFillColor(HexColor('#9A4310')); c.setFont(SANB, 8.5)
        c.drawString(ML + 8, self.y - 11, esp.upper())
        c.setFillColor(HexColor('#B5764C')); c.setFont(SAN, 7.5)
        c.drawRightString(PW - MR - 8, self.y - 11, '%d' % n)
        self.y -= 19

    def cabecalho_tabela(self, cols, cor):
        if self.y - 46 < MB + 8:
            self.nova_pagina()
        c = self.c
        c.setFillColor(cor); c.rect(ML, self.y - 15, CW, 15, stroke=0, fill=1)
        c.setFillColor(white); c.setFont(SANB, 7.5)
        x = ML + 8
        for rot, w in cols:
            c.drawString(x, self.y - 10.5, rot.upper())
            x += w
        self.y -= 15
        self._cols = cols
        self._cor = cor

    def marcas(self, x0, y0, w, h, redes, ativas):
        """Desenha as pilulas de rede, centradas na celula."""
        c = self.c
        fs = 5.8
        larguras = [max(22, stringWidth(r['curto'].upper(), SANB, fs) + 10) for r in redes]
        total = sum(larguras) + 3 * (len(redes) - 1)
        x = x0 + max(0, (w - total) / 2.0)
        for r, lw in zip(redes, larguras):
            on = r['id'] in ativas
            if on:
                c.setFillColor(HexColor(r['cor']))
                c.roundRect(x, y0 + h / 2 - 5.5, lw, 11, 3, stroke=0, fill=1)
                c.setFillColor(white)
            else:
                c.setStrokeColor(BORDA); c.setLineWidth(0.6)
                c.roundRect(x, y0 + h / 2 - 5.5, lw, 11, 3, stroke=1, fill=0)
                c.setFillColor(HexColor('#B6BCC5'))
            c.setFont(SANB, fs)
            c.drawCentredString(x + lw / 2.0, y0 + h / 2 - 2.1, r['curto'].upper())
            x += lw + 3

    def linha(self, celulas, alt=False, negrito_col0=True, redes=None, ativas=None):
        """celulas: lista de (texto_principal, texto_secundario_ou_None) por coluna."""
        cols = self._cols
        alturas = []
        for (txt, sub), (rot, w) in zip(celulas, cols):
            n = len(wrap(txt, SANB if negrito_col0 else SAN, 8, w - 12))
            m = len(wrap(sub, SAN, 6.8, w - 12)) if sub else 0
            alturas.append(n * 9.6 + m * 8.2)
        h = max(alturas) + 8
        if self.y - h < MB + 8:
            self.nova_pagina()
            self.cabecalho_tabela(cols, self._cor)
        c = self.c
        if alt:
            c.setFillColor(CINZA_CL); c.rect(ML, self.y - h, CW, h, stroke=0, fill=1)
        c.setStrokeColor(BORDA); c.setLineWidth(0.4)
        c.line(ML, self.y - h, ML + CW, self.y - h)
        x = ML + 8
        for i, ((txt, sub), (rot, w)) in enumerate(zip(celulas, cols)):
            if txt == '@REDES@' and redes:
                self.marcas(x - 8, self.y - h, w, h, redes, ativas or [])
                x += w
                continue
            yy = self.y - 12
            c.setFillColor(HexColor('#111827'))
            c.setFont(SANB if (i == 0 and negrito_col0) else SAN, 8)
            for ln in wrap(txt, SANB if (i == 0 and negrito_col0) else SAN, 8, w - 12):
                c.drawString(x, yy, ln); yy -= 9.6
            if sub:
                c.setFillColor(CINZA); c.setFont(SAN, 6.8)
                for ln in wrap(sub, SAN, 6.8, w - 12):
                    c.drawString(x, yy, ln); yy -= 8.2
            x += w
        self.y -= h

    def texto(self, txt, font=SAN, size=9, cor=None, gap=4):
        self.espaco(size + gap + 4)
        self.c.setFillColor(cor or HexColor('#374151'))
        self.c.setFont(font, size)
        for ln in wrap(txt, font, size, CW):
            self.espaco(size + gap)
            self.c.drawString(ML, self.y - size, ln)
            self.y -= size + gap

    def salvar(self):
        self.c.showPage()
        self.c.save()
