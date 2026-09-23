# -*- coding: utf-8 -*-
"""Etapa 6: o nome do arquivo PDF.

O app da Amil põe o plano no nome do arquivo, o que faz sentido lá (são vinte
planos) e nenhum aqui — há um produto só, e o nome saía repetido:
"Rede Nossa Saude Nossa Saúde todos os planos - Curitiba, Rmc e Paranaguá.pdf".
O cliente precisa receber "Nossa Saúde - Ponta Grossa.pdf".
"""
import io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
AQUI = os.path.dirname(os.path.abspath(__file__))
ALVO = os.path.join(AQUI, 'montar_site.py')
t = io.open(ALVO, encoding='utf-8').read()
n = 0

ASPAS = chr(39) * 3   # o código gerado usa ''' para blocos de JS


def sub(de, para, vezes=1):
    global t, n
    if t.count(de) != vezes:
        raise SystemExit('esperava %d de %r, achei %d' % (vezes, de[:110], t.count(de)))
    t = t.replace(de, para)
    n += vezes


NOVO = '\n'.join([
    '# o nome do arquivo e o que o cliente ve na conversa: operadora e recorte',
    'app = troca(app,',
    '            ' + ASPAS + 'var nome = "Rede Amil " +',
    '               (comparativo',
    '                 ? (nomes.length <= 3 ? nomes.join(" x ")',
    '                                      : nomes.length + " planos")',
    '                 : nomes[0]) +',
    '               " - " + rotuloCidade + ".pdf";' + ASPAS + ',',
    '            ' + ASPAS + 'var nome = "Nossa Saúde - " + rotuloCidade + ".pdf";'
    + ASPAS + ')',
    '',
    '# a cidade vem em caixa alta da operadora e precisa virar Título; o nome da',
    '# região já vem certo e não pode virar "Curitiba, Rmc e Paranaguá"',
    'app = troca(app,',
    '            ' + ASPAS + 'var rotuloCidade = bruto.replace(' + ASPAS + ',',
    '            ' + ASPAS + 'var rotuloCidade = bruto !== bruto.toUpperCase() ? bruto',
    '      : bruto.replace(' + ASPAS + ')',
])

sub('app = troca(app, ' + chr(39) + 'var nome = "Rede Amil " +' + chr(39)
    + ', ' + chr(39) + 'var nome = "Rede Nossa Saude " +' + chr(39) + ')', NOVO)

io.open(ALVO, 'w', encoding='utf-8').write(t)
print('etapa 6: %d trocas' % n)
