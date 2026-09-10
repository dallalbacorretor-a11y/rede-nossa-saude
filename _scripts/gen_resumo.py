# -*- coding: utf-8 -*-
import os, sys, collections
import common as C

sys.stdout.reconfigure(encoding='utf-8')
D = C.carregar()
ITENS, REDES = D['itens'], D['redes']
AMPLAS = C.redes_amplas(D)
IDS_AMPLAS = {r['id'] for r in AMPLAS}
SITE_URL = 'https://dallalbacorretor-a11y.github.io/rede-nossa-saude/'
REPO_URL = 'https://github.com/dallalbacorretor-a11y/rede-nossa-saude'

L = []
w = L.append
nred = lambda rid, lst=None: sum(1 for i in (lst if lst is not None else ITENS) if rid in i['redes'])

w('# RESUMO — Rede credenciada Nossa Saúde · Campos Gerais / PR')
w('')
w('**Operadora:** %s (CNPJ %s) · **UF:** PR · **Cidades:** %d' % (C.OPERADORA, C.OPER_CNPJ, len(C.CIDADES)))
w('**Consulta:** %s · **Fonte:** buscador oficial `prestador.nossasaude.com.br/rede/rede.php`' % C.DATA_REF)
w('**Site publicado:** %s (repositório: %s)' % (SITE_URL, REPO_URL))
w('')
w('> %s' % C.AVISO)
w('')
w('## O que foi levantado')
w('')
w('Todos os **328 planos ativos** da Nossa Saúde foram mapeados para a rede credenciada que cada um')
w('usa. A operadora tem 26 redes cadastradas; **18** são usadas por algum plano e, dessas, apenas')
w('**%d chegam aos Campos Gerais**. Todo o material é organizado por rede, não por plano — planos da' % len(REDES))
w('mesma rede enxergam exatamente os mesmos prestadores (verificado prestador a prestador).')
w('')
w('| Rede | Prestadores | Planos | Cidades atendidas |')
w('|---|---:|---:|---|')
for r in REDES:
    w('| **%s** | %d | %d | %s |' % (r['nome'], nred(r['id']), len(r['planos']),
                                     ', '.join(C.cidades_da_rede(D, r['id']))))
w('')
for r in REDES:
    w('- **%s** — %s' % (r['nome'], r['desc']))
w('')
w('## A rede em números')
w('')
w('| Cidade | Hospitais | Clínicas | Labs e Imagem | Profissionais | Total | ' +
  ' | '.join(r['curto'] for r in REDES) + ' |')
w('|---|---:|---:|---:|---:|---:|' + '---:|' * len(REDES))
tot = [0] * 4
for cid in C.CIDADES:
    recs = [i for i in ITENS if i['cidade'] == cid]
    n = [sum(1 for x in recs if x['categoria'] == k) for k in C.CATS]
    tot = [a + b for a, b in zip(tot, n)]
    w('| %s | %d | %d | %d | %d | **%d** | %s |'
      % (cid, n[0], n[1], n[2], n[3], len(recs),
         ' | '.join(str(nred(r['id'], recs)) or '—' for r in REDES)))
w('| **TOTAL** | **%d** | **%d** | **%d** | **%d** | **%d** | %s |'
  % (tot[0], tot[1], tot[2], tot[3], len(ITENS),
     ' | '.join('**%d**' % nred(r['id']) for r in REDES)))
w('')
w('## Hospitais e pronto-socorro')
w('')
w('| Cidade | Hospital | ' + ' | '.join(r['curto'] for r in REDES) + ' |')
w('|---|---|' + '---|' * len(REDES))
hosp = sorted([i for i in ITENS if i['categoria'] == C.CATS[0]],
              key=lambda x: (C.CIDADES.index(x['cidade']), x['nome_exib'].lower()))
for i in hosp:
    w('| %s | %s (%s) | %s |' % (i['cidade'], i['nome_exib'], i['tipo'],
                                 ' | '.join('✔' if r['id'] in i['redes'] else '—' for r in REDES)))
for cid in C.CIDADES:
    if not any(i['cidade'] == cid for i in hosp):
        w('| %s | *sem hospital credenciado — referência em Ponta Grossa* | %s |'
          % (cid, ' | '.join('—' for r in REDES)))
w('')
dif = [i for i in ITENS if 0 < len(IDS_AMPLAS & set(i['redes'])) < len(IDS_AMPLAS)]
w('## %s: as diferenças' % ' x '.join(r['nome'] for r in AMPLAS))
w('')
w('As redes que atendem todas as nove cidades são quase iguais — estes **%d prestadores** são toda a' % len(dif))
w('diferença entre elas.')
w('')
w('| Cidade | Prestador | Categoria | ' + ' | '.join(r['curto'] for r in AMPLAS) + ' |')
w('|---|---|---|' + '---|' * len(AMPLAS))
for i in sorted(dif, key=lambda x: (C.CIDADES.index(x['cidade']), x['nome_exib'].lower())):
    w('| %s | %s | %s | %s |' % (i['cidade'], i['nome_exib'], C.CAT_CURTA[i['categoria']],
                                 ' | '.join('✔' if r['id'] in i['redes'] else '—' for r in AMPLAS)))
w('')
w('## Pontos de atenção para a venda')
w('')
pg = [i for i in ITENS if i['cidade'] == 'Ponta Grossa']
w('- **Ponta Grossa concentra a rede**: %d dos %d prestadores (%.0f%%). Cliente das cidades menores'
  % (len(pg), len(ITENS), 100.0 * len(pg) / len(ITENS)))
w('  resolve consulta e exame simples na cidade, mas depende de Ponta Grossa para hospital e')
w('  especialidade.')
sem_hosp = [c for c in C.CIDADES if not any(i['cidade'] == c for i in hosp)]
w('- **Sem hospital credenciado na cidade:** %s.' % ', '.join(sem_hosp))
for r in REDES:
    if r['id'] in IDS_AMPLAS:
        continue
    cids = C.cidades_da_rede(D, r['id'])
    sem = [c for c in C.CIDADES if c not in cids]
    w('- **%s tem cobertura reduzida:** só atende em %s. Cliente de %s com um plano dessa rede'
      % (r['nome'], ', '.join(cids), ', '.join(sem)))
    w('  não tem atendimento local — são %d planos nessa situação.' % len(r['planos']))
w('- **Hospital Moura (Telêmaco Borba)** está na Rede Coral mas **não** na Rede Coral CG. Quem vende')
w('  VIDA NOVA CG na cidade tem o Instituto Doutor Feitosa (IDF) como hospital, não o Moura.')
w('')
w('## Como a rede foi levantada')
w('')
w('1. Entrada pelo site da operadora: **Rede Credenciada → "Listar todas as redes"** (a URL direta')
w('   de `comum/redeCredenciada.php` redireciona para a home sem a sessão criada nesse passo).')
w('2. `POST comum/buscaRede.php` com cada `plano` devolve a rede credenciada daquele plano —')
w('   é o que dá o mapa **plano → rede** dos 328 planos.')
w('3. `POST comum/imprimirRedeCredenciada.php` devolve o **PDF oficial completo** da consulta,')
w('   sem paginação. Um PDF por (rede × UF) para achar quais redes chegam à região, depois um PDF')
w('   por (rede × cidade) para as 9 cidades.')
w('4. Os PDFs foram parseados com `pdfplumber` e viraram xlsx, PDFs de apresentação e o site.')
w('')
w('Detalhes técnicos e o passo a passo para atualizar: `04 - SITE/_scripts/LEIAME.md`.')
w('')
w('## Arquivos gerados')
w('')
w('- `01 - REDE CREDENCIADA/Nossa Saúde/REDE NOSSA SAUDE - CAMPOS GERAIS (todas as redes).xlsx`')
w('  — resumo, rede completa com colunas por rede, uma aba por cidade, diferenças entre redes,')
w('  aba da rede de cobertura reduzida e a tabela **planos × rede**.')
w('- `02 - COMPARATIVOS DE REDE/NOSSA SAUDE - CAMPOS GERAIS - CLIENTES (Principais).pdf`')
w('  — hospitais, clínicas e laboratórios, sem médicos pessoa física. É o que vai para o cliente.')
w('- `02 - COMPARATIVOS DE REDE/NOSSA SAUDE - CAMPOS GERAIS - Guia COMPLETO (todas as redes).pdf`')
w('  — tudo, com os profissionais agrupados por especialidade dentro de cada cidade.')
w('- `04 - SITE/` — o site estático publicado no GitHub Pages (%s).' % SITE_URL)
w('- `03 - MATERIAIS ORIGINAIS .../Nossa Saúde/` — os PDFs oficiais da operadora e o mapa de cobertura.')
w('')
w('---')
w('')
w('Mazza Broker · %s · %s · %s' % (C.CORRETOR, C.CORRETOR_TEL, C.CORRETOR_MAIL))

destino = os.path.join(C.P01, 'RESUMO.md')
open(destino, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('OK', destino)
