# -*- coding: utf-8 -*-
"""Site estático (GitHub Pages) — rede única da Nossa Saúde nos Campos Gerais, download por cidade."""
import os, sys, json, shutil, re, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

AQUI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(AQUI, 'site')
D = json.load(open(os.path.join(AQUI, 'dados_unico.json'), encoding='utf-8'))
IND = json.load(open(os.path.join(AQUI, 'indice_cidades.json'), encoding='utf-8'))
ITENS, CIDADES, EXAMES = D['itens'], D['cidades'], D['exames']

META = {
    'operadora': 'Nossa Saúde', 'cnpj': '02.862.447/0001-03', 'regiao': 'Campos Gerais / PR',
    'data': '10 de setembro de 2026',
    'corretor': 'Alan Vinicius Dall Alba', 'tel': '(41) 99547-6715', 'whats': '5541995476715',
    'mail': 'alan.vinicius@mazzabroker.com.br',
    'fonte': ('Rede Credenciada oficial da Nossa Saúde (prestador.nossasaude.com.br), consultada em '
              '10 de setembro de 2026, sem filtro de plano.'),
    'aviso': ('A rede credenciada é definida e alterada exclusivamente pela operadora. Esta lista '
              'soma todos os planos da Nossa Saúde — antes de contratar, confirme no portal da '
              'operadora se o prestador atende o plano específico.'),
}
CATS = ['Hospitais e Pronto-Socorro', 'Clínicas e Centros Médicos',
        'Laboratórios e Imagem', 'Profissionais (médicos e demais)']
CAT_CURTA = {CATS[0]: 'Hospitais', CATS[1]: 'Clínicas', CATS[2]: 'Labs e imagem',
             CATS[3]: 'Médicos'}


def slug(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-').lower()


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
    cidades.append({
        'nome': it['cidade'], 'slug': it['slug'], 'pdf': 'arquivos/cidades/rede-nossa-saude-%s.pdf' % it['slug'],
        'kb': it['kb'], 'total': len(lst),
        'hosp': sum(1 for i in lst if i['internacao']),
        'lab': sum(1 for i in lst if i['naturezas'] and not i['internacao']),
        'clin': sum(1 for i in lst if i['categoria'] == CATS[1]),
        'prof': sum(1 for i in lst if i['categoria'] == CATS[3]),
        'hospitais': [i['nome_exib'] for i in lst if i['internacao']],
    })

PAYLOAD = {'meta': META, 'cidades': cidades, 'ordem': CIDADES, 'cats': CATS,
           'catcurta': CAT_CURTA, 'exames': EXAMES, 'itens': itens}

# ---------------------------------------------------------------- html
INDEX = r"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rede Credenciada Nossa Saúde — Campos Gerais | Mazza Broker</title>
<meta name="description" content="Baixe a rede credenciada da Nossa Saúde da sua cidade: hospitais, laboratórios, exames de imagem, clínicas e médicos em Ponta Grossa, Telêmaco Borba, Jaguariaíva, Castro, Irati, Palmeira, Carambeí, Prudentópolis e Piraí do Sul.">
<meta name="theme-color" content="#0D2A4F">
<meta property="og:title" content="Rede Credenciada Nossa Saúde — Campos Gerais">
<meta property="og:description" content="A rede da Nossa Saúde nas 9 cidades dos Campos Gerais, com PDF pronto para baixar por cidade.">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='18' fill='%230D2A4F'/><rect y='0' width='100' height='11' fill='%232733C4'/><path d='M50 80C35 67 23 57 23 44a15 15 0 0 1 27-9 15 15 0 0 1 27 9c0 13-12 23-27 36z' fill='%239A7513'/></svg>">
<link rel="stylesheet" href="estilo.css">
</head>
<body>

<header class="capa">
  <div class="wrap">
    <div class="eyebrow"><i></i>CAMPOS GERAIS · PARANÁ</div>
    <h1>Rede Credenciada<em>Nossa Saúde</em></h1>
    <div class="regua"></div>
    <p class="lead">Todos os planos da operadora somados numa lista só. Escolha a sua cidade,
       baixe o PDF e consulte hospitais, laboratórios, exames de imagem, clínicas e médicos.</p>
    <div class="kpis" id="kpis"></div>
    <div class="assina">
      <span class="tag"><b>Mazza</b><i>B R O K E R</i></span>
      <div class="quem"><b id="aQuem"></b><span id="aContato"></span></div>
    </div>
  </div>
</header>

<nav class="abas"><div class="wrap">
  <button class="aba on" data-aba="cidades">Baixar por cidade</button>
  <button class="aba" data-aba="buscar">Buscar na rede</button>
  <button class="aba" data-aba="sobre">Sobre</button>
</div></nav>

<section id="pane-cidades" class="pane"><div class="wrap">
  <h2 class="sec"><i></i>Baixe a rede da sua cidade</h2>
  <p class="sub">Um PDF por cidade, no padrão dos materiais da Mazza Broker: rede em números,
     hospitais, exames por natureza, clínicas e médicos por especialidade.</p>
  <div class="grade-cid" id="gradeCid"></div>

  <h2 class="sec"><i></i>A região inteira</h2>
  <p class="sub">As nove cidades num documento só, com as tabelas separadas por cidade dentro de
     cada especialidade.</p>
  <div class="grade-extra" id="gradeExtra"></div>

  <h2 class="sec"><i></i>A rede em números</h2>
  <div class="scroll"><table class="tab" id="tabCid"></table></div>

  <h2 class="sec"><i></i>Exames e diagnóstico</h2>
  <p class="sub">Quantos prestadores realizam cada natureza de exame em cada cidade.</p>
  <div class="scroll"><table class="tab" id="tabExames"></table></div>
</div></section>

<section id="pane-buscar" class="pane" hidden>
  <div class="barra"><div class="wrap">
    <input type="search" id="q" placeholder="Buscar hospital, laboratório, médico, especialidade, bairro…">
    <select id="fcidade"><option value="">Todas as cidades</option></select>
    <select id="fesp"><option value="">Todas as especialidades</option></select>
    <button class="btn" id="limpar">Limpar</button>
    <div class="chips" id="chips"></div>
  </div></div>
  <div class="wrap">
    <div class="cont" id="cont"></div>
    <div id="lista"></div>
  </div>
</section>

<section id="pane-sobre" class="pane" hidden><div class="wrap">
  <h2 class="sec"><i></i>Sobre este material</h2>
  <div class="texto" id="txtSobre"></div>
  <h2 class="sec"><i></i>Todos os downloads</h2>
  <div class="grade-extra" id="gradeTodos"></div>
</div></section>

<footer class="rodape"><div class="wrap">
  <span class="tag"><b>Mazza</b><i>B R O K E R</i></span>
  <div class="quem"><b id="rQuem"></b><span id="rContato"></span></div>
  <p class="mini" id="rFonte"></p>
</div></footer>

<a class="whats" id="btnWhats" target="_blank" rel="noopener" aria-label="Falar no WhatsApp">
  <svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5.1-1.3A10 10 0 1 0 12 2zm0 2a8 8 0 1 1-4.1 14.9l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 0 1 12 4zm-3 4c-.3 0-.6.1-.8.4-.3.3-.9.9-.9 2.1s.9 2.4 1 2.6c.1.2 1.7 2.8 4.3 3.8 2.1.8 2.6.7 3 .6.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.3.2-1.4l-.6-.3-1.8-.9c-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.5 6.5 0 0 1-3.2-2.8c-.1-.2 0-.4.1-.5l.5-.6.2-.4v-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4H9z"/></svg>
</a>

<script src="dados.js"></script>
<script src="app.js"></script>
</body>
</html>
"""

CSS = r""":root{
  --navy:#0D2A4F; --navy2:#16375F; --royal:#2733C4; --ouro:#9A7513; --ouro-cl:#C8A24A;
  --bg:#FFFFFF; --bg2:#F7F8FB; --card:#FFFFFF; --txt:#1A2432; --txt2:#4A5568; --txt3:#89909C;
  --borda:#E2E6EC; --sombra:0 1px 2px rgba(13,42,79,.06),0 2px 6px rgba(13,42,79,.05);
}
@media (prefers-color-scheme:dark){:root{
  --bg:#0B1220; --bg2:#111A2B; --card:#131D30; --txt:#E9EEF6; --txt2:#AFBBCC; --txt3:#7A8699;
  --borda:#22304A; --sombra:0 1px 2px rgba(0,0,0,.4);
}}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--txt);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
img{max-width:100%}
.wrap{max-width:1160px;margin:0 auto;padding:0 20px}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}

/* ---------- capa ---------- */
.capa{background:var(--navy);color:#fff;padding:0 0 34px;position:relative;overflow:hidden}
.capa::before{content:"";position:absolute;inset:0 0 auto 0;height:13px;background:var(--royal)}
.capa::after{content:"";position:absolute;top:13px;left:0;right:0;height:4px;background:var(--ouro)}
.capa .wrap{padding-top:64px;position:relative}
.eyebrow{display:flex;align-items:center;gap:9px;font-size:11px;font-weight:700;
  letter-spacing:.16em;color:var(--ouro-cl)}
.eyebrow i{display:block;width:3px;height:12px;background:var(--ouro-cl)}
h1{font-family:Georgia,"Times New Roman",serif;font-size:clamp(30px,6.4vw,46px);margin:12px 0 0;
  line-height:1.08;font-weight:700}
h1 em{display:block;color:var(--ouro-cl);font-style:italic;font-weight:400;
  font-size:clamp(24px,5vw,36px);margin-top:2px}
.regua{width:224px;height:1px;background:#5C7291;margin:22px 0 16px}
.lead{color:#A9BAD1;max-width:600px;font-size:14.5px;margin:0}
.kpis{display:flex;flex-wrap:wrap;gap:0;margin:28px 0 0;border:1px solid #26456E;border-radius:4px}
.kpi{flex:1 1 33.33%;min-width:150px;padding:14px 18px;border-right:1px solid #26456E;
  border-bottom:1px solid #26456E}
.kpi b{display:block;font-family:Georgia,serif;font-size:26px;line-height:1.1}
.kpi span{font-size:11px;color:#8FA3BE}
.assina{display:flex;align-items:center;gap:14px;margin-top:30px;flex-wrap:wrap}
.tag{display:inline-flex;flex-direction:column;justify-content:center;background:var(--ouro);
  color:#fff;padding:6px 20px 6px 12px;clip-path:polygon(0 0,100% 0,calc(100% - 11px) 50%,100% 100%,0 100%);
  padding-right:26px}
.tag b{font-family:Georgia,serif;font-size:15px;line-height:1.05}
.tag i{font-style:normal;font-size:7px;font-weight:700;letter-spacing:.08em}
.quem b{display:block;font-size:13.5px;font-weight:600}
.quem span{font-size:12.5px;color:#8FA3BE}
.capa .quem b{color:#fff}

/* ---------- abas ---------- */
.abas{background:var(--navy2);position:sticky;top:0;z-index:30}
.abas .wrap{display:flex;gap:2px;overflow-x:auto}
.aba{flex:0 0 auto;font:inherit;font-size:13.5px;color:#A9BAD1;background:none;border:0;
  border-bottom:3px solid transparent;padding:13px 16px;cursor:pointer;white-space:nowrap}
.aba:hover{color:#fff}
.aba.on{color:#fff;border-bottom-color:var(--ouro);font-weight:600}
.pane{padding-bottom:20px}

/* ---------- títulos ---------- */
.sec{display:flex;align-items:center;gap:11px;font-family:Georgia,serif;font-size:21px;
  margin:38px 0 4px;font-weight:700}
.sec i{display:block;width:3.4px;height:19px;background:var(--ouro);flex:0 0 auto}
.sub{color:var(--txt3);font-size:13px;margin:0 0 4px 15px;max-width:760px}

/* ---------- cards de cidade ---------- */
.grade-cid{display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));gap:14px;margin-top:18px}
.ccid{background:var(--card);border:1px solid var(--borda);border-top:3px solid var(--navy);
  border-radius:6px;padding:16px 18px 14px;box-shadow:var(--sombra);display:flex;flex-direction:column}
.ccid h3{font-family:Georgia,serif;font-size:19px;margin:0}
.ccid .uf{font-size:11px;color:var(--txt3);letter-spacing:.1em;font-weight:700}
.ccid .n{display:flex;gap:16px;margin:12px 0 10px;flex-wrap:wrap}
.ccid .n div{font-size:11.5px;color:var(--txt3);line-height:1.25}
.ccid .n b{display:block;font-family:Georgia,serif;font-size:19px;color:var(--navy);font-weight:700}
.ccid .hosp{font-size:12px;color:var(--txt2);border-top:1px solid var(--borda);padding-top:9px;
  margin-bottom:12px;flex:1}
.ccid .hosp em{color:var(--txt3);font-style:normal}
.baixar{display:flex;align-items:center;justify-content:space-between;gap:8px;
  background:var(--navy);color:#fff;text-decoration:none;border-radius:4px;
  padding:10px 14px;font-size:13px;font-weight:600}
.baixar:hover{background:var(--royal)}
.baixar span{font-size:11px;font-weight:400;color:#A9BAD1}
.grade-extra{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin-top:16px}
.dl{display:block;background:var(--card);border:1px solid var(--borda);border-left:3px solid var(--ouro);
  border-radius:6px;padding:14px 16px;text-decoration:none;color:inherit;box-shadow:var(--sombra)}
.dl:hover{border-color:var(--ouro)}
.dl b{display:block;font-size:14px;margin-bottom:2px}
.dl span{font-size:12px;color:var(--txt3)}

/* ---------- tabelas ---------- */
.tab{border-collapse:collapse;width:100%;font-size:13px;margin-top:16px}
.tab th{background:var(--navy);color:#fff;text-align:left;padding:9px 12px;font-size:10.5px;
  text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;font-weight:700}
.tab td{padding:8px 12px;border-bottom:1px solid var(--borda)}
.tab tbody tr:nth-child(even) td{background:var(--bg2)}
.tab tbody tr:last-child td{border-bottom:0}
.tab .num{text-align:center}
.tab .zero{color:var(--txt3)}
.tab tfoot td{background:var(--ouro);color:#fff;font-weight:700;border:0}

/* ---------- busca ---------- */
.barra{background:var(--card);border-bottom:1px solid var(--borda);box-shadow:var(--sombra);
  padding:14px 0;margin-bottom:4px}
.barra .wrap{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
input[type=search],select{font:inherit;font-size:14px;color:var(--txt);background:var(--bg2);
  border:1px solid var(--borda);border-radius:5px;padding:9px 12px;max-width:100%}
input[type=search]{flex:1 1 240px;min-width:180px}
.btn{font:inherit;font-size:13px;border:1px solid var(--borda);background:var(--bg2);color:var(--txt2);
  border-radius:999px;padding:7px 14px;cursor:pointer}
.btn:hover{border-color:var(--ouro);color:var(--ouro)}
.btn.on{background:var(--navy);border-color:var(--navy);color:#fff}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.cont{font-size:12.5px;color:var(--txt3);margin:18px 0 0}
.cidade{display:flex;align-items:baseline;gap:10px;font-family:Georgia,serif;font-size:20px;
  margin:30px 0 0;padding-left:11px;border-left:3.4px solid var(--ouro)}
.cidade small{font-size:12px;color:var(--txt3);font-family:inherit}
.grade{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;margin-top:14px}
.card{background:var(--card);border:1px solid var(--borda);border-radius:6px;padding:14px 16px;
  box-shadow:var(--sombra)}
.card h3{margin:0;font-size:14.5px;line-height:1.3}
.rz{font-size:11.5px;color:var(--txt3);margin-top:2px}
.selo{display:inline-block;font-size:9.5px;font-weight:700;letter-spacing:.06em;color:#fff;
  background:var(--ouro);border-radius:3px;padding:2px 7px;margin-bottom:6px}
.selo.cat{background:var(--navy)}
.esp{margin:9px 0 0}
.esp span{display:inline-block;background:var(--bg2);border:1px solid var(--borda);color:var(--txt2);
  border-radius:4px;padding:2px 7px;margin:0 4px 4px 0;font-size:11px}
.lin{margin:7px 0 0;font-size:12.5px;color:var(--txt2)}
.lin a{color:var(--royal);text-decoration:none}
.lin a:hover{text-decoration:underline}
.lin b{color:var(--txt)}
.cc{margin-top:8px;font-size:11.5px;color:var(--txt3)}
.vazio{padding:44px 0;text-align:center;color:var(--txt3)}

/* ---------- texto / rodapé ---------- */
.texto{font-size:14px;color:var(--txt2);max-width:820px;margin-top:14px}
.texto h4{font-size:14px;color:var(--txt);margin:18px 0 4px}
.texto p{margin:6px 0}
.destaque{background:var(--bg2);border-left:3.4px solid var(--ouro);padding:14px 16px;
  border-radius:0 5px 5px 0;margin:16px 0}
.rodape{background:var(--navy);color:#8FA3BE;margin-top:46px;padding:28px 0 96px;font-size:12.5px}
.rodape .wrap{display:flex;flex-wrap:wrap;gap:16px;align-items:center}
.rodape .quem b{color:#fff}
.rodape a{color:var(--ouro-cl);text-decoration:none}
.mini{flex:1 1 100%;font-size:11.5px;color:#6B7C93;margin:6px 0 0}
.whats{position:fixed;right:16px;bottom:16px;width:54px;height:54px;border-radius:50%;
  background:#25D366;color:#fff;display:flex;align-items:center;justify-content:center;
  box-shadow:0 4px 14px rgba(0,0,0,.28);z-index:40}
@media (max-width:640px){
  .kpi{flex:1 1 50%}
  .capa .wrap{padding-top:44px}
  select{flex:1 1 100%}
}
@media print{.abas,.barra,.whats{display:none}}
"""

APP = r"""(function () {
  const D = window.DADOS, m = D.meta;
  const $ = s => document.querySelector(s);
  const esc = s => (s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const norm = s => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const plural = (n, s, p) => n + ' ' + (n === 1 ? s : p);

  D.itens.forEach(i => {
    i._b = norm([i.n, i.rz, i.t, i.doc, i.e.join(' '), i.end.join(' '), i.cc.join(' '), i.c].join(' '));
  });
  const total = D.itens.length;
  const nCat = k => D.itens.filter(i => i.k === k).length;
  const nHosp = D.itens.filter(i => i.int).length;
  const nLab = D.itens.filter(i => i.nat.length && !i.int).length;

  /* ---------------- topo ---------------- */
  $('#kpis').innerHTML = [
    [total, 'prestadores credenciados'], [D.ordem.length, 'cidades atendidas'],
    [nHosp, 'hospitais para internação'], [nLab, 'laboratórios e imagem'],
    [nCat(D.cats[1]), 'clínicas e centros médicos'], [nCat(D.cats[3]), 'médicos e profissionais']
  ].map(([v, r]) => `<div class="kpi"><b>${v}</b><span>${r}</span></div>`).join('');

  const contato = `<a href="https://wa.me/${m.whats}">${esc(m.tel)}</a> · <a href="mailto:${m.mail}">${esc(m.mail)}</a>`;
  $('#aQuem').textContent = m.corretor;
  $('#aContato').innerHTML = contato;
  $('#rQuem').textContent = m.corretor + ' · corretor de saúde';
  $('#rContato').innerHTML = contato;
  $('#rFonte').textContent = m.fonte + ' ' + m.aviso;
  $('#btnWhats').href = 'https://wa.me/' + m.whats + '?text=' +
    encodeURIComponent('Olá Alan! Vi a rede credenciada da Nossa Saúde e quero saber mais.');

  /* ---------------- abas ---------------- */
  document.querySelectorAll('.aba').forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll('.aba').forEach(x => x.classList.toggle('on', x === b));
    document.querySelectorAll('.pane').forEach(p => { p.hidden = p.id !== 'pane-' + b.dataset.aba; });
    window.scrollTo({top: 0, behavior: 'smooth'});
    history.replaceState(null, '', '#' + b.dataset.aba);
  }));

  /* ---------------- cards de cidade ---------------- */
  $('#gradeCid').innerHTML = D.cidades.map(c => {
    const hosp = c.hospitais.length
      ? esc(c.hospitais.join(' · '))
      : '<em>Sem hospital credenciado na cidade — internação em Ponta Grossa.</em>';
    return `<article class="ccid">
      <div class="uf">PARANÁ</div>
      <h3>${esc(c.nome)}</h3>
      <div class="n">
        <div><b>${c.total}</b>prestadores</div>
        <div><b>${c.hosp || '—'}</b>hospitais</div>
        <div><b>${c.lab || '—'}</b>labs e imagem</div>
        <div><b>${c.prof || '—'}</b>médicos</div>
      </div>
      <div class="hosp">${hosp}</div>
      <a class="baixar" href="${esc(c.pdf)}" download>Baixar o PDF <span>${c.kb} KB</span></a>
    </article>`;
  }).join('');

  const EXTRAS = [
    {href: 'arquivos/rede-nossa-saude-campos-gerais.pdf', tit: 'PDF da região inteira',
     desc: 'As nove cidades num documento só, separadas por cidade dentro de cada especialidade.'},
    {href: 'arquivos/rede-nossa-saude-campos-gerais.xlsx', tit: 'Planilha completa (XLSX)',
     desc: 'Todos os prestadores em tabela, com uma aba por cidade — para filtrar e trabalhar.'},
  ];
  const cartao = d => `<a class="dl" href="${esc(d.href)}" download><b>${esc(d.tit)}</b><span>${esc(d.desc)}</span></a>`;
  $('#gradeExtra').innerHTML = EXTRAS.map(cartao).join('');
  $('#gradeTodos').innerHTML = EXTRAS.map(cartao).join('') +
    D.cidades.map(c => cartao({href: c.pdf, tit: 'Rede de ' + c.nome,
      desc: plural(c.total, 'prestador', 'prestadores') + ' · PDF de ' + c.kb + ' KB'})).join('');

  /* ---------------- tabelas ---------------- */
  const soma = f => D.cidades.reduce((a, c) => a + f(c), 0);
  $('#tabCid').innerHTML =
    '<thead><tr><th>Cidade</th><th class="num">Hospitais</th><th class="num">Labs e imagem</th>' +
    '<th class="num">Clínicas</th><th class="num">Médicos</th><th class="num">Total</th><th>PDF</th></tr></thead><tbody>' +
    D.cidades.map(c => `<tr><td><b>${esc(c.nome)}</b></td>` +
      [c.hosp, c.lab, c.clin, c.prof].map(v => `<td class="num${v ? '' : ' zero'}">${v || '—'}</td>`).join('') +
      `<td class="num"><b>${c.total}</b></td>` +
      `<td><a href="${esc(c.pdf)}" download>baixar</a></td></tr>`).join('') +
    '</tbody><tfoot><tr><td>TOTAL</td>' +
    [c => c.hosp, c => c.lab, c => c.clin, c => c.prof].map(f => `<td class="num">${soma(f)}</td>`).join('') +
    `<td class="num">${total}</td><td></td></tr></tfoot>`;

  $('#tabExames').innerHTML =
    '<thead><tr><th>Natureza do exame</th>' +
    D.ordem.map(c => `<th class="num">${esc(c)}</th>`).join('') + '<th class="num">Total</th></tr></thead><tbody>' +
    D.exames.map(nat => {
      const lst = D.itens.filter(i => i.nat.includes(nat));
      return `<tr><td><b>${esc(nat)}</b></td>` +
        D.ordem.map(c => {
          const n = lst.filter(i => i.c === c).length;
          return `<td class="num${n ? '' : ' zero'}">${n || '—'}</td>`;
        }).join('') + `<td class="num"><b>${lst.length}</b></td></tr>`;
    }).join('') + '</tbody>';

  /* ---------------- busca ---------------- */
  let st = {q: '', cidade: '', esp: '', cats: new Set()};
  D.ordem.forEach(c => $('#fcidade').insertAdjacentHTML('beforeend', `<option>${esc(c)}</option>`));
  [...new Set(D.itens.flatMap(i => i.e))].sort((a, b) => a.localeCompare(b, 'pt'))
    .forEach(e => $('#fesp').insertAdjacentHTML('beforeend', `<option>${esc(e)}</option>`));
  $('#chips').innerHTML = D.cats.map(k =>
    `<button class="btn" data-cat="${esc(k)}">${esc(D.catcurta[k])}</button>`).join('');

  function render() {
    const q = norm(st.q).split(/\s+/).filter(Boolean);
    const sel = D.itens.filter(i =>
      (!st.cidade || i.c === st.cidade) &&
      (!st.esp || i.e.includes(st.esp)) &&
      (!st.cats.size || st.cats.has(i.k)) &&
      q.every(t => i._b.includes(t)));
    $('#cont').textContent = sel.length === total
      ? total + ' prestadores credenciados nas nove cidades'
      : sel.length + ' de ' + total + ' prestadores';

    const porCidade = new Map(D.ordem.map(c => [c, []]));
    sel.forEach(i => porCidade.get(i.c).push(i));
    let h = '';
    for (const c of D.ordem) {
      const lst = porCidade.get(c);
      if (!lst.length) continue;
      lst.sort((a, b) => D.cats.indexOf(a.k) - D.cats.indexOf(b.k) || a.n.localeCompare(b.n, 'pt'));
      const cid = D.cidades.find(x => x.nome === c);
      h += `<h2 class="cidade">${esc(c)}<small>${plural(lst.length, 'prestador', 'prestadores')}` +
           ` · <a href="${esc(cid.pdf)}" download>baixar o PDF da cidade</a></small></h2><div class="grade">`;
      for (const i of lst) {
        const maps = i.end.length
          ? ` <a href="https://maps.google.com/?q=${encodeURIComponent(i.end[0] + ' ' + i.c + ' PR')}" target="_blank" rel="noopener">ver no mapa</a>` : '';
        h += `<div class="card">
          <div><span class="selo cat">${esc(D.catcurta[i.k])}</span>${i.int ? ' <span class="selo">INTERNAÇÃO</span>' : ''}</div>
          <h3>${esc(i.n)}</h3>
          ${i.rz ? `<div class="rz">${esc(i.rz)}</div>` : ''}
          ${i.doc ? `<div class="rz">${esc(i.doc)} · ${esc(i.t)}</div>` : `<div class="rz">${esc(i.t)}</div>`}
          <div class="esp">${i.e.map(e => `<span>${esc(e)}</span>`).join('')}</div>
          ${i.end.map(e => `<div class="lin">${esc(e)}${maps}</div>`).join('')}
          <div class="lin">${i.tel.length
            ? i.tel.map(t => `<b><a href="tel:${t.replace(/\D/g, '')}">${esc(t)}</a></b>`).join(' · ')
            : '<span class="rz">Telefone não informado</span>'}</div>
          ${i.cc.length ? `<div class="cc">Corpo clínico: ${esc(i.cc.slice(0, 8).join(', '))}${i.cc.length > 8 ? ' e mais ' + (i.cc.length - 8) : ''}</div>` : ''}
        </div>`;
      }
      h += '</div>';
    }
    $('#lista').innerHTML = h || '<div class="vazio">Nenhum prestador encontrado com esses filtros.</div>';
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
    document.querySelectorAll('[data-cat]').forEach(b => b.classList.remove('on'));
    render();
  });

  /* ---------------- sobre ---------------- */
  $('#txtSobre').innerHTML = `
    <p>Esta é a rede credenciada da <b>${esc(m.operadora)}</b> (CNPJ ${esc(m.cnpj)}) nas nove cidades
       dos Campos Gerais atendidas pela operadora: ${esc(D.ordem.join(', '))}.</p>
    <h4>Todos os planos numa lista só</h4>
    <p>A Nossa Saúde tem produtos diferentes, e alguns usam redes credenciadas diferentes. Este
       material soma todos eles: se um prestador aparece aqui, ele é credenciado da operadora
       naquela cidade por algum plano.</p>
    <div class="destaque">${esc(m.aviso)}</div>
    <h4>Como foi levantado</h4>
    <p>Direto da rede credenciada oficial da operadora, cidade por cidade, sem filtro de plano.
       Os PDFs oficiais gerados pelo próprio sistema da Nossa Saúde foram lidos e reorganizados
       por hospital, natureza de exame, clínica e especialidade médica.</p>
    <h4>Fonte</h4>
    <p>${esc(m.fonte)}</p>
    <h4>Ficou em dúvida sobre o seu plano?</h4>
    <p>Me chame no WhatsApp <a href="https://wa.me/${m.whats}">${esc(m.tel)}</a> que eu confiro no
       portal da operadora se aquele prestador atende exatamente o seu plano.</p>`;

  /* ---------------- start ---------------- */
  const h = (location.hash || '').replace('#', '');
  const alvo = document.querySelector('.aba[data-aba="' + h + '"]');
  if (alvo) alvo.click();
  render();
})();
"""

README = """# Rede Credenciada Nossa Saúde — Campos Gerais

Site estático com a rede credenciada da **Nossa Saúde** nas 9 cidades dos Campos Gerais / PR:
Ponta Grossa, Telêmaco Borba, Jaguariaíva, Castro, Irati, Palmeira, Carambeí, Prudentópolis e
Piraí do Sul.

**No ar em:** https://dallalbacorretor-a11y.github.io/rede-nossa-saude/

Publicado por **Mazza Broker** — {corretor} · {tel} · {mail}

## O que tem

- **Um PDF por cidade** para baixar e mandar pro cliente, no padrão visual dos materiais da
  corretora: rede em números, hospitais, exames por natureza, clínicas e médicos por especialidade
- PDF da região inteira e planilha XLSX com uma aba por cidade
- Busca por hospital, laboratório, médico, especialidade ou bairro
- Tabelas de cobertura por cidade e por natureza de exame

## Números

| | |
|---|---|
| Prestadores | {total} |
| Cidades | 9 |
| Hospitais para internação | {hosp} |
| Laboratórios e imagem | {lab} |
| Consulta | {data} |

## Todos os planos numa lista só

A operadora tem produtos que usam redes credenciadas diferentes. Este material soma todos eles:
se um prestador aparece aqui, é credenciado da Nossa Saúde naquela cidade por algum plano.

> {aviso}

{fonte}

## Estrutura

```
index.html      estilo.css      app.js      dados.js     (window.DADOS)
arquivos/       xlsx, PDF da região
arquivos/cidades/   um PDF por cidade
_scripts/       pipeline que baixa a rede e regera tudo (ver _scripts/LEIAME.md)
```

Sem build: é HTML/CSS/JS puro. GitHub Pages em `main`, pasta raiz.
"""


def main():
    arquivos = os.path.join(SITE, 'arquivos')
    guardar = None
    if os.path.isdir(arquivos):
        guardar = os.path.join(AQUI, '_arquivos_tmp')
        shutil.rmtree(guardar, ignore_errors=True)
        shutil.move(arquivos, guardar)
    shutil.rmtree(SITE, ignore_errors=True)
    os.makedirs(SITE, exist_ok=True)
    if guardar:
        shutil.move(guardar, arquivos)
    else:
        os.makedirs(arquivos, exist_ok=True)

    open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(INDEX)
    open(os.path.join(SITE, 'estilo.css'), 'w', encoding='utf-8').write(CSS)
    open(os.path.join(SITE, 'app.js'), 'w', encoding='utf-8').write(APP)
    open(os.path.join(SITE, 'dados.js'), 'w', encoding='utf-8').write(
        'window.DADOS = ' + json.dumps(PAYLOAD, ensure_ascii=False, separators=(',', ':')) + ';\n')
    open(os.path.join(SITE, '.nojekyll'), 'w').write('')
    open(os.path.join(SITE, 'README.md'), 'w', encoding='utf-8').write(README.format(
        corretor=META['corretor'], tel=META['tel'], mail=META['mail'], total=len(itens),
        hosp=sum(1 for i in ITENS if i['internacao']),
        lab=sum(1 for i in ITENS if i['naturezas'] and not i['internacao']),
        data=META['data'], aviso=META['aviso'], fonte=META['fonte']))
    print('site gerado | %d prestadores · %d cidades · %d PDFs de cidade'
          % (len(itens), len(cidades), len(os.listdir(os.path.join(arquivos, 'cidades')))))


if __name__ == '__main__':
    main()
