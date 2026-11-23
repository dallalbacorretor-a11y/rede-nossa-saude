;
window.ORDEM_UF=["PR", "SC", "SP"];
window.DADOS=window.DADOS_UF[window.ORDEM_UF[0]];
window.CORRETOR={"nome": "Alan Vinicius Dall Alba", "corretora": "Mazza Broker", "email": "alan.vinicius@mazzabroker.com.br", "fone": "(41) 99547-6715"};
/* pdf_web.js — escrevente de PDF que roda no navegador.
   O visualizador do link não deixa a página imprimir, então o PDF é montado
   aqui, byte a byte. Usa as fontes reduzidas que o Python embutiu (Constantia
   e Segoe UI), como fontes compostas Identity-H: o texto vai em índices de
   glifo, e o mapa de código→glifo vem pronto do Python. */
(function (global) {
  "use strict";

  function bytes(str) {                       // string latin-1 -> bytes
    var a = new Uint8Array(str.length);
    for (var i = 0; i < str.length; i++) a[i] = str.charCodeAt(i) & 0xff;
    return a;
  }

  function deBase64(b64) {
    var bruto = atob(b64), a = new Uint8Array(bruto.length);
    for (var i = 0; i < bruto.length; i++) a[i] = bruto.charCodeAt(i);
    return a;
  }

  function hex4(n) { return ("0000" + n.toString(16)).slice(-4); }

  function PDF(largura, altura) {
    this.L = largura;
    this.A = altura;
    this.fontes = {};       // apelido -> {dados, ref}
    this.paginas = [];      // cada pagina: array de operadores
    this.atual = null;
  }

  PDF.prototype.addFonte = function (apelido, dados) {
    this.fontes[apelido] = { d: dados, id: "F" + (Object.keys(this.fontes).length + 1) };
  };

  PDF.prototype.novaPagina = function () {
    this.atual = [];
    this.paginas.push(this.atual);
    return this.paginas.length;
  };

  PDF.prototype.pagina = function () { return this.paginas.length; };

  // ---------------------------------------------------------------- medidas
  PDF.prototype.larguraTexto = function (texto, apelido, corpo) {
    var f = this.fontes[apelido];
    if (!f) return 0;
    var soma = 0, cmap = f.d.cmap, larg = f.d.larg;
    for (var i = 0; i < texto.length; i++) {
      var gid = cmap[texto.charCodeAt(i)];
      if (gid === undefined) gid = cmap[63];         // "?" quando falta glifo
      soma += (larg[gid] || 500);
    }
    return soma * corpo / 1000;
  };

  /* Quebra em linhas que cabem em `maxLargura`. Corta palavra só quando ela
     sozinha não cabe — endereço comprido não pode empurrar a coluna. */
  PDF.prototype.quebrar = function (texto, apelido, corpo, maxLargura) {
    var palavras = String(texto == null ? "" : texto).split(/\s+/);
    var linhas = [], atual = "";
    for (var i = 0; i < palavras.length; i++) {
      var p = palavras[i];
      if (!p) continue;
      var teste = atual ? atual + " " + p : p;
      if (this.larguraTexto(teste, apelido, corpo) <= maxLargura) {
        atual = teste;
        continue;
      }
      if (atual) { linhas.push(atual); atual = ""; }
      while (this.larguraTexto(p, apelido, corpo) > maxLargura && p.length > 1) {
        var corte = p.length;
        while (corte > 1 &&
               this.larguraTexto(p.slice(0, corte), apelido, corpo) > maxLargura) {
          corte--;
        }
        linhas.push(p.slice(0, corte));
        p = p.slice(corte);
      }
      atual = p;
    }
    if (atual) linhas.push(atual);
    return linhas.length ? linhas : [""];
  };

  // ---------------------------------------------------------------- desenho
  function cor(hex) {
    var n = parseInt(hex.replace("#", ""), 16);
    return (((n >> 16) & 255) / 255).toFixed(3) + " " +
           (((n >> 8) & 255) / 255).toFixed(3) + " " +
           ((n & 255) / 255).toFixed(3);
  }

  PDF.prototype.retangulo = function (x, y, l, a, hex) {
    this.atual.push(cor(hex) + " rg " +
      x.toFixed(2) + " " + y.toFixed(2) + " " +
      l.toFixed(2) + " " + a.toFixed(2) + " re f");
  };

  PDF.prototype.linha = function (x1, y1, x2, y2, hex, espessura) {
    this.atual.push(cor(hex) + " RG " + (espessura || 0.5).toFixed(2) + " w " +
      x1.toFixed(2) + " " + y1.toFixed(2) + " m " +
      x2.toFixed(2) + " " + y2.toFixed(2) + " l S");
  };

  /* Poligono preenchido: [[x,y],[x,y],...]. Usado no selo da corretora,
     que tem o canto direito em diagonal. */
  PDF.prototype.poligono = function (pontos, hex) {
    if (!pontos || pontos.length < 3) return;
    var d = cor(hex) + " rg " +
            pontos[0][0].toFixed(2) + " " + pontos[0][1].toFixed(2) + " m";
    for (var i = 1; i < pontos.length; i++) {
      d += " " + pontos[i][0].toFixed(2) + " " + pontos[i][1].toFixed(2) + " l";
    }
    this.atual.push(d + " h f");
  };

  /* Circulo por quatro Beziers. k = 0.5523 e a constante que aproxima o
     quarto de circulo com erro invisivel na impressao. */
  PDF.prototype.circulo = function (cx, cy, r, hex, contorno, espessura) {
    var k = 0.5523 * r, n = function (v) { return v.toFixed(2); };
    var d = (contorno ? cor(hex) + " RG " + (espessura || 0.8).toFixed(2) + " w "
                      : cor(hex) + " rg ") +
      n(cx - r) + " " + n(cy) + " m " +
      n(cx - r) + " " + n(cy + k) + " " + n(cx - k) + " " + n(cy + r) + " " +
      n(cx) + " " + n(cy + r) + " c " +
      n(cx + k) + " " + n(cy + r) + " " + n(cx + r) + " " + n(cy + k) + " " +
      n(cx + r) + " " + n(cy) + " c " +
      n(cx + r) + " " + n(cy - k) + " " + n(cx + k) + " " + n(cy - r) + " " +
      n(cx) + " " + n(cy - r) + " c " +
      n(cx - k) + " " + n(cy - r) + " " + n(cx - r) + " " + n(cy - k) + " " +
      n(cx - r) + " " + n(cy) + " c";
    this.atual.push(d + (contorno ? " S" : " f"));
  };

  /* Retangulo de cantos arredondados - as pilulas do cabecalho de coluna. */
  PDF.prototype.pilula = function (x, y, l, a, hex) {
    var r = Math.min(a / 2, l / 2), k = 0.5523 * r;
    var n = function (v) { return v.toFixed(2); };
    var d = cor(hex) + " rg " +
      n(x + r) + " " + n(y) + " m " +
      n(x + l - r) + " " + n(y) + " l " +
      n(x + l - r + k) + " " + n(y) + " " + n(x + l) + " " + n(y + r - k) + " " +
      n(x + l) + " " + n(y + r) + " c " +
      n(x + l) + " " + n(y + a - r) + " l " +
      n(x + l) + " " + n(y + a - r + k) + " " + n(x + l - r + k) + " " + n(y + a) + " " +
      n(x + l - r) + " " + n(y + a) + " c " +
      n(x + r) + " " + n(y + a) + " l " +
      n(x + r - k) + " " + n(y + a) + " " + n(x) + " " + n(y + a - r + k) + " " +
      n(x) + " " + n(y + a - r) + " c " +
      n(x) + " " + n(y + r) + " l " +
      n(x) + " " + n(y + r - k) + " " + n(x + r - k) + " " + n(y) + " " +
      n(x + r) + " " + n(y) + " c";
    this.atual.push(d + " h f");
  };

  PDF.prototype.texto = function (x, y, texto, apelido, corpo, hex) {
    var f = this.fontes[apelido];
    if (!f || texto == null || texto === "") return;
    var s = String(texto), cmap = f.d.cmap, saida = "";
    for (var i = 0; i < s.length; i++) {
      var gid = cmap[s.charCodeAt(i)];
      if (gid === undefined) gid = cmap[63] || 0;
      saida += hex4(gid);
    }
    this.atual.push("BT " + cor(hex || "#000000") + " rg /" + f.id + " " +
      corpo + " Tf " + x.toFixed(2) + " " + y.toFixed(2) + " Td <" +
      saida + "> Tj ET");
  };

  // ----------------------------------------------------------------- saida
  PDF.prototype.gerar = function () {
    var partes = [], deslocamento = 0, posicoes = [], eu = this;

    function push(dado) {
      var b = (dado instanceof Uint8Array) ? dado : bytes(dado);
      partes.push(b);
      deslocamento += b.length;
    }
    function objeto(num, corpoTxt, fluxo) {
      posicoes[num] = deslocamento;
      push(num + " 0 obj\n" + corpoTxt + "\n");
      if (fluxo) {
        push("stream\n");
        push(fluxo);
        push("\nendstream\n");
      }
      push("endobj\n");
    }

    var apelidos = Object.keys(this.fontes);
    // 1 catalogo, 2 arvore de paginas, depois paginas, conteudos e fontes
    var nPag = this.paginas.length;
    var idPagina = function (i) { return 3 + i; };
    var idConteudo = function (i) { return 3 + nPag + i; };
    var baseFonte = 3 + nPag * 2;
    var idsFonte = {};
    apelidos.forEach(function (a, i) { idsFonte[a] = baseFonte + i * 5; });
    var total = baseFonte + apelidos.length * 5 - 1;

    push("%PDF-1.4\n%\xE2\xE3\xCF\xD3\n");

    var recursos = "<< /Font << " + apelidos.map(function (a) {
      return "/" + eu.fontes[a].id + " " + idsFonte[a] + " 0 R";
    }).join(" ") + " >> >>";

    objeto(1, "<< /Type /Catalog /Pages 2 0 R >>");
    var filhos = [];
    for (var i = 0; i < nPag; i++) filhos.push(idPagina(i) + " 0 R");
    objeto(2, "<< /Type /Pages /Count " + nPag + " /Kids [" +
              filhos.join(" ") + "] >>");

    for (i = 0; i < nPag; i++) {
      objeto(idPagina(i), "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 " +
        this.L.toFixed(2) + " " + this.A.toFixed(2) + "] /Resources " +
        recursos + " /Contents " + idConteudo(i) + " 0 R >>");
    }
    for (i = 0; i < nPag; i++) {
      var conteudo = this.paginas[i].join("\n");
      objeto(idConteudo(i), "<< /Length " + conteudo.length + " >>", conteudo);
    }

    apelidos.forEach(function (a) {
      var f = eu.fontes[a], d = f.d, id = idsFonte[a];
      var arquivo = deBase64(d.b64);
      var nome = "AAAAAA+" + d.nome.replace(/[^A-Za-z0-9]/g, "");

      // larguras por glifo, no formato /W [ gid [larg] ... ]
      var w = [];
      Object.keys(d.larg).forEach(function (gid) {
        w.push(gid + " [" + d.larg[gid] + "]");
      });

      objeto(id, "<< /Type /Font /Subtype /Type0 /BaseFont /" + nome +
        " /Encoding /Identity-H /DescendantFonts [" + (id + 1) + " 0 R]" +
        " /ToUnicode " + (id + 3) + " 0 R >>");
      objeto(id + 1, "<< /Type /Font /Subtype /CIDFontType2 /BaseFont /" + nome +
        " /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >>" +
        " /FontDescriptor " + (id + 2) + " 0 R /DW 500 /W [" + w.join(" ") + "]" +
        " /CIDToGIDMap /Identity >>");
      objeto(id + 2, "<< /Type /FontDescriptor /FontName /" + nome +
        " /Flags 4 /FontBBox [" + d.bbox.join(" ") + "] /ItalicAngle " +
        (d.italico ? -12 : 0) + " /Ascent " + d.ascent + " /Descent " +
        d.descent + " /CapHeight 700 /StemV 80 /FontFile2 " + (id + 4) +
        " 0 R >>");

      // ToUnicode: deixa o cliente copiar e buscar texto dentro do PDF
      var pares = [];
      Object.keys(d.cmap).forEach(function (codigo) {
        pares.push("<" + hex4(d.cmap[codigo]) + "> <" + hex4(+codigo) + ">");
      });
      var cmapTxt = "/CIDInit /ProcSet findresource begin 12 dict begin " +
        "begincmap /CMapName /A def /CMapType 2 def 1 begincodespacerange " +
        "<0000> <FFFF> endcodespacerange\n";
      for (var k = 0; k < pares.length; k += 100) {
        var lote = pares.slice(k, k + 100);
        cmapTxt += lote.length + " beginbfchar\n" + lote.join("\n") +
                   "\nendbfchar\n";
      }
      cmapTxt += "endcmap CMapName currentdict /CMap defineresource pop " +
                 "end end";
      objeto(id + 3, "<< /Length " + cmapTxt.length + " >>", cmapTxt);
      objeto(id + 4, "<< /Length " + arquivo.length +
             " /Length1 " + arquivo.length + " >>", arquivo);
    });

    var inicioXref = deslocamento;
    var xref = "xref\n0 " + (total + 1) + "\n0000000000 65535 f \n";
    for (i = 1; i <= total; i++) {
      var pos = posicoes[i] || 0;
      xref += ("0000000000" + pos).slice(-10) + " 00000 n \n";
    }
    push(xref);
    push("trailer\n<< /Size " + (total + 1) + " /Root 1 0 R >>\nstartxref\n" +
         inicioXref + "\n%%EOF\n");

    var tamanho = partes.reduce(function (s, p) { return s + p.length; }, 0);
    var saida = new Uint8Array(tamanho), p = 0;
    partes.forEach(function (b) { saida.set(b, p); p += b.length; });
    return saida;
  };

  global.PDFWeb = PDF;
})(window);

/* relatorio.js — monta o PDF de apresentação a partir do que estiver filtrado
   na tela. Mesma estrutura do gerador em Python: capa, a rede em números,
   referências hospitalares, e as seções linha por linha. */
(function (global) {
  "use strict";

  var MM = 72 / 25.4;
  var L = 297 * MM, A = 210 * MM;          // A4 paisagem
  var MARGEM = 11 * MM;   // mais largura util para as colunas
  var UTIL = L - 2 * MARGEM;

  var NAVY = "#0d2a4f", NAVY_MEIO = "#20456f", OURO = "#9a7513",
      OURO_CLARO = "#e3c46a", TINTA = "#1b2331", CINZA = "#66707f",
      CINZA_CLARO = "#98a1b0", RISCO = "#e4e9f0", ZEBRA = "#f7f9fc",
      BRANCO = "#ffffff";

  var COR_LINHA = { "PME/PJ": "#2733c4", "Adesao": "#7c2f6d",
                    "Amil S": "#0b6154", "Black": "#3a3a3a" };

  var MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
               "julho", "agosto", "setembro", "outubro", "novembro",
               "dezembro"];

  var ORDEM = ["Hospitais", "Pronto-socorro 24h", "Pronto atendimento",
               "Laboratorios e imagem", "Hemodialise", "Telemedicina", "TEA",
               "Clinicas e consultorios"];

  function limpo(s) {
    return String(s == null ? "" : s)
      .replace(/\s*-\s*\d{6,}\s*$/, "")
      .replace(/^(HOSPITAIS|PRONTO SOCORRO|PRONTO ATENDIMENTO)\s*-\s*/, "");
  }

  /* Bairro + cidade onde o prestador está. A busca da Amil por uma cidade
     devolve a rede da região, então o bairro sozinho confundiria. */
  function localizacao(item) {
    var b = (item.b || []).slice(0, 2).join(" · ");
    var c = (item.cr || []).join(" / ");
    return c && b ? b + " — " + c : (b || c);
  }

  var MINUSCULAS = { da: 1, das: 1, de: 1, di: 1, do: 1, dos: 1, e: 1, em: 1,
                     na: 1, nas: 1, no: 1, nos: 1, ou: 1, para: 1, por: 1 };
  var SIGLAS = { BR: 1, PR: 1, SC: 1, RS: 1, TEA: 1, ATM: 1, UTI: 1, CDI: 1, SUS: 1, RX: 1, TC: 1, RM: 1,
                 SPA: 1, PS: 1, UPA: 1, AME: 1, LTDA: 1, ME: 1, EPP: 1, SA: 1,
                 INC: 1, IPO: 1, HGU: 1, NSA: 1, CEM: 1, CCC: 1, FP: 1,
                 S: 1, N: 1 };

  /* Nome proprio e endereco: caixa de texto, nao caixa alta. Siglas de duas
     a quatro letras ficam como estao. */
  function nomeBonito(t) {
    if (!t) return "";
    if (!/[A-ZÀ-Ú]{3}/.test(t)) return t;
    return String(t).replace(/[A-Za-zÀ-ú][A-Za-zÀ-ú'-]*/g, function (pal, i) {
      // o token leva o hifen junto ("Br-116" casa como "Br-"), entao a
      // consulta da sigla ignora pontuacao no fim
      var alto = pal.toUpperCase(), nu = alto.replace(/[-']+$/, "");
      if (SIGLAS[nu]) return nu + alto.slice(nu.length);
      var baixo = pal.toLowerCase();
      if (i > 0 && MINUSCULAS[baixo]) return baixo;
      return baixo.charAt(0).toUpperCase() + baixo.slice(1);
    });
  }

  function capitalizar(s) {
    var t = limpo(s).toLowerCase().replace(/(^|[\s(\/-])([a-zà-ú])/g,
      function (m, a, b) { return a + b.toUpperCase(); });
    return t.replace(/\bDa\b/g, "da").replace(/\bDe\b/g, "de")
            .replace(/\bDo\b/g, "do").replace(/\bDos\b/g, "dos")
            .replace(/\bE\b/g, "e").replace(/\bOu\b/g, "ou")
            .replace(/\bCom\b/g, "com").replace(/\bPor\b/g, "por")
            .replace(/\bTea\b/g, "TEA").replace(/\bAtm\b/g, "ATM");
  }

  // ------------------------------------------------------------- construtor
  function Relatorio(fontes, opcoes) {
    this.f = fontes;
    this.o = opcoes || {};
    this.pdf = new global.PDFWeb(L, A);
    this.y = 0;
  }

  Relatorio.prototype.carregarFontes = function () {
    var eu = this;
    ["serif", "serifB", "serifI", "sans", "sansM", "sansB"].forEach(function (k) {
      if (eu.f[k]) eu.pdf.addFonte(k, eu.f[k]);
    });
  };

  /* Constelacao da rede: os circulos do mapa, em ouro sobre o navy da capa.
     Ocupa a metade direita, longe do titulo. */
  Relatorio.prototype.constelacao = function (cidades, x0, y0, larg, alt) {
    if (!cidades || cidades.length < 2) return;
    var p = this.pdf;
    var lats = cidades.map(function (c) { return c.lat; });
    var lngs = cidades.map(function (c) { return c.lng; });
    var la0 = Math.min.apply(null, lats), la1 = Math.max.apply(null, lats);
    var lo0 = Math.min.apply(null, lngs), lo1 = Math.max.apply(null, lngs);
    var k = Math.cos((la0 + la1) / 2 * Math.PI / 180);
    var dl = Math.max((lo1 - lo0) * k, 1e-6), da = Math.max(la1 - la0, 1e-6);
    var e = Math.min(larg / dl, alt / da);
    var cx = x0 + (larg - dl * e) / 2, cy = y0 + (alt - da * e) / 2;
    var maior = Math.max.apply(null, cidades.map(function (c) { return c.n; }));
    cidades.forEach(function (c) {
      var px = cx + (c.lng - lo0) * k * e;
      var py = cy + (c.lat - la0) * e;
      var raio = 2.2 + 15 * Math.sqrt(c.n / maior);
      // sem canal de transparencia no gerador: o tom faz o papel do veu
      p.circulo(px, py, raio, "#3f6199", true, 0.8);
    });
  };

  Relatorio.prototype.capa = function () {
    var p = this.pdf, hoje = new Date(), o = this.o;
    p.novaPagina();
    p.retangulo(0, 0, L, A, NAVY);
    // longe do titulo, que chega a ~65% da largura
    this.constelacao(o.mapa, L * 0.60, A * 0.16, L * 0.33, A * 0.58);
    p.retangulo(0, A - 7 * MM, L, 7 * MM, o.cor);
    p.retangulo(0, A - 9 * MM, L, 2 * MM, OURO);

    p.retangulo(30 * MM, A - 71 * MM, 3.4, 12, OURO);
    p.texto(30 * MM + 11, A - 69 * MM,
            (o.cidade || "").toUpperCase(), "sansB", 9, OURO_CLARO);
    p.texto(30 * MM, A - 82 * MM, "Rede Credenciada Amil", "serifB", 42, BRANCO);
    p.texto(30 * MM, A - 101 * MM,
            o.semCidadeNaCapa ? o.produto : o.produto + "  ·  " + o.cidade,
            "serifI", 31, OURO_CLARO);
    p.linha(30 * MM, A - 110 * MM, 92 * MM, A - 110 * MM, OURO, 1.2);
    /* Num comparativo o subtitulo so diz "4 planos comparados"; o cliente
       precisa ver QUAIS sao, entao eles vem listados logo abaixo. */
    var recuo = 0;
    if (o.comparativo && o.listaProdutos && o.listaProdutos.length > 3) {
      var linhasP = p.quebrar(o.listaProdutos.join("   ·   "), "sans", 11,
                              200 * MM);
      for (var i = 0; i < linhasP.length; i++) {
        p.texto(30 * MM, A - 118 * MM - i * 15, linhasP[i], "sans", 11,
                "#cfe0f5");
      }
      recuo = linhasP.length * 15 + 4;
    }
    p.texto(30 * MM, A - 121 * MM - recuo,
            "Levantado na busca avançada oficial da Amil em " + hoje.getDate() +
            " de " + MESES[hoje.getMonth()] + " de " + hoje.getFullYear(),
            "sans", 9.5, "#9fb8d8");

    selo(p, 30 * MM, 26 * MM, 44, (o.corretor || {}).corretora);
    p.texto(30 * MM, 18 * MM, o.corretor.nome, "sans", 9.4, "#c7d8ee");
    p.texto(30 * MM, 12 * MM, o.corretor.email + "        " + o.corretor.fone,
            "sans", 9.4, "#9fb8d8");
  };

  /* Selo da corretora: tag dourada com o canto direito em diagonal, do
     jeito que aparece no material impresso. Desenhado em vetor - nitido em
     qualquer zoom e nao pesa no arquivo como uma imagem pesaria. */
  /* Clareia ou escurece uma cor. Tres produtos da mesma linha (Bronze,
     Prata e Ouro sao todos PME/PJ) sairiam com pilulas identicas; o tom
     diferencia a coluna sem inventar uma cor fora da identidade. */
  function tom(hex, fator) {
    var n = parseInt(hex.replace("#", ""), 16);
    var r0 = (n >> 16) & 255, g0 = (n >> 8) & 255, b0 = n & 255;
    function m(c) {
      var v = fator >= 0 ? c + (255 - c) * fator : c * (1 + fator);
      return Math.max(0, Math.min(255, Math.round(v)));
    }
    return "#" + [m(r0), m(g0), m(b0)].map(function (v) {
      return ("0" + v.toString(16)).slice(-2);
    }).join("");
  }

  /* O selo desenha a marca em duas linhas: a primeira palavra em serifa e
     o resto espacado embaixo - "Mazza" sobre "BROKER". A marca vem travada
     pela pagina; o corretor troca so o proprio contato. */
  function partesDaMarca(nome) {
    var t = String(nome || "Mazza Broker").trim().split(/\s+/);
    return { alto: t[0], baixo: t.slice(1).join(" ").toUpperCase() };
  }

  function selo(p, x, y, altura, marca) {
    var alt = altura || 22;
    var m = partesDaMarca(marca);
    var corpoM = alt * 0.46;                    // nome em serifa
    var corpoB = alt * 0.15;                    // resto, espacado embaixo
    var recuo = alt * 0.34;
    var baixo = m.baixo.split("").join(" ");
    var lm = p.larguraTexto(m.alto, "serifB", corpoM);
    var lb = p.larguraTexto(baixo, "sansB", corpoB);
    var bico = alt * 0.5;
    var larg = recuo + Math.max(lm, lb) + bico + alt * 0.3;
    p.poligono([[x, y], [x + larg, y], [x + larg - bico, y + alt],
                [x, y + alt]], OURO);
    p.texto(x + recuo, y + alt * 0.40, m.alto, "serifB", corpoM, BRANCO);
    // a segunda linha alinha a direita da primeira, como no logo impresso
    p.texto(x + recuo + lm - lb, y + alt * 0.17, baixo, "sansB",
            corpoB, BRANCO);
    return larg;
  }

  Relatorio.prototype.novaPagina = function () {
    var p = this.pdf;
    p.novaPagina();
    p.retangulo(0, A - 3.4 * MM, L, 3.4 * MM, this.o.cor);
    p.linha(MARGEM, 11.5 * MM, L - MARGEM, 11.5 * MM, RISCO, 0.6);
    var larg = selo(p, MARGEM, 4.2 * MM, 20,
                    (this.o.corretor || {}).corretora);
    p.texto(MARGEM + larg + 10, 7 * MM, "Rede credenciada Amil " +
            this.o.produto + "  —  " + this.o.cidade, "sans", 7.6, CINZA_CLARO);
    var n = String(p.pagina());
    p.texto(L - MARGEM - p.larguraTexto(n, "sansB", 9), 7 * MM, n,
            "sansB", 9, OURO);
    this.y = A - 12.5 * MM;   // era 22 mm: 9,5 mm de papel em branco por pagina
  };

  /* Quanto sobra no pe da pagina antes de virar. Era 16 mm; a 13 mm cabe
     mais uma linha inteira de prestador por pagina. */
  var PE = 12 * MM;   // 1 mm acima do fio do rodape

  Relatorio.prototype.espaco = function (altura) {
    if (this.y - altura < PE) this.novaPagina();
  };

  Relatorio.prototype.titulo = function (texto, subtitulo) {
    this.espaco(28);
    // barra vertical colorida antes do titulo: assinatura do material
    this.pdf.retangulo(MARGEM, this.y - 3.5, 4, 18.5, this.o.cor);
    this.pdf.texto(MARGEM + 13, this.y, texto, "serifB", 18, NAVY);
    this.y -= 13;
    if (subtitulo) {
      var linhas = this.pdf.quebrar(subtitulo, "sans", CORPO.dado, UTIL * 0.72);
      for (var i = 0; i < linhas.length; i++) {
        this.pdf.texto(MARGEM + 13, this.y, linhas[i], "sans", CORPO.dado, CINZA);
        this.y -= 11.4;
      }
    }
    this.y -= 2;
  };

  Relatorio.prototype.faixa = function (nome, quantos) {
    this.espaco(40);
    var p = this.pdf, alt = 21;
    p.retangulo(MARGEM, this.y - alt + 5, UTIL, alt, NAVY);
    p.retangulo(MARGEM, this.y - alt + 5, 4, alt, this.o.cor);
    p.texto(MARGEM + 11, this.y - 8.5, nome.toUpperCase(), "sansB",
            CORPO.faixa, BRANCO);
    var dir = quantos + (quantos === 1 ? " prestador" : " prestadores");
    p.texto(MARGEM + UTIL - 11 - p.larguraTexto(dir, "sansB", CORPO.faixa),
            this.y - 8.5, dir, "sansB", CORPO.faixa, "#a8bdd8");
    this.y -= alt + 3;
  };

  /* Cabeçalho das colunas. Redesenhado sempre que a tabela vira a página. */
  Relatorio.prototype.cabecalhoTabela = function (cols, desdeCentrada) {
    var p = this.pdf, x = MARGEM;
    for (var i = 0; i < cols.length; i++) {
      if (desdeCentrada >= 0 && i >= desdeCentrada) {
        // pilula colorida com o nome do produto, centrada na coluna
        var partes = p.quebrar(cols[i].rot, "sansB", CORPO.coluna,
                               cols[i].l - 12);
        var nLin = Math.min(2, partes.length);
        var largP = 0;
        for (var j = 0; j < nLin; j++) {
          largP = Math.max(largP, p.larguraTexto(partes[j], "sansB",
                                                 CORPO.coluna));
        }
        var altP = nLin * 8.6 + 5;
        var idx = i - desdeCentrada;
        var base = this.o.cores ? (this.o.cores[idx] || NAVY_MEIO) : NAVY_MEIO;
        // conta quantos produtos antes deste ja usam a mesma cor de linha
        var repetido = 0;
        if (this.o.cores) {
          for (var q = 0; q < idx; q++) {
            if (this.o.cores[q] === base) repetido++;
          }
        }
        var corP = repetido ? tom(base, -0.16 * repetido) : base;
        p.pilula(x + cols[i].l / 2 - largP / 2 - 7, this.y - altP + 7.5,
                 largP + 14, altP, corP);
        for (var j2 = 0; j2 < nLin; j2++) {
          p.texto(x + cols[i].l / 2 -
                  p.larguraTexto(partes[j2], "sansB", CORPO.coluna) / 2,
                  this.y - j2 * 8.6, partes[j2], "sansB", CORPO.coluna, BRANCO);
        }
      } else {
        p.texto(x + 8, this.y, cols[i].rot, "sansB", CORPO.coluna, CINZA_CLARO);
      }
      x += cols[i].l;
    }
    if (desdeCentrada >= 0) this.y -= 9.4;
    this.y -= 4;
    p.linha(MARGEM, this.y, MARGEM + UTIL, this.y, NAVY_MEIO, 0.9);
    // a folga acompanha o maior corpo que pode vir logo abaixo
    this.y -= alturaAcima(Math.max(CORPO.nome, CORPO.cidade)) + 4;
  };

  /* Altura de linha e teto de linhas por celula. O que engordava o PDF era a
     coluna de especialidades: 10 itens viravam 7 linhas e cada prestador
     ocupava 80 pt. Com teto de 2 linhas cabem ~3x mais prestadores por
     pagina, e a informacao completa continua no link e no CSV. */
  /* Entrelinha acompanha o corpo: 10,2 pt de texto pede ~11,6 pt de linha.
     A folga continua enxuta - o ganho de densidade veio das margens e do
     teto de linhas, nao de espremer a tipografia. */
  var ENTRE = 11.6;
  var FOLGA = 5;

  var CORPO = { nome: 10.2, dado: 9, esp: 8.2, coluna: 7.6, faixa: 12,
                cidade: 11.4 };

  /* Altura que as hastes altas ocupam acima da linha de base. Toda folga
     abaixo de uma regua sai daqui - foi o que faltava e fez a regua cortar
     o texto quando a tipografia cresceu. */
  function alturaAcima(corpo) { return corpo * 0.78; }
  var TETO = { nome: 2, endereco: 2, bairro: 2, telefone: 2, esp: 2 };

  /* Visto desenhado a vetor. As fontes embutidas (Constantia e Segoe UI) nao
     trazem o glifo U+2713 - pedir por ele imprime caixa vazia, o mesmo erro
     que a estrela ja tinha causado. Duas retas resolvem e ficam nitidas. */
  function visto(p, cx, cy, cor) {
    p.linha(cx - 3.8, cy + 0.5, cx - 1.1, cy - 2.7, cor, 1.8);
    p.linha(cx - 1.5, cy - 2.7, cx + 4.2, cy + 5.0, cor, 1.8);
  }

  function cortar(linhas, teto) {
    if (linhas.length <= teto) return linhas;
    var saida = linhas.slice(0, teto);
    saida[teto - 1] = saida[teto - 1].replace(/[\s,;·|]+$/, "") + "…";
    return saida;
  }

  /* Cidade onde o prestador de fato esta. Um prestador pode ter unidade em
     mais de uma cidade; a primeira e a que manda no agrupamento. */
  function cidadeDe(item) {
    var c = (item.cr && item.cr.length) ? item.cr : (item.cid || []);
    return c[0] || "";
  }

  /* Quebra a lista em blocos por cidade, cidade com mais prestadores
     primeiro - a rede da praca principal e o que o cliente olha antes. */
  function porCidade(lista) {
    var mapa = {}, ordem = [];
    lista.forEach(function (item) {
      var c = cidadeDe(item);
      if (!mapa[c]) { mapa[c] = []; ordem.push(c); }
      mapa[c].push(item);
    });
    ordem.sort(function (a, b) {
      return mapa[b].length - mapa[a].length ||
             (a < b ? -1 : 1);
    });
    return ordem.map(function (c) { return { cidade: c, itens: mapa[c] }; });
  }

  Relatorio.prototype.cabecaCidade = function (nome, quantos) {
    var p = this.pdf;
    this.espaco(46);
    this.y -= 8;
    var c = CORPO.cidade;
    p.retangulo(MARGEM, this.y - 2.5, 3, c * 1.15, this.o.cor);
    var rot = nomeBonito(nome);
    p.texto(MARGEM + 9, this.y, rot, "sansB", c, this.o.cor);
    p.texto(MARGEM + 9 + p.larguraTexto(rot, "sansB", c) + 8, this.y,
            quantos + (quantos === 1 ? " prestador" : " prestadores"),
            "sans", 9, CINZA_CLARO);
    this.y -= alturaAcima(CORPO.nome) + 6;
  };

  Relatorio.prototype.tabela = function (lista, comEspecialidades, produtos) {
    var p = this.pdf, eu = this;
    produtos = produtos || [];
    var comProdutos = produtos.length > 1;

    var fatias, rotulos;
    if (comProdutos) {
      // uma coluna estreita por produto, no lugar das especialidades
      var base = [0.235, 0.255, 0.115, 0.105];
      var sobra = 1 - base.reduce(function (a, b) { return a + b; }, 0);
      fatias = base.slice();
      rotulos = ["Prestador", "Endereço", "Bairro", "Telefone"];
      produtos.forEach(function (pr) {
        fatias.push(sobra / produtos.length);
        rotulos.push((pr.rotulo + " " + (pr.acomodacao || "")).trim());
      });
    } else {
      fatias = comEspecialidades
        ? [0.235, 0.275, 0.105, 0.115, 0.270]
        : [0.285, 0.335, 0.150, 0.230];
      rotulos = comEspecialidades
        ? ["Prestador", "Endereço", "Bairro", "Telefone", "Especialidades"]
        : ["Prestador", "Endereço", "Bairro", "Telefone"];
    }
    var cols = fatias.map(function (f, i) {
      return { l: UTIL * f, rot: rotulos[i] };
    });

    this.espaco(36);
    this.cabecalhoTabela(cols, comProdutos ? 4 : -1);

    var blocos = this.o.semCidade ? [{ cidade: "", itens: lista }]
                                  : porCidade(lista);
    var indice = 0, eu2 = this;
    blocos.forEach(function (bloco) {
      if (bloco.cidade) eu2.cabecaCidade(bloco.cidade, bloco.itens.length);
      bloco.itens.forEach(function (item) {
        indice++;
        eu2.linhaTabela(item, indice, cols, comProdutos, comEspecialidades,
                        produtos);
      });
    });
    this.y -= 6;
  };

  Relatorio.prototype.linhaTabela = function (item, indice, cols, comProdutos,
                                              comEspecialidades, produtos) {
    var p = this.pdf, eu = this;
    (function (item, indice) {
      var celulas = [
        cortar(p.quebrar(nomeBonito(item.n), "sansM", CORPO.nome,
                         cols[0].l - 14), TETO.nome),
        cortar(p.quebrar(nomeBonito((item.e || []).slice(0, 2).join("  |  ")),
                         "sans", CORPO.dado, cols[1].l - 14), TETO.endereco),
        cortar(p.quebrar(nomeBonito(localizacao(item)), "sans", CORPO.dado,
                         cols[2].l - 14), TETO.bairro),
        cortar(p.quebrar((item.t || []).slice(0, 2).join("  "), "sans",
                         CORPO.dado, cols[3].l - 14), TETO.telefone)
      ];
      var selo = (item.s && item.s.length) ? item.s.join(" · ").toUpperCase() : "";
      if (comProdutos) {
        produtos.forEach(function () { celulas.push([""]); });
      } else if (comEspecialidades) {
        var esp = (item.esp || []).slice(0, 6).map(capitalizar).join(", ");
        var sobraE = (item.esp || []).length - 6;
        if (sobraE > 0) esp += " e mais " + sobraE;
        celulas.push(cortar(p.quebrar(esp, "sans", CORPO.esp, cols[4].l - 14),
                            TETO.esp));
      }

      var linhas = Math.max.apply(null, celulas.map(function (c) {
        return c.length;
      }));
      var altura = linhas * ENTRE + (selo ? 11 : 0) + FOLGA;
      if (eu.y - altura < PE) {
        eu.novaPagina();
        eu.cabecalhoTabela(cols, comProdutos ? 4 : -1);
      }
      if (indice % 2 === 1) {
        p.retangulo(MARGEM, eu.y - altura + 8, UTIL, altura, ZEBRA);
      }

      var x = MARGEM, topo = eu.y;
      celulas.forEach(function (linhasCelula, ci) {
        var ehProduto = comProdutos && ci >= 4;
        if (ehProduto) {
          var pr = produtos[ci - 4];
          var tem = (item.meus || []).indexOf(pr.codigo) >= 0;
          var corPr = COR_LINHA[pr.linha] || NAVY_MEIO;
          if (tem) {
            // circulo em volta do visto, como no material impresso
            p.circulo(x + cols[ci].l / 2, topo + 1.2, 6.2, corPr, true, 0.9);
            visto(p, x + cols[ci].l / 2, topo + 0.2, corPr);
          } else {
            // celula vazia e ambigua: o travessao diz "nao atende"
            p.linha(x + cols[ci].l / 2 - 3.5, topo + 1.2,
                    x + cols[ci].l / 2 + 3.5, topo + 1.2, CINZA_CLARO, 1.1);
          }
          x += cols[ci].l;
          return;
        }
        var yy = topo;
        var corpo = ci === 0 ? CORPO.nome : (ci === 4 ? CORPO.esp : CORPO.dado);
        var fonte = ci === 0 ? "sansM" : "sans";
        var tinta = ci === 0 ? NAVY : (ci === 4 ? CINZA : TINTA);
        for (var k = 0; k < linhasCelula.length; k++) {
          p.texto(x + 8, yy, linhasCelula[k], fonte, corpo, tinta);
          yy -= ENTRE;
        }
        if (ci === 0 && selo) {
          p.texto(x + 8, yy + 1.5, selo, "sansB", 7, OURO);
        }
        x += cols[ci].l;
      });
      eu.y -= altura;
      p.linha(MARGEM, eu.y + 6, MARGEM + UTIL, eu.y + 6, RISCO, 0.5);
    })(item, indice);
  };

  Relatorio.prototype.numeros = function (cartoes) {
    var p = this.pdf, eu = this, larg = UTIL / 3, alt = 46;
    for (var faixa = 0; faixa < 2; faixa++) {
      this.espaco(alt + 6);
      var y0 = this.y - alt + 12;
      p.retangulo(MARGEM, y0, UTIL, alt, BRANCO);
      for (var c = 0; c < 3; c++) {
        var item = cartoes[faixa * 3 + c];
        if (!item) continue;
        var x = MARGEM + c * larg;
        p.linha(x, y0, x, y0 + alt, RISCO, 0.6);
        p.texto(x + 16, this.y - 12, String(item[0]), "serifB", 28, NAVY);
        p.texto(x + 16, this.y - 27, item[1], "sans", 8.6, CINZA);
      }
      p.linha(MARGEM, y0, MARGEM + UTIL, y0, RISCO, 0.6);
      p.linha(MARGEM, y0 + alt, MARGEM + UTIL, y0 + alt, RISCO, 0.6);
      p.linha(MARGEM + UTIL, y0, MARGEM + UTIL, y0 + alt, RISCO, 0.6);
      p.linha(MARGEM, y0, MARGEM, y0 + alt, RISCO, 0.6);
      this.y -= alt + 4;
    }
    this.y -= 10;
  };

  Relatorio.prototype.referencias = function (hospitais) {
    var p = this.pdf, eu = this, larg = UTIL / 5;
    for (var i = 0; i < hospitais.length; i += 5) {
      var fatia = hospitais.slice(i, i + 5);
      var celulas = fatia.map(function (h) {
        return p.quebrar(nomeBonito(h.n), "sansM", 9.4, larg - 22);
      });
      var linhas = Math.max.apply(null, celulas.map(function (c) {
        return c.length;
      }));
      var alt = linhas * 12 + 28;
      this.espaco(alt + 4);
      var y0 = this.y - alt + 12;
      p.retangulo(MARGEM, y0, UTIL, alt, BRANCO);
      fatia.forEach(function (h, c) {
        var x = MARGEM + c * larg, yy = eu.y - 2;
        p.linha(x, y0, x, y0 + alt, RISCO, 0.6);
        celulas[c].forEach(function (linha) {
          p.texto(x + 11, yy, linha, "sansM", 9.4, NAVY);
          yy -= 12;
        });
        if (h.s && h.s.length) {
          p.texto(x + 11 + p.larguraTexto(celulas[c][celulas[c].length - 1],
                  "sansM", 9.4) + 4, yy + 12, "ACRED.", "sansB", 6.6, OURO);
        }
        p.texto(x + 11, yy - 1,
                nomeBonito((h.b || [])[0] || "") + " · " + (h.esp || []).length +
                " especialidades", "sans", 7.8, CINZA);
      });
      p.linha(MARGEM, y0, MARGEM + UTIL, y0, RISCO, 0.6);
      p.linha(MARGEM, y0 + alt, MARGEM + UTIL, y0 + alt, RISCO, 0.6);
      p.linha(MARGEM + UTIL, y0, MARGEM + UTIL, y0 + alt, RISCO, 0.6);
      p.linha(MARGEM, y0, MARGEM, y0 + alt, RISCO, 0.6);
      this.y -= alt + 4;
    }
  };

  global.Relatorio = Relatorio;
  global.RelatorioAux = { MM: MM, L: L, A: A, MARGEM: MARGEM, UTIL: UTIL,
                          ORDEM: ORDEM, COR_LINHA: COR_LINHA, NAVY: NAVY,
                          CINZA: CINZA, TINTA: TINTA, capitalizar: capitalizar };
})(window);
