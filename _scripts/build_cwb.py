# -*- coding: utf-8 -*-
"""Base da rede em Curitiba, região metropolitana e Paranaguá.

Mesma classificação dos Campos Gerais — reaproveita o build_unico, só troca a
pasta de PDFs e a lista de cidades.
"""
import os, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')
import parse
import build_unico as BU

PASTA = 'pdfs_cwb'
SAIDA = 'dados_cwb.json'

# Curitiba e os municípios da RMC onde a operadora tem rede, mais Paranaguá.
CIDADES = {
    'CURITIBA': 'Curitiba',
    'SAO JOSE DOS PINHAIS': 'São José dos Pinhais',
    'ARAUCARIA': 'Araucária',
    'FAZENDA RIO GRANDE': 'Fazenda Rio Grande',
    'CAMPO LARGO': 'Campo Largo',
    'PINHAIS': 'Pinhais',
    'COLOMBO': 'Colombo',
    'TIJUCAS DO SUL': 'Tijucas do Sul',
    'CAMPINA GRANDE DO SUL': 'Campina Grande do Sul',
    'LAPA': 'Lapa',
    'RIO NEGRO': 'Rio Negro',
    'PIRAQUARA': 'Piraquara',
    'AGUDOS DO SUL': 'Agudos do Sul',
    'BALSA NOVA': 'Balsa Nova',
    'DOUTOR ULYSSES': 'Doutor Ulysses',
    'PARANAGUA': 'Paranaguá',
}
# Ordem de exibição: Curitiba primeiro, depois a RMC por tamanho, Paranaguá no fim
ORDEM = ['Curitiba', 'São José dos Pinhais', 'Paranaguá', 'Araucária',
         'Fazenda Rio Grande', 'Campo Largo', 'Pinhais', 'Colombo',
         'Tijucas do Sul', 'Campina Grande do Sul', 'Lapa', 'Rio Negro',
         'Piraquara', 'Agudos do Sul', 'Balsa Nova', 'Doutor Ulysses']


def main():
    prest = {}
    for f in sorted(os.listdir(PASTA)):
        if not f.startswith('TODOS__'):
            continue
        cid = CIDADES[f[:-4].split('__')[1].replace('_', ' ')]
        for r in parse.parse(os.path.join(PASTA, f)):
            k = (r['nome'].strip().upper(), r['registro'].strip().upper(), cid)
            if k not in prest:
                prest[k] = BU.normaliza(r, cid)
        print('%-24s ok' % cid)

    itens = list(prest.values())
    itens.sort(key=lambda x: (ORDEM.index(x['cidade']), x['nome_exib'].lower()))
    json.dump({'itens': itens, 'cidades': ORDEM, 'exames': [e[0] for e in BU.EXAMES]},
              open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('\ntotal:', len(itens))
    for c in ORDEM:
        lst = [i for i in itens if i['cidade'] == c]
        print('  %-22s %4d  (hosp %d · exames %d · prof %d)'
              % (c, len(lst),
                 sum(1 for i in lst if i['internacao']),
                 sum(1 for i in lst if i['naturezas'] and not i['internacao']),
                 sum(1 for i in lst if i['categoria'] == 'Profissionais (médicos e demais)')))


if __name__ == '__main__':
    main()
