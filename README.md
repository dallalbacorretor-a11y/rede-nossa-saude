# Rede credenciada Nossa Saúde — Vida Leve e Vida Nova CG

Página da rede credenciada dos planos que a corretora comercializa na Nossa Saúde. **Um plano por
região**, porque cada um usa uma rede diferente e nenhum alcança a praça do outro:

| Região | Plano | Rede | Prestadores | Cidades | Hospitais |
|---|---|---|---|---|---|
| Curitiba, RMC e Litoral | **Vida Leve** | Rede Laranja | 361 | 18 | 22 |
| Campos Gerais | **Vida Nova CG** | Rede Coral CG | 308 | 9 | 7 |

O botão no topo da página alterna entre as duas.

**No ar em:** https://dallalbacorretor-a11y.github.io/rede-nossa-saude/

Publicado por **Mazza Broker** — Alan Vinicius Dall Alba · (41) 99547-6715 ·
alan.vinicius@mazzabroker.com.br

## As cidades

**Vida Leve** (coleta de 23/09/2026) — Curitiba, São José dos Pinhais, Paranaguá, Araucária,
Fazenda Rio Grande, Campo Largo, Pinhais, Colombo, Tijucas do Sul, Campina Grande do Sul,
Piraquara, Agudos do Sul, Balsa Nova, Antonina, Morretes, Guaratuba, Matinhos e Pontal do Paraná.

**Vida Nova CG** (coleta de 01/10/2026) — Ponta Grossa, Telêmaco Borba, Jaguariaíva, Castro,
Irati, Palmeira, Carambeí, Prudentópolis e Piraí do Sul.

Todos os planos com o mesmo nome compartilham a rede: no Vida Leve, individual, empresarial, por
adesão e o Vida Leve Litoral; no Vida Nova CG, os doze planos da linha.

## Mesmo padrão da Amil e da Paraná Clínicas

A página é o **mesmo aplicativo** dos outros dois estudos da corretora, recolorido para a marca da
operadora:

- abas **Visão geral · Rede completa**
- mapa de bolhas por cidade, filtros por cidade, categoria, especialidade e bairro
- **PDF gerado na hora pela própria página**, já assinado por quem está usando, um por região ou
  por cidade: `Nossa Saúde Vida Leve - Curitiba.pdf`
- **Meus dados**: cada corretor assina o próprio material; a corretora Mazza Broker é fixa
- **Direcionamento interno**: quem a operadora só libera por encaminhamento aparece com o selo
  ENCAMINHAMENTO e um **D** no lugar do visto — no Vida Leve são 18, entre eles Pilar, Cruz
  Vermelha, INC, Pequeno Príncipe, Menino Deus, Erasto Gaertner e Erastinho; no Vida Nova CG,
  nenhum

Os hospitais incluem os que a própria operadora classifica como *Hospital Especializado*
(clínicas de olhos, por exemplo), porque é assim que eles saem na rede oficial.

> A rede é definida e alterada exclusivamente pela operadora. Esta lista é o retrato da data
> indicada no topo — antes de contratar, confirme no portal da operadora.

## Estrutura

```
index.html              a página inteira (CSS, app e dados num arquivo só)
_scripts/               coleta e preparo dos dados (ver _scripts/LEIAME.md)
_scripts/padrao/        o template da casa e a adaptação para a Nossa Saúde
```

Sem build: o `index.html` é servido como está. GitHub Pages em `main`, pasta raiz.
