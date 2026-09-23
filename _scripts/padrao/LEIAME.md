# A página no padrão da casa

A página da Nossa Saúde é o **mesmo aplicativo** do site da Amil e do da Paraná Clínicas. Ele vive
em `base/` (três arquivos, copiados do estudo da Amil) e é adaptado por `montar_site.py`.

```
base/amil_head.html    CSS + marcação (até antes dos <script>)
base/amil_lib.js       fontes e o gerador de PDF
base/amil_app.js       a aplicação
```

## Como gerar

```bash
python dados_ns.py      # dados_unico.json + dados_cwb.json -> dados/dados_ns.json (formato do app)
python montar_site.py   # base + dados -> saida/index.html
```

Depois é só copiar `saida/index.html` para a raiz do repositório e dar push.

## Como o montar_site.py foi feito

A Paraná Clínicas já tinha percorrido o caminho Amil → outra operadora, incluindo a parte chata:
fazer o app parar de deduzir categoria pelo vocabulário da Amil e passar a confiar no `cat` que vem
no dado. Em vez de refazer essa cirurgia, o arquivo daqui **deriva do dela**:

```
montar_site_pc_referencia.py   cópia do montar_site.py da Paraná Clínicas
adaptar.py    etapa 1 — paleta, título, região
adaptar2.py   etapa 2 — um produto só, categorias da Nossa Saúde nos quadros e seções
adaptar3.py   etapa 3 — textos, cores do PDF, remove o "direcionamento interno" (não existe aqui)
adaptar4.py   etapa 4 — esconde a aba "Entre planos" quando só há um produto
adaptar5.py   etapa 5 — duas regiões: título, caixa do mapa por região, ORDEM_UF pelos dados
adaptar6.py   etapa 6 — o nome do PDF: "Nossa Saúde - <cidade ou região>.pdf"
```

Rodando as seis em ordem, sai o `montar_site.py`. Toda troca passa por `troca()` / `sub()`, que
estoura se o texto original não existir mais — se a Amil mudar o app base, a adaptação falha alto
em vez de sair torta.

```bash
python adaptar.py && python adaptar2.py && python adaptar3.py && python adaptar4.py && python adaptar5.py && python adaptar6.py
```

## O formato que o app espera

`window.DADOS_UF = {"CG": {...}, "CWB": {...}}`, uma chave por região — o app mostra um botão por
chave (na Amil as chaves são PR, SC e SP). Cada região tem:

| campo | o que é |
|---|---|
| `gerado_em`, `uf`, `estado` | data da coleta e o nome da região no título |
| `produtos` | `[{codigo, rotulo, acomodacao, linha, cor, ans, nome}]` — aqui, um só |
| `categorias` | ordem de exibição; a de hospital **precisa** começar com "Hospitais" |
| `catsExame` | quais categorias são lugar de exame |
| `centros` | `{"BAIRRO\|CIDADE": [lat, lon, quantos]}` — alimenta o "Perto de" |
| `prestadores` | `n, c, cid, cr, b, e, t, mail, acess, eq, p, pp, dir, cat, cats, esp, pc, s, xy` |

`dados_ns.py` monta isso a partir do `dados_unico.json` (Campos Gerais) e do `dados_cwb.json`
(Curitiba, RMC e Paranaguá). Para acrescentar uma região, basta coletar os PDFs, gerar o JSON e
somar uma linha em `REGIOES` — mais a data em `GERADO_EM` e a sede de cada cidade nova em `COORD`.

## O que é diferente aqui

- **Um produto só.** O material soma todos os planos da operadora, então `produtos` tem um item e a
  aba "Entre planos" fica escondida.
- **Sem direcionamento interno.** A Nossa Saúde não publica hospital liberado só por
  encaminhamento; o "D" no lugar do visto foi removido.
- **Coordenadas por cidade.** A operadora não publica endereço geocodificado, então cada prestador
  recebe a sede do próprio município (IBGE) — o mapa fica com uma bolha por cidade, que é a
  granularidade certa para esse número de cidades. A caixa do mapa é calculada por região.
