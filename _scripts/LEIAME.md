# Pipeline — rede credenciada Nossa Saúde (Campos Gerais)

Rodar dentro desta pasta `_scripts`. Precisa de `requests`, `pdfplumber`, `openpyxl`, `reportlab`
(e `pymupdf` só se quiser rasterizar os PDFs para conferir).

## Fluxo normal (rede única, todos os planos somados)

```bash
python scrape.py "" TODOS   # 1 PDF oficial por cidade, sem filtro de plano  -> pdfs/
python build_unico.py       # parseia os PDFs                                -> dados_unico.json
python gen_cidades.py       # 9 PDFs de cidade + o PDF da região             -> 02 - COMPARATIVOS + site
python gen_xlsx2.py         # a planilha                                     -> 01 - REDE CREDENCIADA + site
python tracar_mapa.py       # contorno do PR a partir do mapa da operadora   -> mapa_pr.json
python gen_site3.py         # o site estático                                -> ./site
python gen_resumo2.py       # RESUMO.md
```

Depois copiar `site/` para a raiz do repositório e dar `git push` — o GitHub Pages republica sozinho.

**Ordem importa:** `gen_site3.py` recria a pasta `site/` preservando `site/arquivos/`. Se rodar do
zero, rode `gen_site3.py` primeiro e depois `gen_cidades.py` / `gen_xlsx2.py`, que copiam os
arquivos para dentro do site.

## Fluxo opcional (conferir rede por rede)

Serve para saber qual rede credenciada cada plano usa — útil quando o cliente pergunta se o
prestador X atende o plano dele.

```bash
python map_planos.py        # 328 planos -> rede de cada um   -> planos_redes.json
UFS=PR python scrape_all.py # 1 PDF por rede x UF             -> pdfs_rede/
python scrape_cg2.py        # rede x cidade (plano represent.) -> pdfs_cg/
python build_data2.py       # -> dados_multi.json
```

## Como o site da operadora funciona

`prestador.nossasaude.com.br/comum/redeCredenciada.php` **redireciona para a home** se acessado
direto. É preciso criar a sessão antes:

1. `GET /rede/rede.php`
2. `POST /comum/RedeCredenciadaBuscaUsuario.php` com `todos=<qualquer coisa>` (botão "Listar todas as redes")
3. `GET /comum/redeCredenciada.php`

Depois disso:

- `POST /comum/imprimirRedeCredenciada.php?idsessao=` com os campos do `#form1` devolve
  `<SCRIPT>document.location='../temp/<hash>.pdf'</SCRIPT>` → baixar esse PDF. É o caminho rápido:
  um request devolve a consulta inteira, sem paginação (`/comum/listaRedeCredenciada.php` pagina
  de 5 em 5).
- `POST /comum/buscaRede.php` com `{plano, local:'rede', rede:''}` devolve as redes credenciadas
  daquele plano — é o que dá o mapa plano → rede.
- `cidade=''` traz o estado inteiro. Filtrar por `plano` é ligeiramente mais completo que filtrar
  por `tipoRede`.

## Formato do PDF oficial

```
NOME ( CNPJ: 00.000.000/0001-00) - Clínica     <- ou (CRM-PR 12345) - Médico
NOME FANTASIA
ESPECIALIDADE - RQE nº 12345
- Fulano de Tal (CRM-PR 99999) - Cardiologia   <- corpo clínico do prestador acima
Tel: (42)0000-0000
RUA X, 123 - COMPLEMENTO
BAIRRO - CIDADE - PR - CEP: 00000-000
```

Conselhos variam bastante (CRM, CRP, CREFITO, CREFONO, CRO, CRN...) — por isso o regex de
`parse.py` usa `(?:CNPJ|C[A-Z]{2,8})`.

## Arquivos deste diretório

| Arquivo | O que faz |
|---|---|
| `scrape.py` | sessão no site da operadora + download do PDF oficial |
| `parse.py` | lê o PDF oficial e devolve os prestadores estruturados |
| `textutil.py` | caixa alta da operadora → Título Com Acentos |
| `build_unico.py` | monta `dados_unico.json` (rede única) |
| `pdfamil.py` | motor de layout dos PDFs (padrão visual da corretora) |
| `gen_cidades.py` | gera os PDFs por cidade e o da região |
| `gen_xlsx2.py` / `gen_site3.py` / `gen_resumo2.py` | planilha, site e resumo |
| `tracar_mapa.py` | traca o contorno do Parana do mapa da operadora -> `mapa_pr.json` |
| `map_planos.py`, `scrape_all.py`, `scrape_cg2.py`, `build_data2.py` | trilha rede-a-rede |
