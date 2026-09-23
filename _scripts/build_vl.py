# -*- coding: utf-8 -*-
"""Base da rede do plano VIDA LEVE (Rede Laranja).

Mesma classificação dos outros levantamentos — reaproveita o build_unico, só
troca a pasta de PDFs e a lista de cidades. Cidade sem prestador no plano fica
de fora sozinha.
"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
import parse
import build_unico as BU

PASTA = 'pdfs_vl'
SAIDA = 'dados_vl.json'

CIDADES = {
    'CURITIBA': 'Curitiba', 'SAO JOSE DOS PINHAIS': 'São José dos Pinhais',
    'ARAUCARIA': 'Araucária', 'FAZENDA RIO GRANDE': 'Fazenda Rio Grande',
    'CAMPO LARGO': 'Campo Largo', 'PINHAIS': 'Pinhais', 'COLOMBO': 'Colombo',
    'TIJUCAS DO SUL': 'Tijucas do Sul',
    'CAMPINA GRANDE DO SUL': 'Campina Grande do Sul',
    'PIRAQUARA': 'Piraquara', 'AGUDOS DO SUL': 'Agudos do Sul',
    'BALSA NOVA': 'Balsa Nova', 'CAMPO MAGRO': 'Campo Magro',
    'PARANAGUA': 'Paranaguá', 'ANTONINA': 'Antonina', 'MORRETES': 'Morretes',
    'GUARATUBA': 'Guaratuba', 'MATINHOS': 'Matinhos',
    'PONTAL DO PARANA': 'Pontal do Paraná',
}
# Curitiba, depois a região metropolitana por tamanho, depois o litoral
ORDEM = ['Curitiba', 'São José dos Pinhais', 'Araucária', 'Fazenda Rio Grande',
         'Campo Largo', 'Pinhais', 'Colombo', 'Tijucas do Sul',
         'Campina Grande do Sul', 'Piraquara', 'Agudos do Sul', 'Balsa Nova',
         'Campo Magro',
         'Paranaguá', 'Antonina', 'Morretes', 'Guaratuba', 'Matinhos',
         'Pontal do Paraná']


def main():
    prest = {}
    for f in sorted(os.listdir(PASTA)):
        if not f.startswith('VL__'):
            continue
        cid = CIDADES[f[:-4].split('__')[1].replace('_', ' ')]
        for r in parse.parse(os.path.join(PASTA, f)):
            k = (r['nome'].strip().upper(), r['registro'].strip().upper(), cid)
            if k not in prest:
                prest[k] = BU.normaliza(r, cid)

    itens = list(prest.values())
    cidades = [c for c in ORDEM if any(i['cidade'] == c for i in itens)]
    itens.sort(key=lambda x: (cidades.index(x['cidade']), x['nome_exib'].lower()))
    json.dump({'itens': itens, 'cidades': cidades,
               'exames': [e[0] for e in BU.EXAMES]},
              open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('total:', len(itens), 'em', len(cidades), 'cidades')
    for c in cidades:
        lst = [i for i in itens if i['cidade'] == c]
        print('  %-22s %4d  (hosp %d · exames %d · prof %d)'
              % (c, len(lst),
                 sum(1 for i in lst if i['internacao']),
                 sum(1 for i in lst if i['naturezas'] and not i['internacao']),
                 sum(1 for i in lst if i['categoria'] == 'Profissionais (médicos e demais)')))
    fora = [c for c in ORDEM if c not in cidades]
    if fora:
        print('sem rede no plano:', ', '.join(fora))


if __name__ == '__main__':
    main()
