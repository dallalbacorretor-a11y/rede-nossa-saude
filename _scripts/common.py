# -*- coding: utf-8 -*-
"""Definições compartilhadas do estudo Nossa Saúde — Campos Gerais (todas as redes)."""
import json, os, re, unicodedata

BASE = r'C:\Users\Dalla\OneDrive\Desktop\NOSSA SAÚDE\ESTUDO CAMPOS GERAIS'
P01 = os.path.join(BASE, '01 - REDE CREDENCIADA', 'Nossa Saúde')
P02 = os.path.join(BASE, '02 - COMPARATIVOS DE REDE')
P03 = os.path.join(BASE, '03 - MATERIAIS ORIGINAIS (PDFs das operadoras)', 'Nossa Saúde')
PSITE = os.path.join(BASE, '04 - SITE')

OPERADORA = 'Nossa Saúde'
OPER_CNPJ = '02.862.447/0001-03'
REGIAO = 'Campos Gerais / PR'
CORRETOR = 'Alan Vinicius Dall Alba'
CORRETOR_TEL = '(41) 99547-6715'
CORRETOR_WHATS = '5541995476715'
CORRETOR_MAIL = 'alan.vinicius@mazzabroker.com.br'
DATA_REF = '10/09/2026'

# rótulo curto e cor de cada rede credenciada presente nos Campos Gerais
REDE_INFO = {
    '284223248': {'curto': 'Coral',    'cor': '#C2410C',
                  'desc': 'Rede regional ampla — a maior nos Campos Gerais. Usada pela maior parte '
                          'dos produtos da operadora que atendem a região.'},
    '379593581': {'curto': 'Coral CG', 'cor': '#0F766E',
                  'desc': 'Rede específica dos Campos Gerais, usada pela linha VIDA NOVA CG. '
                          'Praticamente igual à Coral, com poucas diferenças pontuais.'},
    '68808209':  {'curto': 'Azul',     'cor': '#1D4ED8',
                  'desc': 'Rede enxuta: nos Campos Gerais só alcança Ponta Grossa (e um ponto em '
                          'Castro). Cliente de outra cidade não tem atendimento local.'},
}

CIDADES = ['Ponta Grossa', 'Telêmaco Borba', 'Jaguariaíva', 'Castro', 'Irati',
           'Palmeira', 'Carambeí', 'Prudentópolis', 'Piraí do Sul']

CATS = ['Hospitais e Pronto-Socorro', 'Clínicas e Centros Médicos',
        'Laboratórios e Imagem', 'Profissionais (médicos e demais)']

CAT_CURTA = {'Hospitais e Pronto-Socorro': 'Hospitais',
             'Clínicas e Centros Médicos': 'Clínicas',
             'Laboratórios e Imagem': 'Labs e Imagem',
             'Profissionais (médicos e demais)': 'Profissionais'}

CAT_COR = {'Hospitais e Pronto-Socorro': '#B3261E',
           'Clínicas e Centros Médicos': '#1D4E89',
           'Laboratórios e Imagem': '#1F7A5A',
           'Profissionais (médicos e demais)': '#6B4E9B'}

NAVY = '#12233F'
NAVY2 = '#1D3557'
LARANJA = '#EE6B22'
LARANJA_CLARO = '#FDEFE5'
DOURADO = '#C8A24A'
CINZA = '#6B7280'
CINZA_CLARO = '#F4F5F7'
BORDA = '#DCDFE4'

AVISO = ('A rede credenciada é definida e alterada exclusivamente pela operadora. '
         'Confirme no portal da Nossa Saúde antes de contratar ou de utilizar o serviço.')

FONTE = ('Fonte: Rede Credenciada oficial da Nossa Saúde (prestador.nossasaude.com.br), '
         'consulta em ' + DATA_REF + '.')

_AQUI = os.path.dirname(os.path.abspath(__file__))


def carregar(path=None):
    d = json.load(open(path or os.path.join(_AQUI, 'dados_multi.json'), encoding='utf-8'))
    for r in d['redes']:
        r.update(REDE_INFO.get(r['id'], {'curto': r['nome'].replace('REDE ', '').title(),
                                         'cor': '#555555', 'desc': ''}))
    d['redes'].sort(key=lambda r: -sum(1 for i in d['itens'] if r['id'] in i['redes']))
    return d


def redes_amplas(d, minimo=8):
    """Redes que alcancam quase todas as cidades (as comparaveis entre si)."""
    out = []
    for r in d['redes']:
        n = len({i['cidade'] for i in d['itens'] if r['id'] in i['redes']})
        if n >= minimo:
            out.append(r)
    return out or d['redes']


def cidades_da_rede(d, rid):
    return [c for c in CIDADES if any(i['cidade'] == c and rid in i['redes'] for i in d['itens'])]


def ordena(itens):
    return sorted(itens, key=lambda r: (CATS.index(r['categoria']), r['nome_exib'].lower()))


def tels(rec):
    out = []
    for e in rec['enderecos']:
        for t in re.split(r'\s*/\s*', e.get('tel', '') or ''):
            t = t.strip()
            if t and t not in out:
                out.append(t)
    return out


def enderecos_txt(rec):
    out = []
    for e in rec['enderecos']:
        p = e['logradouro']
        if e['bairro']:
            p += ' — ' + e['bairro']
        if e['cep']:
            p += ' — CEP ' + e['cep']
        if p and p not in out:
            out.append(p)
    return out


def slug(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-').lower()
