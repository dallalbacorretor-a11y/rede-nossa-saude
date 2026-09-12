# Atlas da Rede Nossa Saúde — Campos Gerais

Site estático com a rede credenciada da **Nossa Saúde** nas 9 cidades dos Campos Gerais / PR:
Ponta Grossa, Telêmaco Borba, Jaguariaíva, Castro, Irati, Palmeira, Carambeí, Prudentópolis e
Piraí do Sul.

**No ar em:** https://dallalbacorretor-a11y.github.io/rede-nossa-saude/

Publicado por **Mazza Broker** — Alan Vinicius Dall Alba · (41) 99547-6715 · alan.vinicius@mazzabroker.com.br

## O que tem

- Mapa do Paraná com as nove cidades: clique numa e veja os números e os hospitais dela
- **Um guia em PDF por cidade** para mandar pro cliente, além do PDF da região e da planilha
- Mapa de calor de onde fazer cada natureza de exame
- Busca por prestador, especialidade, bairro ou cidade

## Números

| | |
|---|---|
| Prestadores | 328 |
| Cidades | 9 |
| Hospitais para internação | 9 |
| Consulta | 10 de setembro de 2026 |

> A rede é definida e alterada exclusivamente pela operadora. Esta lista soma todos os planos da Nossa Saúde — antes de contratar, confirme no portal da operadora se o prestador atende o plano específico.

Rede credenciada oficial da operadora, em prestador.nossasaude.com.br, consultada em 10 de setembro de 2026 sem filtro de plano.

## Estrutura

```
index.html   estilo.css   app.js   dados.js      (dados em window.DADOS)
arquivos/            PDF da região e planilha
arquivos/cidades/    um PDF por cidade
_scripts/            pipeline que baixa a rede e regera tudo (ver _scripts/LEIAME.md)
```

O contorno do Paraná é traçado a partir do mapa de cobertura da operadora por
`_scripts/tracar_mapa.py`, e as cidades são posicionadas pelas coordenadas reais.

Sem build: HTML, CSS e JS puros. GitHub Pages em `main`, pasta raiz.
