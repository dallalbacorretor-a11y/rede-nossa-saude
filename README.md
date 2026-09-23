# Rede credenciada Nossa Saúde — Paraná

Página da rede credenciada da **Nossa Saúde** em duas regiões, com um botão para alternar entre
elas:

- **Campos Gerais** — Ponta Grossa, Telêmaco Borba, Jaguariaíva, Castro, Irati, Palmeira, Carambeí,
  Prudentópolis e Piraí do Sul.
- **Curitiba, RMC e Paranaguá** — Curitiba, São José dos Pinhais, Paranaguá, Araucária, Fazenda Rio
  Grande, Campo Largo, Pinhais, Colombo, Tijucas do Sul, Campina Grande do Sul, Lapa, Rio Negro,
  Piraquara, Agudos do Sul, Balsa Nova e Doutor Ulysses.

**No ar em:** https://dallalbacorretor-a11y.github.io/rede-nossa-saude/

Publicado por **Mazza Broker** — Alan Vinicius Dall Alba · (41) 99547-6715 ·
alan.vinicius@mazzabroker.com.br

## Mesmo padrão da Amil e da Paraná Clínicas

A página é o **mesmo aplicativo** dos outros dois estudos da corretora, recolorido para a marca da
operadora. Vem tudo junto de lá:

- abas **Visão geral · Rede completa** (a de "Entre planos" some aqui: o material soma todos os
  planos numa rede só, então ela compararia o plano com ele mesmo)
- o seletor de região no topo — o mesmo mecanismo que na Amil alterna PR / SC / SP
- mapa de bolhas por cidade, filtros por cidade, categoria, especialidade e bairro
- **PDF gerado na hora pela própria página**, já assinado por quem está usando
- **Meus dados**: cada corretor assina o próprio material; a corretora Mazza Broker é fixa
- **Direcionamento interno**: quem a operadora só libera por encaminhamento aparece com o selo
  ENCAMINHAMENTO e um **D** no lugar do visto — em Curitiba são Pilar, Cruz Vermelha, INC,
  Pequeno Príncipe, Menino Deus, Erasto Gaertner e Erastinho, entre outros

## Números

| | Campos Gerais | Curitiba, RMC e Paranaguá |
|---|---|---|
| Prestadores | 328 | 372 |
| Cidades | 9 | 16 |
| Hospitais | 9 | 23 |
| Consulta | 10/09/2026 | 23/09/2026 |

Os hospitais da região de Curitiba incluem os que a própria operadora classifica como *Hospital
Especializado* (clínicas de olhos, por exemplo), porque é assim que eles saem na rede oficial.
Dos 23, **7 são de acesso por encaminhamento** e estão marcados como tal.

> A rede é definida e alterada exclusivamente pela operadora. Esta lista soma todos os planos da
> Nossa Saúde — antes de contratar, confirme no portal da operadora se o prestador atende o plano
> específico.

Rede credenciada oficial da operadora, em prestador.nossasaude.com.br, consultada sem filtro de
plano nas datas acima.

## Estrutura

```
index.html              a página inteira (CSS, app e dados num arquivo só)
_scripts/               coleta e preparo dos dados (ver _scripts/LEIAME.md)
_scripts/padrao/        o template da casa e a adaptação para a Nossa Saúde
```

Sem build: o `index.html` é servido como está. GitHub Pages em `main`, pasta raiz.
