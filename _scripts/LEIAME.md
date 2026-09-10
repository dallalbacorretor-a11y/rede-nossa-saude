# Pipeline — rede credenciada Nossa Saúde (Campos Gerais)

Rodar dentro desta pasta `_scripts`. Precisa de `requests`, `pdfplumber`, `openpyxl`, `reportlab`
(e `pymupdf` só para conferir os PDFs).

```bash
# 1. mapeia os 328 planos da operadora -> rede credenciada de cada um  (planos_redes.json)
python map_planos.py

# 2. descobre quais redes chegam ao Paraná (1 PDF oficial por rede x UF, em pdfs_rede/)
UFS=PR python scrape_all.py

# 3. baixa a rede das 9 cidades, por rede credenciada, usando um plano representativo
#    de cada uma (rep_planos.json) -> pdfs_cg/
python scrape_cg2.py

# 4. parseia os PDFs -> dados_multi.json
python build_data2.py

# 5. gera as entregas
python gen_site.py     # site estático em ./site  (copiar para a raiz do repositório)
python gen_xlsx.py     # planilha -> 01 - REDE CREDENCIADA + site/arquivos
python gen_pdf.py      # os dois PDFs -> 02 - COMPARATIVOS + site/arquivos
python gen_resumo.py   # RESUMO.md
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
  um request devolve a rede inteira, sem paginação (`/comum/listaRedeCredenciada.php` pagina de 5 em 5).
- `POST /comum/buscaRede.php` com `{plano, local:'rede', rede:''}` devolve as redes credenciadas
  daquele plano — é o que dá o mapa plano → rede.
- Filtrar por `cidade=''` traz o estado inteiro; filtrar por `plano` é ligeiramente mais completo
  que filtrar por `tipoRede` (o filtro de rede perdeu 1 prestador em Ponta Grossa na conferência).

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

Conselhos variam bastante (CRM, CRP, CREFITO, CREFONO, CRO, CRN...) — por isso o regex usa
`(?:CNPJ|C[A-Z]{2,8})`.
