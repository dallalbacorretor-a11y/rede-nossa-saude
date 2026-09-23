# -*- coding: utf-8 -*-
"""Monta a pagina da rede Nossa Saude no padrao da casa (mesmo app da Amil).

Toda troca passa por troca(), que estoura se o texto original nao existir mais -
assim uma mudanca no arquivo de origem falha alto em vez de sair silenciosa.
"""
import json, io, os, sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _local  # noqa: F401  (fixa o diretorio de trabalho)

SAI = os.path.join(_local.RAIZ, "index.html")
HOJE = "10/09/2026"          # data da coleta da rede
import datetime
VERSAO = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

L = lambda f: io.open(f, encoding="utf-8").read()
head = L(os.path.join(_local.BASE, "amil_head.html"))     # CSS + markup (ate antes dos <script>)
lib = L(os.path.join(_local.BASE, "amil_lib.js"))         # fontes + gerador de PDF
app = L(os.path.join(_local.BASE, "amil_app.js"))         # aplicacao
dados = json.load(open("dados/dados_ns.json", encoding="utf-8"))

trocas = 0
def troca(txt, de, para, n=1):
    global trocas
    if txt.count(de) != n:
        raise SystemExit("ESPERAVA %d ocorrencia(s) de:\n  %r\nachei %d"
                         % (n, de[:120], txt.count(de)))
    trocas += n
    return txt.replace(de, para)


# ====================================================== 1) paleta e cabecalho
# Laranja e marrom da Nossa Saude (nossasaude.com.br) no lugar do navy.
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
}
CORES_ESCURO = {
    "--marca-fundo:#0b1a2f": "--marca-fundo:#241f1d",
    "--banda:#1c3a5e": "--banda:#6b3a1c",
    "--marca-texto:#9dbfec": "--marca-texto:#ff8a5c",
    "--sobre-marca:#dbe7f7": "--sobre-marca:#f3e8e2",
    "--amil:#8d99ff": "--plano-a:#ff7a4f",
    "--adesao:#e08fd0": "--plano-b:#e0a05a",
    "--amils:#48c7b4": "--plano-c:#c3b07a",
    "--papel:#0a0f17": "--papel:#171310",
    "--carta:#131a25": "--carta:#221d1a",
    "--risco:#25303f": "--risco:#332b27",
    "--realce:#19212e": "--realce:#1e1917",
    "--tinta:#e7ecf4": "--tinta:#f2ede9",
    "--tinta-fraca:#94a0b4": "--tinta-fraca:#c9beb7",
}
# o bloco escuro aparece duas vezes (media query + [data-theme=dark])
for de, para in CORES_CLARO.items():
    head = head.replace(de, para)
for de, para in CORES_ESCURO.items():
    head = head.replace(de, para)
# o que sobrou referenciando os nomes antigos
for a, b in (("var(--amil)", "var(--plano-a)"), ("var(--adesao)", "var(--plano-b)"),
             ("var(--amils)", "var(--plano-c)")):
    head = head.replace(a, b)
    app = app.replace(a, b)

# o navy do gradiente do topo e do botao de estado
head = head.replace("rgba(214,177,85,.16)", "rgba(230,150,60,.18)")
head = head.replace("#16233a", "#241f1d")

head = troca(head, "<title>Rede Amil Paraná, Santa Catarina e São Paulo</title>",
             "<title>Rede credenciada Nossa Saúde — Paraná</title>")
head = troca(head,
             '<h1>Rede credenciada <em>Amil</em> — <span id="tituloEstado">Paraná, '
             'Santa Catarina e São Paulo</span></h1>',
             '<h1>Rede credenciada <em>Nossa Saúde</em> — '
             '<span id="tituloEstado">Campos Gerais</span></h1>')

# "Rede de (praça)" nao existe aqui: a busca da Nossa Saude e por cidade.
head = troca(head, '<span class="rotulo">Rede de (praça)</span>',
             '<span class="rotulo">Cidade</span>')
# some com o filtro duplicado de cidade (o elemento fica no DOM: o app o le)
head = troca(head, '<div class="campo"><span class="rotulo">Cidade do prestador</span>',
             '<div class="campo" style="display:none"><span class="rotulo">Cidade do prestador</span>')

head = troca(head,
             '<span class="miudo" style="margin-left:auto">A busca por cidade traz a rede\n'
             '      da região — parte dos prestadores fica em municípios vizinhos.</span>',
             '<span class="miudo" style="margin-left:auto">Rede levantada cidade a cidade '
             'na busca oficial da operadora.</span>')

head = troca(head,
             '<p class="nota-familia">Cada cartão é uma <b>rede</b>, não um contrato:\n'
             '     enfermaria e apartamento (QC e QP) compartilham a mesma rede, e a linha\n'
             '     de <b>Adesão</b> usa a rede do PME/PJ correspondente — Adesão Prata está\n'
             '     dentro de Prata, Adesão Ouro dentro de Ouro, e assim por diante.</p>',
             '<p class="nota-familia">Este material soma <b>todos os planos</b> da Nossa '
             'Saúde na região: se o prestador está aqui, ele é credenciado da operadora '
             'naquela cidade por algum plano. Confirme no portal da operadora se ele atende '
             'o plano específico do cliente.</p>')

head = head.replace("portal da Amil", "portal da Nossa Saúde")
# Carimbo da versão publicada. O GitHub Pages serve a página com dez minutos de
# cache, e uma aba já aberta fica na versão antiga até recarregar - sem isto,
# nao da para saber se o que esta na tela e a ultima publicacao.
head = troca(head, '<span class="assina" id="assinaRodape"></span>',
             '<span class="assina" id="assinaRodape"></span>\n'
             '  <span class="versao" title="Se esta data estiver atrasada, '
             'recarregue a página segurando Shift">versão ' + VERSAO + '</span>')
# a contagem de medicos do corpo clinico abre a lista no title
head = troca(head, "</style>",
             ".equipe{cursor:help;border-bottom:1px dotted currentColor}\n"
             ".rodape .versao{display:block;margin-top:4px;font-size:10.5px;"
             "opacity:.55;font-variant-numeric:tabular-nums}\n</style>")
head = troca(head, "A comparação usa a praça filtrada na aba Rede completa.",
             "A comparação usa a cidade filtrada na aba Rede completa.")

# ================================================================ 2) o app
app = troca(app,
            'var COR = { "PME/PJ": "var(--plano-a)", "Adesao": "var(--plano-b)", '
            '"Amil S": "var(--plano-c)" };',
            'var COR = { "Nossa Saúde": "var(--marca-texto)" };')
app = troca(app,
            'var COR_GRAFICO = { "PME/PJ": "#4457e0", "Adesao": "#b03a97",\n'
            '                      "Amil S": "#0f9a80", "Black": "#5b6472" };',
            'var COR_GRAFICO = { "Nossa Saúde": "#e6411c" };')

# mapa: a rede e so os Campos Gerais - o retangulo do Parana inteiro
# jogaria tudo num canto da tela.
m = 0.06
caixas = []
for _ch, _reg in dados.items():
    _la = [p["xy"][0] for p in _reg["prestadores"] if p["xy"][0] is not None]
    _lo = [p["xy"][1] for p in _reg["prestadores"] if p["xy"][1] is not None]
    caixas.append("%s: { lat: [%.3f, %.3f], lng: [%.3f, %.3f] }," %
                  (_ch, min(_la) - m, max(_la) + m, min(_lo) - m, max(_lo) + m))
app = troca(app, "PR: { lat: [-26.72, -22.51], lng: [-54.62, -48.02] },",
            "\n    ".join(caixas))

app = troca(app, '"rede-amil-pr-"', '"rede-parana-clinicas-"')
app = troca(app, '"Rede que a Amil devolve para "',
            '"Rede da Nossa Saúde em "')
app = troca(app,
            '". Parte dos prestadores fica em municípios vizinhos — use a aba " +\n'
            '        "Rede completa para ver cidade por cidade."',
            '". Use a aba Rede completa para ver prestador por prestador."')
app = app.replace("Levantado na busca avançada oficial da Amil.",
                  "Levantado na rede credenciada oficial da Nossa Saúde, somando todos os planos.")
app = troca(app,
            '"Amil devolveu na data da capa, para os planos "',
            '"a Nossa Saúde devolveu na data da capa, somando todos os planos "')
app = app.replace("Confirme no portal da Amil", "Confirme no portal da Nossa Saúde")
app = troca(app, '("Amil " + nA + " x " + nB + " - " + onde + ".pdf")',
            '("Nossa Saude " + nA + " x " + nB + " - " + onde + ".pdf")')
# o nome do arquivo e o que o cliente ve na conversa: operadora e recorte
app = troca(app,
            '''var nome = "Rede Amil " +
               (comparativo
                 ? (nomes.length <= 3 ? nomes.join(" x ")
                                      : nomes.length + " planos")
                 : nomes[0]) +
               " - " + rotuloCidade + ".pdf";''',
            '''var nome = "Nossa Saúde - " + rotuloCidade + ".pdf";''')

# a cidade vem em caixa alta da operadora e precisa virar Título; o nome da
# região já vem certo e não pode virar "Curitiba, Rmc e Paranaguá"
app = troca(app,
            '''var rotuloCidade = bruto.replace(''',
            '''var rotuloCidade = bruto !== bruto.toUpperCase() ? bruto
      : bruto.replace(''')
app = troca(app,
            'var aviso = "Cada plano deste material representa uma rede: enfermaria e " +\n'
            '      "apartamento compartilham a mesma rede credenciada, e a linha de Adesão " +\n'
            '      "usa a rede do PME/PJ correspondente. " +',
            'var aviso = "Este material soma todos os planos da Nossa Saúde na " +\n'
            '      "região: se o prestador está aqui, ele é credenciado da operadora " +\n'
            '      "naquela cidade por algum plano. " +')
app = troca(app, '"da Amil apresentava na data da capa e não substitui a consulta ao "',
            '"da Nossa Saúde apresentava na data da capa e não substitui a consulta ao "')
app = troca(app, '"operadora. Este documento é o retrato do que a busca avançada oficial "',
            '"operadora. Este documento é o retrato do que a rede credenciada oficial "')

# ajustes de texto: aqui nao existe "praca" - a busca da operadora e por cidade
app = app.replace('". Escolha uma praça no filtro da aba Rede completa " +',
                  '". Use os filtros da aba Rede completa " +')
app = app.replace('" inteira. Escolha uma praça " +\n'
                  '            "no filtro da aba Rede completa para recortar este panorama."',
                  '". Filtre por cidade ou plano na aba " +\n'
                  '            "Rede completa para recortar este panorama."')
app = app.replace('"Rede de " + (D.estado || D.uf) + " inteira.',
                  '"Rede dos três planos em " + (D.estado || D.uf) + ".')

# ------------------------------------------------- categorias da operadora
# O app da Amil traz tres categorias no codigo ("Hospitais", "Laboratorios e
# imagem", "Clinicas e consultorios") e deduz a do prestador contando
# especialidades. Aqui quem classifica e o build_dados, a partir do campo
# tipo_estabelecimento da operadora - que separa hospital geral de
# especializado e tira os centros de imagem de dentro de "Clinica". Entao o
# app passa a confiar no `cat` que vem no dado, e as listas de categoria
# passam a sair de D.
app = troca(app, 'var CAT_EXAME = { "Laboratorios e imagem": 1 };',
            'var CAT_EXAME = {};   // preenchido por mapearEspecialidadesDeExame')
app = troca(app,
            '  function mapearEspecialidadesDeExame() {\n'
            '    ESP_EXAME = {};\n'
            '    D.prestadores.forEach(function (p) {\n'
            '      var lista = p.pc && p.pc["Laboratorios e imagem"];\n'
            '      (lista || []).forEach(function (e) { ESP_EXAME[e] = 1; });\n'
            '    });\n'
            '  }',
            '  function mapearEspecialidadesDeExame() {\n'
            '    ESP_EXAME = {};\n'
            '    CAT_EXAME = {};\n'
            '    (D.catsExame || []).forEach(function (c) { CAT_EXAME[c] = 1; });\n'
            '    TIPO_LUGAR = {};\n'
            '    (D.categorias || []).forEach(function (c) { TIPO_LUGAR[c] = 1; });\n'
            '    CAT_ELETIVA = {};\n'
            '    (D.categorias || []).forEach(function (c) {\n'
            '      if (!/^Hospitais/.test(c)) CAT_ELETIVA[c] = 1;\n'
            '    });\n'
            '    D.prestadores.forEach(function (p) {\n'
            '      Object.keys(CAT_EXAME).forEach(function (c) {\n'
            '        ((p.pc && p.pc[c]) || []).forEach(function (e) { ESP_EXAME[e] = 1; });\n'
            '      });\n'
            '    });\n'
            '  }')
app = troca(app,
            '  var TIPO_LUGAR = { "Hospitais": 1, "Laboratorios e imagem": 1,\n'
            '                     "Clinicas e consultorios": 1 };',
            '  var TIPO_LUGAR = {};   // idem')
app = troca(app,
            '  var CAT_ELETIVA = { "Laboratorios e imagem": 1,\n'
            '                      "Clinicas e consultorios": 1 };',
            '  var CAT_ELETIVA = {};  // idem')
app = troca(app,
            '  function tipoDe(p) {\n'
            '    var c = p.cats || [];\n'
            '    // pronto-socorro entra aqui junto com hospital: o Hospital de Caridade de\n'
            '    // Palmeira a Amil classifica so como PS, e ele nao e lugar de exame eletivo\n'
            '    if (c.indexOf("Hospitais") >= 0 || c.indexOf("Pronto-socorro 24h") >= 0) {\n'
            '      return "Hospitais";\n'
            '    }\n'
            '    var exames = quantos(p, "Laboratorios e imagem");\n'
            '    var consultas = quantos(p, "Clinicas e consultorios");\n'
            '    if (exames > consultas) return "Laboratorios e imagem";\n'
            '    if (consultas > 0) return "Clinicas e consultorios";\n'
            '    if (exames > 0) return "Laboratorios e imagem";\n'
            '    return null;\n'
            '  }',
            '  function tipoDe(p) {\n'
            '    return p.cat || null;   // quem classifica e o build_dados\n'
            '  }')
# hospital geral e especializado: os dois valem a ressalva de "so internado"
app = app.replace(
    '    var c = p.cats || [];\n'
    '    return c.indexOf("Hospitais") >= 0 || c.indexOf("Pronto-socorro 24h") >= 0;',
    '    return /^Hospitais/.test(tipoDe(p) || "");')

# quadros do PDF: os da Amil ("Pronto-socorro 24h", "Centros de diagnostico por
# imagem") nao existem aqui e saiam zerados
app = troca(app,
            '    var hosp = daCategoria("Hospitais");\n'
            '    var ps = daCategoria("Pronto-socorro 24h");\n'
            '    var pa = daCategoria("Pronto atendimento");\n'
            '    var lab = daCategoria("Laboratorios e imagem");\n'
            '    var hemo = daCategoria("Hemodialise");\n'
            '    var tea = daCategoria("TEA");\n'
            '    var tele = daCategoria("Telemedicina");\n'
            '    var cons = daCategoria("Clinicas e consultorios");',
            '    var hosp = daCategoria("Hospitais");\n'
            '    var imagem = daCategoria("Diagnóstico por imagem");\n'
            '    var lab = daCategoria("Laboratórios e análises clínicas");\n'
            '    var proc = daCategoria("Exames e procedimentos");\n'
            '    var cons = daCategoria("Clínicas e consultórios");\n'
            '    var prof = daCategoria("Médicos e demais profissionais");')
app = troca(app,
            '    rel.numeros([\n'
            '      [hosp.length, "Hospitais para internação"],\n'
            '      [ps.length, "Pronto-socorro 24 horas"],\n'
            '      [nAnalises, "Laboratórios de análises clínicas"],\n'
            '      [nImagem, "Centros de diagnóstico por imagem"],\n'
            '      [cons.length, "Clínicas e consultórios"],\n'
            '      [lista.length, "Prestadores no total"]\n'
            '    ]);',
            '    rel.numeros([\n'
            '      [hosp.length, "Hospitais para internação"],\n'
            '      [imagem.length, "Centros de diagnóstico por imagem"],\n'
            '      [lab.length, "Laboratórios de análises clínicas"],\n'
            '      [proc.length, "Exames e procedimentos"],\n'
            '      [cons.length, "Clínicas e consultórios"],\n'
            '      [prof.length, "Médicos e demais profissionais"],\n'
            '      [lista.length, "Prestadores no total"]\n'
            '    ].filter(function (n) { return n[0]; }));')

# secoes do PDF: pelas categorias da operadora, e os grupos de exame passam a
# ser as proprias categorias (antes eram regex sobre nomes de exame da Amil,
# que nao batem com o vocabulario daqui)
app = troca(app,
            '    secao("Hospitais para internação", hosp);\n'
            '    secao("Pronto-socorro 24 horas", ps);\n'
            '    secao("Pronto atendimento", pa);',
            '    secao("Hospitais e internação", hosp);')
app = troca(app,
            '    var nomesGrupo = ["Análises clínicas e patologia", "Diagnóstico por imagem",\n'
            '                      "Exames funcionais", "Endoscopia e procedimentos",\n'
            '                      "Oncologia", "Outros exames"];',
            '    var nomesGrupo = (D.catsExame || []).slice();')
app = troca(app,
            '    secao("Hemodiálise", hemo);\n'
            '    secao("TEA — transtorno do espectro autista", tea);\n'
            '    secao("Telemedicina", tele);',
            '    secao("Clínicas e consultórios", cons);\n'
            '    secao("Médicos e demais profissionais", prof);')
app = troca(app,
            '    var porGrupo = {};\n'
            '    lab.forEach(function (p) {\n'
            '      p.esp.forEach(function (e) {\n'
            '        var g = grupoExame(e);\n'
            '        porGrupo[g] = porGrupo[g] || {};\n'
            '        if (!porGrupo[g][p.n]) {\n'
            '          var q = {}; for (var k in p) q[k] = p[k];\n'
            '          q.esp = [];\n'
            '          porGrupo[g][p.n] = q;\n'
            '        }\n'
            '        porGrupo[g][p.n].esp.push(e);\n'
            '      });\n'
            '    });',
            '    var porGrupo = {};\n'
            '    (D.catsExame || []).forEach(function (g) {\n'
            '      daCategoria(g).forEach(function (p) {\n'
            '        porGrupo[g] = porGrupo[g] || {};\n'
            '        porGrupo[g][p.n] = p;\n'
            '      });\n'
            '    });')
app = troca(app,
            '    var nAnalises = contarCentros("Análises clínicas e patologia");\n'
            '    var nImagem = contarCentros("Diagnóstico por imagem");',
            '')

# Quadros do panorama: passam a contar pelas categorias novas. "Onde se
# interna" e a pergunta que o cliente faz, entao hospital geral ganha quadro
# proprio.
app = troca(app,
            '    var hospitais = lista.filter(function (p) {\n'
            '      return tipoDe(p) === "Hospitais";\n'
            '    }).length;\n'
            '    var exames = lista.filter(function (p) {\n'
            '      return tipoDe(p) === "Laboratorios e imagem";\n'
            '    }).length;\n'
            '    var consultorios = lista.filter(function (p) {\n'
            '      return tipoDe(p) === "Clinicas e consultorios";\n'
            '    }).length;',
            '    function daCat() {\n'
            '      var quais = Array.prototype.slice.call(arguments);\n'
            '      return lista.filter(function (p) {\n'
            '        return quais.indexOf(tipoDe(p)) >= 0;\n'
            '      }).length;\n'
            '    }\n'
            '    var hospitais = daCat("Hospitais");\n'
            '    var imagem = daCat("Diagnóstico por imagem");\n'
            '    var exames = daCat("Laboratórios e análises clínicas",\n'
            '                       "Exames e procedimentos");\n'
            '    var medicos = daCat("Médicos e demais profissionais");\n'
            '    var consultorios = daCat("Clínicas e consultórios");')
app = troca(app,
            '    $("panNumeros").innerHTML = [\n'
            '      [lista.length, "prestadores"],\n'
            '      [cidades.length, cidades.length === 1 ? "cidade" : "cidades"],\n'
            '      [hospitais, "hospitais"],\n'
            '      [exames, "exames e laboratórios"],\n'
            '      [consultorios, "clínicas e consultórios"]\n'
            '    ].map(function (n) {',
            '    $("panNumeros").innerHTML = [\n'
            '      [lista.length, "prestadores"],\n'
            '      [cidades.length, cidades.length === 1 ? "cidade" : "cidades"],\n'
            '      [hospitais, "hospitais"],\n'
            '      [imagem, "centros de imagem"],\n'
            '      [exames, "laboratórios e exames"],\n'
            '      [consultorios, "clínicas e consultórios"],\n'
            '      [medicos, "médicos e profissionais"]\n'
            '    ].filter(function (n) { return n[0]; }).map(function (n) {')

# A Nossa Saude nao publica acreditacao de prestador, entao a marca ACRED.
# nunca apareceria - prometer uma legenda que
# nao existe e pior que nao ter legenda.
app = troca(app,
            '    if (hosp.length) {\n'
            '      rel.titulo("Principais referências hospitalares",\n'
            '        "Os hospitais de maior cobertura na sua rede. A marca ACRED. indica " +\n'
            '        "programa de acreditação reconhecido pela operadora.");\n'
            '      rel.referencias(hosp.slice(0, 10));\n'
            '    }',
            '    var refs = hosp;\n'
            '    if (refs.length) {\n'
            '      rel.titulo("Principais referências hospitalares",\n'
            '        "Os hospitais da rede na região — é onde a internação acontece.");\n'
            '      rel.referencias(refs.slice(0, 10));\n'
            '    }')

# Aqui os tres planos sao de uma linha so, entao colorir pela linha pintaria
# tudo de vermelho. Cada plano ganha sua cor - a mesma no cartao, na coluna da
# tabela e na barra do grafico. Como token CSS, e nao hex, para o modo escuro
# usar a versao clara validada; o hex fica so para o PDF.
app = troca(app, 'var COR = { "Nossa Saúde": "var(--marca-texto)" };',
            'var COR = { "Nossa Saúde": "var(--marca-texto)" };\n'
            '  var VAR_PLANO = { ns: "var(--plano-a)" };')
app = troca(app, 'b.style.setProperty("--cor", p.cor || COR[p.linha] || "var(--plano-a)");',
            'b.style.setProperty("--cor", VAR_PLANO[p.codigo] || p.cor ||\n'
            '                                COR[p.linha] || "var(--plano-a)");')
app = troca(app, '\'" style="--cor:\' + (COR[c.linha] || "var(--plano-a)") + \'">\' +',
            '\'" style="--cor:\' + (VAR_PLANO[c.codigo] || COR[c.linha] ||\n'
            '                                        "var(--plano-a)") + \'">\' +')
app = troca(app, 'var cor = COR_GRAFICO[d.linha] || "var(--marca-texto)";',
            'var cor = VAR_PLANO[d.cod] || COR_GRAFICO[d.linha] || "var(--marca-texto)";')
app = troca(app, "return { rot: rotuloProduto(pr), linha: pr.linha,",
            "return { rot: rotuloProduto(pr), linha: pr.linha, cod: pr.codigo,")
app = troca(app, "return { rot: d.rot, linha: d.linha, v: d.n };",
            "return { rot: d.rot, linha: d.linha, cod: d.cod, v: d.n };")
app = troca(app, "return { rot: d.rot, linha: d.linha, v: d.cid };",
            "return { rot: d.rot, linha: d.linha, cod: d.cod, v: d.cid };")
# capa do PDF na cor do plano (o PDF nao tem modo escuro: hex mesmo)
app = troca(app, 'cor: aux.COR_LINHA[produto.linha] || "#20456f",',
            'cor: produto.cor || aux.COR_LINHA[produto.linha] || "#332d2b",')
app = troca(app, 'cor: aux.COR_LINHA[prodA ? prodA.linha : "PME/PJ"] || "#20456f",',
            'cor: (prodA && prodA.cor) || "#332d2b",')

# ------------------------------------- dados que a operadora publica e o app
# da Amil nao tinha onde mostrar: e-mail, acessibilidade e corpo clinico.
# Buscar pelo nome do medico e o caso real do corretor - "meu cliente quer o
# Dr. Fulano, onde ele atende?".
app = troca(app,
            '      if (q && semAcento(p.n).indexOf(q) < 0 && (p.c || "").indexOf(q) < 0) {\n'
            '        return false;\n'
            '      }',
            '      if (q && semAcento(p.n).indexOf(q) < 0 && (p.c || "").indexOf(q) < 0 &&\n'
            '          !(p.eq || []).some(function (m) {\n'
            '            return semAcento(m[0]).indexOf(q) >= 0;\n'
            '          })) {\n'
            '        return false;\n'
            '      }', 2)   # a aba Rede completa e a aba Entre planos
app = troca(app,
            '           \'<div class="miudo">\' + esc(p.t.join(" · ")) + "</div></td>";',
            '           \'<div class="miudo">\' + esc(p.t.join(" · ")) +\n'
            '           (p.mail && p.mail.length\n'
            '             ? " · " + esc(p.mail[0]) : "") +\n'
            '           (p.acess ? \' · <span title="Prestador com acessibilidade \'\n'
            '                      + \'declarada à operadora">acessível</span>\' : "") +\n'
            '           (p.eq && p.eq.length\n'
            '             ? \'<span class="equipe" title="\' +\n'
            '               esc(p.eq.slice(0, 14).map(function (m) {\n'
            '                 return m[0] + (m[2] ? " — " + m[2] : "");\n'
            '               }).join("\\n")) + (p.eq.length > 14 ? "\\n…" : "") +\n'
            '               \'"> · equipe de \' + p.eq.length + \' médicos</span>\'\n'
            '             : "") + "</div></td>";')

# Por ultimo, o que sobrou de "=== Hospitais" espalhado pelas contagens
# (cartao do plano, bolha do mapa, "hospitais que saem" da aba Entre planos).
# Depois dos blocos acima, senao esta troca os desfiguraria antes da hora.
for _de, _para in (('tipoDe(p) === "Hospitais"', '/^Hospitais/.test(tipoDe(p) || "")'),
                   ('tipoDe(p) !== "Hospitais"', '!/^Hospitais/.test(tipoDe(p) || "")')):
    if _de not in app:
        raise SystemExit("nao achei mais: " + _de)
    trocas += app.count(_de)
    app = app.replace(_de, _para)

# =============================================================== 3) o PDF
lib = troca(lib, 'window.ORDEM_UF=["PR", "SC", "SP"];',
            'window.ORDEM_UF=' + json.dumps(list(dados)) + ';')
lib = troca(lib, 'var NAVY = "#0d2a4f", NAVY_MEIO = "#20456f", OURO = "#9a7513",',
            'var NAVY = "#332d2b", NAVY_MEIO = "#4c4441", OURO = "#9a7513",')
lib = troca(lib, 'var COR_LINHA = { "PME/PJ": "#2733c4", "Adesao": "#7c2f6d",\n'
                 '                    "Amil S": "#0b6154", "Black": "#3a3a3a" };',
            'var COR_LINHA = { "Nossa Saúde": "#e6411c" };')
lib = troca(lib, '"Rede Credenciada Amil"', '"Rede Credenciada Nossa Saúde"')
lib = troca(lib, '"Levantado na busca avançada oficial da Amil em "',
            '"Levantado na rede credenciada oficial da Nossa Saúde em "')
lib = troca(lib, '"Rede credenciada Amil " +', '"Rede credenciada Nossa Saúde " +')
lib = lib.replace('RISCO = "#e4e9f0", ZEBRA = "#f7f9fc"',
                  'RISCO = "#e6e1dd", ZEBRA = "#fdf9f6"')
lib = lib.replace('"#cfe0f5"', '"#f7ddcb"').replace('"#9fb8d8"', '"#e0b193"')
lib = lib.replace('"#c7d8ee"', '"#f8e3d5"')
lib = lib.replace('OURO_CLARO = "#e3c46a"', 'OURO_CLARO = "#e8c87d"')

if "Amil" in app or "Amil" in lib.split("window.FONTES")[0]:
    import re
    sobrou = set(re.findall(r".{40}Amil.{40}", app))
    print("AVISO: ainda ha mencoes a Amil no app (provavelmente comentarios):", len(sobrou))

# ============================================================== 4) monta
# ------------------------------------------------ produto unico: sem comparativo
# A aba "Entre planos" existe para confrontar duas redes. Aqui o material soma
# todos os planos numa rede so - ela compararia o plano com ele mesmo.
if max(len(r["produtos"]) for r in dados.values()) < 2:
    head = troca(head,
                 '<button type="button" class="aba" data-aba="entre">Entre planos</button>',
                 '<button type="button" class="aba" data-aba="entre" id="abaEntre"'
                 ' hidden>Entre planos</button>')
    app = troca(app, '$("dataColeta").textContent = "atualizado em " + D.gerado_em;',
                '$("dataColeta").textContent = "atualizado em " + D.gerado_em;\n'
                '    if (D.produtos.length < 2) {\n'
                '      var abaE = $("abaEntre");\n'
                '      if (abaE) abaE.hidden = true;\n'
                '    }')

blob = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
pagina = (head + "\n<script>window.DADOS_UF=" + blob + ";\n"
          + lib.split(";\n", 1)[1] + "</script>\n<script>" + app + "</script>\n")
io.open(SAI, "w", encoding="utf-8").write(pagina)
print("trocas conferidas:", trocas)
print("gravado:", SAI, round(len(pagina.encode("utf-8")) / 1024 / 1024, 2), "MB")
