# -*- coding: utf-8 -*-
"""Base da rede do plano VIDA NOVA CG (Rede Coral CG), nos Campos Gerais.

É o plano que a operadora vende nas nove cidades dos Campos Gerais — o Vida
Leve, que a corretora comercializa em Curitiba, não tem rede nenhuma aqui.
Os doze planos VIDA NOVA CG usam a mesma rede, então basta filtrar por um
representativo: `VNCGA2301`, código `413168400`.

Mesma classificação dos outros levantamentos; só troca a pasta e as cidades.
"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
import parse
import build_unico as BU

PASTA = 'pdfs_vncg'
SAIDA = 'dados_vncg.json'

CIDADES = {
    'PONTA GROSSA': 'Ponta Grossa', 'TELEMACO BORBA': 'Telêmaco Borba',
    'JAGUARIAIVA': 'Jaguariaíva', 'CASTRO': 'Castro', 'IRATI': 'Irati',
    'PALMEIRA': 'Palmeira', 'CARAMBEI': 'Carambeí',
    'PRUDENTOPOLIS': 'Prudentópolis', 'PIRAI DO SUL': 'Piraí do Sul',
}
ORDEM = ['Ponta Grossa', 'Telêmaco Borba', 'Jaguariaíva', 'Castro', 'Irati',
         'Palmeira', 'Carambeí', 'Prudentópolis', 'Piraí do Sul']


def main():
    prest = {}
    for f in sorted(os.listdir(PASTA)):
        if not f.startswith('VNCG__'):
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


if __name__ == '__main__':
    main()
