  /* ======================================== PDF (padrao Central de Rede) ===
     O PDF sai pelo pdf-rede.js, o mesmo gerador da Amil, do Bradesco e da
     SulAmerica: aqui a pagina so DESCREVE o documento (capa, "Como ler",
     blocos) e o pdf-rede.js o monta com o pdfmake, sem cortar texto.
     O montar_site.py cola este arquivo no lugar do motor de PDF antigo. */

  function apelidoCidade() {
    // se você filtrou por onde o prestador fica, é esse o recorte do material
    var c = temEscolha("cidr") ? escolhidos("cidr") : escolhidos("cid");
    if (!c.length) return D.estado || D.uf;
    if (c.length === 1) return c[0];
    if (c.length === 2) return c[0] + " e " + c[1];
    return c[0] + " e mais " + (c.length - 1) + " cidades";
  }

  /* "PONTA GROSSA" -> "Ponta Grossa"; o nome da regiao ja vem em caixa mista. */
  function rotuloDoRecorte() {
    var bruto = apelidoCidade();
    return bruto !== bruto.toUpperCase() ? bruto
      : bruto.replace(/(^|\s)(\S)(\S*)/g, function (m, a, b, c) {
          return a + b.toUpperCase() + c.toLowerCase();
        }).replace(/\bE\b/g, "e");
  }

  var MESES_PDF = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
                   "agosto", "setembro", "outubro", "novembro", "dezembro"];

  /* "01/10/2026" -> "1 de outubro de 2026". A data e a da COLETA da regiao
     (gerado_em), nunca a do dia em que o PDF e gerado. */
  function dataDaColeta() {
    var d = String(D.gerado_em || "").split("/");
    if (d.length !== 3 || !(d[1] >= 1 && d[1] <= 12)) return D.gerado_em || "";
    return Number(d[0]) + " de " + MESES_PDF[d[1] - 1] + " de " + d[2];
  }

  function corDoProduto(p) {
    return (p && p.cor) || "#e6411c";
  }

  function nomeDoPlano(p) {
    return p.acomodacao ? p.rotulo + " (" + p.acomodacao + ")" : p.rotulo;
  }

  function telefoneBonito(t) {
    return String(t || "").replace(/^(\d{2})-(\d{4,5})-(\d{4})$/, "($1) $2-$3");
  }

  function assinaturaDoc() {
    var c = corretor || {};
    var p = [c.corretora || "Mazza Broker"];
    ["nome", "fone", "email"].forEach(function (k) { if (c[k]) p.push(c[k]); });
    return "Documento gerado em " + new Date().toLocaleDateString("pt-BR") + "  ·  " +
           p.join("  ·  ");
  }

  /* Prestadores da cidade com mais rede primeiro, depois as outras. */
  function porCidadeENome(lista) {
    var cidadeDe = function (p) {
      return ((p.cr && p.cr.length) ? p.cr : (p.cid || []))[0] || "";
    };
    var conta = {};
    lista.forEach(function (p) { conta[cidadeDe(p)] = (conta[cidadeDe(p)] || 0) + 1; });
    return lista.slice().sort(function (a, b) {
      var ca = cidadeDe(a), cb = cidadeDe(b);
      if (ca !== cb) return (conta[cb] - conta[ca]) || (ca < cb ? -1 : 1);
      return ordenarPorNome(a, b);
    });
  }

  /* Uma linha da tabela no formato do pdf-rede.js. Nada e cortado: todos os
     enderecos, telefones, bairros e especialidades do prestador; o pdfmake
     quebra a linha onde precisar. */
  function linhaPdf(p, produtos, comEsp) {
    var cid = (p.cr && p.cr.length) ? p.cr : (p.cid || []);
    var meus = p.meus || produtosDe(p);
    var esps = p.espPdf || p.esp || [];
    var detalhe = [];
    if (p.obs && p.obs.length) {
      detalhe.push(["Observação da operadora: ", true]);
      detalhe.push([p.obs.join(" · "), false]);
    }
    return {
      nome: bonito(p.n),
      tag: (p.s && p.s.length) ? p.s.join(" · ") : "",
      detalhe: detalhe,
      esp: comEsp ? especialidades(esps).join(" · ") : "",
      end: (p.e || []).map(bonito).join("\n"),
      tel: (p.t || []).map(telefoneBonito).join("\n"),
      bairro: (p.b || []).join(" · "),
      cidade: bonito(cid.join(" / ")),
      marcas: produtos.map(function (pr) {
        if (meus.indexOf(pr.codigo) < 0) return false;
        // direcionamento interno: o visto vem com um D embaixo
        return (p.dir || []).indexOf(pr.codigo) >= 0 ? "D" : true;
      })
    };
  }

  function blocoPdf(titulo, itens, produtos, comEsp) {
    return { tipo: "bloco", titulo: titulo,
             conta: itens.length + (itens.length === 1 ? " prestador" : " prestadores"),
             endereco: true, telefone: true,
             produtos: produtos.map(function (pr) {
               return { nome: pr.rotulo, cor: corDoProduto(pr) };
             }),
             linhas: itens.map(function (p) { return linhaPdf(p, produtos, comEsp); }) };
  }

  /* "Rede Nossa Saúde - Vida Nova CG - Ponta Grossa-PR.pdf" (o pdf-rede.js
     tira os acentos na hora de salvar). */
  function nomeArquivo(partes) {
    return partes.filter(Boolean).join(" - ").replace(/\s*\/\s*/g, "-")
                 .replace(/[\/\\:*?"<>|]+/g, "-").replace(/\s+/g, " ").trim() + ".pdf";
  }

  /* Botao em "Montando..." enquanto o PDF sai; volta sozinho no fim. */
  function entregarPdf(botao, doc) {
    if (!window.PDFRede) {
      avisar("<b>O gerador de PDF não carregou nesta página.</b> Recarregue e tente de novo.", true);
      return;
    }
    var rotulo = botao.textContent;
    botao.disabled = true;
    botao.textContent = "Montando…";
    function fim() { botao.disabled = false; botao.textContent = rotulo; }
    setTimeout(function () {
      var r;
      try { r = window.PDFRede.baixar(doc()); }
      catch (e) { fim(); avisar("<b>Não consegui montar o PDF:</b> " + esc(e.message || e), true); return; }
      Promise.resolve(r).then(fim, function (e) {
        fim();
        avisar("<b>Não consegui montar o PDF:</b> " + esc(e && e.message ? e.message : e), true);
      });
    }, 30);
  }

  function documentoRede(produtos) {
    var comparativo = produtos.length > 1;
    var lista = filtrar();
    var rotuloCidade = rotuloDoRecorte();
    var onde = rotuloCidade + " / PR";
    var nomes = produtos.map(nomeDoPlano);
    var cores = produtos.map(corDoProduto);
    var coleta = dataDaColeta();

    /* Cada prestador entra uma vez, no bloco da categoria dele - a mesma
       conta do site. Filtrou especialidade? A linha lista so a escolhida. */
    function daCategoria(cat) {
      return lista.filter(function (p) { return tipoDe(p) === cat; }).map(function (p) {
        var q = {}; for (var k in p) q[k] = p[k];
        q.meus = produtosDe(p);
        q.espPdf = temEscolha("esp")
          ? p.esp.filter(function (e) { return estado.f.esp[e]; })
          : p.esp;
        return q;
      });
    }
    var blocos = D.categorias.map(function (cat) {
      var itens = daCategoria(cat);
      itens = /^Hospitais/.test(cat)
        ? itens.sort(function (a, b) {
            return b.espPdf.length - a.espPdf.length || ordenarPorNome(a, b);
          })
        : porCidadeENome(itens);
      return [cat, itens];
    });

    var cidades = {};
    lista.forEach(function (p) {
      ((p.cr && p.cr.length) ? p.cr : (p.cid || [])).forEach(function (c) { cidades[c] = 1; });
    });
    var ROTULO_PLACAR = {
      "Hospitais": "hospitais", "Diagnóstico por imagem": "centros de imagem",
      "Laboratórios e análises clínicas": "laboratórios",
      "Exames e procedimentos": "exames e procedimentos",
      "Clínicas e consultórios": "clínicas e consultórios",
      "Médicos e demais profissionais": "médicos e profissionais"
    };
    var placar = [[lista.length, "prestadores"],
                  [Object.keys(cidades).length,
                   Object.keys(cidades).length === 1 ? "cidade" : "cidades"]];
    blocos.forEach(function (b) {
      if (b[1].length) placar.push([b[1].length, ROTULO_PLACAR[b[0]] || b[0]]);
    });
    if (comparativo) {
      produtos.forEach(function (pr, i) {
        placar.push([lista.filter(function (p) {
          return produtosDe(p).indexOf(pr.codigo) >= 0;
        }).length, pr.rotulo]);
      });
    }

    var recorte = [(comparativo ? "planos " : "plano ") +
                   nomes.join(estado.modo === "e" ? " e " : " ou ")];
    if (rotuloCidade !== (D.estado || D.uf)) recorte.push("região " + (D.estado || D.uf));
    if (temEscolha("cat")) recorte.push("categoria " + escolhidos("cat").join(", "));
    if (temEscolha("esp")) recorte.push("especialidade " +
      escolhidos("esp").map(especialidade).join(", "));
    if (temEscolha("bairro")) recorte.push("bairro " + escolhidos("bairro").map(bonito).join(", "));
    recorte.push("rede levantada em " + coleta);

    var temDir = lista.some(function (p) { return p.dir && p.dir.length; });
    var textoPlano = [["O ", false], ["visto", true],
      [" na coluna do plano significa que o prestador atende quem tem esse plano. " +
       "Cada região tem aqui o plano que a Nossa Saúde vende nela, com a rede " +
       "daquele plano; os outros planos da operadora usam outras redes.", false]];
    if (temDir) {
      textoPlano.push([" D", true], [" embaixo do visto é ", false],
                      ["direcionamento interno", true],
                      [": a operadora só libera o prestador por encaminhamento.", false]);
    }

    var secoes = [
      { tipo: "leitura",
        cartoes: [
          { titulo: comparativo ? "Os " + nomes.length + " planos" : "O plano",
            etiquetas: nomes.map(function (n, i) { return [n, cores[i]]; }),
            texto: textoPlano },
          { titulo: "Como a rede está organizada",
            texto: [["Cada bloco é um tipo de prestador: ", false], ["hospitais", true],
                    [", ", false], ["diagnóstico por imagem", true], [", ", false],
                    ["laboratórios", true], [", ", false], ["exames e procedimentos", true],
                    [", ", false], ["clínicas e consultórios", true], [" e ", false],
                    ["médicos e demais profissionais", true],
                    [". Endereço e telefone têm coluna própria; sob o nome vêm as " +
                     "especialidades, e a coluna de bairro diz também a cidade.", false]] },
          { titulo: "De onde vêm os dados",
            texto: [["Rede credenciada oficial da Nossa Saúde", true],
                    [", cidade por cidade, filtrada no plano " + nomes.join(", ") +
                     ". Rede levantada em " + coleta + ".", false]] }
        ],
        aviso: [["Antes de contratar. ", true],
                ["A rede credenciada é definida e alterada exclusivamente pela Nossa Saúde, " +
                 "a qualquer tempo. Este documento reproduz a rede oficial na data indicada e " +
                 "serve para orientar a escolha — ", false],
                ["confirme no portal da Nossa Saúde antes de contratar.", true]] }
    ];
    blocos.forEach(function (b) {
      secoes.push(blocoPdf(b[0], b[1], produtos, true));
    });
    var c = corretor || {};
    if (c.nome || c.fone || c.email) {
      secoes.push({ tipo: "texto", titulo: "Seu corretor", conta: c.corretora || "Mazza Broker",
                    texto: [[c.nome || "", true],
                            [(c.nome ? "  ·  " : "") + (c.corretora || "Mazza Broker"), false],
                            [[c.fone, c.email].filter(Boolean).length
                              ? "\n" + [c.fone, c.email].filter(Boolean).join("   ·   ") : "",
                             false]] });
    }

    return {
      arquivo: nomeArquivo(["Rede Nossa Saúde", produtos.map(function (p) {
        return p.rotulo; }).join(" e "), onde]),
      rodape: "Rede credenciada Nossa Saúde   ·   " + nomes.join(", ") + "   ·   " + onde,
      corretora: c.corretora || "Mazza Broker",
      corretorNome: c.nome || "",
      capa: { titulo: "Rede credenciada", destaque: "Nossa Saúde", onde: onde,
              recorte: recorte.join("  ·  "), placar: placar, cores: cores,
              assinatura: assinaturaDoc() },
      secoes: secoes
    };
  }

  function gerarPDF() {
    var produtos = produtosEscolhidos();
    if (!produtos.length) {
      avisar("<b>Marque pelo menos um produto.</b> O PDF sai com uma coluna " +
             "para cada produto marcado.");
      return;
    }
    if (produtos.length > MAX_COLUNAS_PDF) {
      avisar("<b>" + produtos.length + " produtos não cabem na página.</b> " +
             "O comparativo aceita até " + MAX_COLUNAS_PDF +
             " colunas — desmarque alguns e gere de novo.", true);
      return;
    }
    entregarPdf($("pdf"), function () { return documentoRede(produtos); });
  }

  /* ---------------- PDF da troca de plano (aba Entre planos) ----------------
     A aba so aparece quando a regiao tem mais de um plano. */
  function gerarPDFEntre() {
    var codA = $("planoA").value, codB = $("planoB").value;
    if (!codA || !codB || codA === codB) return;
    entregarPdf($("pdfEntre"), function () {
      var r = compararPlanos(codA, codB);
      var nA = nomeProduto(codA), nB = nomeProduto(codB);
      var prodA = D.produtos.filter(function (p) { return p.codigo === codA; })[0] ||
                  { codigo: codA, rotulo: nA };
      var prodB = D.produtos.filter(function (p) { return p.codigo === codB; })[0] ||
                  { codigo: codB, rotulo: nB };
      var praças = escolhidos("cid");
      var onde = praças.length ? praças.map(bonito).join(", ") : (D.estado || D.uf);
      var mantidos = r.noA.length - r.perde.length;
      var pct = r.noA.length ? Math.round(100 * mantidos / r.noA.length) : 100;
      var hosp = r.perde.filter(function (p) { return /^Hospitais/.test(tipoDe(p) || ""); })
                        .sort(ordenarPorNome);
      var outros = porCidadeENome(r.perde.filter(function (p) {
        return !/^Hospitais/.test(tipoDe(p) || "");
      }).map(function (p) {
        var q = {}; for (var k in p) q[k] = p[k];
        q.meus = [codA]; return q;
      }));
      var secoes = [
        { tipo: "texto", titulo: "O que a troca significa", conta: onde, texto: [
          ["O ", false], [nA, true], [" atende " + r.noA.length.toLocaleString("pt-BR") +
          " prestadores em " + r.cidadesA + " cidades. O ", false], [nB, true],
          [" atende " + r.noB.length.toLocaleString("pt-BR") + " em " + r.cidadesB +
           ". Dos que o cliente tem hoje, ", false], [mantidos.toLocaleString("pt-BR"), true],
          [" continuam na rede e ", false], [r.perde.length.toLocaleString("pt-BR"), true],
          [" saem. Em troca, o " + nB + " acrescenta ", false],
          [r.ganha.length.toLocaleString("pt-BR"), true],
          [" prestadores que hoje ele não tem.", false]] },
        { tipo: "grade", titulo: "Hospitais que saem da rede", conta: hosp.length,
          cor: corDoProduto(prodA), itens: hosp.map(function (p) {
            var cid = (p.cr && p.cr.length) ? p.cr : (p.cid || []);
            return { nome: bonito(p.n), sub: [bonito((p.e || [])[0] || ""),
                                              bonito((p.b || [])[0] || ""),
                                              bonito(cid[0] || ""),
                                              telefoneBonito((p.t || [])[0] || "")]
                                             .filter(Boolean).join(" · ") };
          }) }
      ];
      if (!hosp.length) {
        secoes.push({ tipo: "texto", texto: [["Nenhum hospital se perde nessa troca", true],
          [" em " + onde + ". A diferença entre os dois planos está em clínicas, " +
           "exames ou consultórios.", false]] });
      }
      if (r.cidadesSomem.length) {
        secoes.push({ tipo: "texto", titulo: "Cidades que ficam sem rede",
                      conta: r.cidadesSomem.length,
                      texto: [[r.cidadesSomem.map(bonito).join(" · "), false]] });
      }
      secoes.push(blocoPdf("Outros prestadores que saem no " + nB, outros, [prodA], false));
      return {
        arquivo: nomeArquivo(["Rede Nossa Saúde", "troca de " + nA + " para " + nB, onde]),
        rodape: "Nossa Saúde   ·   " + nA + " para " + nB + "   ·   " + onde,
        corretora: (corretor || {}).corretora || "Mazza Broker",
        corretorNome: (corretor || {}).nome || "",
        capa: { titulo: "O que muda", destaque: nA + " para " + nB, onde: onde,
                recorte: "rede levantada em " + dataDaColeta(),
                placar: [[pct + "%", "da rede mantida"], [r.perde.length, "prestadores a menos"],
                         [hosp.length, "hospitais a menos"], [r.cidadesSomem.length, "cidades sem rede"]],
                cores: [corDoProduto(prodA), corDoProduto(prodB)], assinatura: assinaturaDoc() },
        secoes: secoes
      };
    });
  }

