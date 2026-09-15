# Rede credenciada Nossa Saúde — Campos Gerais

Página da rede credenciada da **Nossa Saúde** nas 9 cidades dos Campos Gerais / PR:
Ponta Grossa, Telêmaco Borba, Jaguariaíva, Castro, Irati, Palmeira, Carambeí, Prudentópolis e
Piraí do Sul.

**No ar em:** https://dallalbacorretor-a11y.github.io/rede-nossa-saude/

Publicado por **Mazza Broker** — Alan Vinicius Dall Alba · (41) 99547-6715 ·
alan.vinicius@mazzabroker.com.br

## Mesmo padrão da Amil e da Paraná Clínicas

A página é o **mesmo aplicativo** dos outros dois estudos da corretora, recolorido para a marca da
operadora. Vem tudo junto de lá:

- abas **Visão geral · Rede completa** (a de "Entre planos" some aqui: o material soma todos os
  planos numa rede só, então ela compararia o plano com ele mesmo)
- mapa de bolhas por cidade, filtros por cidade, categoria, especialidade e bairro
- **PDF gerado na hora pela própria página**, já assinado por quem está usando
- **Meus dados**: cada corretor assina o próprio material; a corretora Mazza Broker é fixa

## Números

| | |
|---|---|
| Prestadores | 328 |
| Cidades | 9 |
| Hospitais | 9 |
| Consulta | 10/09/2026 |

> A rede é definida e alterada exclusivamente pela operadora. Esta lista soma todos os planos da
> Nossa Saúde — antes de contratar, confirme no portal da operadora se o prestador atende o plano
> específico.

Rede credenciada oficial da operadora, em prestador.nossasaude.com.br, consultada em
10 de setembro de 2026 sem filtro de plano.

## Estrutura

```
index.html              a página inteira (CSS, app e dados num arquivo só)
_scripts/               coleta e preparo dos dados (ver _scripts/LEIAME.md)
_scripts/padrao/        o template da casa e a adaptação para a Nossa Saúde
```

Sem build: o `index.html` é servido como está. GitHub Pages em `main`, pasta raiz.
