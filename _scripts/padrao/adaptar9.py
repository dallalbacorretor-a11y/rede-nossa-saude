# -*- coding: utf-8 -*-
"""Etapa 9: correções da auditoria de 20/11/2026.

Cada correção vira um bloco de troca() no montar_site.py, logo antes da
montagem da página ("4) monta"), quando head, lib e app já passaram pelas
etapas 1 a 8. Como nas outras etapas, toda troca estoura se o texto de
origem sumir.
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


BLOCOS = [r'''# ========================================= 3b) correcoes da auditoria
# Etapa 9 (adaptar9.py), auditoria de 20/11/2026.
''']

# 1) a data da capa do PDF
BLOCOS.append(r'''# A capa do PDF dizia "Levantado ... em <hoje>": a data em que o PDF era
# montado, nao a da coleta - e o aviso "retrato da data da capa" depende
# dela. A capa passa a usar o gerado_em da regiao que esta na tela.
lib = troca(lib, "var p = this.pdf, hoje = new Date(), o = this.o;",
            "var p = this.pdf, o = this.o;\n"
            "    // data da COLETA da regiao (gerado_em, dd/mm/aaaa), nunca a do dia\n"
            "    var coleta = String(o.dataColeta || (window.DADOS || {}).gerado_em || \"\")\n"
            "      .split(\"/\");\n"
            "    var temColeta = coleta.length === 3 && coleta[1] >= 1 && coleta[1] <= 12;")
lib = troca(lib,
            '"Levantado na rede credenciada oficial da Nossa Saúde em " + hoje.getDate() +\n'
            '            " de " + MESES[hoje.getMonth()] + " de " + hoje.getFullYear(),',
            '"Levantado na rede credenciada oficial da Nossa Saúde" + (temColeta\n'
            '              ? " em " + Number(coleta[0]) + " de " + MESES[coleta[1] - 1] +\n'
            '                " de " + coleta[2]\n'
            '              : ""),')
app = troca(app, "var rel = new window.Relatorio(window.FONTES, {",
            "var rel = new window.Relatorio(window.FONTES, {\n"
            "      dataColeta: D.gerado_em,   // a capa diz quando a rede foi levantada",
            2)
''')

# 2) o nome do CSV
BLOCOS.append(r'''# O CSV saia como "rede-parana-clinicas-<cidade>.csv" (sobra do modelo da
# Parana Clinicas). Agora: rede-nossa-saude-<regiao>-<cidade>.csv, sem acento
# nem espaco; sem cidade filtrada, "todas-as-cidades".
app = troca(app,
            r"""    entregar("rede-parana-clinicas-" + apelidoCidade().toLowerCase()
      .replace(/\s+/g, "-") + ".csv", csv);""",
            r"""    var slug = function (s) {
      return semAcento(s).toLowerCase().replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");
    };
    var ondeCsv = (temEscolha("cidr") || temEscolha("cid"))
      ? apelidoCidade() : "todas as cidades";
    entregar("rede-nossa-saude-" + slug(D.estado || D.uf) + "-" +
             slug(ondeCsv) + ".csv", csv);""")
''')

MARCA ='# ============================================================== 4) monta\n'
sub(MARCA, '\n'.join(BLOCOS) + '\n' + MARCA)

io.open(ALVO, 'w', encoding='utf-8').write(t)
print('etapa 9: %d trocas' % n)
