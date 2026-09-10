(function () {
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
