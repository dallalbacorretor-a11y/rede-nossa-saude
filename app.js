(function () {
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
