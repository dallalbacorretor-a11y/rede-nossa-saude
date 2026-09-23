# Rede credenciada Nossa Saúde — Vida Leve

Página da rede credenciada do plano **Vida Leve** da Nossa Saúde, que é o que a corretora
comercializa. Todos os Vida Leve — individual, empresarial e por adesão, e também o Vida Leve
Litoral — usam **uma rede só, a Rede Laranja**.

**No ar em:** https://dallalbacorretor-a11y.github.io/rede-nossa-saude/

Publicado por **Mazza Broker** — Alan Vinicius Dall Alba · (41) 99547-6715 ·
alan.vinicius@mazzabroker.com.br

## Onde o Vida Leve tem rede

Curitiba, região metropolitana e litoral — 18 cidades:

Curitiba, São José dos Pinhais, Paranaguá, Araucária, Fazenda Rio Grande, Campo Largo, Pinhais,
Colombo, Tijucas do Sul, Campina Grande do Sul, Piraquara, Agudos do Sul, Balsa Nova, Antonina,
Morretes, Guaratuba, Matinhos e Pontal do Paraná.

**Nos Campos Gerais o Vida Leve não tem rede credenciada.** Lá a operadora atende pelas redes
Azul e Coral, de outros planos. O estudo dos Campos Gerais, com todos os planos somados, está no
histórico do repositório (até o commit `78e5ae1`).

## Números

| | |
|---|---|
| Prestadores | 361 |
| Cidades | 18 |
| Hospitais | 22 |
| Por encaminhamento | 18 |
| Consulta | 23/09/2026 |

Os hospitais incluem os que a própria operadora classifica como *Hospital Especializado*
(clínicas de olhos, por exemplo), porque é assim que eles saem na rede oficial.

## Mesmo padrão da Amil e da Paraná Clínicas

A página é o **mesmo aplicativo** dos outros dois estudos da corretora, recolorido para a marca da
operadora:

- abas **Visão geral · Rede completa**
- mapa de bolhas por cidade, filtros por cidade, categoria, especialidade e bairro
- **PDF gerado na hora pela própria página**, já assinado por quem está usando
- **Meus dados**: cada corretor assina o próprio material; a corretora Mazza Broker é fixa
- **Direcionamento interno**: quem a operadora só libera por encaminhamento aparece com o selo
  ENCAMINHAMENTO e um **D** no lugar do visto — Pilar, Cruz Vermelha, INC, Pequeno Príncipe,
  Menino Deus, Erasto Gaertner e Erastinho, entre outros

> A rede é definida e alterada exclusivamente pela operadora. Esta lista é o retrato da data
> acima — antes de contratar, confirme no portal da operadora.

## Estrutura

```
index.html              a página inteira (CSS, app e dados num arquivo só)
_scripts/               coleta e preparo dos dados (ver _scripts/LEIAME.md)
_scripts/padrao/        o template da casa e a adaptação para a Nossa Saúde
```

Sem build: o `index.html` é servido como está. GitHub Pages em `main`, pasta raiz.
