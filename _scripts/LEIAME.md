# Pipeline — rede credenciada Nossa Saúde (Campos Gerais + Curitiba/RMC/Paranaguá)

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

No site publicado dá para trocar sem rodar nada: **Meus dados** (na barra de navegação ou no cartão
de contato) guarda os dados no navegador e gera um link `?c=...` para mandar a outro corretor.
**Os PDFs acompanham**: a página gera o PDF na hora, já com o nome de quem está usando.

O `corretor.json` vale para os arquivos gerados pelos scripts (planilha, resumo e os PDFs que
ficam no computador).


Rodar dentro desta pasta `_scripts`. Precisa de `requests`, `pdfplumber`, `openpyxl`, `reportlab`
(e `pymupdf` só se quiser rasterizar os PDFs para conferir).

## Fluxo normal (rede única, todos os planos somados)

```bash
python scrape.py "" TODOS   # 1 PDF oficial por cidade, sem filtro de plano  -> pdfs/
python build_unico.py       # parseia os PDFs                                -> dados_unico.json
python gen_cidades.py       # 9 PDFs de cidade + o PDF da região             -> 02 - COMPARATIVOS + site
python gen_xlsx2.py         # a planilha                                     -> 01 - REDE CREDENCIADA + site
python gen_resumo2.py       # RESUMO.md

# a pagina publicada (padrao da casa, igual Amil e Parana Clinicas):
cd padrao
python dados_ns.py          # dados_unico.json + dados_cwb.json -> dados/dados_ns.json
python montar_site.py       # base + dados -> saida/index.html
```

## Segunda região — Curitiba, RMC e Paranaguá

Mesmo caminho, outra pasta de PDFs. Só entra no site: os PDFs por cidade dessa região saem da
própria página, na hora.

```bash
python scrape_cwb.py        # 1 PDF oficial por cidade (16 cidades)  -> pdfs_cwb/
python build_cwb.py         # parseia                                -> dados_cwb.json
cd padrao && python dados_ns.py && python montar_site.py
```

As cidades da RMC atendidas foram conferidas no PDF do Paraná inteiro — fora Curitiba e São José
dos Pinhais, a maioria tem de 1 a 13 prestadores. Para incluir mais uma cidade (o litoral, por
exemplo), acrescente em `scrape_cwb.py` (`CIDADES`), em `build_cwb.py` (`CIDADES` e `ORDEM`) e a
sede do município em `padrao/dados_ns.py` (`COORD`).

Depois copiar `padrao/saida/index.html` para a raiz do repositório e dar `git push` — o GitHub
Pages republica sozinho.

A página é o mesmo aplicativo da Amil e da Paraná Clínicas; o PDF por cidade sai dela, na hora,
já assinado por quem está usando. Ver `padrao/LEIAME.md`.

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
| `build_unico.py` | monta `dados_unico.json` (rede única, Campos Gerais) |
| `scrape_cwb.py` / `build_cwb.py` | a mesma coleta para Curitiba, RMC e Paranaguá -> `dados_cwb.json` |
| `pdfamil.py` | motor de layout dos PDFs (padrão visual da corretora) |
| `gen_cidades.py` | gera os PDFs por cidade e o da região |
| `gen_xlsx2.py` / `gen_resumo2.py` | planilha e resumo |
| `padrao/` | a pagina publicada, no template da casa (ver `padrao/LEIAME.md`) |
| `corretor.py` / `corretor.json` | quem assina o material (a corretora e fixa) |
| `map_planos.py`, `scrape_all.py`, `scrape_cg2.py`, `build_data2.py` | trilha rede-a-rede |
