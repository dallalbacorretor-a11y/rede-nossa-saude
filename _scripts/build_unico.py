# -*- coding: utf-8 -*-
"""Base unificada: todos os planos da Nossa Saúde tratados como uma rede só, por cidade.

Fonte: os PDFs oficiais 'TODOS OS PLANOS' (filtro de cidade, sem filtro de plano/rede).
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')
import parse
from textutil import titulo

ARQ = {'PONTA_GROSSA': 'Ponta Grossa', 'TELEMACO_BORBA': 'Telêmaco Borba',
       'JAGUARIAIVA': 'Jaguariaíva', 'CASTRO': 'Castro', 'IRATI': 'Irati',
       'PALMEIRA': 'Palmeira', 'CARAMBEI': 'Carambeí', 'PRUDENTOPOLIS': 'Prudentópolis',
       'PIRAI_DO_SUL': 'Piraí do Sul'}
ORDEM = ['Ponta Grossa', 'Telêmaco Borba', 'Jaguariaíva', 'Castro', 'Irati',
         'Palmeira', 'Carambeí', 'Prudentópolis', 'Piraí do Sul']

CHAVES_LAB = ('ANALISE', 'RADIOLOG', 'IMAGEM', 'TOMOGRAF', 'RESSON', 'MAMOGRAF', 'DENSITO',
              'DESINTOM', 'ULTRASSON', 'PATOLOG', 'ENDOSCOP', 'COLONOSCOP', 'ECOCARDIO',
              'ELETROCARDIO', 'AUDIOMETRIA', 'URODINAMICA', 'ERGOMETRIC', 'HOLTER', 'LABORAT',
              'CITOLOG', 'RAIO', 'DIAGNOS')

# natureza do exame -> palavras-chave da especialidade (ordem importa)
EXAMES = [
    ('Análises clínicas e patologia', ('ANALISE', 'PATOLOG', 'CITOLOG', 'CITOPATOLOG',
                                       'ANATOMIA PATOLOGICA', 'LABORATORIO')),
    ('Diagnóstico por imagem',        ('RADIOLOG', 'IMAGEM', 'TOMOGRAF', 'RESSON', 'MAMOGRAF',
                                       'ULTRASSON', 'DENSITO', 'DESINTOM', 'RAIO', 'DOPPLER',
                                       'CINTILOGRAF')),
    ('Endoscopia e procedimentos',    ('ENDOSCOP', 'COLONOSCOP', 'BRONCOSCOP', 'HISTEROSCOP',
                                       'CISTOSCOP')),
    ('Exames funcionais',             ('AUDIOMETRIA', 'ERGOMETRIC', 'ELETROCARDIO', 'ECOCARDIO',
                                       'HOLTER', 'MAPA', 'ESPIROMETRIA', 'URODINAMICA',
                                       'ELETROENCEFALO', 'ELETRONEURO', 'IMPEDANCIOMETRIA',
                                       'POLISSONOGRAF')),
]

HOSP_INTERNA = {'Hospital geral', 'Hospital e Maternidade', 'Hospital Especializado',
                'Hospital Ortopedico', 'Hospital Psiquiatrico', 'Hospital dia'}
PS = {'Pronto atendimento', 'Pronto Atendimento'}


def limpa_esp(e):
    return re.sub(r'\s*-\s*RQE.*$', '', e).strip()


def natureza(esp):
    up = esp.upper()
    for nome, chaves in EXAMES:
        if any(k in up for k in chaves):
            return nome
    return None


def normaliza(r, cidade):
    es, vis = [], set()
    for e in r['especialidades']:
        e = limpa_esp(e)
        if e and e not in vis:
            vis.add(e); es.append(e)
    cat = parse.categoria(r['tipo'])
    if cat == 'Laboratórios e Imagem' and r['tipo'] in ('Serviço de diagnose e terapia',
                                                        'Clínica / Laboratório'):
        if not any(k in e.upper() for e in es for k in CHAVES_LAB):
            cat = 'Clínicas e Centros Médicos'
    cc, vis = [], set()
    for m in r.get('corpo_clinico', []):
        n = titulo(m['nome'])
        if n.lower() not in vis:
            vis.add(n.lower()); cc.append({'nome': n, 'registro': m['registro']})
    ends = [{'tel': e['tel'], 'logradouro': titulo(e['logradouro']),
             'bairro': titulo(e['bairro']), 'cep': e['cep']} for e in r['enderecos']]
    esp_exib = [titulo(e) for e in es]
    return {
        'cidade': cidade, 'categoria': cat, 'tipo': r['tipo'],
        'tipo_exib': titulo(r['tipo']),
        'nome_exib': titulo(r['fantasia'] or r['nome']),
        'razao': titulo(r['nome']),
        'cnpj': r['registro'][5:].strip() if r['registro'].startswith('CNPJ') else '',
        'conselho': '' if r['registro'].startswith('CNPJ') else r['registro'],
        'especialidades': es, 'esp_exib': esp_exib,
        'naturezas': sorted({n for n in (natureza(e) for e in esp_exib) if n},
                            key=lambda x: [e[0] for e in EXAMES].index(x)),
        'internacao': r['tipo'] in HOSP_INTERNA,
        'pronto_socorro': r['tipo'] in PS or any('URGENC' in e.upper() or 'EMERGENC' in e.upper()
                                                 for e in es),
        'enderecos': ends, 'corpo_clinico': cc,
    }


def main():
    prest = {}
    for f in sorted(os.listdir('pdfs')):
        if not f.startswith('TODOS__'):
            continue
        cid = ARQ[f[:-4].split('__')[1]]
        for r in parse.parse('pdfs/' + f):
            k = (r['nome'].strip().upper(), r['registro'].strip().upper(), cid)
            if k not in prest:
                prest[k] = normaliza(r, cid)
        print('%-16s ok' % cid)

    itens = list(prest.values())
    itens.sort(key=lambda x: (ORDEM.index(x['cidade']), x['nome_exib'].lower()))
    json.dump({'itens': itens, 'cidades': ORDEM, 'exames': [e[0] for e in EXAMES]},
              open('dados_unico.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('\ntotal:', len(itens))
    for c in ORDEM:
        lst = [i for i in itens if i['cidade'] == c]
        print('  %-16s %4d  (hosp %d · ps %d · exames %d · prof %d)'
              % (c, len(lst),
                 sum(1 for i in lst if i['internacao']),
                 sum(1 for i in lst if i['pronto_socorro']),
                 sum(1 for i in lst if i['naturezas'] and not i['internacao']),
                 sum(1 for i in lst if i['categoria'] == 'Profissionais (médicos e demais)')))
    print('\nespecialidades sem natureza de exame reconhecida (amostra):')
    todas = collections.Counter(e for i in itens for e in i['esp_exib'] if not natureza(e))
    print('  ', ', '.join(k for k, _ in todas.most_common(18)))


if __name__ == '__main__':
    main()
