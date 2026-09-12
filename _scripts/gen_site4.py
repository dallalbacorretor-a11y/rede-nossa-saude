# -*- coding: utf-8 -*-
"""Site da rede credenciada — atlas com imagem de satélite e galeria de guias."""
import os, sys, json, shutil, re, math
sys.stdout.reconfigure(encoding='utf-8')

AQUI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(AQUI, 'site')
D = json.load(open(os.path.join(AQUI, 'dados_unico.json'), encoding='utf-8'))
IND = json.load(open(os.path.join(AQUI, 'indice_cidades.json'), encoding='utf-8'))
MAPA = json.load(open(os.path.join(AQUI, 'mapa_pr.json'), encoding='utf-8'))
SAT = json.load(open(os.path.join(AQUI, 'satelite.json'), encoding='utf-8'))
ITENS, CIDADES, EXAMES = D['itens'], D['cidades'], D['exames']

META = {
    'operadora': 'Nossa Saúde', 'razao': 'Nossa Saúde Operadora de Planos Privados de Saúde',
    'cnpj': '02.862.447/0001-03', 'data': '10 de setembro de 2026',
    'corretor': 'Alan Vinicius Dall Alba', 'tel': '(41) 99547-6715', 'whats': '5541995476715',
    'mail': 'alan.vinicius@mazzabroker.com.br',
    'satelite': SAT['atribuicao'],
    'fonte': ('Rede credenciada oficial da operadora, em prestador.nossasaude.com.br, consultada em '
              '10 de setembro de 2026 sem filtro de plano.'),
    'aviso': ('A rede é definida e alterada exclusivamente pela operadora. Esta lista soma todos os '
              'planos da Nossa Saúde — antes de contratar, confirme no portal da operadora se o '
              'prestador atende o plano específico.'),
}
CATS = ['Hospitais e Pronto-Socorro', 'Clínicas e Centros Médicos',
        'Laboratórios e Imagem', 'Profissionais (médicos e demais)']
CAT_CURTA = {CATS[0]: 'Hospital', CATS[1]: 'Clínica', CATS[2]: 'Laboratório e imagem',
             CATS[3]: 'Profissional'}
COORD = {
    'Ponta Grossa': (-25.095, -50.162), 'Telêmaco Borba': (-24.324, -50.617),
    'Jaguariaíva': (-24.251, -49.706), 'Castro': (-24.791, -50.012),
    'Irati': (-25.468, -50.651), 'Palmeira': (-25.429, -50.007),
    'Carambeí': (-24.915, -50.098), 'Prudentópolis': (-25.213, -50.978),
    'Piraí do Sul': (-24.526, -49.945),
}
LADO = {'Ponta Grossa': 'd', 'Telêmaco Borba': 'e', 'Jaguariaíva': 'd', 'Castro': 'd',
        'Irati': 'e', 'Palmeira': 'd', 'Carambeí': 'e', 'Prudentópolis': 'e', 'Piraí do Sul': 'd'}


def merc(lat, lon, z, tile=256):
    n = 2.0 ** z * tile
    x = (lon + 180.0) / 360.0 * n
    s = math.radians(lat)
    y = (1.0 - math.log(math.tan(s) + 1.0 / math.cos(s)) / math.pi) / 2.0 * n
    return x, y


_ox, _oy = merc(SAT['norte'], SAT['oeste'], SAT['zoom'])


def no_satelite(lat, lon):
    x, y = merc(lat, lon, SAT['zoom'])
    return round(x - _ox, 1), round(y - _oy, 1)


def tels(r):
    out = []
    for e in r['enderecos']:
        for t in re.split(r'\s*/\s*', e.get('tel') or ''):
            t = t.strip()
            if t and t not in out:
                out.append(t)
    return out


def ends(r):
    out = []
    for e in r['enderecos']:
        p = e['logradouro']
        if e['bairro']:
            p += ' — ' + e['bairro']
        if p and p not in out:
            out.append(p)
    return out


itens = [{
    'c': i['cidade'], 'k': i['categoria'], 't': i['tipo_exib'], 'n': i['nome_exib'],
    'rz': i['razao'] if i['razao'].lower() != i['nome_exib'].lower() else '',
    'doc': ('CNPJ ' + i['cnpj']) if i['cnpj'] else i['conselho'],
    'e': i['esp_exib'], 'nat': i['naturezas'], 'int': 1 if i['internacao'] else 0,
    'end': ends(i), 'tel': tels(i), 'cc': [m['nome'] for m in i['corpo_clinico']],
} for i in ITENS]

cidades = []
for it in IND:
    lst = [i for i in ITENS if i['cidade'] == it['cidade']]
    sx, sy = no_satelite(*COORD[it['cidade']])
    cidades.append({
        'nome': it['cidade'], 'slug': it['slug'], 'kb': it['kb'],
        'pdf': 'arquivos/cidades/rede-nossa-saude-%s.pdf' % it['slug'],
        'capa': 'img/capas/capa-%s.jpg' % it['slug'],
        'x': sx, 'y': sy, 'lado': LADO[it['cidade']],
        'ix': MAPA['cidades'][it['cidade']][0], 'iy': MAPA['cidades'][it['cidade']][1],
        'total': len(lst),
        'hosp': sum(1 for i in lst if i['internacao']),
        'lab': sum(1 for i in lst if 'Análises clínicas e patologia' in i['naturezas'] and not i['internacao']),
        'img': sum(1 for i in lst if 'Diagnóstico por imagem' in i['naturezas'] and not i['internacao']),
        'clin': sum(1 for i in lst if i['categoria'] == CATS[1]),
        'prof': sum(1 for i in lst if i['categoria'] == CATS[3]),
        'paginas': it.get('paginas', 0),
        'hospitais': [{'n': i['nome_exib'], 'e': (i['enderecos'][0]['bairro'] if i['enderecos'] else '')}
                      for i in lst if i['internacao']],
        'especialidades': len({e for i in lst for e in i['esp_exib']}),
    })

# retângulo da região sobre o mapa do Paraná (mini localizador)
_pr = MAPA['cidades']
CAIXA = {'x': min(v[0] for v in _pr.values()) - 34, 'y': min(v[1] for v in _pr.values()) - 30,
         'w': (max(v[0] for v in _pr.values()) - min(v[0] for v in _pr.values())) + 68,
         'h': (max(v[1] for v in _pr.values()) - min(v[1] for v in _pr.values())) + 60}

def _kb(rel):
    caminho = os.path.join(SITE, 'arquivos', rel)
    return round(os.path.getsize(caminho) / 1024) if os.path.exists(caminho) else 0


REGIAO = {'pdf_kb': _kb('rede-nossa-saude-campos-gerais.pdf'),
          'xlsx_kb': _kb('rede-nossa-saude-campos-gerais.xlsx')}

PAYLOAD = {'meta': META, 'regiao': REGIAO, 'cidades': cidades, 'ordem': CIDADES, 'cats': CATS,
           'catcurta': CAT_CURTA, 'exames': EXAMES, 'itens': itens,
           'sat': {'w': SAT['largura'], 'h': SAT['altura'], 'src': SAT['arquivo']},
           'pr': {'viewBox': MAPA['viewBox'], 'path': MAPA['path'], 'caixa': CAIXA}}

# ------------------------------------------------------------------ HTML
INDEX = r"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas da Rede Nossa Saúde</title>
<meta name="description" content="A rede credenciada da Nossa Saúde nas nove cidades dos Campos Gerais: hospitais, laboratórios, exames de imagem, clínicas e médicos, com o guia em PDF de cada cidade.">
<meta name="theme-color" content="#0B2545">
<meta property="og:title" content="Atlas da Rede Nossa Saúde — Campos Gerais">
<meta property="og:description" content="Escolha a sua cidade no mapa e baixe o guia da rede credenciada.">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='10' fill='%230B2545'/><circle cx='32' cy='27' r='11' fill='none' stroke='%23E2661F' stroke-width='5'/><rect x='29.5' y='34' width='5' height='20' fill='%23A67C0E'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="estilo.css">
</head>
<body>

<header class="masthead">
  <div class="faixa"></div>
  <div class="wrap topo">
    <div class="marca">
      <span class="selo">Mazza<i>Broker</i></span>
      <span class="registro">Corretora de saúde · Alan Vinicius Dall Alba</span>
    </div>
    <a class="fone" id="foneTopo" href="#"></a>
  </div>
  <div class="wrap titulo">
    <p class="sobre-titulo">Rede credenciada · Campos Gerais · Paraná</p>
    <h1>Atlas da rede <em>Nossa Saúde</em></h1>
    <p class="chamada">Nove cidades, uma rede. Todos os planos da operadora somados numa lista só —
      escolha a cidade no mapa e leve o guia em PDF para o cliente.</p>
    <p class="carimbo" id="carimbo"></p>
  </div>
</header>

<nav class="navegacao"><div class="wrap">
  <a href="#atlas">Mapa</a>
  <a href="#guias">Baixar guias</a>
  <a href="#cidades">Números</a>
  <a href="#exames">Exames</a>
  <a href="#buscar">Buscar</a>
  <a href="#sobre">Sobre</a>
  <a class="nav-zap" id="navZap" href="#" target="_blank" rel="noopener">Falar comigo</a>
</div></nav>

<section id="atlas" class="atlas"><div class="wrap atlas-grade">
  <figure class="mapa">
    <div class="moldura-mapa" id="molduraMapa"></div>
    <figcaption>
      <span>Cada ponto é uma cidade atendida e o tamanho acompanha o número de prestadores. As
        linhas ligam as cidades a Ponta Grossa, referência da região para internação e alta
        complexidade. Toque num ponto para ver a cidade.</span>
      <span class="credito" id="creditoSat"></span>
    </figcaption>
  </figure>
  <div class="dossie" id="dossie"></div>
</div></section>

<section id="guias" class="faixa-clara"><div class="wrap">
  <div class="cabeca">
    <h2>Baixe o guia da sua cidade</h2>
    <p>Um documento por cidade, pronto para mandar no WhatsApp: hospitais, exames por natureza,
      clínicas e médicos por especialidade. Clique na capa para baixar.</p>
  </div>
  <div class="galeria" id="galeria"></div>
  <p class="extra-planilha" id="extraPlanilha"></p>
</div></section>

<section id="cidades"><div class="wrap">
  <div class="cabeca">
    <h2>A rede em números</h2>
    <p>O que cada cidade tem credenciado hoje.</p>
  </div>
  <div class="scroll"><table class="registro-tab" id="tabCidades"></table></div>
</div></section>

<section id="exames" class="faixa-clara"><div class="wrap">
  <div class="cabeca">
    <h2>Onde fazer cada exame</h2>
    <p>Prestadores por natureza de exame em cada cidade. Quanto mais forte a cor, mais opções.</p>
  </div>
  <div class="scroll"><table class="mapa-calor" id="tabExames"></table></div>
</div></section>

<section id="buscar"><div class="wrap">
  <div class="cabeca">
    <h2>Buscar na rede</h2>
    <p>Nome do prestador, especialidade, bairro ou cidade.</p>
  </div>
  <div class="filtros">
    <input type="search" id="q" placeholder="Ex.: Santa Casa, cardiologia, Uvaranas, laboratório…">
    <select id="fcidade" aria-label="Cidade"><option value="">Todas as cidades</option></select>
    <select id="fesp" aria-label="Especialidade"><option value="">Todas as especialidades</option></select>
    <div class="chips" id="chips"></div>
    <button class="btn-limpar" id="limpar" type="button">Limpar</button>
  </div>
  <p class="contagem" id="contagem"></p>
  <div id="lista"></div>
</div></section>

<section id="sobre" class="faixa-clara"><div class="wrap sobre-grade">
  <div>
    <div class="cabeca"><h2>Sobre este material</h2></div>
    <div class="texto" id="txtSobre"></div>
  </div>
  <aside class="cartao-contato">
    <span class="selo grande">Mazza<i>Broker</i></span>
    <p class="quem" id="sbQuem"></p>
    <p class="funcao">Corretor de saúde</p>
    <a class="botao" id="sbZap" href="#" target="_blank" rel="noopener">Chamar no WhatsApp</a>
    <a class="link-mail" id="sbMail" href="#"></a>
    <p class="mini" id="sbFonte"></p>
  </aside>
</div></section>

<footer class="rodape"><div class="wrap">
  <p id="rdRegistro"></p>
  <p class="mini" id="rdAviso"></p>
</div></footer>

<a class="zap" id="zapFlutuante" target="_blank" rel="noopener" aria-label="Falar no WhatsApp">
  <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5.1-1.3A10 10 0 1 0 12 2zm0 2a8 8 0 1 1-4.1 14.9l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 0 1 12 4zm-3 4c-.3 0-.6.1-.8.4-.3.3-.9.9-.9 2.1s.9 2.4 1 2.6c.1.2 1.7 2.8 4.3 3.8 2.1.8 2.6.7 3 .6.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.3.2-1.4l-.6-.3-1.8-.9c-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.5 6.5 0 0 1-3.2-2.8c-.1-.2 0-.4.1-.5l.5-.6.2-.4v-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4H9z"/></svg>
  <span>Falar comigo</span>
</a>

<script src="dados.js"></script>
<script src="app.js"></script>
</body>
</html>
"""

CSS = r""":root{
  --tinta:#0B2545;
  --tinta-2:#16365E;
  --papel:#F1F3F7;
  --papel-2:#E7EBF2;
  --superficie:#FFFFFF;
  --texto:#152437;
  --texto-2:#4B5D75;
  --texto-3:#7A8CA3;
  --regra:#D5DCE6;
  --regra-forte:#B9C4D2;
  --ouro:#A67C0E;
  --ouro-cl:#C79A2A;
  --laranja:#E2661F;
  --laranja-rgb:226,102,31;
  --laranja-suave:#FBEDE4;
  --royal:#2733C4;
  --sombra:0 1px 1px rgba(11,37,69,.04), 0 6px 20px -12px rgba(11,37,69,.22);
  --sombra-alta:0 2px 4px rgba(11,37,69,.06), 0 18px 40px -20px rgba(11,37,69,.35);
  --serif:"Newsreader",Georgia,"Times New Roman",serif;
  --sans:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,"SFMono-Regular",Menlo,monospace;
  --coluna:1180px;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --tinta:#07111F; --tinta-2:#0F2440;
  --papel:#0A1524; --papel-2:#0E1B2D; --superficie:#101E33;
  --texto:#E7EDF6; --texto-2:#AFC0D6; --texto-3:#7C8CA3;
  --regra:#1E3050; --regra-forte:#2C426A;
  --ouro:#D2A63C; --ouro-cl:#E3BD5E;
  --laranja:#F0813F; --laranja-rgb:240,129,63; --laranja-suave:#2A1A11;
  --royal:#7C86F5;
  --sombra:0 1px 1px rgba(0,0,0,.3), 0 6px 20px -12px rgba(0,0,0,.6);
  --sombra-alta:0 2px 4px rgba(0,0,0,.35), 0 18px 40px -20px rgba(0,0,0,.8);
}}
:root[data-theme="dark"]{
  --tinta:#07111F; --tinta-2:#0F2440;
  --papel:#0A1524; --papel-2:#0E1B2D; --superficie:#101E33;
  --texto:#E7EDF6; --texto-2:#AFC0D6; --texto-3:#7C8CA3;
  --regra:#1E3050; --regra-forte:#2C426A;
  --ouro:#D2A63C; --ouro-cl:#E3BD5E;
  --laranja:#F0813F; --laranja-rgb:240,129,63; --laranja-suave:#2A1A11;
  --royal:#7C86F5;
  --sombra:0 1px 1px rgba(0,0,0,.3), 0 6px 20px -12px rgba(0,0,0,.6);
  --sombra-alta:0 2px 4px rgba(0,0,0,.35), 0 18px 40px -20px rgba(0,0,0,.8);
}

*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:64px}
body{margin:0;background:var(--papel);color:var(--texto);
  font:16px/1.6 var(--sans);-webkit-font-smoothing:antialiased}
img{max-width:100%;display:block}
a{color:var(--royal)}
h1,h2,h3{text-wrap:balance;margin:0}
.wrap{max-width:var(--coluna);margin:0 auto;padding:0 24px}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
section{padding:64px 0}
.faixa-clara{background:var(--papel-2)}
:focus-visible{outline:2px solid var(--royal);outline-offset:3px;border-radius:2px}

.selo{display:inline-flex;align-items:baseline;gap:7px;font-family:var(--serif);
  font-size:19px;font-weight:600;color:var(--ouro);letter-spacing:-.01em}
.selo i{font-family:var(--mono);font-style:normal;font-size:9px;font-weight:500;
  letter-spacing:.22em;text-transform:uppercase;color:var(--ouro);opacity:.85}
.selo.grande{font-size:24px}

/* ---------- masthead ---------- */
.masthead{background:var(--tinta);color:#fff;position:relative}
.masthead .faixa{height:5px;background:linear-gradient(90deg,var(--royal) 0 62%,var(--ouro) 62% 100%)}
.topo{display:flex;align-items:center;justify-content:space-between;gap:16px;
  padding-top:16px;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,.1)}
.marca{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
.masthead .selo,.masthead .selo i{color:var(--ouro-cl)}
.registro{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;
  color:#8FA6C4}
.fone{font-family:var(--mono);font-size:13px;color:#fff;text-decoration:none;
  border:1px solid rgba(255,255,255,.22);border-radius:2px;padding:6px 12px;white-space:nowrap}
.fone:hover{border-color:var(--ouro-cl);color:var(--ouro-cl)}
.titulo{padding-top:52px;padding-bottom:58px;max-width:920px}
.sobre-titulo{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--ouro-cl);margin:0 0 18px}
h1{font-family:var(--serif);font-weight:400;font-size:clamp(38px,6.6vw,68px);line-height:1.02;
  letter-spacing:-.025em}
h1 em{font-style:italic;color:var(--ouro-cl)}
.chamada{max-width:52ch;color:#B7C7DC;font-size:17px;margin:22px 0 0}
.carimbo{font-family:var(--mono);font-size:11px;line-height:1.7;color:#7E93AF;margin:26px 0 0;
  padding-top:14px;border-top:1px solid rgba(255,255,255,.12);max-width:62ch}

/* ---------- navegação ---------- */
.navegacao{position:sticky;top:0;z-index:40;background:var(--superficie);
  border-bottom:1px solid var(--regra)}
.navegacao .wrap{display:flex;gap:2px;align-items:center;overflow-x:auto}
.navegacao a{font-family:var(--mono);font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--texto-2);text-decoration:none;padding:15px 13px;white-space:nowrap;
  border-bottom:2px solid transparent}
.navegacao a:hover{color:var(--texto);border-bottom-color:var(--ouro)}
.nav-zap{margin-left:auto;color:var(--royal)!important}

/* ---------- atlas ---------- */
.atlas{padding:52px 0 64px}
.atlas-grade{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(320px,.8fr);gap:40px;
  align-items:center}
.mapa{margin:0}
.moldura-mapa{position:relative;background:var(--tinta);box-shadow:var(--sombra-alta);
  overflow:hidden}
.moldura-mapa img.satelite{width:100%;height:auto}
.moldura-mapa svg.pontos{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.vinheta{position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(120% 90% at 50% 45%,transparent 45%,rgba(4,18,36,.55) 100%)}
.raio{stroke:#FFD79A;stroke-width:1.4;opacity:.5;fill:none;stroke-dasharray:5 6}
.ponto{cursor:pointer}
.ponto .halo{fill:#E2661F;opacity:.22;transition:opacity .2s ease}
.ponto .disco{fill:#E2661F;stroke:#fff;stroke-width:2.5;transition:fill .2s ease,stroke .2s ease}
.ponto .rotulo{font-family:var(--mono);font-size:30px;font-weight:600;fill:#fff;
  paint-order:stroke;stroke:rgba(4,18,36,.9);stroke-width:8px;stroke-linejoin:round;
  letter-spacing:.02em}
.ponto:hover .halo,.ponto.ativo .halo{opacity:.4}
.ponto.ativo .disco{fill:#fff;stroke:#E2661F;stroke-width:5}
.ponto:focus{outline:none}
.ponto:focus-visible .disco{stroke:#7C86F5;stroke-width:5}
.localizador{position:absolute;right:14px;bottom:14px;width:118px;
  background:rgba(6,20,38,.72);padding:9px 10px 7px;backdrop-filter:blur(3px)}
.localizador svg{width:100%;height:auto;display:block}
.localizador .pr{fill:rgba(255,255,255,.16);stroke:rgba(255,255,255,.5);stroke-width:5}
.localizador .caixa{fill:none;stroke:#E2661F;stroke-width:12}
.localizador p{font-family:var(--mono);font-size:8px;letter-spacing:.16em;text-transform:uppercase;
  color:#C4D3E6;margin:6px 0 0;text-align:center}
.mapa figcaption{display:flex;flex-direction:column;gap:7px;font-size:12.5px;color:var(--texto-3);
  margin-top:14px;max-width:52ch;line-height:1.5}
.mapa .credito{font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;
  color:var(--texto-3);opacity:.8}

.dossie{background:var(--superficie);border:1px solid var(--regra);border-top:3px solid var(--tinta);
  box-shadow:var(--sombra-alta);padding:30px 32px 28px}
.dossie .uf{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--texto-3)}
.dossie h2{font-family:var(--serif);font-size:38px;font-weight:400;letter-spacing:-.02em;
  line-height:1.05;margin:6px 0 0}
.dossie .resumo{font-size:14px;color:var(--texto-2);margin:12px 0 0}
.numeros{display:grid;grid-template-columns:repeat(3,1fr);margin:24px 0 0;
  border-top:1px solid var(--regra)}
.numeros div{padding:14px 0 12px;border-bottom:1px solid var(--regra)}
.numeros div + div{border-left:1px solid var(--regra);padding-left:16px}
.numeros div:nth-child(3n+1){border-left:none;padding-left:0}
.numeros b{display:block;font-family:var(--serif);font-size:30px;font-weight:400;line-height:1;
  font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.numeros span{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--texto-3);display:block;margin-top:7px}
.hospitais{margin:20px 0 0;font-size:14px;color:var(--texto-2)}
.hospitais .rotulo{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--texto-3);margin:0 0 6px}
.hospitais ul{margin:0;padding:0;list-style:none}
.hospitais li{padding:5px 0 5px 15px;position:relative;line-height:1.4}
.hospitais li::before{content:"";position:absolute;left:0;top:12px;width:6px;height:6px;
  background:var(--laranja)}
.hospitais li em{font-style:normal;color:var(--texto-3);font-size:12.5px}
.sem-hosp{font-size:13.5px;color:var(--texto-2);background:var(--laranja-suave);
  border-left:3px solid var(--laranja);padding:11px 14px;margin:20px 0 0;line-height:1.45}

.botao{display:inline-flex;align-items:center;justify-content:space-between;gap:14px;
  background:var(--tinta);color:#fff;text-decoration:none;padding:14px 18px;font-weight:600;
  font-size:14.5px;border:1px solid var(--tinta);transition:background .16s ease}
.botao span{font-family:var(--mono);font-size:10px;letter-spacing:.14em;color:#93AACB}
.botao:hover{background:var(--royal);border-color:var(--royal)}
.dossie .botao{width:100%;margin-top:24px}

/* ---------- cabeçalhos ---------- */
.cabeca{margin-bottom:26px;max-width:60ch}
.cabeca h2{font-family:var(--serif);font-size:clamp(26px,3.4vw,34px);font-weight:400;
  letter-spacing:-.02em;line-height:1.1}
.cabeca p{color:var(--texto-2);font-size:15px;margin:9px 0 0}

/* ---------- galeria de guias ---------- */
.galeria{display:grid;grid-template-columns:repeat(auto-fill,minmax(232px,1fr));gap:22px}
.guia{display:flex;flex-direction:column;text-decoration:none;color:inherit;
  background:var(--superficie);border:1px solid var(--regra);box-shadow:var(--sombra);
  transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease}
.guia:hover{transform:translateY(-4px);box-shadow:var(--sombra-alta);border-color:var(--regra-forte)}
.guia .capa{position:relative;background:var(--tinta);line-height:0}
.guia .capa img{width:100%;height:auto}
.guia .baixar{position:absolute;left:0;right:0;bottom:0;display:flex;align-items:center;
  justify-content:space-between;gap:8px;background:var(--ouro);color:#fff;
  font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
  padding:8px 12px;transform:translateY(100%);transition:transform .18s ease}
.guia .baixar span{opacity:.78}
.guia:hover .baixar,.guia:focus-visible .baixar{transform:translateY(0)}
.guia .corpo{padding:15px 17px 17px;display:flex;flex-direction:column;gap:9px;flex:1}
.guia h3{font-family:var(--serif);font-size:21px;font-weight:600;letter-spacing:-.01em;
  line-height:1.15}
.guia .linha-num{display:flex;flex-wrap:wrap;gap:4px 14px;font-family:var(--mono);font-size:10px;
  letter-spacing:.08em;text-transform:uppercase;color:var(--texto-3)}
.guia .linha-num b{color:var(--texto);font-weight:600;font-size:12px;
  font-variant-numeric:tabular-nums}
.guia .peso{margin-top:auto;font-family:var(--mono);font-size:10px;letter-spacing:.1em;
  text-transform:uppercase;color:var(--royal);display:flex;align-items:center;gap:6px}
.extra-planilha{margin:22px 0 0;font-size:14px;color:var(--texto-2)}
.extra-planilha a{color:var(--royal);font-weight:600}
.guia.destaque{grid-column:span 2}
.guia.destaque h3{font-size:24px}
@media (max-width:560px){.guia.destaque{grid-column:span 1}}

/* ---------- tabela registro ---------- */
.registro-tab{width:100%;border-collapse:collapse;font-size:14.5px}
.registro-tab th{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--texto-3);text-align:right;padding:0 0 10px;font-weight:500;white-space:nowrap}
.registro-tab th:first-child{text-align:left}
.registro-tab thead tr{border-bottom:2px solid var(--tinta)}
.registro-tab td{padding:15px 0;border-bottom:1px solid var(--regra);text-align:right;
  font-variant-numeric:tabular-nums;color:var(--texto-2)}
.registro-tab td:first-child{text-align:left}
.registro-tab tbody tr:hover td{background:var(--superficie)}
.registro-tab .cid{font-family:var(--serif);font-size:21px;color:var(--texto);
  display:block;line-height:1.15}
.registro-tab .cid-sub{font-family:var(--mono);font-size:10px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--texto-3)}
.registro-tab .tot{color:var(--texto);font-weight:600;font-size:16px}
.registro-tab .zero{color:var(--texto-3);opacity:.6}
.registro-tab .baixa{white-space:nowrap;font-family:var(--mono);font-size:11.5px;
  letter-spacing:.06em;text-transform:uppercase;text-decoration:none;color:var(--royal);
  border-bottom:1px solid currentColor;padding-bottom:1px}
.registro-tab tfoot td{border-bottom:none;border-top:2px solid var(--tinta);padding-top:14px;
  font-weight:600;color:var(--texto)}
.registro-tab tfoot .cid{font-family:var(--mono);font-size:11px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--texto-3)}

/* ---------- mapa de calor ---------- */
.mapa-calor{width:100%;border-collapse:collapse;font-size:13.5px}
.mapa-calor th{font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;
  color:var(--texto-3);font-weight:500;padding:0 6px 12px;text-align:center;vertical-align:bottom}
.mapa-calor th:first-child{text-align:left;padding-left:0;min-width:190px}
.mapa-calor thead tr{border-bottom:2px solid var(--tinta)}
.mapa-calor td{padding:5px 6px;text-align:center;font-variant-numeric:tabular-nums}
.mapa-calor td:first-child{text-align:left;padding-left:0;color:var(--texto);font-weight:500;
  white-space:nowrap}
.mapa-calor .celula{display:block;padding:12px 0;min-width:44px;color:var(--texto);font-weight:600}
.mapa-calor .celula.vazio{color:var(--texto-3);opacity:.45;font-weight:400}
.legenda-calor{display:flex;align-items:center;gap:10px;margin-top:18px;font-family:var(--mono);
  font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--texto-3)}
.legenda-calor i{display:block;width:26px;height:12px}

/* ---------- busca ---------- */
.filtros{display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding-bottom:18px;
  border-bottom:2px solid var(--tinta)}
input[type=search],select{font:inherit;font-size:14.5px;color:var(--texto);
  background:var(--superficie);border:1px solid var(--regra-forte);padding:11px 13px;
  border-radius:2px;max-width:100%}
input[type=search]{flex:1 1 280px;min-width:200px}
input[type=search]::placeholder{color:var(--texto-3)}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{font-family:var(--mono);font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;
  border:1px solid var(--regra-forte);background:transparent;color:var(--texto-2);
  padding:9px 13px;cursor:pointer;border-radius:2px}
.chip:hover{border-color:var(--tinta);color:var(--texto)}
.chip.on{background:var(--tinta);border-color:var(--tinta);color:#fff}
.btn-limpar{font-family:var(--mono);font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;
  background:none;border:none;color:var(--royal);cursor:pointer;padding:9px 4px}
.contagem{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--texto-3);margin:16px 0 0}
.cidade-bloco{margin-top:38px}
.cidade-bloco > header{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;
  padding-bottom:10px;border-bottom:1px solid var(--regra-forte)}
.cidade-bloco h3{font-family:var(--serif);font-size:26px;font-weight:400;letter-spacing:-.02em}
.cidade-bloco .qtd{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;
  text-transform:uppercase;color:var(--texto-3)}
.cidade-bloco .baixa{margin-left:auto;font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--royal);text-decoration:none;border-bottom:1px solid currentColor}
.verbete{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1.3fr) minmax(0,1.2fr);
  gap:26px;padding:18px 0;border-bottom:1px solid var(--regra)}
.verbete:hover{background:var(--superficie)}
.verbete .tipo{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--texto-3);display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0}
.verbete .tipo .marca-int{color:var(--laranja);border:1px solid currentColor;padding:1px 6px}
.verbete h4{font-family:var(--serif);font-size:19px;font-weight:600;letter-spacing:-.01em;
  margin:5px 0 0;line-height:1.2}
.verbete .doc{font-family:var(--mono);font-size:10.5px;color:var(--texto-3);margin:5px 0 0;
  letter-spacing:.02em}
.verbete .especialidades{font-size:13.5px;color:var(--texto-2);line-height:1.5;margin:0}
.verbete .corpo{font-size:12px;color:var(--texto-3);margin:7px 0 0;line-height:1.45}
.verbete .contato{font-size:13.5px;color:var(--texto-2);line-height:1.5}
.verbete .contato p{margin:0}
.verbete .contato a{color:var(--royal);text-decoration:none}
.verbete .contato a:hover{text-decoration:underline}
.verbete .fone-lista{font-family:var(--mono);font-size:13px;margin-top:6px;color:var(--texto)}
.vazio{padding:60px 0;text-align:center;color:var(--texto-3);font-size:15px}

/* ---------- sobre e rodapé ---------- */
.sobre-grade{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(280px,.9fr);gap:44px;
  align-items:start}
.texto{font-size:15.5px;color:var(--texto-2);max-width:62ch}
.texto h3{font-family:var(--mono);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--texto-3);margin:26px 0 8px;font-weight:500}
.texto p{margin:0 0 12px}
.texto strong{color:var(--texto);font-weight:600}
.texto .nota{border-left:3px solid var(--ouro);background:var(--superficie);padding:14px 16px;
  font-size:14px}
.cartao-contato{background:var(--tinta);color:#fff;padding:30px 30px 26px}
.cartao-contato .selo,.cartao-contato .selo i{color:var(--ouro-cl)}
.cartao-contato .quem{font-family:var(--serif);font-size:23px;margin:20px 0 0;line-height:1.2}
.cartao-contato .funcao{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:#8FA6C4;margin:6px 0 22px}
.cartao-contato .botao{width:100%;background:var(--ouro);border-color:var(--ouro);
  justify-content:center}
.cartao-contato .botao:hover{background:var(--ouro-cl);border-color:var(--ouro-cl);color:var(--tinta)}
.link-mail{display:block;margin-top:14px;font-family:var(--mono);font-size:12px;color:#B7C7DC;
  text-decoration:none;word-break:break-all}
.link-mail:hover{color:var(--ouro-cl)}
.cartao-contato .mini{font-size:11.5px;color:#7E93AF;line-height:1.55;margin:22px 0 0;
  padding-top:16px;border-top:1px solid rgba(255,255,255,.12)}
.rodape{background:var(--tinta);color:#8FA6C4;padding:30px 0 100px;font-size:12.5px}
.rodape p{margin:0}
.rodape .mini{font-size:11.5px;color:#6C82A0;margin-top:10px;max-width:90ch;line-height:1.6}
.rodape #rdRegistro{font-family:var(--mono);font-size:11px;letter-spacing:.05em;color:#93AACB}
.zap{position:fixed;right:18px;bottom:18px;z-index:50;display:inline-flex;align-items:center;
  gap:9px;background:#1FA855;color:#fff;text-decoration:none;padding:12px 17px;border-radius:40px;
  box-shadow:0 6px 22px -6px rgba(0,0,0,.5);font-size:14px;font-weight:600}
.zap span{display:none}
.zap:hover span{display:inline}

@media (max-width:900px){
  .atlas-grade,.sobre-grade{grid-template-columns:1fr;gap:30px}
  .titulo{padding-top:38px;padding-bottom:42px}
  .verbete{grid-template-columns:1fr;gap:10px}
  .ponto .rotulo{font-size:60px;stroke-width:14px}
}
@media (max-width:560px){
  section{padding:46px 0}
  .wrap{padding:0 18px}
  .dossie{padding:24px 22px}
  .numeros{grid-template-columns:repeat(2,1fr)}
  .numeros div:nth-child(odd){border-left:none;padding-left:0}
  .numeros div:nth-child(even){border-left:1px solid var(--regra);padding-left:16px}
  .registro-tab .esconde-mobile{display:none}
  .mapa-calor th:first-child{min-width:140px}
  .localizador{width:88px;right:8px;bottom:8px}
  .guia .baixar{transform:translateY(0)}
}
@media (prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important}
  html{scroll-behavior:auto}
}
"""

APP = r"""(function () {
  const D = window.DADOS, m = D.meta;
  const $ = s => document.querySelector(s);
  const esc = s => (s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const norm = s => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const plural = (n, s, p) => n + ' ' + (n === 1 ? s : p);
  const zap = 'https://wa.me/' + m.whats + '?text=' +
    encodeURIComponent('Olá Alan! Vi o atlas da rede Nossa Saúde e quero saber mais.');

  D.itens.forEach(i => {
    i._b = norm([i.n, i.rz, i.t, i.doc, i.e.join(' '), i.end.join(' '), i.cc.join(' '), i.c].join(' '));
  });
  const total = D.itens.length;
  const porCidade = c => D.cidades.find(x => x.nome === c);

  $('#foneTopo').href = zap;
  $('#foneTopo').textContent = m.tel;
  $('#navZap').href = zap;
  $('#zapFlutuante').href = zap;
  $('#carimbo').textContent = m.razao + ' · CNPJ ' + m.cnpj + ' — ' + total +
    ' prestadores levantados em ' + m.data + ', somando todos os planos da operadora.';
  $('#creditoSat').textContent = 'Imagens de satélite: ' + m.satelite;

  /* ---------------- mapa de satélite ---------------- */
  const sat = D.sat, pr = D.pr;
  const maior = Math.max(...D.cidades.map(c => c.total));
  const raio = n => 12 + 26 * Math.sqrt(n / maior);
  const hub = porCidade('Ponta Grossa');
  const raios = D.cidades.filter(c => c !== hub)
    .map(c => `<line class="raio" x1="${hub.x}" y1="${hub.y}" x2="${c.x}" y2="${c.y}"></line>`).join('');
  const pontos = D.cidades.map(c => {
    const r = raio(c.total), e = c.lado === 'e';
    return `<g class="ponto" data-cidade="${esc(c.nome)}" tabindex="0" role="button"
              aria-label="Ver a rede de ${esc(c.nome)}">
      <circle class="halo" cx="${c.x}" cy="${c.y}" r="${(r * 2).toFixed(1)}"></circle>
      <circle class="disco" cx="${c.x}" cy="${c.y}" r="${r.toFixed(1)}"></circle>
      <text class="rotulo" x="${(c.x + (e ? -(r + 14) : r + 14)).toFixed(1)}"
            y="${(c.y + 10).toFixed(1)}" text-anchor="${e ? 'end' : 'start'}">${esc(c.nome)}</text>
    </g>`;
  }).join('');
  const cx = pr.caixa;
  $('#molduraMapa').innerHTML =
    `<img class="satelite" src="${sat.src}" width="${sat.w}" height="${sat.h}"
       alt="Imagem de satélite dos Campos Gerais, no Paraná">
     <div class="vinheta"></div>
     <svg class="pontos" viewBox="0 0 ${sat.w} ${sat.h}" preserveAspectRatio="none"
       role="img" aria-label="As nove cidades atendidas sobre o mapa da região">
       <g>${raios}${pontos}</g>
     </svg>
     <div class="localizador">
       <svg viewBox="${pr.viewBox}" role="img" aria-label="Localização da região no Paraná">
         <path class="pr" d="${pr.path}"></path>
         <rect class="caixa" x="${cx.x}" y="${cx.y}" width="${cx.w}" height="${cx.h}"></rect>
       </svg>
       <p>Campos Gerais</p>
     </div>`;

  /* ---------------- dossiê ---------------- */
  function abrirCidade(nome) {
    const c = porCidade(nome);
    if (!c) return;
    document.querySelectorAll('.ponto').forEach(p =>
      p.classList.toggle('ativo', p.dataset.cidade === nome));
    const hosp = c.hospitais.length
      ? `<div class="hospitais"><p class="rotulo">Hospitais na cidade</p><ul>` +
        c.hospitais.map(h => `<li>${esc(h.n)}${h.e ? ` <em>· ${esc(h.e)}</em>` : ''}</li>`).join('') +
        `</ul></div>`
      : `<p class="sem-hosp">Sem hospital credenciado na cidade. Consultas e exames resolvem aqui;
         internação e urgência ficam em Ponta Grossa.</p>`;
    $('#dossie').innerHTML = `
      <p class="uf">Paraná · Campos Gerais</p>
      <h2>${esc(c.nome)}</h2>
      <p class="resumo">${plural(c.total, 'prestador credenciado', 'prestadores credenciados')} e
        ${plural(c.especialidades, 'especialidade', 'especialidades')} na cidade.</p>
      <div class="numeros">
        <div><b>${c.hosp || '—'}</b><span>Hospitais</span></div>
        <div><b>${c.lab || '—'}</b><span>Laboratórios</span></div>
        <div><b>${c.img || '—'}</b><span>Imagem</span></div>
        <div><b>${c.clin || '—'}</b><span>Clínicas</span></div>
        <div><b>${c.prof || '—'}</b><span>Médicos</span></div>
        <div><b>${c.total}</b><span>No total</span></div>
      </div>
      ${hosp}
      <a class="botao" href="${esc(c.pdf)}" download>Baixar o guia de ${esc(c.nome)} <span>PDF · ${c.kb} KB</span></a>`;
  }
  document.querySelectorAll('.ponto').forEach(p => {
    p.addEventListener('click', () => abrirCidade(p.dataset.cidade));
    p.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); abrirCidade(p.dataset.cidade); }
    });
  });
  abrirCidade('Ponta Grossa');

  /* ---------------- galeria de guias ---------------- */
  const cartao = (o) => `<a class="guia${o.destaque ? ' destaque' : ''}" href="${esc(o.href)}" download>
      <div class="capa">
        <img src="${esc(o.capa)}" alt="Capa do guia ${esc(o.titulo)}" loading="lazy" decoding="async">
        <span class="baixar">Baixar <span>PDF · ${o.kb} KB</span></span>
      </div>
      <div class="corpo">
        <h3>${esc(o.titulo)}</h3>
        <p class="linha-num">${o.numeros}</p>
        <span class="peso">↓ ${esc(o.acao)}</span>
      </div>
    </a>`;

  const somaCol = f => D.cidades.reduce((a, c) => a + f(c), 0);
  $('#galeria').innerHTML =
    cartao({
      destaque: true, href: 'arquivos/rede-nossa-saude-campos-gerais.pdf',
      capa: 'img/capas/capa-regiao.jpg', titulo: 'Campos Gerais · as nove cidades',
      kb: D.regiao.pdf_kb, acao: 'Guia completo da região',
      numeros: `<span><b>${total}</b> prestadores</span><span><b>${somaCol(c => c.hosp)}</b> hospitais</span>` +
               `<span><b>9</b> cidades</span>`
    }) +
    D.cidades.map(c => cartao({
      href: c.pdf, capa: c.capa, titulo: c.nome, kb: c.kb, acao: 'Baixar o guia da cidade',
      numeros: `<span><b>${c.total}</b> prestadores</span>` +
               (c.hosp ? `<span><b>${c.hosp}</b> ${c.hosp === 1 ? 'hospital' : 'hospitais'}</span>` : '') +
               `<span><b>${c.especialidades}</b> especialidades</span>`
    })).join('');

  $('#extraPlanilha').innerHTML =
    `Precisa filtrar e trabalhar os dados? Baixe a
     <a href="arquivos/rede-nossa-saude-campos-gerais.xlsx" download>planilha completa em XLSX</a>
     (${D.regiao.xlsx_kb} KB), com uma aba por cidade.`;

  /* ---------------- tabela das cidades ---------------- */
  const cel = v => `<td class="${v ? '' : 'zero'}">${v || '—'}</td>`;
  $('#tabCidades').innerHTML =
    `<thead><tr><th>Cidade</th><th>Hospitais</th><th>Laboratórios</th><th>Imagem</th>
      <th class="esconde-mobile">Clínicas</th><th class="esconde-mobile">Médicos</th>
      <th>Total</th><th>Guia</th></tr></thead><tbody>` +
    D.cidades.map(c => `<tr>
        <td><span class="cid">${esc(c.nome)}</span>
            <span class="cid-sub">${plural(c.especialidades, 'especialidade', 'especialidades')}</span></td>
        ${cel(c.hosp)}${cel(c.lab)}${cel(c.img)}
        <td class="esconde-mobile${c.clin ? '' : ' zero'}">${c.clin || '—'}</td>
        <td class="esconde-mobile${c.prof ? '' : ' zero'}">${c.prof || '—'}</td>
        <td class="tot">${c.total}</td>
        <td><a class="baixa" href="${esc(c.pdf)}" download>baixar</a></td>
      </tr>`).join('') +
    `</tbody><tfoot><tr>
        <td><span class="cid">Nove cidades</span></td>
        <td>${somaCol(c => c.hosp)}</td><td>${somaCol(c => c.lab)}</td><td>${somaCol(c => c.img)}</td>
        <td class="esconde-mobile">${somaCol(c => c.clin)}</td>
        <td class="esconde-mobile">${somaCol(c => c.prof)}</td>
        <td class="tot">${total}</td><td></td>
      </tr></tfoot>`;

  /* ---------------- mapa de calor ---------------- */
  const contaExame = (nat, cid) => D.itens.filter(i => i.nat.includes(nat) && i.c === cid).length;
  const maiorExame = Math.max(...D.exames.flatMap(n => D.ordem.map(c => contaExame(n, c))));
  const wash = n => n ? `background:rgba(var(--laranja-rgb), ${(0.10 + 0.62 * n / maiorExame).toFixed(3)})` : '';
  $('#tabExames').innerHTML =
    '<thead><tr><th>Natureza do exame</th>' +
    D.ordem.map(c => `<th>${esc(c)}</th>`).join('') + '<th>Total</th></tr></thead><tbody>' +
    D.exames.map(nat => {
      const linha = D.ordem.map(c => {
        const n = contaExame(nat, c);
        return `<td><span class="celula${n ? '' : ' vazio'}" style="${wash(n)}">${n || '·'}</span></td>`;
      }).join('');
      const t = D.itens.filter(i => i.nat.includes(nat)).length;
      return `<tr><td>${esc(nat)}</td>${linha}<td><span class="celula">${t}</span></td></tr>`;
    }).join('') + '</tbody>';
  $('#tabExames').insertAdjacentHTML('afterend',
    `<p class="legenda-calor">Menos
       <i style="${wash(1)}"></i><i style="${wash(Math.ceil(maiorExame / 3))}"></i>
       <i style="${wash(Math.ceil(maiorExame * 2 / 3))}"></i><i style="${wash(maiorExame)}"></i>
       Mais prestadores</p>`);

  /* ---------------- busca ---------------- */
  let st = {q: '', cidade: '', esp: '', cats: new Set()};
  D.ordem.forEach(c => $('#fcidade').insertAdjacentHTML('beforeend', `<option>${esc(c)}</option>`));
  [...new Set(D.itens.flatMap(i => i.e))].sort((a, b) => a.localeCompare(b, 'pt'))
    .forEach(e => $('#fesp').insertAdjacentHTML('beforeend', `<option>${esc(e)}</option>`));
  $('#chips').innerHTML = D.cats.map(k =>
    `<button class="chip" type="button" data-cat="${esc(k)}">${esc(D.catcurta[k])}</button>`).join('');

  function render() {
    const q = norm(st.q).split(/\s+/).filter(Boolean);
    const sel = D.itens.filter(i =>
      (!st.cidade || i.c === st.cidade) &&
      (!st.esp || i.e.includes(st.esp)) &&
      (!st.cats.size || st.cats.has(i.k)) &&
      q.every(t => i._b.includes(t)));
    $('#contagem').textContent = sel.length === total
      ? total + ' prestadores nas nove cidades'
      : sel.length + ' de ' + total + ' prestadores';
    const grupos = new Map(D.ordem.map(c => [c, []]));
    sel.forEach(i => grupos.get(i.c).push(i));
    let h = '';
    for (const c of D.ordem) {
      const lst = grupos.get(c);
      if (!lst.length) continue;
      lst.sort((a, b) => D.cats.indexOf(a.k) - D.cats.indexOf(b.k) || a.n.localeCompare(b.n, 'pt'));
      const cid = porCidade(c);
      h += `<section class="cidade-bloco"><header><h3>${esc(c)}</h3>
              <span class="qtd">${plural(lst.length, 'prestador', 'prestadores')}</span>
              <a class="baixa" href="${esc(cid.pdf)}" download>guia em PDF</a></header>`;
      for (const i of lst) {
        const mapa = i.end.length
          ? `<a href="https://maps.google.com/?q=${encodeURIComponent(i.end[0] + ' ' + i.c + ' PR')}" target="_blank" rel="noopener">ver no mapa</a>`
          : '';
        h += `<article class="verbete">
          <div>
            <p class="tipo"><span>${esc(D.catcurta[i.k])} · ${esc(i.t)}</span>${i.int ? '<span class="marca-int">Internação</span>' : ''}</p>
            <h4>${esc(i.n)}</h4>
            ${i.rz ? `<p class="doc">${esc(i.rz)}</p>` : ''}
            ${i.doc ? `<p class="doc">${esc(i.doc)}</p>` : ''}
          </div>
          <div>
            <p class="especialidades">${i.e.length ? esc(i.e.join(' · ')) : '—'}</p>
            ${i.cc.length ? `<p class="corpo">Corpo clínico: ${esc(i.cc.slice(0, 6).join(', '))}${i.cc.length > 6 ? ' e mais ' + (i.cc.length - 6) : ''}</p>` : ''}
          </div>
          <div class="contato">
            ${i.end.map(e => `<p>${esc(e)}</p>`).join('') || '<p>Endereço não informado</p>'}
            <p class="fone-lista">${i.tel.length
              ? i.tel.map(t => `<a href="tel:${t.replace(/\D/g, '')}">${esc(t)}</a>`).join(' · ')
              : 'Telefone não informado'}</p>
            ${mapa ? `<p>${mapa}</p>` : ''}
          </div>
        </article>`;
      }
      h += '</section>';
    }
    $('#lista').innerHTML = h || '<p class="vazio">Nenhum prestador encontrado com esses filtros.</p>';
  }
  $('#q').addEventListener('input', e => { st.q = e.target.value; render(); });
  $('#fcidade').addEventListener('change', e => { st.cidade = e.target.value; render(); });
  $('#fesp').addEventListener('change', e => { st.esp = e.target.value; render(); });
  $('#chips').addEventListener('click', e => {
    const b = e.target.closest('[data-cat]'); if (!b) return;
    const k = b.dataset.cat;
    st.cats.has(k) ? st.cats.delete(k) : st.cats.add(k);
    b.classList.toggle('on'); render();
  });
  $('#limpar').addEventListener('click', () => {
    st = {q: '', cidade: '', esp: '', cats: new Set()};
    $('#q').value = ''; $('#fcidade').value = ''; $('#fesp').value = '';
    document.querySelectorAll('.chip').forEach(b => b.classList.remove('on'));
    render();
  });
  render();

  /* ---------------- sobre ---------------- */
  $('#txtSobre').innerHTML = `
    <p>Este é o levantamento da rede credenciada da <strong>${esc(m.operadora)}</strong> nas nove
      cidades dos Campos Gerais atendidas pela operadora: ${esc(D.ordem.join(', '))}.</p>
    <h3>Todos os planos numa lista só</h3>
    <p>A Nossa Saúde tem produtos diferentes, e alguns usam redes credenciadas diferentes. Aqui eles
      aparecem somados: se um prestador está na lista, ele é credenciado da operadora naquela cidade
      por algum plano.</p>
    <p class="nota">${esc(m.aviso)}</p>
    <h3>Como foi levantado</h3>
    <p>Direto da rede credenciada oficial da operadora, cidade por cidade, sem filtro de plano. Os
      documentos gerados pelo próprio sistema da Nossa Saúde foram lidos e reorganizados por
      hospital, natureza de exame, clínica e especialidade médica — é essa organização que você
      encontra nos guias em PDF.</p>
    <h3>Fonte</h3>
    <p>${esc(m.fonte)} Imagens de satélite: ${esc(m.satelite)}.</p>`;

  $('#sbQuem').textContent = m.corretor;
  $('#sbZap').href = zap;
  $('#sbMail').href = 'mailto:' + m.mail;
  $('#sbMail').textContent = m.mail;
  $('#sbFonte').textContent = 'Material informativo. A contratação e as condições de cada plano ' +
    'seguem as regras da operadora e da ANS.';
  $('#rdRegistro').textContent = m.razao + ' · CNPJ ' + m.cnpj;
  $('#rdAviso').textContent = m.fonte + ' ' + m.aviso;
})();
"""

README = """# Atlas da Rede Nossa Saúde — Campos Gerais

Site estático com a rede credenciada da **Nossa Saúde** nas 9 cidades dos Campos Gerais / PR:
Ponta Grossa, Telêmaco Borba, Jaguariaíva, Castro, Irati, Palmeira, Carambeí, Prudentópolis e
Piraí do Sul.

**No ar em:** https://dallalbacorretor-a11y.github.io/rede-nossa-saude/

Publicado por **Mazza Broker** — {corretor} · {tel} · {mail}

## O que tem

- Mapa de satélite da região com as nove cidades: clique numa e veja os números e os hospitais dela
- **Galeria de guias** — a capa de cada PDF, clique para baixar
- Mapa de calor de onde fazer cada natureza de exame
- Busca por prestador, especialidade, bairro ou cidade

## Números

| | |
|---|---|
| Prestadores | {total} |
| Cidades | 9 |
| Hospitais para internação | {hosp} |
| Consulta | {data} |

> {aviso}

{fonte}

Imagens de satélite: {satelite}.

## Estrutura

```
index.html   estilo.css   app.js   dados.js      (dados em window.DADOS)
img/                 satélite da região
img/capas/           capa de cada guia
arquivos/            PDF da região e planilha
arquivos/cidades/    um PDF por cidade
_scripts/            pipeline que baixa a rede e regera tudo (ver _scripts/LEIAME.md)
```

Sem build: HTML, CSS e JS puros. GitHub Pages em `main`, pasta raiz.
"""


def main():
    guardar = {}
    for sub in ('arquivos', 'img'):
        origem = os.path.join(SITE, sub)
        if os.path.isdir(origem):
            destino = os.path.join(AQUI, '_tmp_' + sub)
            shutil.rmtree(destino, ignore_errors=True)
            shutil.move(origem, destino)
            guardar[sub] = destino
    shutil.rmtree(SITE, ignore_errors=True)
    os.makedirs(SITE, exist_ok=True)
    for sub, destino in guardar.items():
        shutil.move(destino, os.path.join(SITE, sub))

    open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(INDEX)
    open(os.path.join(SITE, 'estilo.css'), 'w', encoding='utf-8').write(CSS)
    open(os.path.join(SITE, 'app.js'), 'w', encoding='utf-8').write(APP)
    open(os.path.join(SITE, 'dados.js'), 'w', encoding='utf-8').write(
        'window.DADOS = ' + json.dumps(PAYLOAD, ensure_ascii=False, separators=(',', ':')) + ';\n')
    open(os.path.join(SITE, '.nojekyll'), 'w').write('')
    open(os.path.join(SITE, 'README.md'), 'w', encoding='utf-8').write(README.format(
        corretor=META['corretor'], tel=META['tel'], mail=META['mail'], total=len(itens),
        hosp=sum(1 for i in ITENS if i['internacao']), data=META['data'],
        aviso=META['aviso'], fonte=META['fonte'], satelite=META['satelite']))
    print('site gerado | satélite %dx%d | %d cidades no mapa'
          % (SAT['largura'], SAT['altura'], len(cidades)))
    for c in cidades:
        print('  %-16s px(%7.1f, %7.1f)' % (c['nome'], c['x'], c['y']))


if __name__ == '__main__':
    main()
