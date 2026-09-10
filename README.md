# Rede credenciada Nossa Saúde — Campos Gerais

Site estático com a rede credenciada da **Nossa Saúde** nas 9 cidades dos Campos Gerais / PR:
Ponta Grossa, Telêmaco Borba, Jaguariaíva, Castro, Irati, Palmeira, Carambeí, Prudentópolis e
Piraí do Sul.

Publicado por **Mazza Broker** — Alan Vinicius Dall Alba · (41) 99547-6715 · alan.vinicius@mazzabroker.com.br

## O que tem

- Busca por hospital, clínica, laboratório, médico, especialidade ou bairro
- Filtro pela **rede credenciada do plano do cliente** (3 redes chegam à região)
- Comparativo entre as redes: cobertura por cidade, hospitais e onde elas se diferenciam
- Tabela "Qual é o meu plano?" com os 147 planos da operadora e a rede de cada um
- XLSX e PDFs para download

## Números

| | |
|---|---|
| Prestadores | 328 |
| Cidades | 9 |
| Redes credenciadas na região | 3 |
| Planos mapeados | 147 |
| Consulta | 10/09/2026 |

## Fonte e validade

Fonte: Rede Credenciada oficial da Nossa Saúde (prestador.nossasaude.com.br), consulta em 10/09/2026.

> A rede credenciada é definida e alterada exclusivamente pela operadora. Confirme no portal da Nossa Saúde antes de contratar ou de utilizar o serviço.

## Como publicar / atualizar

O site é estático: `index.html`, `estilo.css`, `app.js` e `dados.js` (os dados ficam em
`window.DADOS` dentro do `dados.js`). Não precisa de build.

Para atualizar a rede, rodar os scripts em `_scripts/` (ver `_scripts/LEIAME.md`) e regerar
`dados.js` com `python gen_site.py`.

GitHub Pages: Settings → Pages → Source: `Deploy from a branch` → branch `main`, pasta `/ (root)`.
