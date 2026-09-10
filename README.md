# Rede Credenciada Nossa Saúde — Campos Gerais

Site estático com a rede credenciada da **Nossa Saúde** nas 9 cidades dos Campos Gerais / PR:
Ponta Grossa, Telêmaco Borba, Jaguariaíva, Castro, Irati, Palmeira, Carambeí, Prudentópolis e
Piraí do Sul.

**No ar em:** https://dallalbacorretor-a11y.github.io/rede-nossa-saude/

Publicado por **Mazza Broker** — Alan Vinicius Dall Alba · (41) 99547-6715 · alan.vinicius@mazzabroker.com.br

## O que tem

- **Um PDF por cidade** para baixar e mandar pro cliente, no padrão visual dos materiais da
  corretora: rede em números, hospitais, exames por natureza, clínicas e médicos por especialidade
- PDF da região inteira e planilha XLSX com uma aba por cidade
- Busca por hospital, laboratório, médico, especialidade ou bairro
- Tabelas de cobertura por cidade e por natureza de exame

## Números

| | |
|---|---|
| Prestadores | 328 |
| Cidades | 9 |
| Hospitais para internação | 9 |
| Laboratórios e imagem | 38 |
| Consulta | 10 de setembro de 2026 |

## Todos os planos numa lista só

A operadora tem produtos que usam redes credenciadas diferentes. Este material soma todos eles:
se um prestador aparece aqui, é credenciado da Nossa Saúde naquela cidade por algum plano.

> A rede credenciada é definida e alterada exclusivamente pela operadora. Esta lista soma todos os planos da Nossa Saúde — antes de contratar, confirme no portal da operadora se o prestador atende o plano específico.

Rede Credenciada oficial da Nossa Saúde (prestador.nossasaude.com.br), consultada em 10 de setembro de 2026, sem filtro de plano.

## Estrutura

```
index.html      estilo.css      app.js      dados.js     (window.DADOS)
arquivos/       xlsx, PDF da região
arquivos/cidades/   um PDF por cidade
_scripts/       pipeline que baixa a rede e regera tudo (ver _scripts/LEIAME.md)
```

Sem build: é HTML/CSS/JS puro. GitHub Pages em `main`, pasta raiz.
