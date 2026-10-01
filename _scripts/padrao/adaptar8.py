# -*- coding: utf-8 -*-
"""Etapa 8: um plano por região, e não a soma de todos.

Até aqui a página somava todos os planos da operadora. A corretora vende um
plano em cada praça, e cada um usa uma rede diferente:

    Curitiba, RMC e litoral   Vida Leve     Rede Laranja
    Campos Gerais             Vida Nova CG  Rede Coral CG

Nenhum dos dois alcança a região do outro, então somar os planos criava uma
rede que nenhum cliente tem. Aqui some tudo que dizia "somando todos os
planos" e o material passa a responder "o que este plano cobre", que é a
pergunta que o cliente faz. O nome do plano vem do dado, não do texto — o app
troca de região sem recarregar.
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


# a nota acima dos cartões
sub("""             '<p class="nota-familia">Este material soma <b>todos os planos</b> da Nossa '
             'Saúde na região: se o prestador está aqui, ele é credenciado da operadora '
             'naquela cidade por algum plano. Confirme no portal da operadora se ele atende '
             'o plano específico do cliente.</p>')""",
    """             '<p class="nota-familia">Cada região tem aqui <b>o plano que a operadora '
             'vende nela</b>, com a rede daquele plano: <b>Vida Leve</b> (Rede Laranja) em '
             'Curitiba, região metropolitana e litoral; <b>Vida Nova CG</b> (Rede Coral CG) '
             'nos Campos Gerais. Um não atende a praça do outro, e os demais planos da Nossa '
             'Saúde usam outras redes — confirme no portal da operadora antes de contratar.</p>')""")

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
    'no plano da capa.")')

sub("""            '"a Nossa Saúde devolveu na data da capa, somando todos os planos "')""",
    """            '"a Nossa Saúde devolveu na data da capa para este plano "')""")

# o aviso do PDF
sub("""            'var aviso = "Este material soma todos os planos da Nossa Saúde na " +\\n'
            '      "região: se o prestador está aqui, ele é credenciado da operadora " +\\n'
            '      "naquela cidade por algum plano. O D no lugar do visto marca " +\\n'""",
    """            'var aviso = "Esta é a rede do plano da capa, e só dela: os outros " +\\n'
            '      "planos da Nossa Saúde usam outra rede credenciada, e o plano de " +\\n'
            '      "uma praça não atende a praça da outra. O D no lugar do visto marca " +\\n'""")

# e o nome do arquivo diz o plano da região
sub("""            '''var nome = "Nossa Saúde - " + rotuloCidade + ".pdf";''')""",
    """            '''var nome = "Nossa Saúde " + produto.rotulo + " - " + rotuloCidade + ".pdf";''')""")

io.open(ALVO, 'w', encoding='utf-8').write(t)
print('etapa 8: %d trocas' % n)
