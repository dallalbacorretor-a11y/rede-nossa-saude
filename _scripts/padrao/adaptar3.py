# -*- coding: utf-8 -*-
"""Etapa 3: textos, cores do PDF e o que não se aplica à Nossa Saúde."""
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
AQUI = os.path.dirname(os.path.abspath(__file__))
ALVO = os.path.join(AQUI, 'montar_site.py')
t = io.open(ALVO, encoding='utf-8').read()
n = 0


def sub(de, para, vezes=1):
    global t, n
    if t.count(de) != vezes:
        raise SystemExit('esperava %d de %r, achei %d' % (vezes, de[:110], t.count(de)))
    t = t.replace(de, para)
    n += vezes


# ------------------------------------------------ direcionamento não existe aqui
# A Nossa Saúde não publica hospital liberado só por encaminhamento, então o
# "D" no lugar do visto seria uma legenda para algo que nunca aparece.
ini = t.index('# ---------------------------------------------------- direcionamento interno')
fim = t.index('# Por ultimo, o que sobrou de "=== Hospitais"')
t = t[:ini] + t[fim:]
n += 1

# ---------------------------------------------------------------- textos
sub('"Rede da Paraná Clínicas em "', '"Rede da Nossa Saúde em "')
sub('"Levantado na busca oficial de rede credenciada da Paraná Clínicas.")',
    '"Levantado na rede credenciada oficial da Nossa Saúde, somando todos os planos.")')
sub('"a Paraná Clínicas devolveu na data da capa, para os planos "',
    '"a Nossa Saúde devolveu na data da capa, somando todos os planos "')
sub('app = app.replace("Confirme no portal da Amil", "Confirme no portal da Paraná Clínicas")',
    'app = app.replace("Confirme no portal da Amil", "Confirme no portal da Nossa Saúde")')
sub('("Parana Clinicas " + nA + " x " + nB + " - " + onde + ".pdf")',
    '("Nossa Saude " + nA + " x " + nB + " - " + onde + ".pdf")')
sub('\'var nome = "Rede Parana Clinicas " +\'', '\'var nome = "Rede Nossa Saude " +\'')
sub('"da Paraná Clínicas apresentava na data da capa e não substitui a consulta ao "',
    '"da Nossa Saúde apresentava na data da capa e não substitui a consulta ao "')
sub('"operadora. Este documento é o retrato do que a busca oficial de rede "',
    '"operadora. Este documento é o retrato do que a rede credenciada oficial "')

# um produto só: o aviso sobre QC/QP não se aplica
sub("""            'var aviso = "Cada plano deste material representa uma rede: enfermaria (QC) " +\\n'
            '      "e apartamento (QP) compartilham a mesma rede credenciada. " +')""",
    """            'var aviso = "Este material soma todos os planos da Nossa Saúde na " +\\n'
            '      "região: se o prestador está aqui, ele é credenciado da operadora " +\\n'
            '      "naquela cidade por algum plano. " +')""")

# comentários que ainda citam a outra operadora
t = t.replace('a busca da Parana Clinicas e por cidade', 'a busca da Nossa Saude e por cidade')
t = t.replace('# mapa: a rede e so a regiao de Curitiba - o retangulo do Parana inteiro',
              '# mapa: a rede e so os Campos Gerais - o retangulo do Parana inteiro')
t = t.replace('# A Parana Clinicas devolve o campo de acreditacoes VAZIO em todos os',
              '# A Nossa Saude nao publica acreditacao de prestador, entao a marca ACRED.')
t = t.replace('# prestadores, entao a marca ACRED. nunca apareceria - prometer uma legenda que',
              '# nunca apareceria - prometer uma legenda que')
t = t.replace('# proprio; os CIM tambem, porque sao o diferencial da operadora.',
              '# proprio.')

# --------------------------------------------------------- cores do PDF
sub("'cor: produto.cor || aux.COR_LINHA[produto.linha] || \"#8e0e28\",'",
    "'cor: produto.cor || aux.COR_LINHA[produto.linha] || \"#332d2b\",'")
sub("'cor: (prodA && prodA.cor) || \"#8e0e28\",'",
    "'cor: (prodA && prodA.cor) || \"#332d2b\",'")
sub("""lib = troca(lib, 'var NAVY = "#0d2a4f", NAVY_MEIO = "#20456f", OURO = "#9a7513",',
            'var NAVY = "#8e0e28", NAVY_MEIO = "#a81b39", OURO = "#9a7513",')""",
    """lib = troca(lib, 'var NAVY = "#0d2a4f", NAVY_MEIO = "#20456f", OURO = "#9a7513",',
            'var NAVY = "#332d2b", NAVY_MEIO = "#4c4441", OURO = "#9a7513",')""")
sub("""            'var COR_LINHA = { "Paraná Clínicas": "#8e0e28" };')""",
    """            'var COR_LINHA = { "Nossa Saúde": "#e6411c" };')""")
sub("""lib = troca(lib, '"Rede Credenciada Amil"', '"Rede Credenciada Paraná Clínicas"')""",
    """lib = troca(lib, '"Rede Credenciada Amil"', '"Rede Credenciada Nossa Saúde"')""")
sub("""lib = troca(lib, '"Levantado na busca avançada oficial da Amil em "',
            '"Levantado na busca oficial de rede credenciada da Paraná Clínicas em "')""",
    """lib = troca(lib, '"Levantado na busca avançada oficial da Amil em "',
            '"Levantado na rede credenciada oficial da Nossa Saúde em "')""")
sub("""lib = troca(lib, '"Rede credenciada Amil " +', '"Rede credenciada Paraná Clínicas " +')""",
    """# o produto ja se chama "Nossa Saude": repetir a operadora antes dele
# deixava o rodape com "Rede credenciada Nossa Saude Nossa Saude todos os planos"
lib = troca(lib, '"Rede credenciada Amil " +', '"Rede credenciada " +')""")
sub("""lib = lib.replace('RISCO = "#e4e9f0", ZEBRA = "#f7f9fc"',
                  'RISCO = "#eee2e5", ZEBRA = "#fdf9fa"')""",
    """lib = lib.replace('RISCO = "#e4e9f0", ZEBRA = "#f7f9fc"',
                  'RISCO = "#e6e1dd", ZEBRA = "#fdf9f6"')""")
sub("""lib = lib.replace('"#cfe0f5"', '"#f2d6dd"').replace('"#9fb8d8"', '"#e0a9b6"')
lib = lib.replace('"#c7d8ee"', '"#f4dde3"')
lib = lib.replace('OURO_CLARO = "#e3c46a"', 'OURO_CLARO = "#edc97e"')""",
    """lib = lib.replace('"#cfe0f5"', '"#f7ddcb"').replace('"#9fb8d8"', '"#e0b193"')
lib = lib.replace('"#c7d8ee"', '"#f8e3d5"')
lib = lib.replace('OURO_CLARO = "#e3c46a"', 'OURO_CLARO = "#e8c87d"')""")

# a linha morta do replace condicional que a PC deixou para tras
t = t.replace("""lib = troca(lib, 'var RISCO = "#e4e9f0", ZEBRA = "#f7f9fc",',
            'var RISCO = "#eee2e5", ZEBRA = "#fdf8f9",', 0) if False else lib
""", '')

# aviso de sobra: o app agora e da Nossa Saude
t = t.replace('print("AVISO: ainda ha mencoes a Amil no app (provavelmente comentarios):", len(sobrou))',
              'print("AVISO: ainda ha mencoes a Amil no app (provavelmente comentarios):", len(sobrou))')

io.open(ALVO, 'w', encoding='utf-8').write(t)
sobra = len(re.findall(r'Paran[aá] Cl[ií]nicas|Parana Clinicas', t))
print('etapa 3: %d trocas | mencoes restantes a Parana Clinicas: %d' % (n, sobra))
