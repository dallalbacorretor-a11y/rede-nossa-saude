# -*- coding: utf-8 -*-
"""Motor de layout dos PDFs de rede credenciada — padrão visual dos materiais Amil da Mazza Broker."""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, white, Color
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.pdfbase.pdfmetrics import stringWidth

PW, PH = landscape(A4)              # 841.89 x 595.28
ML = MR = 38
MB = 44
CW = PW - ML - MR

# paleta da marca Nossa Saude (nossasaude.com.br): branco, laranja/vermelho
# e o marrom-acinzentado #4C4441 do texto. Sem azul.
# O selo dourado continua sendo a assinatura da Mazza Broker.
AZUL_TOPO = HexColor('#E6411C')     # faixa de topo — vermelho-laranja da marca
NAVY = HexColor('#332D2B')          # marrom escuro (fundo das capas e barras)
NAVY_MED = HexColor('#4C4441')
NAVY_CL = HexColor('#C9A08F')
OURO = HexColor('#9A7513')
OURO_CL = HexColor('#C8A24A')
LARANJA = HexColor('#F07F09')
ALT = HexColor('#FAF7F5')
CINZA = HexColor('#8B8580')
CINZA_ESC = HexColor('#4C4441')
TXT = HexColor('#2A2523')
LINHA = HexColor('#E6E1DD')

SER = 'Times-Roman'
SERB = 'Times-Bold'
SERI = 'Times-Italic'
SAN = 'Helvetica'
SANB = 'Helvetica-Bold'
SANI = 'Helvetica-Oblique'


def wrap(txt, font, size, width):
    txt = (txt or '').strip()
    if not txt:
        return ['']
    out, cur = [], ''
    for w in txt.replace('\n', ' ').split(' '):
        t = (cur + ' ' + w).strip()
        if stringWidth(t, font, size) <= width or not cur:
            cur = t
        else:
            out.append(cur); cur = w
    if cur:
        out.append(cur)
    return out


def corta(txt, font, size, width, linhas):
    """Quebra em no máximo `linhas`, com reticências na última."""
    ls = wrap(txt, font, size, width)
    if len(ls) <= linhas:
        return ls
    ls = ls[:linhas]
    ultima = ls[-1]
    while ultima and stringWidth(ultima + '…', font, size) > width:
        ultima = ultima[:-1]
    ls[-1] = ultima.rstrip(' ,;') + '…'
    return ls


class Folha:
    def __init__(self, path, titulo_doc, rodape):
        self.c = pdfcanvas.Canvas(path, pagesize=(PW, PH))
        self.c.setTitle(titulo_doc)
        self.c.setAuthor('Mazza Broker')
        self.c.setSubject('Rede credenciada')
        self.rodape = rodape
        self.pg = 0
        self.y = 0
        self._cols = None

    # ------------------------------------------------------------ marca
    def tag_mazza(self, x, y, h=34, escala=1.0):
        """Selo dourado da Mazza Broker (retângulo com a ponta direita chanfrada)."""
        c = self.c
        w = h * 2.05
        corte = h * 0.42
        p = c.beginPath()
        p.moveTo(x, y)
        p.lineTo(x + w, y)
        p.lineTo(x + w + corte, y + h / 2.0)
        p.lineTo(x + w, y + h)
        p.lineTo(x, y + h)
        p.close()
        c.setFillColor(OURO)
        c.drawPath(p, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont(SERB, h * 0.42)
        c.drawString(x + h * 0.30, y + h * 0.47, 'Mazza')
        c.setFont(SANB, h * 0.155)
        c.drawString(x + h * 0.33, y + h * 0.22, 'B R O K E R')
        return w + corte

    def _circulo(self, x, y, r, cor, lw=1.0):
        c = self.c
        c.setStrokeColor(cor); c.setLineWidth(lw)
        c.circle(x, y, r, stroke=1, fill=0)

    # ------------------------------------------------------------ capa
    def capa(self, eyebrow, titulo, italico, fonte_txt, contato):
        c = self.c
        c.setFillColor(NAVY); c.rect(0, 0, PW, PH, stroke=0, fill=1)
        c.setFillColor(AZUL_TOPO); c.rect(0, PH - 13, PW, 13, stroke=0, fill=1)
        c.setFillColor(OURO); c.rect(0, PH - 17, PW, 4, stroke=0, fill=1)

        self._circulo(PW * 0.60, PH * 0.66, 9, HexColor('#6E5F59'), 1.0)
        self._circulo(PW * 0.93, PH * 0.24, 19, HexColor('#574B46'), 1.2)
        self._circulo(PW * 0.86, PH * 0.79, 5, HexColor('#6E5F59'), 0.9)

        x = ML + 46
        y = PH * 0.66
        c.setFillColor(OURO_CL); c.rect(x, y + 6, 3.2, 11, stroke=0, fill=1)
        c.setFont(SANB, 8.6)
        c.drawString(x + 11, y + 8, eyebrow.upper())

        c.setFillColor(white); c.setFont(SERB, 41)
        c.drawString(x, y - 34, titulo)
        c.setFillColor(OURO_CL); c.setFont(SERI, 32)
        c.drawString(x, y - 78, italico)

        c.setStrokeColor(HexColor('#8A7A72')); c.setLineWidth(0.9)
        c.line(x, y - 100, x + 224, y - 100)

        c.setFillColor(HexColor('#C4B5AC')); c.setFont(SAN, 8.4)
        for i, ln in enumerate(wrap(fonte_txt, SAN, 8.4, CW * 0.55)):
            c.drawString(x, y - 122 - i * 11.5, ln)

        self.tag_mazza(x, 120, 34)
        c.setFillColor(white); c.setFont(SAN, 9)
        c.drawString(x, 100, contato[0])
        c.setFillColor(HexColor('#C4B5AC')); c.setFont(SAN, 8.6)
        c.drawString(x, 84, contato[1])
        c.drawString(x + 200, 84, contato[2])
        c.showPage()

    # ------------------------------------------------------------ moldura
    def _moldura(self):
        c = self.c
        self.pg += 1
        c.setFillColor(white); c.rect(0, 0, PW, PH, stroke=0, fill=1)
        c.setFillColor(AZUL_TOPO); c.rect(0, PH - 7, PW, 7, stroke=0, fill=1)
        self.tag_mazza(ML, 18, 17)
        c.setFillColor(CINZA); c.setFont(SAN, 7.6)
        c.drawString(ML + 56, 23, self.rodape)
        c.setFillColor(OURO); c.setFont(SANB, 9)
        c.drawRightString(PW - MR, 22, str(self.pg))
        self.y = PH - 40

    def nova_pagina(self):
        if self.pg:
            self.c.showPage()
        self._moldura()

    def espaco(self, h):
        if self.y - h < MB:
            self.nova_pagina()
            return True
        return False

    # ------------------------------------------------------------ blocos
    def secao(self, titulo, subtitulo='', nova=True):
        if nova:
            self.nova_pagina()
        else:
            self.espaco(120)
        c = self.c
        c.setFillColor(OURO); c.rect(ML, self.y - 17, 3.4, 19, stroke=0, fill=1)
        c.setFillColor(NAVY); c.setFont(SERB, 19)
        c.drawString(ML + 13, self.y - 13, titulo)
        self.y -= 22
        if subtitulo:
            c.setFillColor(CINZA); c.setFont(SAN, 7.8)
            for ln in wrap(subtitulo, SAN, 7.8, CW * 0.86):
                c.drawString(ML + 13, self.y - 8, ln)
                self.y -= 10.4
        self.y -= 8

    PLURAL = {'prestador': 'prestadores', 'hospital': 'hospitais',
              'profissional': 'profissionais', 'clínica': 'clínicas'}

    def grupo(self, nome, n, unidade='prestador'):
        self.espaco(74)
        c = self.c
        c.setFillColor(NAVY); c.rect(ML, self.y - 21, CW, 21, stroke=0, fill=1)
        c.setFillColor(white); c.setFont(SANB, 10.5)
        c.drawString(ML + 12, self.y - 14.5, nome.upper())
        c.setFillColor(NAVY_CL); c.setFont(SANB, 9)
        c.drawRightString(PW - MR - 12, self.y - 14.5,
                          '%d %s' % (n, unidade if n == 1 else self.PLURAL.get(unidade, unidade + 's')))
        self.y -= 21

    def cabecalho(self, cols):
        self._cols = cols
        self.espaco(40)
        c = self.c
        c.setFillColor(CINZA); c.setFont(SANB, 6.4)
        x = ML + 12
        for rot, w in cols:
            c.drawString(x, self.y - 9.5, rot)
            x += w
        c.setStrokeColor(NAVY); c.setLineWidth(0.8)
        c.line(ML, self.y - 13.5, ML + CW, self.y - 13.5)
        self.y -= 15

    def subgrupo(self, nome, n):
        self.espaco(52)
        c = self.c
        self.y -= 6
        c.setFillColor(NAVY); c.rect(ML, self.y - 11, 2.6, 11, stroke=0, fill=1)
        c.setFillColor(NAVY); c.setFont(SANB, 9.2)
        c.drawString(ML + 9, self.y - 9, nome)
        c.setFillColor(CINZA); c.setFont(SAN, 7.2)
        c.drawString(ML + 13 + stringWidth(nome, SANB, 9.2), self.y - 9,
                     '%d prestador%s' % (n, '' if n == 1 else 'es'))
        self.y -= 15

    def linha(self, valores, alt=False, tag=None, max_linhas=3, cinza_ultima=True):
        """valores: lista de strings na ordem das colunas de cabecalho()."""
        cols = self._cols
        blocos, altura = [], 0
        for i, ((rot, w), v) in enumerate(zip(cols, valores)):
            fonte = SANB if i == 0 else SAN
            tam = 8.2 if i == 0 else 7.8
            ls = corta(v or '—', fonte, tam, w - 10, max_linhas)
            blocos.append((ls, fonte, tam))
            altura = max(altura, len(ls) * (tam + 2.2))
        if tag:
            altura += 8
        h = altura + 9
        if self.y - h < MB:
            self.nova_pagina()
            self.cabecalho(cols)
        c = self.c
        if alt:
            c.setFillColor(ALT); c.rect(ML, self.y - h, CW, h, stroke=0, fill=1)
        x = ML + 12
        for i, ((ls, fonte, tam), (rot, w)) in enumerate(zip(blocos, cols)):
            yy = self.y - 11
            ultima = cinza_ultima and i == len(cols) - 1
            c.setFillColor(TXT if i == 0 else (CINZA if ultima else CINZA_ESC))
            c.setFont(fonte, tam)
            for ln in ls:
                c.drawString(x, yy, ln)
                yy -= tam + 2.2
            if i == 0 and tag:
                c.setFillColor(OURO); c.setFont(SANB, 5.8)
                c.drawString(x, yy - 1, tag.upper())
            x += w
        self.y -= h

    def stats(self, itens, cols=3):
        """itens: lista de (numero, rotulo)."""
        c = self.c
        linhas = (len(itens) + cols - 1) // cols
        bw = CW / float(cols)
        bh = 62
        self.espaco(linhas * bh + 10)
        y0 = self.y
        c.setStrokeColor(LINHA); c.setLineWidth(0.8)
        c.rect(ML, y0 - linhas * bh, CW, linhas * bh, stroke=1, fill=0)
        for k, (num, rot) in enumerate(itens):
            lin, col = divmod(k, cols)
            x = ML + col * bw
            y = y0 - (lin + 1) * bh
            if col:
                c.setStrokeColor(LINHA); c.line(x, y, x, y + bh)
            if lin:
                c.setStrokeColor(LINHA); c.line(x, y + bh, x + bw, y + bh)
            c.setFillColor(NAVY); c.setFont(SERB, 25)
            c.drawString(x + 18, y + bh - 34, str(num))
            c.setFillColor(CINZA_ESC); c.setFont(SAN, 7.8)
            for i, ln in enumerate(wrap(rot, SAN, 7.8, bw - 32)[:2]):
                c.drawString(x + 18, y + bh - 50 - i * 9.6, ln)
        self.y = y0 - linhas * bh - 16

    def paragrafo(self, txt, font=SAN, size=8.6, cor=None, largura=None, gap=3.4):
        self.espaco(size + gap + 6)
        c = self.c
        c.setFillColor(cor or CINZA_ESC)
        c.setFont(font, size)
        for ln in wrap(txt, font, size, largura or CW * 0.86):
            self.espaco(size + gap)
            c.drawString(ML, self.y - size, ln)
            self.y -= size + gap

    def caixa_aviso(self, titulo, txt):
        self.espaco(76)
        c = self.c
        alt = 30 + 11.5 * len(wrap(txt, SAN, 8.4, CW - 46))
        c.setFillColor(HexColor('#FAF6F3')); c.rect(ML, self.y - alt, CW, alt, stroke=0, fill=1)
        c.setFillColor(OURO); c.rect(ML, self.y - alt, 3.4, alt, stroke=0, fill=1)
        c.setFillColor(NAVY); c.setFont(SANB, 9)
        c.drawString(ML + 16, self.y - 18, titulo.upper())
        c.setFillColor(CINZA_ESC); c.setFont(SAN, 8.4)
        yy = self.y - 32
        for ln in wrap(txt, SAN, 8.4, CW - 46):
            c.drawString(ML + 16, yy, ln); yy -= 11.5
        self.y -= alt + 14

    def salvar(self):
        self.c.showPage()
        self.c.save()
