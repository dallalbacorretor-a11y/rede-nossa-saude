# Pipeline — rede credenciada Nossa Saúde (Campos Gerais)

## Trocar o nome do corretor

Abra **`corretor.json`** nesta pasta, troque os dados e rode de novo os geradores (`gen_cidades.py`,
`gen_xlsx2.py`, `gen_site4.py`, `gen_resumo2.py`). Site, PDFs, planilha e resumo saem no nome novo.

```json
{
 "nome": "Alan Vinicius Dall Alba",
 "cargo": "Corretor de saúde",
 "telefone": "(41) 99547-6715",
 "whatsapp": "5541995476715",
 "email": "alan.vinicius@mazzabroker.com.br"
}
```

A corretora **Mazza Broker** é fixa (está em `corretor.py`) e não muda.

No site publicado dá para trocar sem rodar nada: o cartão de contato tem o botão **Editar meus
dados**, que guarda no navegador e gera um link `?c=...` para mandar a outro corretor. Os PDFs, por
serem arquivos prontos, continuam com o nome de quem os gerou — para mudar neles, é pelo
`corretor.json`.


Rodar dentro desta pasta `_scripts`. Precisa de `requests`, `pdfplumber`, `openpyxl`, `reportlab`
(e `pymupdf` só se quiser rasterizar os PDFs para conferir).

## Fluxo normal (rede única, todos os planos somados)

```bash
python scrape.py "" TODOS   # 1 PDF oficial por cidade, sem filtro de plano  -> pdfs/
python build_unico.py       # parseia os PDFs                                -> dados_unico.json
python gen_cidades.py       # 9 PDFs de cidade + o PDF da região             -> 02 - COMPARATIVOS + site
python gen_xlsx2.py         # a planilha                                     -> 01 - REDE CREDENCIADA + site
python tracar_mapa.py       # contorno do PR a partir do mapa da operadora   -> mapa_pr.json
python baixar_satelite.py   # mosaico de satelite da regiao (Esri)           -> site/img
python gerar_capas.py       # capa de cada guia em JPG                       -> site/img/capas
python gen_site4.py         # o site estatico                                -> ./site
python gen_resumo2.py       # RESUMO.md
```

Depois copiar `site/` para a raiz do repositório e dar `git push` — o GitHub Pages republica sozinho.

**Ordem importa:** `gen_site4.py` recria a pasta `site/` preservando `site/arquivos/`. Se rodar do
zero, rode `gen_site4.py` primeiro e depois `gen_cidades.py` / `gen_xlsx2.py`, que copiam os
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
| `gen_xlsx2.py` / `gen_site4.py` / `gen_resumo2.py` | planilha, site e resumo |
| `baixar_satelite.py` | baixa os tiles do Esri World Imagery e monta a imagem da regiao |
| `gerar_capas.py` | rasteriza a capa de cada PDF para a galeria do site |
| `tracar_mapa.py` | traca o contorno do Parana do mapa da operadora -> `mapa_pr.json` |
| `corretor.py` / `corretor.json` | quem assina o material (a corretora e fixa) |
| `map_planos.py`, `scrape_all.py`, `scrape_cg2.py`, `build_data2.py` | trilha rede-a-rede |
