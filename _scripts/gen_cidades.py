# -*- coding: utf-8 -*-
"""Gera um PDF por cidade + o PDF da região — rede única (todos os planos como um só)."""
import os, sys, json, shutil, collections, unicodedata, re
sys.stdout.reconfigure(encoding='utf-8')
from pdfamil import (Folha, ML, MR, CW, PW, PH, NAVY, OURO, CINZA, CINZA_ESC, NAVY_CL,
                     SAN, SANB, SANI, SERB, wrap)

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = r'C:\Users\Dalla\OneDrive\Desktop\NOSSA SAÚDE\ESTUDO CAMPOS GERAIS'
P02 = os.path.join(BASE, '02 - COMPARATIVOS DE REDE')
P_CID = os.path.join(BASE, '02 - COMPARATIVOS DE REDE', 'Rede por cidade')
SITE_ARQ = os.path.join(AQUI, 'site', 'arquivos')

import corretor as CO

OPERADORA = 'Nossa Saúde'
OPER_CNPJ = '02.862.447/0001-03'
REGIAO = 'Campos Gerais'
CORRETOR = CO.NOME
CORRETOR_CARGO = CO.CARGO
CORRETOR_TEL = CO.TEL
CORRETOR_MAIL = CO.MAIL
DATA_LONGA = '10 de setembro de 2026'
FONTE_CAPA = ('Levantado na rede credenciada oficial da Nossa Saúde em ' + DATA_LONGA +
              ', considerando todos os planos da operadora.')
AVISO = ('A rede credenciada é definida e alterada exclusivamente pela operadora. Esta lista reúne '
         'todos os planos da Nossa Saúde na cidade — antes de contratar ou de encaminhar o paciente, '
         'confirme no portal da operadora se o prestador atende o plano específico.')

D = json.load(open(os.path.join(AQUI, 'dados_unico.json'), encoding='utf-8'))
ITENS, CIDADES, EXAMES = D['itens'], D['cidades'], D['exames']
CAT_PROF = 'Profissionais (médicos e demais)'

COLS = [('Prestador', CW * 0.215), ('Endereço', CW * 0.275), ('Bairro', CW * 0.125),
        ('Telefone', CW * 0.135), ('Especialidades', CW * 0.25)]
COLS_PROF = [('Profissional', CW * 0.215), ('Registro', CW * 0.085),
             ('Endereço', CW * 0.255), ('Bairro', CW * 0.115),
             ('Telefone', CW * 0.13), ('Especialidades', CW * 0.20)]


def slug(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-').lower()


def ends(r):
    return ' | '.join(dict.fromkeys(e['logradouro'] for e in r['enderecos'] if e['logradouro'])) or '—'


def bairros(r):
    b = list(dict.fromkeys(e['bairro'] for e in r['enderecos'] if e['bairro']))
    return ' · '.join(b) or '—'


def tels(r):
    out = []
    for e in r['enderecos']:
        for t in re.split(r'\s*/\s*', e.get('tel') or ''):
            t = t.strip()
            if t and t not in out:
                out.append(t)
    return '  '.join(out) or 'Não informado'


def esp(r):
    return ', '.join(r['esp_exib']) or '—'


def linha_prest(f, r, alt, prof=False):
    if prof:
        f.linha([r['nome_exib'], r['conselho'] or r['cnpj'], ends(r), bairros(r), tels(r), esp(r)],
                alt=alt, max_linhas=2)
    else:
        f.linha([r['nome_exib'], ends(r), bairros(r), tels(r), esp(r)],
                alt=alt, tag=('internação' if r['internacao'] else None), max_linhas=3)


# ---------------------------------------------------------------- seções
def sec_numeros(f, lst, escopo):
    hosp = [r for r in lst if r['internacao']]
    lab = [r for r in lst if 'Análises clínicas e patologia' in r['naturezas'] and not r['internacao']]
    img = [r for r in lst if 'Diagnóstico por imagem' in r['naturezas'] and not r['internacao']]
    clin = [r for r in lst if r['categoria'] == 'Clínicas e Centros Médicos']
    prof = [r for r in lst if r['categoria'] == CAT_PROF]
    f.secao('A sua rede em números',
            'Tudo o que a Nossa Saúde tem credenciado em %s, somando todos os planos da operadora. '
            'Levantado na rede credenciada oficial em %s.' % (escopo, DATA_LONGA))
    f.stats([(len(hosp), 'Hospitais para internação'),
             (len(lab), 'Laboratórios de análises clínicas'),
             (len(img), 'Centros de diagnóstico por imagem'),
             (len(clin), 'Clínicas e centros médicos'),
             (len(prof), 'Médicos e demais profissionais'),
             (len(lst), 'Prestadores no total')])
    return hosp


def bloco(f, itens, chave_grupo, por_cidade, prof=False, unidade='prestador'):
    """Agrupa por chave_grupo (str) e, se por_cidade, subagrupa por cidade."""
    grupos = collections.OrderedDict()
    for nome, lst in chave_grupo:
        if lst:
            grupos[nome] = lst
    for nome, lst in grupos.items():
        f.grupo(nome, len(lst), unidade)
        f.cabecalho(COLS_PROF if prof else COLS)
        if por_cidade:
            for cid in CIDADES:
                sub = [r for r in lst if r['cidade'] == cid]
                if not sub:
                    continue
                f.subgrupo(cid, len(sub))
                f.cabecalho(COLS_PROF if prof else COLS)
                for i, r in enumerate(sorted(sub, key=lambda x: x['nome_exib'].lower())):
                    linha_prest(f, r, i % 2 == 1, prof)
        else:
            for i, r in enumerate(sorted(lst, key=lambda x: x['nome_exib'].lower())):
                linha_prest(f, r, i % 2 == 1, prof)
        f.y -= 10


def sec_hospitais(f, lst, hosp, por_cidade):
    if not hosp:
        f.secao('Hospitais e pronto-socorro',
                'Não há hospital credenciado nesta cidade. Em urgência e internação, a referência da '
                'região é Ponta Grossa — Santa Casa de Misericórdia, Hospital do Coração Bom Jesus e '
                'Centro Hospitalar São Camilo.')
        return
    f.secao('Hospitais e pronto-socorro',
            'Internação, cirurgia e atendimento de urgência. É por aqui que o cliente pergunta '
            'primeiro — confirme sempre a acomodação prevista no plano (enfermaria ou apartamento).')
    bloco(f, lst, [('Hospitais', hosp)], por_cidade, unidade='hospital')


def sec_exames(f, lst, por_cidade):
    grupos = []
    for nat in EXAMES:
        g = [r for r in lst if nat in r['naturezas']]
        grupos.append((nat, g))
    if not any(g for _, g in grupos):
        return
    f.secao('Exames e diagnóstico',
            'Separados por natureza do exame. Para exame eletivo, procure os laboratórios e centros '
            'de diagnóstico. Os hospitais também realizam esses exames, mas em regra para pacientes '
            'internados e em urgência — o selo "internação" marca esses casos.')
    bloco(f, lst, grupos, por_cidade)


def sec_clinicas(f, lst, por_cidade):
    clin = [r for r in lst if r['categoria'] == 'Clínicas e Centros Médicos']
    if not clin:
        return
    porespec = collections.defaultdict(list)
    for r in clin:
        for e in (r['esp_exib'] or ['Sem especialidade informada']):
            porespec[e].append(r)
    grupos = [(e, porespec[e]) for e in sorted(porespec, key=lambda s: (-len(porespec[s]), s.lower()))]
    f.secao('Clínicas e centros médicos',
            'Consultas e procedimentos ambulatoriais, agrupados por especialidade. Uma clínica com '
            'mais de uma especialidade aparece em cada grupo em que atende.')
    bloco(f, lst, grupos, por_cidade)


def sec_medicos(f, lst, por_cidade):
    prof = [r for r in lst if r['categoria'] == CAT_PROF]
    if not prof:
        return
    porespec = collections.defaultdict(list)
    for r in prof:
        for e in (r['esp_exib'] or ['Sem especialidade informada']):
            porespec[e].append(r)
    grupos = [(e, porespec[e]) for e in sorted(porespec, key=lambda s: (s == 'Médico', s.lower()))]
    f.secao('Médicos e demais profissionais',
            'Profissionais pessoa física credenciados, por especialidade. Quem tem mais de uma '
            'especialidade aparece em cada grupo. O registro no conselho vem na segunda coluna.')
    bloco(f, lst, grupos, por_cidade, prof=True, unidade='profissional')


def sec_final(f, escopo):
    f.secao('Observações e contato',
            'O que vale conferir antes de fechar, e como falar comigo.')
    f.caixa_aviso('Antes de contratar', AVISO)
    f.paragrafo('Todos os planos, uma lista só', SANB, 10.5, NAVY, gap=6)
    f.paragrafo('A Nossa Saúde tem produtos diferentes que usam redes credenciadas diferentes. Este '
                'material soma todos eles: se um prestador aparece aqui, ele é credenciado da '
                'operadora em %s por algum plano. Para saber se ele atende exatamente o plano do '
                'cliente, me chame — eu confiro no portal da operadora e te respondo com o print.'
                % escopo, gap=4)
    f.y -= 8
    f.paragrafo('Fonte', SANB, 10.5, NAVY, gap=6)
    f.paragrafo('Rede Credenciada oficial da %s (CNPJ %s), em prestador.nossasaude.com.br, '
                'consultada em %s.' % (OPERADORA, OPER_CNPJ, DATA_LONGA), gap=4)
    f.y -= 16
    c = f.c
    f.espaco(96)
    c.setFillColor(NAVY); c.rect(ML, f.y - 78, CW, 78, stroke=0, fill=1)
    c.setFillColor(OURO); c.rect(ML, f.y - 78, 3.4, 78, stroke=0, fill=1)
    f.tag_mazza(ML + 22, f.y - 58, 26)
    c.setFillColor(NAVY_CL); c.setFont(SANB, 7.6)
    c.drawString(ML + 130, f.y - 26, CORRETOR_CARGO.upper())
    f.registrar('cargo', ML + 130, f.y - 26, 7.6, '#C9A08F', '#332D2B', 260, )
    c.setFillColor(__import__('reportlab').lib.colors.white); c.setFont(SAN, 11)
    c.drawString(ML + 130, f.y - 42, CORRETOR)
    f.registrar('nome', ML + 130, f.y - 42, 11, '#FFFFFF', '#332D2B', 320)
    c.setFillColor(NAVY_CL); c.setFont(SAN, 9)
    c.drawString(ML + 130, f.y - 58, '%s   ·   %s' % (CORRETOR_TEL, CORRETOR_MAIL))
    f.registrar('contato', ML + 130, f.y - 58, 9, '#C9A08F', '#332D2B', 360)
    f.y -= 92


# ---------------------------------------------------------------- documentos
ASSINATURAS = {}


def pdf_cidade(cid):
    lst = [r for r in ITENS if r['cidade'] == cid]
    nome = 'Nossa Saúde - %s.pdf' % cid
    path = os.path.join(P_CID, nome)
    f = Folha(path, 'Rede credenciada Nossa Saúde — %s' % cid,
              'Rede credenciada Nossa Saúde  —  %s' % cid)
    f.capa(cid, 'Rede Credenciada', 'Nossa Saúde', FONTE_CAPA,
           (CORRETOR, CORRETOR_MAIL, CORRETOR_TEL))
    hosp = sec_numeros(f, lst, cid)
    sec_hospitais(f, lst, hosp, por_cidade=False)
    sec_exames(f, lst, por_cidade=False)
    sec_clinicas(f, lst, por_cidade=False)
    sec_medicos(f, lst, por_cidade=False)
    sec_final(f, cid)
    ASSINATURAS[nome] = f.assinatura
    f.salvar()
    return path, len(lst)


def pdf_regiao():
    nome = 'Nossa Saúde - Campos Gerais.pdf'
    path = os.path.join(P02, nome)
    f = Folha(path, 'Rede credenciada Nossa Saúde — Campos Gerais',
              'Rede credenciada Nossa Saúde  —  Campos Gerais')
    f.capa('Campos Gerais · PR', 'Rede Credenciada', 'Nossa Saúde', FONTE_CAPA,
           (CORRETOR, CORRETOR_MAIL, CORRETOR_TEL))
    hosp = sec_numeros(f, ITENS, 'nas nove cidades dos Campos Gerais')

    # índice das cidades
    f.secao('As nove cidades', 'Quantos prestadores a Nossa Saúde tem credenciado em cada cidade '
                               'atendida na região.')
    f.cabecalho([('Cidade', CW * 0.24), ('Hospitais', CW * 0.13), ('Labs e imagem', CW * 0.15),
                 ('Clínicas', CW * 0.13), ('Profissionais', CW * 0.15), ('Total', CW * 0.20)])
    for i, cid in enumerate(CIDADES):
        l = [r for r in ITENS if r['cidade'] == cid]
        nh = sum(1 for r in l if r['internacao'])
        nl = sum(1 for r in l if r['naturezas'] and not r['internacao'])
        nc = sum(1 for r in l if r['categoria'] == 'Clínicas e Centros Médicos')
        np = sum(1 for r in l if r['categoria'] == CAT_PROF)
        f.linha([cid, str(nh) if nh else '—', str(nl) if nl else '—',
                 str(nc) if nc else '—', str(np) if np else '—', str(len(l))],
                alt=i % 2 == 1, max_linhas=1, cinza_ultima=False)
    f.y -= 10
    f.caixa_aviso('Como a região funciona',
                  'Ponta Grossa concentra a estrutura de alta complexidade: %d dos %d prestadores '
                  'da região, os três hospitais de referência e a maior parte das especialidades. '
                  'Castro, Carambeí, Jaguariaíva e Piraí do Sul não têm hospital credenciado — '
                  'nessas cidades o atendimento local resolve consulta e exame, e a internação é '
                  'em Ponta Grossa.'
                  % (sum(1 for r in ITENS if r['cidade'] == 'Ponta Grossa'), len(ITENS)))

    sec_hospitais(f, ITENS, hosp, por_cidade=True)
    sec_exames(f, ITENS, por_cidade=True)
    sec_clinicas(f, ITENS, por_cidade=True)
    sec_medicos(f, ITENS, por_cidade=True)
    sec_final(f, 'na região')
    ASSINATURAS[nome] = f.assinatura
    f.salvar()
    return path, len(ITENS)


if __name__ == '__main__':
    os.makedirs(P_CID, exist_ok=True)
    for velho in os.listdir(P02):
        if velho.endswith('.pdf'):
            os.remove(os.path.join(P02, velho))
    for velho in os.listdir(P_CID):
        os.remove(os.path.join(P_CID, velho))

    assinaturas = {}
    indice = []
    for cid in CIDADES:
        p, n = pdf_cidade(cid)
        indice.append({'cidade': cid, 'arquivo': 'Nossa Saúde - %s.pdf' % cid,
                       'slug': slug(cid), 'n': n, 'kb': round(os.path.getsize(p) / 1024)})
        print('%-16s %4d prestadores  %6d bytes' % (cid, n, os.path.getsize(p)))
    p, n = pdf_regiao()
    print('%-16s %4d prestadores  %6d bytes' % ('REGIÃO', n, os.path.getsize(p)))

    if os.path.isdir(SITE_ARQ):
        dest = os.path.join(SITE_ARQ, 'cidades')
        shutil.rmtree(dest, ignore_errors=True)
        os.makedirs(dest, exist_ok=True)
        for it in indice:
            shutil.copy2(os.path.join(P_CID, it['arquivo']),
                         os.path.join(dest, it['arquivo']))
        shutil.copy2(p, os.path.join(SITE_ARQ, os.path.basename(p)))
    json.dump(indice, open(os.path.join(AQUI, 'indice_cidades.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump({'padrao': {'nome': CORRETOR, 'cargo': CORRETOR_CARGO,
                          'tel': CORRETOR_TEL, 'mail': CORRETOR_MAIL},
               'marcas': ASSINATURAS},
              open(os.path.join(AQUI, 'assinaturas.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    if os.path.isdir(SITE_ARQ):
        shutil.copy2(os.path.join(AQUI, 'assinaturas.json'),
                     os.path.join(os.path.dirname(SITE_ARQ), 'assinaturas.json'))
