# -*- coding: utf-8 -*-
"""Gera o site estático (GitHub Pages) da rede credenciada Nossa Saúde — Campos Gerais."""
import os, sys, json, shutil, collections
sys.stdout.reconfigure(encoding='utf-8')
import common as C

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
d = C.carregar()
ITENS, REDES, CIDADES = d['itens'], d['redes'], C.CIDADES

# ---------------------------------------------------------------- payload
planos = []
for r in REDES:
    for p in r['planos']:
        txt = p['txt']
        cod = txt.split(' - ')[0].strip()
        nome = txt
        for sep in (' - Individual Familiar', ' - Coletivo Empresarial', ' - Coletivo por Adesão',
                    ' - Coletivo por AdesÃ£o'):
            if sep in nome:
                nome = nome.split(sep)[0]
                break
        nome = nome.replace(cod + ' - ', '').replace(cod + ' -', '').strip(' -') or cod
        tipo = ('Individual / Familiar' if 'Individual' in txt else
                'Coletivo Empresarial' if 'Empresarial' in txt else
                'Coletivo por Adesão' if 'Ades' in txt else '—')
        ans = txt.split('Registro ANS:')[-1].strip() if 'Registro ANS:' in txt else ''
        planos.append({'cod': cod, 'nome': nome, 'tipo': tipo, 'ans': ans, 'rede': r['id']})
planos.sort(key=lambda p: (p['nome'].lower(), p['cod']))

itens = []
for i in ITENS:
    itens.append({
        'c': i['cidade'], 'k': i['categoria'], 't': i['tipo'], 'n': i['nome_exib'],
        'rz': i['razao'] if i['razao'].lower() != i['nome_exib'].lower() else '',
        'doc': ('CNPJ ' + i['cnpj']) if i['cnpj'] else i['conselho'],
        'e': i['esp_exib'], 'end': C.enderecos_txt(i), 'tel': C.tels(i),
        'cc': [m['nome'] for m in i['corpo_clinico']], 'r': i['redes'],
    })
itens.sort(key=lambda x: (CIDADES.index(x['c']), C.CATS.index(x['k']), x['n'].lower()))

PAYLOAD = {
    'meta': {'operadora': C.OPERADORA, 'cnpj': C.OPER_CNPJ, 'regiao': C.REGIAO,
             'data': C.DATA_REF, 'fonte': C.FONTE, 'aviso': C.AVISO,
             'corretor': C.CORRETOR, 'tel': C.CORRETOR_TEL, 'whats': C.CORRETOR_WHATS,
             'mail': C.CORRETOR_MAIL},
    'redes': [{'id': r['id'], 'nome': r['nome'], 'curto': r['curto'], 'cor': r['cor'],
               'desc': r['desc'], 'nplanos': len(r['planos']),
               'ampla': r['id'] in {x['id'] for x in C.redes_amplas(d)},
               'cidades': C.cidades_da_rede(d, r['id'])} for r in REDES],
    'cidades': CIDADES, 'cats': C.CATS, 'catcurta': C.CAT_CURTA, 'catcor': C.CAT_COR,
    'planos': planos, 'itens': itens,
}

# ---------------------------------------------------------------- html
INDEX = r"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rede credenciada Nossa Saúde — Campos Gerais | Mazza Broker</title>
<meta name="description" content="Consulte a rede credenciada da Nossa Saúde nas 9 cidades dos Campos Gerais: hospitais, clínicas, laboratórios e médicos por especialidade, por plano.">
<meta name="theme-color" content="#12233F">
<meta property="og:title" content="Rede credenciada Nossa Saúde — Campos Gerais">
<meta property="og:description" content="Hospitais, clínicas, laboratórios e médicos credenciados em Ponta Grossa, Telêmaco Borba, Jaguariaíva, Castro, Irati, Palmeira, Carambeí, Prudentópolis e Piraí do Sul.">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%2312233F'/><path d='M50 78C36 66 24 56 24 44a15 15 0 0 1 26-10 15 15 0 0 1 26 10c0 12-12 22-26 34z' fill='%23EE6B22'/></svg>">
<link rel="stylesheet" href="estilo.css">
</head>
<body>

<header class="topo">
  <div class="wrap">
    <div class="marca">Mazza Broker · Corretora de saúde</div>
    <h1>Rede credenciada <em>Nossa Saúde</em></h1>
    <p class="lead">Campos Gerais / PR — 9 cidades. Veja onde você é atendido: hospitais, clínicas,
       laboratórios, exames de imagem e médicos por especialidade.</p>
    <div class="kpis" id="kpis"></div>
  </div>
</header>

<nav class="abas"><div class="wrap">
  <button class="aba on" data-aba="rede">Rede credenciada</button>
  <button class="aba" data-aba="comparativo">Comparar redes</button>
  <button class="aba" data-aba="planos">Qual é o meu plano?</button>
  <button class="aba" data-aba="sobre">Sobre / downloads</button>
</div></nav>

<!-- ------------------------------------------------ rede -->
<section id="pane-rede" class="pane">
  <div class="barra"><div class="wrap">
    <input type="search" id="q" placeholder="Buscar hospital, laboratório, médico, especialidade, bairro…">
    <select id="fplano" title="Filtrar pela rede do seu plano"></select>
    <select id="fcidade"><option value="">Todas as cidades</option></select>
    <select id="fesp"><option value="">Todas as especialidades</option></select>
    <button class="btn" id="limpar">Limpar</button>
    <div class="chips" id="chips"></div>
  </div></div>
  <div class="wrap">
    <p class="aviso-rede" id="avisoRede" hidden></p>
    <div class="cont" id="cont"></div>
    <div id="lista"></div>
  </div>
</section>

<!-- ------------------------------------------------ comparativo -->
<section id="pane-comparativo" class="pane" hidden>
  <div class="wrap">
    <h2 class="tit">Comparativo por rede credenciada</h2>
    <p class="sub">Cada produto da Nossa Saúde usa uma rede. Nos Campos Gerais existem três.
       A tabela mostra quais prestadores cada uma alcança.</p>
    <div id="cardsRede" class="cards-rede"></div>

    <h3 class="tit3">Cobertura por cidade</h3>
    <div class="scroll"><table id="tabCid" class="tab"></table></div>

    <h3 class="tit3">Hospitais e pronto-socorro</h3>
    <div class="scroll"><table id="tabHosp" class="tab"></table></div>

    <h3 class="tit3" id="tituloDif">Onde as redes se diferenciam</h3>
    <p class="sub" id="subDif"></p>
    <div class="scroll"><table id="tabDif" class="tab"></table></div>

    <h3 class="tit3" id="tituloRestrita" hidden>Redes de cobertura reduzida</h3>
    <div id="restritas"></div>
  </div>
</section>

<!-- ------------------------------------------------ planos -->
<section id="pane-planos" class="pane" hidden>
  <div class="wrap">
    <h2 class="tit">Qual é o meu plano?</h2>
    <p class="sub">Procure o nome ou o código que aparece na sua carteirinha ou na proposta.
       O site mostra qual rede credenciada aquele plano usa.</p>
    <input type="search" id="qplano" class="busca-larga" placeholder="Ex.: VIDA NOVA CG, CAPITA, MILLENIUM, VNCG2301…">
    <div class="scroll"><table id="tabPlanos" class="tab"></table></div>
  </div>
</section>

<!-- ------------------------------------------------ sobre -->
<section id="pane-sobre" class="pane" hidden>
  <div class="wrap">
    <h2 class="tit">Sobre este material</h2>
    <div class="sec" id="secSobre"></div>
    <h3 class="tit3">Materiais para baixar</h3>
    <div class="downloads" id="downloads"></div>
  </div>
</section>

<footer class="rodape"><div class="wrap">
  <div>
    <b>Mazza Broker</b>
    <div id="rodapeContato"></div>
  </div>
  <p class="mini" id="rodapeFonte"></p>
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
  --navy:#12233F; --navy2:#1D3557; --laranja:#EE6B22; --laranja-cl:#FDEFE5;
  --dourado:#C8A24A; --bg:#F6F7F9; --card:#FFFFFF; --txt:#111827; --txt2:#4B5563;
  --txt3:#8A93A0; --borda:#E3E6EB;
  --sombra:0 1px 2px rgba(16,24,40,.06),0 1px 3px rgba(16,24,40,.05);
}
@media (prefers-color-scheme:dark){:root{
  --navy:#0C1727; --navy2:#16273F; --bg:#0E141C; --card:#161E29; --txt:#EAEEF4;
  --txt2:#AEB8C6; --txt3:#75818F; --borda:#26303D; --laranja-cl:#2A1B10;
  --sombra:0 1px 2px rgba(0,0,0,.4);
}}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--txt);
  font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
img{max-width:100%}
.wrap{max-width:1180px;margin:0 auto;padding:0 18px}

.topo{background:var(--navy);color:#fff;padding:28px 0 24px;border-bottom:4px solid var(--laranja)}
.marca{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--dourado);font-weight:700}
h1{font-family:Georgia,"Times New Roman",serif;font-size:clamp(24px,5vw,34px);margin:8px 0 0;line-height:1.15}
h1 em{color:var(--dourado);font-style:italic;font-weight:400}
.lead{color:#B9C4D3;max-width:640px;margin:10px 0 0;font-size:14px}
.kpis{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 0}
.kpi{background:rgba(255,255,255,.06);border-left:3px solid var(--laranja);border-radius:6px;padding:8px 13px;min-width:104px}
.kpi b{display:block;font-size:19px;line-height:1.15}
.kpi span{font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:#9FB0C6}

.abas{background:var(--navy2);position:sticky;top:0;z-index:30}
.abas .wrap{display:flex;gap:2px;overflow-x:auto}
.aba{flex:0 0 auto;font:inherit;font-size:13.5px;color:#B9C4D3;background:none;border:0;
  border-bottom:3px solid transparent;padding:13px 15px;cursor:pointer;white-space:nowrap}
.aba:hover{color:#fff}
.aba.on{color:#fff;border-bottom-color:var(--laranja);font-weight:600}

.barra{background:var(--card);border-bottom:1px solid var(--borda);box-shadow:var(--sombra);padding:12px 0}
.barra .wrap{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
input[type=search],select{font:inherit;font-size:14px;color:var(--txt);background:var(--bg);
  border:1px solid var(--borda);border-radius:8px;padding:9px 12px;max-width:100%}
input[type=search]{flex:1 1 240px;min-width:180px}
select{max-width:100%}
.busca-larga{width:100%;margin:10px 0 4px}
.btn{font:inherit;font-size:13px;border:1px solid var(--borda);background:var(--bg);color:var(--txt2);
  border-radius:999px;padding:7px 13px;cursor:pointer}
.btn:hover{border-color:var(--laranja);color:var(--laranja)}
.btn.on{background:var(--navy);border-color:var(--navy);color:#fff}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.cont{font-size:13px;color:var(--txt3);margin:16px 0 0}
.aviso-rede{background:var(--laranja-cl);border-left:4px solid var(--laranja);color:#9A4310;
  border-radius:8px;padding:11px 14px;font-size:13.5px;margin:16px 0 0}

.cidade{font-family:Georgia,serif;font-size:19px;margin:26px 0 2px;
  border-left:4px solid var(--laranja);padding-left:10px}
.cidade small{font-size:12px;color:var(--txt3);font-weight:400;margin-left:8px;font-family:inherit}
.grade{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:12px;margin-top:12px}
.card{background:var(--card);border:1px solid var(--borda);border-left:4px solid var(--cor,#888);
  border-radius:10px;padding:13px 15px;box-shadow:var(--sombra)}
.card h3{margin:0;font-size:15px;line-height:1.3}
.rz{font-size:11.5px;color:var(--txt3);margin-top:2px}
.tag{display:inline-block;font-size:10px;text-transform:uppercase;letter-spacing:.05em;
  font-weight:700;color:var(--cor);margin-bottom:5px}
.esp{margin:8px 0 0}
.esp span{display:inline-block;background:var(--laranja-cl);color:#9A4310;border-radius:5px;
  padding:2px 7px;margin:0 4px 4px 0;font-size:11px}
.lin{margin:7px 0 0;font-size:12.5px;color:var(--txt2)}
.lin b{color:var(--txt);font-weight:600}
.lin a{color:var(--laranja);text-decoration:none}
.lin a:hover{text-decoration:underline}
.cc{margin-top:7px;font-size:11.5px;color:var(--txt3)}
.redes{margin-top:9px;display:flex;flex-wrap:wrap;gap:5px}
.pill{font-size:10.5px;font-weight:700;border-radius:999px;padding:2.5px 9px;color:#fff}
.pill.off{background:transparent;color:var(--txt3);border:1px dashed var(--borda);font-weight:500}
.vazio{padding:44px 0;text-align:center;color:var(--txt3)}

.tit{font-family:Georgia,serif;font-size:22px;margin:26px 0 4px}
.tit3{font-family:Georgia,serif;font-size:17px;margin:30px 0 4px}
.sub{color:var(--txt2);font-size:13.5px;margin:4px 0 12px;max-width:760px}
.cards-rede{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin:14px 0 6px}
.crede{background:var(--card);border:1px solid var(--borda);border-top:4px solid var(--cor);
  border-radius:10px;padding:14px 16px;box-shadow:var(--sombra)}
.crede h4{margin:0 0 2px;font-size:15px;color:var(--cor)}
.crede .n{font-size:26px;font-weight:700;line-height:1.1}
.crede .u{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--txt3)}
.crede p{font-size:12.5px;color:var(--txt2);margin:9px 0 0}

.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.tab{border-collapse:collapse;width:100%;font-size:13px;background:var(--card);
  border:1px solid var(--borda);border-radius:10px;overflow:hidden}
.tab th{background:var(--navy);color:#fff;text-align:left;padding:9px 11px;font-size:11px;
  text-transform:uppercase;letter-spacing:.04em;white-space:nowrap}
.tab td{padding:8px 11px;border-bottom:1px solid var(--borda);vertical-align:top}
.tab tbody tr:nth-child(even) td{background:rgba(127,127,127,.045)}
.tab tbody tr:last-child td{border-bottom:0}
.tab .num,.tab .ck{text-align:center}
.ok{font-weight:700}
.nao{color:var(--txt3)}
.tab tfoot td{background:var(--laranja);color:#fff;font-weight:700;border:0}

.sec{background:var(--card);border:1px solid var(--borda);border-radius:10px;padding:16px 18px;
  box-shadow:var(--sombra);font-size:13.5px;color:var(--txt2)}
.sec p{margin:8px 0}
.sec b{color:var(--txt)}
.downloads{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin-top:12px}
.dl{display:block;background:var(--card);border:1px solid var(--borda);border-left:4px solid var(--laranja);
  border-radius:10px;padding:13px 15px;text-decoration:none;color:inherit;box-shadow:var(--sombra)}
.dl:hover{border-color:var(--laranja)}
.dl b{display:block;font-size:14px}
.dl span{font-size:12px;color:var(--txt3)}

.rodape{background:var(--navy);color:#9FB0C6;margin-top:44px;padding:26px 0 90px;font-size:12.5px}
.rodape b{color:var(--dourado);font-family:Georgia,serif;font-size:17px;display:block;margin-bottom:4px}
.mini{font-size:11.5px;color:#7A8899;margin-top:16px}
.whats{position:fixed;right:16px;bottom:16px;width:54px;height:54px;border-radius:50%;
  background:#25D366;color:#fff;display:flex;align-items:center;justify-content:center;
  box-shadow:0 4px 14px rgba(0,0,0,.28);z-index:40}
@media (max-width:620px){
  .kpi{flex:1 1 calc(50% - 10px);min-width:0}
  .barra .wrap{gap:7px}
  select{flex:1 1 100%}
}
@media print{.abas,.barra,.whats{display:none}}
"""

APP = r"""(function () {
  const D = window.DADOS;
  const $ = s => document.querySelector(s);
  const esc = s => (s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const norm = s => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const rede = id => D.redes.find(r => r.id === id) || {curto: id, cor: '#888', nome: id};

  D.itens.forEach(i => {
    i._b = norm([i.n, i.rz, i.t, i.doc, i.e.join(' '), i.end.join(' '), i.cc.join(' '), i.c].join(' '));
  });
  const total = D.itens.length;

  /* ---------------- topo ---------------- */
  const cont = k => D.itens.filter(i => i.k === k).length;
  $('#kpis').innerHTML = [
    [total, 'prestadores'], [D.cidades.length, 'cidades'],
    [cont(D.cats[0]), 'hospitais e PS'], [cont(D.cats[2]), 'labs e imagem'],
    [cont(D.cats[1]), 'clínicas'], [cont(D.cats[3]), 'profissionais']
  ].map(([v, r]) => `<div class="kpi"><b>${v}</b><span>${r}</span></div>`).join('');

  const m = D.meta;
  $('#rodapeContato').innerHTML =
    `${esc(m.corretor)} · corretor de saúde<br>` +
    `<a style="color:#C8A24A" href="https://wa.me/${m.whats}">${esc(m.tel)}</a> · ` +
    `<a style="color:#C8A24A" href="mailto:${m.mail}">${esc(m.mail)}</a>`;
  $('#rodapeFonte').textContent = m.fonte + ' ' + m.aviso;
  $('#btnWhats').href = 'https://wa.me/' + m.whats +
    '?text=' + encodeURIComponent('Olá Alan! Vi a rede credenciada da Nossa Saúde e quero saber mais.');

  /* ---------------- abas ---------------- */
  document.querySelectorAll('.aba').forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll('.aba').forEach(x => x.classList.toggle('on', x === b));
    document.querySelectorAll('.pane').forEach(p => { p.hidden = p.id !== 'pane-' + b.dataset.aba; });
    window.scrollTo({top: 0, behavior: 'smooth'});
    location.hash = b.dataset.aba;
  }));

  /* ---------------- filtros ---------------- */
  let st = {q: '', rede: '', cidade: '', esp: '', cats: new Set()};

  const selPlano = $('#fplano');
  selPlano.innerHTML = '<option value="">Todos os planos / todas as redes</option>' +
    D.redes.map(r => `<option value="${r.id}">Rede ${esc(r.curto)} — ${r.nplanos} planos</option>`).join('');

  D.cidades.forEach(c => $('#fcidade').insertAdjacentHTML('beforeend', `<option>${esc(c)}</option>`));
  [...new Set(D.itens.flatMap(i => i.e))].sort((a, b) => a.localeCompare(b, 'pt'))
    .forEach(e => $('#fesp').insertAdjacentHTML('beforeend', `<option>${esc(e)}</option>`));
  $('#chips').innerHTML = D.cats.map(k =>
    `<button class="btn" data-cat="${esc(k)}">${esc(D.catcurta[k])}</button>`).join('');

  function render() {
    const q = norm(st.q).split(/\s+/).filter(Boolean);
    const sel = D.itens.filter(i =>
      (!st.rede || i.r.includes(st.rede)) &&
      (!st.cidade || i.c === st.cidade) &&
      (!st.esp || i.e.includes(st.esp)) &&
      (!st.cats.size || st.cats.has(i.k)) &&
      q.every(t => i._b.includes(t)));

    const av = $('#avisoRede');
    if (st.rede) {
      const r = rede(st.rede);
      const cids = D.cidades.filter(c => D.itens.some(i => i.c === c && i.r.includes(st.rede)));
      const sem = D.cidades.filter(c => !cids.includes(c));
      av.hidden = false;
      av.innerHTML = `<b>Rede ${esc(r.curto)}</b> — ${esc(r.desc)}` +
        (sem.length ? `<br>Sem prestador nesta rede em: <b>${esc(sem.join(', '))}</b>.` : '');
    } else { av.hidden = true; }

    $('#cont').textContent = sel.length === total
      ? total + ' prestadores credenciados nas 9 cidades'
      : sel.length + ' de ' + total + ' prestadores';

    const porCidade = new Map(D.cidades.map(c => [c, []]));
    sel.forEach(i => porCidade.get(i.c).push(i));
    let h = '';
    for (const c of D.cidades) {
      const lst = porCidade.get(c);
      if (!lst.length) continue;
      h += `<h2 class="cidade">${esc(c)}<small>${lst.length} ${lst.length === 1 ? 'prestador' : 'prestadores'}</small></h2><div class="grade">`;
      for (const i of lst) {
        const maps = i.end.length
          ? ` <a href="https://maps.google.com/?q=${encodeURIComponent(i.end[0] + ' ' + i.c + ' PR')}" target="_blank" rel="noopener">ver no mapa</a>` : '';
        h += `<div class="card" style="--cor:${D.catcor[i.k]}">
          <div class="tag">${esc(D.catcurta[i.k])} · ${esc(i.t)}</div>
          <h3>${esc(i.n)}</h3>
          ${i.rz ? `<div class="rz">${esc(i.rz)}</div>` : ''}
          ${i.doc ? `<div class="rz">${esc(i.doc)}</div>` : ''}
          <div class="esp">${i.e.map(e => `<span>${esc(e)}</span>`).join('')}</div>
          ${i.end.map(e => `<div class="lin">${esc(e)}${maps}</div>`).join('')}
          <div class="lin">${i.tel.length
            ? i.tel.map(t => `<b><a href="tel:${t.replace(/\D/g, '')}">${esc(t)}</a></b>`).join(' · ')
            : '<span class="nao">Telefone não informado</span>'}</div>
          ${i.cc.length ? `<div class="cc">Corpo clínico: ${esc(i.cc.slice(0, 8).join(', '))}${i.cc.length > 8 ? ' e mais ' + (i.cc.length - 8) : ''}</div>` : ''}
          <div class="redes">${D.redes.map(r => i.r.includes(r.id)
            ? `<span class="pill" style="background:${r.cor}">${esc(r.curto)}</span>`
            : `<span class="pill off">${esc(r.curto)}</span>`).join('')}</div>
        </div>`;
      }
      h += '</div>';
    }
    $('#lista').innerHTML = h || '<div class="vazio">Nenhum prestador encontrado com esses filtros.</div>';
  }

  $('#q').addEventListener('input', e => { st.q = e.target.value; render(); });
  selPlano.addEventListener('change', e => { st.rede = e.target.value; render(); });
  $('#fcidade').addEventListener('change', e => { st.cidade = e.target.value; render(); });
  $('#fesp').addEventListener('change', e => { st.esp = e.target.value; render(); });
  $('#chips').addEventListener('click', e => {
    const b = e.target.closest('[data-cat]'); if (!b) return;
    const k = b.dataset.cat;
    st.cats.has(k) ? st.cats.delete(k) : st.cats.add(k);
    b.classList.toggle('on'); render();
  });
  $('#limpar').addEventListener('click', () => {
    st = {q: '', rede: '', cidade: '', esp: '', cats: new Set()};
    $('#q').value = ''; selPlano.value = ''; $('#fcidade').value = ''; $('#fesp').value = '';
    document.querySelectorAll('[data-cat]').forEach(b => b.classList.remove('on'));
    render();
  });

  /* ---------------- comparativo ---------------- */
  const nr = r => D.itens.filter(i => i.r.includes(r.id)).length;
  $('#cardsRede').innerHTML = D.redes.map(r => `
    <div class="crede" style="--cor:${r.cor}">
      <h4>Rede ${esc(r.curto)}</h4>
      <div class="n">${nr(r)}</div>
      <div class="u">prestadores · ${r.nplanos} planos</div>
      <p>${esc(r.desc)}</p>
    </div>`).join('');

  const cab = extra => '<thead><tr>' + extra +
    D.redes.map(r => `<th class="ck" style="background:${r.cor}">${esc(r.curto)}</th>`).join('') + '</tr></thead>';
  const ck = (i, r) => i.r.includes(r.id)
    ? `<td class="ck ok" style="color:${r.cor}">✔</td>` : '<td class="ck nao">—</td>';

  $('#tabCid').innerHTML = cab('<th>Cidade</th><th class="num">Total</th>') + '<tbody>' +
    D.cidades.map(c => {
      const t = D.itens.filter(i => i.c === c);
      return `<tr><td><b>${esc(c)}</b></td><td class="num">${t.length}</td>` +
        D.redes.map(r => {
          const n = t.filter(i => i.r.includes(r.id)).length;
          return `<td class="ck" style="${n ? 'color:' + r.cor + ';font-weight:700' : ''}">${n || '—'}</td>`;
        }).join('') + '</tr>';
    }).join('') + '</tbody><tfoot><tr><td>TOTAL</td><td class="num">' + total + '</td>' +
    D.redes.map(r => `<td class="ck">${nr(r)}</td>`).join('') + '</tr></tfoot>';

  const hosp = D.itens.filter(i => i.k === D.cats[0])
    .sort((a, b) => D.cidades.indexOf(a.c) - D.cidades.indexOf(b.c) || a.n.localeCompare(b.n, 'pt'));
  $('#tabHosp').innerHTML = cab('<th>Cidade</th><th>Hospital</th>') + '<tbody>' +
    hosp.map(i => `<tr><td>${esc(i.c)}</td><td><b>${esc(i.n)}</b><div class="rz">${esc(i.t)}</div></td>` +
      D.redes.map(r => ck(i, r)).join('') + '</tr>').join('') + '</tbody>';

  const amplas = D.redes.filter(r => r.ampla);
  const idsA = amplas.map(r => r.id);
  const dif = D.itens.filter(i => {
    const n = idsA.filter(x => i.r.includes(x)).length;
    return n > 0 && n < idsA.length;
  }).sort((a, b) => D.cidades.indexOf(a.c) - D.cidades.indexOf(b.c) ||
                    D.cats.indexOf(a.k) - D.cats.indexOf(b.k) || a.n.localeCompare(b.n, 'pt'));
  $('#tituloDif').textContent = amplas.map(r => 'Rede ' + r.curto).join(' x ') + ': as diferenças';
  $('#subDif').innerHTML = 'As ' + amplas.length + ' redes que atendem as nove cidades são quase ' +
    'iguais. Estes <b>' + dif.length + ' prestadores</b> são toda a diferença entre elas.';
  const cabA = extra => '<thead><tr>' + extra +
    amplas.map(r => `<th class="ck" style="background:${r.cor}">${esc(r.curto)}</th>`).join('') + '</tr></thead>';
  $('#tabDif').innerHTML = cabA('<th>Cidade</th><th>Prestador</th><th>Categoria</th>') + '<tbody>' +
    dif.map(i => `<tr><td>${esc(i.c)}</td><td><b>${esc(i.n)}</b><div class="rz">${esc(i.t)}</div></td>` +
      `<td>${esc(D.catcurta[i.k])}</td>` + amplas.map(r => ck(i, r)).join('') + '</tr>').join('') + '</tbody>';

  const restritas = D.redes.filter(r => !r.ampla);
  if (restritas.length) {
    $('#tituloRestrita').hidden = false;
    $('#restritas').innerHTML = restritas.map(r => {
      const sem = D.cidades.filter(c => !r.cidades.includes(c));
      const lst = D.itens.filter(i => i.r.includes(r.id));
      const hosp = lst.filter(i => i.k === D.cats[0]);
      return `<div class="sec" style="border-left:4px solid ${r.cor}">
        <p><b>Rede ${esc(r.curto)}</b> — ${lst.length} prestadores, usada por ${r.nplanos} planos.
           Atende só em <b>${esc(r.cidades.join(', '))}</b>.</p>
        <p>Sem prestador credenciado em: <b>${esc(sem.join(', '))}</b>. Cliente dessas cidades com um
           plano desta rede não tem atendimento local.</p>
        <p>Hospitais nesta rede: ${hosp.length ? esc(hosp.map(h => h.n + ' (' + h.c + ')').join(' · ')) : 'nenhum'}.</p>
      </div>`;
    }).join('');
  }

  /* ---------------- planos ---------------- */
  function renderPlanos(f) {
    const t = norm(f || '');
    const lst = D.planos.filter(p => !t || norm(p.cod + ' ' + p.nome + ' ' + p.tipo).includes(t));
    $('#tabPlanos').innerHTML =
      '<thead><tr><th>Código</th><th>Plano</th><th>Contratação</th><th>Registro ANS</th><th>Rede credenciada</th></tr></thead><tbody>' +
      (lst.length ? lst.map(p => {
        const r = rede(p.rede);
        return `<tr><td><b>${esc(p.cod)}</b></td><td>${esc(p.nome)}</td><td>${esc(p.tipo)}</td>` +
               `<td>${esc(p.ans)}</td><td><span class="pill" style="background:${r.cor}">${esc(r.curto)}</span></td></tr>`;
      }).join('') : '<tr><td colspan="5">Nenhum plano encontrado com esse termo.</td></tr>') +
      '</tbody>';
  }
  $('#qplano').addEventListener('input', e => renderPlanos(e.target.value));
  renderPlanos('');

  /* ---------------- sobre ---------------- */
  $('#secSobre').innerHTML = `
    <p><b>O que é:</b> a rede credenciada da <b>${esc(m.operadora)}</b> (CNPJ ${esc(m.cnpj)}) nas nove
       cidades dos Campos Gerais atendidas pela operadora: ${esc(D.cidades.join(', '))}.</p>
    <p><b>Como foi levantado:</b> os dados vêm do buscador oficial da operadora
       (prestador.nossasaude.com.br), consultados em ${esc(m.data)} cidade por cidade e rede por rede.
       Foram mapeados os ${D.planos.length} planos ativos da operadora que atendem a região e
       agrupados nas ${D.redes.length} redes credenciadas que chegam aos Campos Gerais.</p>
    <p><b>Por que "rede" e não "plano":</b> planos diferentes podem usar a mesma rede credenciada.
       Todos os planos de uma mesma rede enxergam exatamente os mesmos prestadores — muda a
       acomodação, a coparticipação e o preço, não a lista de médicos e hospitais.</p>
    <p><b>${esc(m.aviso)}</b></p>
    <p class="rz">${esc(m.fonte)}</p>`;

  $('#downloads').innerHTML = D.downloads.map(dl =>
    `<a class="dl" href="${esc(dl.href)}" download><b>${esc(dl.tit)}</b><span>${esc(dl.desc)}</span></a>`).join('');

  /* ---------------- start ---------------- */
  const h = (location.hash || '').replace('#', '');
  const alvo = document.querySelector('.aba[data-aba="' + h + '"]');
  if (alvo) alvo.click();
  render();
})();
"""

DOWNLOADS = [
    {'href': 'arquivos/rede-nossa-saude-campos-gerais.xlsx',
     'tit': 'Planilha completa (XLSX)',
     'desc': 'Todos os prestadores, com colunas por rede credenciada e uma aba por cidade.'},
    {'href': 'arquivos/rede-nossa-saude-clientes.pdf',
     'tit': 'PDF para o cliente',
     'desc': 'Hospitais, clínicas e laboratórios por cidade — resumido, pronto para enviar.'},
    {'href': 'arquivos/rede-nossa-saude-completo.pdf',
     'tit': 'Guia completo (PDF)',
     'desc': 'Tudo, incluindo os médicos agrupados por especialidade em cada cidade.'},
]

README = """# Rede credenciada Nossa Saúde — Campos Gerais

Site estático com a rede credenciada da **Nossa Saúde** nas 9 cidades dos Campos Gerais / PR:
Ponta Grossa, Telêmaco Borba, Jaguariaíva, Castro, Irati, Palmeira, Carambeí, Prudentópolis e
Piraí do Sul.

Publicado por **Mazza Broker** — {corretor} · {tel} · {mail}

## O que tem

- Busca por hospital, clínica, laboratório, médico, especialidade ou bairro
- Filtro pela **rede credenciada do plano do cliente** ({nredes} redes chegam à região)
- Comparativo entre as redes: cobertura por cidade, hospitais e onde elas se diferenciam
- Tabela "Qual é o meu plano?" com os {nplanos} planos da operadora e a rede de cada um
- XLSX e PDFs para download

## Números

| | |
|---|---|
| Prestadores | {total} |
| Cidades | 9 |
| Redes credenciadas na região | {nredes} |
| Planos mapeados | {nplanos} |
| Consulta | {data} |

## Fonte e validade

{fonte}

> {aviso}

## Como publicar / atualizar

O site é estático: `index.html`, `estilo.css`, `app.js` e `dados.js` (os dados ficam em
`window.DADOS` dentro do `dados.js`). Não precisa de build.

Para atualizar a rede, rodar os scripts em `_scripts/` (ver `_scripts/LEIAME.md`) e regerar
`dados.js` com `python gen_site.py`.

GitHub Pages: Settings → Pages → Source: `Deploy from a branch` → branch `main`, pasta `/ (root)`.
"""


def main():
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    os.makedirs(os.path.join(SITE, 'arquivos'), exist_ok=True)
    PAYLOAD['downloads'] = DOWNLOADS
    open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(INDEX)
    open(os.path.join(SITE, 'estilo.css'), 'w', encoding='utf-8').write(CSS)
    open(os.path.join(SITE, 'app.js'), 'w', encoding='utf-8').write(APP)
    open(os.path.join(SITE, 'dados.js'), 'w', encoding='utf-8').write(
        'window.DADOS = ' + json.dumps(PAYLOAD, ensure_ascii=False, separators=(',', ':')) + ';\n')
    open(os.path.join(SITE, '.nojekyll'), 'w').write('')
    open(os.path.join(SITE, 'README.md'), 'w', encoding='utf-8').write(README.format(
        corretor=C.CORRETOR, tel=C.CORRETOR_TEL, mail=C.CORRETOR_MAIL,
        nredes=len(REDES), nplanos=len(planos), total=len(itens),
        data=C.DATA_REF, fonte=C.FONTE, aviso=C.AVISO))
    tam = sum(os.path.getsize(os.path.join(SITE, f)) for f in os.listdir(SITE)
              if os.path.isfile(os.path.join(SITE, f)))
    print('site gerado em', SITE, '| %d prestadores, %d planos, %d redes | %.0f KB'
          % (len(itens), len(planos), len(REDES), tam / 1024))


if __name__ == '__main__':
    main()
