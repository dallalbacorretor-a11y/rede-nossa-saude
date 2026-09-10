# -*- coding: utf-8 -*-
"""Monta a base multi-rede: prestadores das 9 cidades dos Campos Gerais, por rede credenciada."""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')
import parse
from textutil import titulo

CIDADES_ALVO = {
    'PONTA GROSSA': 'Ponta Grossa', 'CASTRO': 'Castro', 'CARAMBEI': 'Carambeí',
    'PALMEIRA': 'Palmeira', 'TELEMACO BORBA': 'Telêmaco Borba', 'JAGUARIAIVA': 'Jaguariaíva',
    'PIRAI DO SUL': 'Piraí do Sul', 'PRUDENTOPOLIS': 'Prudentópolis', 'IRATI': 'Irati',
}
ORDEM = ['Ponta Grossa', 'Telêmaco Borba', 'Jaguariaíva', 'Castro', 'Irati',
         'Palmeira', 'Carambeí', 'Prudentópolis', 'Piraí do Sul']

CHAVES_LAB = ('ANALISE', 'RADIOLOG', 'IMAGEM', 'TOMOGRAF', 'RESSON', 'MAMOGRAF', 'DENSITO',
              'DESINTOM', 'ULTRASSON', 'PATOLOG', 'ENDOSCOP', 'COLONOSCOP', 'ECOCARDIO',
              'ELETROCARDIO', 'AUDIOMETRIA', 'URODINAMICA', 'ERGOMETRIC', 'HOLTER', 'LABORAT',
              'CITOLOG', 'RAIO', 'DIAGNOS')


def limpa_esp(e):
    return re.sub(r'\s*-\s*RQE.*$', '', e).strip()


def chave(r):
    """Identidade do prestador entre redes."""
    return (r['nome'].strip().upper(), r['registro'].strip().upper())


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
    ends = []
    for e in r['enderecos']:
        ends.append({'tel': e['tel'], 'logradouro': titulo(e['logradouro']),
                     'bairro': titulo(e['bairro']), 'cep': e['cep']})
    return {
        'cidade': CIDADES_ALVO[cidade.upper()],
        'categoria': cat, 'tipo': r['tipo'],
        'nome_exib': titulo(r['fantasia'] or r['nome']),
        'razao': titulo(r['nome']),
        'cnpj': r['registro'][5:].strip() if r['registro'].startswith('CNPJ') else '',
        'conselho': '' if r['registro'].startswith('CNPJ') else r['registro'],
        'especialidades': es, 'esp_exib': [titulo(e) for e in es],
        'enderecos': ends, 'corpo_clinico': cc,
    }


def main():
    cat = json.load(open('catalogo.json', encoding='utf-8'))
    pr = json.load(open('planos_redes.json', encoding='utf-8'))
    nome_rede = dict(cat['redes'])

    # prestadores por (chave, cidade) -> registro; e conjunto de redes
    prest = {}
    redes_com_dados = []
    for f in sorted(os.listdir('pdfs_cg')):
        rid, cidarq = f[:-4].split('__')
        cid = cidarq.replace('_', ' ')
        recs = parse.parse('pdfs_cg/' + f)
        for r in recs:
            k = chave(r) + (cid,)
            if k not in prest:
                prest[k] = normaliza(r, cid)
                prest[k]['redes'] = []
            if rid not in prest[k]['redes']:
                prest[k]['redes'].append(rid)
        if recs:
            redes_com_dados.append(rid)
        print('%-16s %-16s %4d prestadores' % (nome_rede.get(rid, rid), cid, len(recs)))

    itens = list(prest.values())
    redes_usadas = sorted({r for i in itens for r in i['redes']}, key=lambda x: nome_rede.get(x, x))

    # planos por rede (só as redes presentes nas 9 cidades)
    planos_por_rede = collections.defaultdict(list)
    for pid, d in pr['mapa'].items():
        for rid, _ in d['redes']:
            planos_por_rede[rid].append({'id': pid, 'txt': d['plano']})

    json.dump({
        'itens': itens,
        'redes': [{'id': r, 'nome': nome_rede.get(r, r),
                   'planos': sorted(planos_por_rede.get(r, []), key=lambda p: p['txt'])}
                  for r in redes_usadas],
        'cidades': ORDEM,
    }, open('dados_multi.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('\nredes presentes nos Campos Gerais: %d' % len(redes_usadas))
    for r in redes_usadas:
        n = sum(1 for i in itens if r in i['redes'])
        print('  %-34s %4d prestadores  · %d planos' % (nome_rede.get(r, r), n, len(planos_por_rede.get(r, []))))
    print('\nprestadores distintos (prestador x cidade): %d' % len(itens))
    for c in ORDEM:
        print('  %-16s %4d' % (c, sum(1 for i in itens if i['cidade'] == c)))


if __name__ == '__main__':
    main()
