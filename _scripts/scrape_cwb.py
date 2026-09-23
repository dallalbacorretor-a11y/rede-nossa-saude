# -*- coding: utf-8 -*-
"""Baixa a rede da Nossa Saúde em Curitiba, região metropolitana e Paranaguá.

Um PDF oficial por cidade, sem filtro de plano — mesmo caminho do estudo dos
Campos Gerais. Retoma de onde parou.
"""
import os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from scrape import sess, get_pdf

OUT = 'pdfs_cwb'
os.makedirs(OUT, exist_ok=True)

# Municípios da RMC onde a operadora tem rede (conferido no PDF do Paraná
# inteiro), mais Paranaguá.
CIDADES = [
    'CURITIBA', 'SAO JOSE DOS PINHAIS', 'ARAUCARIA', 'FAZENDA RIO GRANDE',
    'CAMPO LARGO', 'PINHAIS', 'COLOMBO', 'TIJUCAS DO SUL',
    'CAMPINA GRANDE DO SUL', 'LAPA', 'RIO NEGRO', 'PIRAQUARA',
    'AGUDOS DO SUL', 'BALSA NOVA', 'DOUTOR ULYSSES',
    'PARANAGUA',
]

if __name__ == '__main__':
    s = sess()
    for c in CIDADES:
        fn = '%s/TODOS__%s.pdf' % (OUT, c.replace(' ', '_'))
        if os.path.exists(fn) and os.path.getsize(fn) > 2000:
            print('%-24s ja baixado' % c)
            continue
        b = None
        for tent in range(3):
            try:
                t0 = time.time()
                b = get_pdf(s, estado='PR', cidade=c)
                if b and b[:4] == b'%PDF':
                    break
            except Exception as e:
                print('   erro', c, e)
            time.sleep(2)
            b = None
            s = sess()
        if b:
            open(fn, 'wb').write(b)
            print('%-24s %7d bytes  %5.1fs' % (c, len(b), time.time() - t0))
        else:
            print('%-24s VAZIO / FALHOU' % c)
    print('fim')
