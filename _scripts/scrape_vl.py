# -*- coding: utf-8 -*-
"""Baixa a rede do plano VIDA LEVE, cidade a cidade.

Todos os planos VIDA LEVE (e VIDA LEVE LITORAL), individual, empresarial e por
adesão, usam **uma rede só: a REDE LARANJA** (código 68287168). Então basta
filtrar por um plano representativo — aqui o VL1001 Individual Familiar.

Filtrar por `plano` traz um pouco mais que filtrar por `tipoRede` (em Curitiba,
235 contra 233), por isso o filtro daqui é o plano.

Cidades: as da região metropolitana onde a operadora tem rede, mais o litoral
inteiro. As que voltarem vazias ficam de fora do material — a Rede Laranja não
chega aos Campos Gerais, por exemplo.
"""
import os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from scrape import sess, get_pdf

PLANO = '20338136'          # VL1001 - VIDA LEVE - Individual Familiar
OUT = 'pdfs_vl'
os.makedirs(OUT, exist_ok=True)

CIDADES = [
    'CURITIBA', 'SAO JOSE DOS PINHAIS', 'ARAUCARIA', 'FAZENDA RIO GRANDE',
    'CAMPO LARGO', 'PINHAIS', 'COLOMBO', 'TIJUCAS DO SUL',
    'CAMPINA GRANDE DO SUL', 'LAPA', 'RIO NEGRO', 'PIRAQUARA',
    'AGUDOS DO SUL', 'BALSA NOVA', 'DOUTOR ULYSSES', 'QUATRO BARRAS',
    'ALMIRANTE TAMANDARE', 'CAMPO MAGRO', 'CONTENDA', 'MANDIRITUBA',
    'SAO JOSE DOS PINHAIS',
    # litoral
    'PARANAGUA', 'ANTONINA', 'MORRETES', 'GUARATUBA', 'MATINHOS',
    'PONTAL DO PARANA', 'GUARAQUECABA',
]

if __name__ == '__main__':
    s = sess()
    for c in dict.fromkeys(CIDADES):
        fn = '%s/VL__%s.pdf' % (OUT, c.replace(' ', '_'))
        if os.path.exists(fn) and os.path.getsize(fn) > 2000:
            print('%-24s ja baixado' % c)
            continue
        b = None
        for _ in range(3):
            try:
                t0 = time.time()
                b = get_pdf(s, estado='PR', cidade=c, plano=PLANO)
                if b and b[:4] == b'%PDF':
                    break
            except Exception as e:
                print('   erro', c, e)
            time.sleep(2)
            b, s = None, sess()
        if b:
            open(fn, 'wb').write(b)
            print('%-24s %7d bytes  %5.1fs' % (c, len(b), time.time() - t0))
        else:
            print('%-24s VAZIO / FALHOU' % c)
    print('fim')
