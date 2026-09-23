# -*- coding: utf-8 -*-
"""Etapa 5: duas regiões no mesmo site.

O app já alterna entre chaves de `DADOS_UF` (é o que a Amil faz com PR/SC/SP);
aqui as chaves são CG (Campos Gerais) e CWB (Curitiba, região e litoral).
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


# o titulo da aba cobre as duas regioes; o <h1> o app troca sozinho
sub('             "<title>Rede credenciada Nossa Saúde — Campos Gerais</title>")',
    '             "<title>Rede credenciada Nossa Saúde — Paraná</title>")')

# a caixa do mapa passa a ter uma entrada por regiao
sub('''lats = [p["xy"][0] for p in dados["PR"]["prestadores"] if p["xy"][0] is not None]
lngs = [p["xy"][1] for p in dados["PR"]["prestadores"] if p["xy"][1] is not None]
m = 0.06
app = troca(app, "PR: { lat: [-26.72, -22.51], lng: [-54.62, -48.02] },",
            "PR: { lat: [%.3f, %.3f], lng: [%.3f, %.3f] }," %
            (min(lats) - m, max(lats) + m, min(lngs) - m, max(lngs) + m))''',
    '''m = 0.06
caixas = []
for _ch, _reg in dados.items():
    _la = [p["xy"][0] for p in _reg["prestadores"] if p["xy"][0] is not None]
    _lo = [p["xy"][1] for p in _reg["prestadores"] if p["xy"][1] is not None]
    caixas.append("%s: { lat: [%.3f, %.3f], lng: [%.3f, %.3f] }," %
                  (_ch, min(_la) - m, max(_la) + m, min(_lo) - m, max(_lo) + m))
app = troca(app, "PR: { lat: [-26.72, -22.51], lng: [-54.62, -48.02] },",
            "\\n    ".join(caixas))''')

# o seletor de regiao so aparece com mais de uma chave
sub("lib = troca(lib, 'window.ORDEM_UF=[\"PR\", \"SC\", \"SP\"];', 'window.ORDEM_UF=[\"PR\"];')",
    "lib = troca(lib, 'window.ORDEM_UF=[\"PR\", \"SC\", \"SP\"];',\n"
    "            'window.ORDEM_UF=' + json.dumps(list(dados)) + ';')")

# a checagem de produto unico vale para qualquer regiao
sub('if len(dados["PR"]["produtos"]) < 2:',
    'if max(len(r["produtos"]) for r in dados.values()) < 2:')

io.open(ALVO, 'w', encoding='utf-8').write(t)
print('etapa 5: %d trocas' % n)
