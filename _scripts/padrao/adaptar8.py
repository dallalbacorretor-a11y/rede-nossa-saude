# -*- coding: utf-8 -*-
"""Etapa 8: o material passa a ser de um plano só — o VIDA LEVE.

Até aqui a página somava todos os planos da operadora. A corretora comercializa
o **Vida Leve**, que usa uma rede só (a REDE LARANJA) e tem um recorte
geográfico próprio: Curitiba, região metropolitana e litoral — nos Campos
Gerais esse plano não tem rede nenhuma.

Então some tudo que dizia "somando todos os planos": o material agora responde
"o que o Vida Leve cobre", que é a pergunta que o cliente faz.
"""
import io, os, sys
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


# o nome do plano no título, que é a primeira coisa que o cliente lê
sub("""             '<h1>Rede credenciada <em>Nossa Saúde</em> — '
             '<span id="tituloEstado">Campos Gerais</span></h1>')""",
    """             '<h1>Rede credenciada <em>Nossa Saúde</em> <b>Vida Leve</b> — '
             '<span id="tituloEstado">Curitiba, RMC e Litoral</span></h1>')""")

sub('             "<title>Rede credenciada Nossa Saúde — Paraná</title>")',
    '             "<title>Rede credenciada Nossa Saúde Vida Leve</title>")')

# a nota acima dos cartões
sub("""             '<p class="nota-familia">Este material soma <b>todos os planos</b> da Nossa '
             'Saúde na região: se o prestador está aqui, ele é credenciado da operadora '
             'naquela cidade por algum plano. Confirme no portal da operadora se ele atende '
             'o plano específico do cliente.</p>')""",
    """             '<p class="nota-familia">Esta é a rede do plano <b>Vida Leve</b> da Nossa '
             'Saúde — a Rede Laranja, a mesma no individual, no empresarial e na adesão. '
             'Os outros planos da operadora usam outra rede, e nos Campos Gerais o Vida Leve '
             'não tem rede credenciada. Confirme no portal da operadora antes de contratar.</p>')""")

# a etapa 7 pendura a legenda do "D" no fim dessa nota — o texto mudou
sub('\n'.join([
    '             "o plano específico do cliente.</p>",',
    '             "o plano específico do cliente. <b>D</b> na coluna do plano é "',
]), '\n'.join([
    '             "antes de contratar.</p>",',
    '             "antes de contratar. <b>D</b> na coluna do plano é "',
]))

# a linha de origem, na capa do PDF
sub('                  "Levantado na rede credenciada oficial da Nossa Saúde, '
    'somando todos os planos.")',
    '                  "Levantado na rede credenciada oficial da Nossa Saúde, '
    'no plano Vida Leve.")')

sub("""            '"a Nossa Saúde devolveu na data da capa, somando todos os planos "')""",
    """            '"a Nossa Saúde devolveu na data da capa para o plano Vida Leve "')""")

# o aviso do PDF
sub("""            'var aviso = "Este material soma todos os planos da Nossa Saúde na " +\\n'
            '      "região: se o prestador está aqui, ele é credenciado da operadora " +\\n'
            '      "naquela cidade por algum plano. O D no lugar do visto marca " +\\n'""",
    """            'var aviso = "Esta é a rede do plano Vida Leve da Nossa Saúde — a Rede " +\\n'
            '      "Laranja, a mesma no individual, no empresarial e na adesão. Os " +\\n'
            '      "outros planos da operadora usam outra rede. O D no lugar do visto marca " +\\n'""")

# e o nome do arquivo passa a dizer o plano
sub("""            '''var nome = "Nossa Saúde - " + rotuloCidade + ".pdf";''')""",
    """            '''var nome = "Nossa Saúde Vida Leve - " + rotuloCidade + ".pdf";''')""")

io.open(ALVO, 'w', encoding='utf-8').write(t)
print('etapa 8: %d trocas' % n)
