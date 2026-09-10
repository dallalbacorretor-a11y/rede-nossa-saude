(function () {
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
