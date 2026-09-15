# -*- coding: utf-8 -*-
"""Deriva o montar_site.py da Nossa Saúde a partir do da Paraná Clínicas.

A Paraná Clínicas já tinha feito o caminho Amil -> outra operadora, inclusive a
parte chata (fazer o app confiar nas categorias que vêm no dado). Reaproveitar
aquele arquivo evita refazer essa cirurgia — aqui só trocamos o que é da PC.
"""
import io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
AQUI = os.path.dirname(os.path.abspath(__file__))

t = io.open(os.path.join(AQUI, 'montar_site_pc_referencia.py'), encoding='utf-8').read()
n = 0


def sub(de, para, vezes=1):
    global t, n
    if t.count(de) != vezes:
        raise SystemExit('esperava %d de %r, achei %d' % (vezes, de[:90], t.count(de)))
    t = t.replace(de, para)
    n += vezes


# ---------------------------------------------------------------- cabeçalho
sub('"""Monta a pagina da rede Parana Clinicas reaproveitando o app do site da Amil.',
    '"""Monta a pagina da rede Nossa Saude no padrao da casa (mesmo app da Amil).')
sub('SAI = os.path.join(_local.RAIZ, "index.html")',
    'SAI = os.path.join(_local.RAIZ, "index.html")')
sub('HOJE = "12/09/2026"          # data da coleta da rede',
    'HOJE = "10/09/2026"          # data da coleta da rede')
sub('dados = json.load(open("dados/dados_pc.json", encoding="utf-8"))',
    'dados = json.load(open("dados/dados_ns.json", encoding="utf-8"))')

# ------------------------------------------------------------------ paleta
sub('''# Vermelho e branco da Parana Clinicas (SulAmerica) no lugar do navy.
# O ouro continua: e o acento da Mazza Broker, igual no material da Amil.
CORES_CLARO = {
    "--marca-fundo:#0d2a4f": "--marca-fundo:#8e0e28",
    "--banda:#25507f": "--banda:#b03050",
    "--marca-texto:#0d2a4f": "--marca-texto:#8e0e28",
    "--amil:#2733c4": "--plano-a:#a80a32",
    "--adesao:#7c2f6d": "--plano-b:#6b3f8f",
    "--amils:#0b6154": "--plano-c:#b5761b",
    "--papel:#f2f5f9": "--papel:#f7f4f4",
    "--risco:#dbe2ec": "--risco:#e9dfe1",
    "--realce:#f6f8fc": "--realce:#fbf6f7",
}''',
    '''# Laranja e marrom da Nossa Saude (nossasaude.com.br) no lugar do navy.
# O ouro continua: e o acento da Mazza Broker, igual no material da Amil.
CORES_CLARO = {
    "--marca-fundo:#0d2a4f": "--marca-fundo:#38312e",
    "--banda:#25507f": "--banda:#8a4a26",
    "--marca-texto:#0d2a4f": "--marca-texto:#c0350f",
    "--amil:#2733c4": "--plano-a:#e6411c",
    "--adesao:#7c2f6d": "--plano-b:#b4601a",
    "--amils:#0b6154": "--plano-c:#7b6a3f",
    "--papel:#f2f5f9": "--papel:#f7f4f2",
    "--risco:#dbe2ec": "--risco:#e6e1dd",
    "--realce:#f6f8fc": "--realce:#fdf6f1",
}''')
sub('''CORES_ESCURO = {
    "--marca-fundo:#0b1a2f": "--marca-fundo:#3b0a16",
    "--banda:#1c3a5e": "--banda:#6d1330",
    "--marca-texto:#9dbfec": "--marca-texto:#eaa8b6",
    "--sobre-marca:#dbe7f7": "--sobre-marca:#f7e6ea",
    "--amil:#8d99ff": "--plano-a:#d1445f",
    "--adesao:#e08fd0": "--plano-b:#9b6ec4",
    "--amils:#48c7b4": "--plano-c:#b08529",
    "--papel:#0a0f17": "--papel:#130d0f",
    "--carta:#131a25": "--carta:#1b1416",
    "--risco:#25303f": "--risco:#3a2a2e",
    "--realce:#19212e": "--realce:#241a1d",
    "--tinta:#e7ecf4": "--tinta:#f2e9eb",
    "--tinta-fraca:#94a0b4": "--tinta-fraca:#b7a3a8",
}''',
    '''CORES_ESCURO = {
    "--marca-fundo:#0b1a2f": "--marca-fundo:#241f1d",
    "--banda:#1c3a5e": "--banda:#6b3a1c",
    "--marca-texto:#9dbfec": "--marca-texto:#ff8a5c",
    "--sobre-marca:#dbe7f7": "--sobre-marca:#f3e8e2",
    "--amil:#8d99ff": "--plano-a:#ff7a4f",
    "--adesao:#e08fd0": "--plano-b:#e0a05a",
    "--amils:#48c7b4": "--plano-c:#c3b municipal",
    "--papel:#0a0f17": "--papel:#171310",
    "--carta:#131a25": "--carta:#221d1a",
    "--risco:#25303f": "--risco:#332b27",
    "--realce:#19212e": "--realce:#1e1917",
    "--tinta:#e7ecf4": "--tinta:#f2ede9",
    "--tinta-fraca:#94a0b4": "--tinta-fraca:#c9beb7",
}''')
sub('"--plano-c:#c3b municipal"', '"--plano-c:#c3b07a"')

sub('head = head.replace("rgba(214,177,85,.16)", "rgba(233,197,106,.20)")\n'
    'head = head.replace("#16233a", "#3b0a16")',
    'head = head.replace("rgba(214,177,85,.16)", "rgba(230,150,60,.18)")\n'
    'head = head.replace("#16233a", "#241f1d")')

# ------------------------------------------------------------------ títulos
sub('             "<title>Rede credenciada Paraná Clínicas — Curitiba e Região</title>")',
    '             "<title>Rede credenciada Nossa Saúde — Campos Gerais</title>")')
sub("""             '<h1>Rede credenciada <em>Paraná Clínicas</em> — '
             '<span id="tituloEstado">Curitiba e Região</span></h1>')""",
    """             '<h1>Rede credenciada <em>Nossa Saúde</em> — '
             '<span id="tituloEstado">Campos Gerais</span></h1>')""")

# nota de família: aqui é um produto só
sub("""             '<p class="nota-familia">Cada cartão é uma <b>rede</b>, não um contrato: '
             'enfermaria e apartamento (<b>QC</b> e <b>QP</b>) compartilham a mesma rede — '
             'por isso Paraná 400 AHO QC e Paraná 600 AHO QP não aparecem à parte, '
             'estão dentro do 400 e do 600.</p>')""",
    """             '<p class="nota-familia">Este material soma <b>todos os planos</b> da Nossa '
             'Saúde na região: se o prestador está aqui, ele é credenciado da operadora '
             'naquela cidade por algum plano. Confirme no portal da operadora se ele atende '
             'o plano específico do cliente.</p>')""")
sub('head = head.replace("portal da Amil", "portal da Paraná Clínicas")',
    'head = head.replace("portal da Amil", "portal da Nossa Saúde")')

io.open(os.path.join(AQUI, 'montar_site.py'), 'w', encoding='utf-8').write(t)
print('etapa 1: %d trocas' % n)

