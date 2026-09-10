# -*- coding: utf-8 -*-
import os, sys, collections, shutil
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth
import common as C
from pdfbase import (Doc, PW, PH, ML, MR, MB, CW, NAVY, LARANJA, LARANJA_CL, DOURADO,
                     CINZA, CINZA_CL, BORDA, CAT_COR, SER, SERB, SERI, SAN, SANB, SANI,
                     wrap, elide)

sys.stdout.reconfigure(encoding='utf-8')
os.makedirs(C.P02, exist_ok=True)

D = C.carregar()
ITENS, REDES = D['itens'], D['redes']
AMPLAS = C.redes_amplas(D)
IDS_AMPLAS = {r['id'] for r in AMPLAS}
NRED = len(REDES)

TOTAL = len(ITENS)
por_cat = lambda k, lst=None: sum(1 for i in (lst if lst is not None else ITENS) if i['categoria'] == k)
N_HOSP, N_CLIN, N_LAB, N_MED = [por_cat(k) for k in C.CATS]


def da_cidade(cid, cats=None):
    return C.ordena([i for i in ITENS if i['cidade'] == cid and (not cats or i['categoria'] in cats)])


def end_txt(r):
    return ' | '.join(C.enderecos_txt(r)) or '—'


def tel_txt(r):
    t = C.tels(r)
    return ' · '.join(t) if t else 'Não informado'


def corpo_txt(r, limite=8, mostrar=True):
    cc = r['corpo_clinico']
    if not cc or not mostrar:
        return ''
    n = [m['nome'] for m in cc]
    if len(n) > limite:
        return 'Corpo clínico: ' + ', '.join(n[:limite]) + ' e mais %d profissionais' % (len(n) - limite)
    return 'Corpo clínico: ' + ', '.join(n)


COLS_INST = [('Prestador', CW * 0.27), ('Especialidades / serviços', CW * 0.21),
             ('Endereço', CW * 0.26), ('Telefone', CW * 0.13), ('Redes', CW * 0.13)]
COLS_PROF = [('Profissional', CW * 0.24), ('Registro', CW * 0.09),
             ('Demais especialidades', CW * 0.15), ('Endereço', CW * 0.26),
             ('Telefone', CW * 0.13), ('Redes', CW * 0.13)]


def bloco_institucional(doc, cat, recs, corpo=True):
    if not recs:
        return
    doc.titulo_categoria(cat, len(recs))
    doc.cabecalho_tabela(COLS_INST, CAT_COR[cat])
    for i, r in enumerate(recs):
        sub_nome = r['razao'] if r['razao'].lower() != r['nome_exib'].lower() else ''
        if r['cnpj']:
            sub_nome = sub_nome + ('  ·  ' if sub_nome else '') + 'CNPJ ' + r['cnpj']
        doc.linha([(r['nome_exib'], sub_nome),
                   (' • '.join(r['esp_exib']), corpo_txt(r, mostrar=corpo)),
                   (end_txt(r), r['tipo']),
                   (tel_txt(r), ''),
                   ('@REDES@', '')],
                  alt=(i % 2 == 1), redes=REDES, ativas=r['redes'])
    doc.y -= 10


def bloco_profissionais(doc, recs):
    if not recs:
        return
    doc.titulo_categoria(C.CATS[3], len(recs))
    porespec = collections.defaultdict(list)
    for r in recs:
        for e in (r['esp_exib'] or ['Sem especialidade informada']):
            porespec[e].append(r)
    for esp in sorted(porespec, key=lambda s: (s == 'Médico', s.lower())):
        lst = sorted(porespec[esp], key=lambda r: r['nome_exib'].lower())
        doc.espaco(96)
        doc.sub_especialidade(esp, len(lst))
        doc.cabecalho_tabela(COLS_PROF, HexColor('#8A6BB5'))
        for i, r in enumerate(lst):
            outras = [e for e in r['esp_exib'] if e != esp]
            doc.linha([(r['nome_exib'], r['tipo']),
                       (r['conselho'] or r['cnpj'], ''),
                       (' • '.join(outras) if outras else '—', ''),
                       (end_txt(r), ''),
                       (tel_txt(r), ''),
                       ('@REDES@', '')],
                      alt=(i % 2 == 1), redes=REDES, ativas=r['redes'])
        doc.y -= 8


def pagina_como_ler(doc, cards, caixa_titulo, caixa_txt):
    doc.secao = 'Como usar'
    doc.nova_pagina()
    c = doc.c
    c.setFillColor(NAVY); c.setFont(SERB, 22)
    c.drawString(ML, doc.y - 6, 'Como usar este material')
    c.setFillColor(CINZA); c.setFont(SAN, 9.5)
    c.drawString(ML, doc.y - 24, 'Consulta em %s · operadora %s (CNPJ %s) · %s'
                 % (C.DATA_REF, C.OPERADORA, C.OPER_CNPJ, C.REGIAO))
    doc.y -= 48
    x = ML
    w = (CW - 2 * 14) / 3.0
    ytop = doc.y
    for tit, txt, cor in cards:
        c.setFillColor(HexColor('#FFFFFF')); c.setStrokeColor(BORDA); c.setLineWidth(0.8)
        c.roundRect(x, ytop - 112, w, 112, 6, stroke=1, fill=1)
        c.setFillColor(HexColor(cor)); c.rect(x, ytop - 112, w, 4, stroke=0, fill=1)
        c.setFillColor(HexColor(cor)); c.setFont(SANB, 10)
        c.drawString(x + 14, ytop - 26, tit.upper())
        c.setFillColor(HexColor('#374151')); c.setFont(SAN, 8.6)
        yy = ytop - 44
        for ln in wrap(txt, SAN, 8.6, w - 28):
            c.drawString(x + 14, yy, ln); yy -= 11.4
        x += w + 14
    doc.y = ytop - 130
    c.setFillColor(NAVY); c.roundRect(ML, doc.y - 62, CW, 62, 6, stroke=0, fill=1)
    c.setFillColor(LARANJA); c.rect(ML, doc.y - 62, 5, 62, stroke=0, fill=1)
    c.setFillColor(DOURADO); c.setFont(SANB, 10)
    c.drawString(ML + 18, doc.y - 22, caixa_titulo.upper())
    c.setFillColor(HexColor('#D5DDE8')); c.setFont(SAN, 8.8)
    yy = doc.y - 38
    for ln in wrap(caixa_txt, SAN, 8.8, CW - 40):
        c.drawString(ML + 18, yy, ln); yy -= 11.5
    doc.y -= 84


def pagina_redes(doc):
    doc.secao = 'As redes'
    doc.nova_pagina()
    c = doc.c
    c.setFillColor(NAVY); c.setFont(SERB, 22)
    c.drawString(ML, doc.y - 6, 'As redes credenciadas da região')
    c.setFillColor(CINZA); c.setFont(SAN, 9.5)
    c.drawString(ML, doc.y - 24, 'Cada produto da Nossa Saúde usa uma rede. Planos da mesma rede '
                                 'enxergam exatamente os mesmos prestadores.')
    doc.y -= 48
    x = ML
    w = (CW - (NRED - 1) * 14) / float(NRED)
    ytop = doc.y
    for r in REDES:
        n = sum(1 for i in ITENS if r['id'] in i['redes'])
        cids = C.cidades_da_rede(D, r['id'])
        c.setFillColor(HexColor('#FFFFFF')); c.setStrokeColor(BORDA); c.setLineWidth(0.8)
        c.roundRect(x, ytop - 136, w, 136, 6, stroke=1, fill=1)
        c.setFillColor(HexColor(r['cor'])); c.rect(x, ytop - 136, w, 4, stroke=0, fill=1)
        c.setFillColor(HexColor(r['cor'])); c.setFont(SANB, 11)
        c.drawString(x + 14, ytop - 24, ('Rede ' + r['curto']).upper())
        c.setFillColor(HexColor('#111827')); c.setFont(SANB, 24)
        c.drawString(x + 14, ytop - 52, str(n))
        c.setFillColor(CINZA); c.setFont(SAN, 8)
        c.drawString(x + 14, ytop - 64, 'PRESTADORES  ·  %d PLANOS' % len(r['planos']))
        c.setFillColor(HexColor('#374151')); c.setFont(SAN, 8.2)
        yy = ytop - 80
        for ln in wrap(r['desc'], SAN, 8.2, w - 28)[:4]:
            c.drawString(x + 14, yy, ln); yy -= 10.4
        c.setFillColor(CINZA); c.setFont(SANI, 7.6)
        yy -= 4
        for ln in wrap('Atende em: ' + ', '.join(cids), SANI, 7.6, w - 28)[:3]:
            c.drawString(x + 14, yy, ln); yy -= 9.4
        x += w + 14
    doc.y = ytop - 154

    c.setFillColor(NAVY); c.setFont(SERB, 14)
    c.drawString(ML, doc.y - 12, 'Cobertura por cidade')
    doc.y -= 30
    larg = [CW * 0.20, CW * 0.10] + [(CW * 0.70) / NRED] * NRED
    c.setFillColor(NAVY); c.rect(ML, doc.y - 16, sum(larg), 16, stroke=0, fill=1)
    c.setFillColor(white); c.setFont(SANB, 8)
    xx = ML + 8
    for rot, w_ in zip(['Cidade', 'Total'], larg[:2]):
        c.drawString(xx, doc.y - 11, rot.upper()); xx += w_
    for r, w_ in zip(REDES, larg[2:]):
        c.setFillColor(HexColor(r['cor'])); c.rect(xx - 8, doc.y - 16, w_, 16, stroke=0, fill=1)
        c.setFillColor(white); c.setFont(SANB, 8)
        c.drawString(xx, doc.y - 11, ('Rede ' + r['curto']).upper()); xx += w_
    doc.y -= 16
    for k, cid in enumerate(C.CIDADES):
        lst = [i for i in ITENS if i['cidade'] == cid]
        if k % 2 == 0:
            c.setFillColor(CINZA_CL); c.rect(ML, doc.y - 15, sum(larg), 15, stroke=0, fill=1)
        xx = ML + 8
        c.setFillColor(HexColor('#111827')); c.setFont(SANB, 8)
        c.drawString(xx, doc.y - 10.5, cid); xx += larg[0]
        c.setFont(SAN, 8); c.drawString(xx, doc.y - 10.5, str(len(lst))); xx += larg[1]
        for r, w_ in zip(REDES, larg[2:]):
            n = sum(1 for i in lst if r['id'] in i['redes'])
            c.setFillColor(HexColor(r['cor']) if n else HexColor('#B6BCC5'))
            c.setFont(SANB if n else SAN, 8)
            c.drawString(xx, doc.y - 10.5, str(n) if n else '—'); xx += w_
        doc.y -= 15
    c.setFillColor(LARANJA); c.rect(ML, doc.y - 16, sum(larg), 16, stroke=0, fill=1)
    c.setFillColor(white); c.setFont(SANB, 8)
    xx = ML + 8
    c.drawString(xx, doc.y - 11, 'TOTAL'); xx += larg[0]
    c.drawString(xx, doc.y - 11, str(TOTAL)); xx += larg[1]
    for r, w_ in zip(REDES, larg[2:]):
        c.drawString(xx, doc.y - 11, str(sum(1 for i in ITENS if r['id'] in i['redes']))); xx += w_
    doc.y -= 28

    dif = [i for i in ITENS if 0 < len(IDS_AMPLAS & set(i['redes'])) < len(IDS_AMPLAS)]
    doc.texto('%s: as diferenças' % ' x '.join('Rede ' + r['curto'] for r in AMPLAS),
              SERB, 14, NAVY, gap=8)
    doc.texto('As redes que atendem todas as nove cidades são quase iguais — estes %d prestadores '
              'são toda a diferença entre elas.' % len(dif), SAN, 8.8, HexColor('#374151'), gap=8)
    doc.cabecalho_tabela([('Cidade', CW * 0.16), ('Prestador', CW * 0.42),
                          ('Categoria', CW * 0.18), ('Redes', CW * 0.24)], NAVY)
    for i, r in enumerate(sorted(dif, key=lambda x: (C.CIDADES.index(x['cidade']),
                                                     x['nome_exib'].lower()))):
        doc.linha([(r['cidade'], ''), (r['nome_exib'], r['tipo']),
                   (C.CAT_CURTA[r['categoria']], ''), ('@REDES@', '')],
                  alt=(i % 2 == 1), redes=AMPLAS, ativas=r['redes'])
    doc.y -= 12

    for r in REDES:
        if r['id'] in IDS_AMPLAS:
            continue
        cids = C.cidades_da_rede(D, r['id'])
        sem = [c_ for c_ in C.CIDADES if c_ not in cids]
        doc.texto('Rede %s — cobertura reduzida' % r['curto'], SERB, 13, HexColor(r['cor']), gap=6)
        doc.texto('Atende só em %s. Sem prestador credenciado em: %s. Cliente dessas cidades com um '
                  'plano desta rede não tem atendimento local.'
                  % (', '.join(cids), ', '.join(sem)), SAN, 8.8, HexColor('#374151'), gap=8)


def pagina_avisos(doc):
    doc.secao = 'Observações'
    doc.nova_pagina()
    c = doc.c
    c.setFillColor(NAVY); c.setFont(SERB, 22)
    c.drawString(ML, doc.y - 6, 'Observações e contato')
    doc.y -= 40
    doc.texto('Planos por rede credenciada', SERB, 14, NAVY, gap=8)
    for r in REDES:
        doc.texto('Rede %s — %d planos' % (r['curto'], len(r['planos'])), SANB, 9.4,
                  HexColor(r['cor']), gap=4)
        nomes = sorted({(p['txt'].split(' - ')[1].strip() if ' - ' in p['txt'] else p['txt'])
                        for p in r['planos']})
        doc.texto(' · '.join(n for n in nomes if n) or '—', SAN, 8.2, HexColor('#374151'), gap=8)
    doc.texto('Fonte e validade', SERB, 14, NAVY, gap=8)
    doc.texto(C.FONTE, SAN, 8.8, HexColor('#374151'), gap=4)
    doc.texto(C.AVISO, SAN, 8.8, HexColor('#374151'), gap=10)
    doc.espaco(90)
    c.setFillColor(NAVY); c.roundRect(ML, doc.y - 70, CW, 70, 6, stroke=0, fill=1)
    c.setFillColor(LARANJA); c.rect(ML, doc.y - 70, 5, 70, stroke=0, fill=1)
    c.setFillColor(DOURADO); c.setFont(SERB, 16)
    c.drawString(ML + 20, doc.y - 26, 'Mazza Broker')
    c.setFillColor(white); c.setFont(SAN, 9.5)
    c.drawString(ML + 20, doc.y - 43, C.CORRETOR + '  ·  corretor de saúde')
    c.setFillColor(HexColor('#9FB0C6')); c.setFont(SAN, 9)
    c.drawString(ML + 20, doc.y - 58, '%s  ·  %s' % (C.CORRETOR_TEL, C.CORRETOR_MAIL))
    doc.y -= 84


CARDS = [
    ('As marcas coloridas',
     'Cada prestador traz as redes credenciadas em que ele está: %s. Marca colorida = atende; '
     'marca vazada = não atende naquela rede.' % ', '.join(r['curto'] for r in REDES), C.NAVY2),
    ('Rede, não plano',
     'A Nossa Saúde tem %d planos que atendem a região, mas só %d redes credenciadas. Planos da '
     'mesma rede têm exatamente os mesmos prestadores — muda a acomodação, a coparticipação e o preço.'
     % (sum(len(r['planos']) for r in REDES), NRED), C.LARANJA),
    ('Confira antes de fechar',
     'A rede muda por decisão da operadora. Confirme no portal da Nossa Saúde antes de contratar, '
     'principalmente o hospital e o laboratório que o cliente usa.', '#1F7A5A'),
]


def pdf_completo():
    path = os.path.join(C.P02, 'NOSSA SAUDE - CAMPOS GERAIS - Guia COMPLETO (todas as redes).pdf')
    doc = Doc(path, 'completo')
    doc.capa('Rede credenciada', 'Nossa Saúde · Campos Gerais',
             'Guia completo da rede credenciada da Nossa Saúde nas 9 cidades dos Campos Gerais, com '
             'a marcação de qual rede — e portanto quais planos — alcança cada prestador. Inclui '
             'hospitais, clínicas, laboratórios, imagem e todos os profissionais por especialidade.',
             [('prestadores', TOTAL), ('cidades', len(C.CIDADES)), ('redes credenciadas', NRED),
              ('planos mapeados', sum(len(r['planos']) for r in REDES)), ('hospitais', N_HOSP)])
    pagina_como_ler(doc, CARDS, 'Antes de fechar com o cliente', C.AVISO + '  ' + C.FONTE)
    pagina_redes(doc)
    for cid in C.CIDADES:
        recs = da_cidade(cid)
        n = [por_cat(k, recs) for k in C.CATS]
        doc.titulo_cidade(cid, '%d prestadores  ·  %d hospitais  ·  %d labs e imagem  ·  %d profissionais'
                          % (len(recs), n[0], n[2], n[3]))
        for cat in C.CATS[:3]:
            bloco_institucional(doc, cat, [r for r in recs if r['categoria'] == cat])
        bloco_profissionais(doc, [r for r in recs if r['categoria'] == C.CATS[3]])
    pagina_avisos(doc)
    doc.salvar()
    return path


def pdf_clientes():
    path = os.path.join(C.P02, 'NOSSA SAUDE - CAMPOS GERAIS - CLIENTES (Principais).pdf')
    doc = Doc(path, 'clientes')
    doc.capa('Onde você é atendido', 'Nossa Saúde · Campos Gerais',
             'Os hospitais, clínicas, laboratórios e centros de imagem da Nossa Saúde em cada uma das '
             '9 cidades dos Campos Gerais, com a indicação de quais redes credenciadas atendem cada '
             'um. A lista completa de médicos por especialidade está no guia completo.',
             [('hospitais e PS', N_HOSP), ('laboratórios e imagem', N_LAB),
              ('clínicas', N_CLIN), ('cidades', len(C.CIDADES)), ('redes', NRED)])
    pagina_como_ler(doc, CARDS, 'Importante', C.AVISO + '  ' + C.FONTE)
    pagina_redes(doc)
    for cid in C.CIDADES:
        recs = da_cidade(cid, C.CATS[:3])
        n_prof = por_cat(C.CATS[3], [i for i in ITENS if i['cidade'] == cid])
        doc.titulo_cidade(cid, '%d estabelecimentos  ·  + %d profissionais no guia completo'
                          % (len(recs), n_prof),
                          forcar_pagina=(cid == C.CIDADES[0]),
                          minimo=130 + 46 * max(1, len(recs)))
        for cat in C.CATS[:3]:
            bloco_institucional(doc, cat, [r for r in recs if r['categoria'] == cat], corpo=False)
        if not recs:
            doc.texto('Sem estabelecimento credenciado nesta cidade — atendimento em Ponta Grossa.',
                      SANI, 9, CINZA)
    pagina_avisos(doc)
    doc.salvar()
    return path


if __name__ == '__main__':
    for velho in os.listdir(C.P02):
        if 'VIDA NOVA CG' in velho and velho.endswith('.pdf'):
            os.remove(os.path.join(C.P02, velho))
    p1 = pdf_clientes()
    p2 = pdf_completo()
    destinos = {p1: 'rede-nossa-saude-clientes.pdf', p2: 'rede-nossa-saude-completo.pdf'}
    site = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site', 'arquivos')
    for p in (p1, p2):
        print('OK', os.path.getsize(p), p)
        if os.path.isdir(site):
            shutil.copy2(p, os.path.join(site, destinos[p]))
