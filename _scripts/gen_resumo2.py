# -*- coding: utf-8 -*-
import os, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = r'C:\Users\Dalla\OneDrive\Desktop\NOSSA SAÚDE\ESTUDO CAMPOS GERAIS'
P01 = os.path.join(BASE, '01 - REDE CREDENCIADA', 'Nossa Saúde')
SITE = 'https://dallalbacorretor-a11y.github.io/rede-nossa-saude/'
REPO = 'https://github.com/dallalbacorretor-a11y/rede-nossa-saude'

D = json.load(open(os.path.join(AQUI, 'dados_unico.json'), encoding='utf-8'))
ITENS, CIDADES, EXAMES = D['itens'], D['cidades'], D['exames']
M = json.load(open(os.path.join(AQUI, 'dados_multi.json'), encoding='utf-8'))
NOME_REDE = {r['id']: r['nome'] for r in M['redes']}

CATS = ['Hospitais e Pronto-Socorro', 'Clínicas e Centros Médicos',
        'Laboratórios e Imagem', 'Profissionais (médicos e demais)']
L, w = [], None
L = []
w = L.append

w('# RESUMO — Rede credenciada Nossa Saúde · Campos Gerais / PR')
w('')
w('**Operadora:** Nossa Saúde (CNPJ 02.862.447/0001-03) · **UF:** PR · **Cidades:** 9')
w('**Consulta:** 10/09/2026 · **Fonte:** rede credenciada oficial em `prestador.nossasaude.com.br`, '
  '**sem filtro de plano**')
w('**Site publicado:** %s · **Repositório:** %s' % (SITE, REPO))
w('')
w('> A rede credenciada é definida e alterada exclusivamente pela operadora. Este material soma')
w('> todos os planos — antes de contratar, confirme no portal da operadora se o prestador atende o')
w('> plano específico do cliente.')
w('')
w('## Como o material está montado')
w('')
w('**Todos os planos entram como uma rede só.** Se um prestador aparece na lista, ele é credenciado')
w('da Nossa Saúde naquela cidade por algum plano da operadora. É a visão que o cliente quer ver')
w('primeiro — "o que a Nossa Saúde tem aqui na minha cidade".')
w('')
w('Entrega principal: **um PDF por cidade**, no padrão visual dos materiais Amil da corretora')
w('(capa navy, "a sua rede em números", hospitais, exames por natureza, clínicas e médicos por')
w('especialidade). Mais o PDF da região inteira, a planilha e o site com download por cidade.')
w('')
w('## A rede em números')
w('')
w('| Cidade | Hospitais | Labs e imagem | Clínicas | Médicos | Total | PDF |')
w('|---|---:|---:|---:|---:|---:|---|')
tot = [0, 0, 0, 0]
for cid in CIDADES:
    lst = [i for i in ITENS if i['cidade'] == cid]
    n = [sum(1 for i in lst if i['internacao']),
         sum(1 for i in lst if i['naturezas'] and not i['internacao']),
         sum(1 for i in lst if i['categoria'] == CATS[1]),
         sum(1 for i in lst if i['categoria'] == CATS[3])]
    tot = [a + b for a, b in zip(tot, n)]
    w('| %s | %s | %s | %s | %s | **%d** | `Rede Nossa Saude - %s.pdf` |'
      % (cid, n[0] or '—', n[1] or '—', n[2] or '—', n[3] or '—', len(lst), cid))
w('| **TOTAL** | **%d** | **%d** | **%d** | **%d** | **%d** | |' % (tot[0], tot[1], tot[2], tot[3], len(ITENS)))
w('')
w('## Exames e diagnóstico')
w('')
w('Prestadores por natureza de exame (o mesmo agrupamento que aparece nos PDFs).')
w('')
w('| Natureza | ' + ' | '.join(CIDADES) + ' | Total |')
w('|---|' + '---:|' * (len(CIDADES) + 1))
for nat in EXAMES:
    lst = [i for i in ITENS if nat in i['naturezas']]
    w('| %s | %s | **%d** |' % (nat,
                                ' | '.join(str(sum(1 for i in lst if i['cidade'] == c)) or '—' for c in CIDADES),
                                len(lst)))
w('')
w('## Hospitais')
w('')
hosp = [i for i in ITENS if i['internacao']]
for cid in CIDADES:
    hs = [i for i in hosp if i['cidade'] == cid]
    if hs:
        for h in sorted(hs, key=lambda x: x['nome_exib'].lower()):
            end = (h['enderecos'][0]['logradouro'] if h['enderecos'] else '—')
            tel = (h['enderecos'][0]['tel'] if h['enderecos'] else '') or 'sem telefone'
            w('- **%s** — %s (%s) · %s · %s' % (cid, h['nome_exib'], h['tipo_exib'], end, tel))
    else:
        w('- **%s** — sem hospital credenciado; internação em Ponta Grossa.' % cid)
w('')
w('## Para o corretor: o que está por trás da lista única')
w('')
w('A operadora tem **328 planos ativos**, agrupados em 18 redes credenciadas. Aos Campos Gerais')
w('chegam **3** — e é isso que a lista única soma:')
w('')
w('| Rede | Prestadores na região | Planos | Cobertura |')
w('|---|---:|---:|---|')
for r in M['redes']:
    n = sum(1 for i in M['itens'] if r['id'] in i['redes'])
    cids = [c for c in CIDADES if any(i['cidade'] == c and r['id'] in i['redes'] for i in M['itens'])]
    w('| %s | %d | %d | %s |' % (r['nome'], n, len(r['planos']),
                                 'as 9 cidades' if len(cids) == 9 else ', '.join(cids)))
w('')
w('Três coisas para não prometer errado:')
w('')
w('- **Rede Azul só atende Ponta Grossa** (e um ponto em Castro). São 66 planos. Cliente das outras')
w('  sete cidades com um plano dessa rede não tem atendimento local.')
w('- **Hospital Moura (Telêmaco Borba)** está na Rede Coral e **não** na Coral CG (linha VIDA NOVA CG).')
w('  Na Coral CG o hospital da cidade é o Instituto Doutor Feitosa (IDF).')
w('- Coral e Coral CG, que atendem as nove cidades, diferem em apenas 21 prestadores.')
w('')
w('O detalhamento rede a rede está em `_scripts/dados_multi.json` e nos PDFs oficiais por rede em')
w('`03 - MATERIAIS ORIGINAIS`.')
w('')
w('## Como atualizar')
w('')
w('Scripts em `04 - SITE/_scripts/` (ver `LEIAME.md`). Resumindo:')
w('')
w('```')
w('python scrape.py "" TODOS      # baixa o PDF oficial de cada cidade, sem filtro de plano')
w('python build_unico.py          # parseia -> dados_unico.json')
w('python gen_cidades.py          # os 9 PDFs de cidade + o PDF da região')
w('python gen_xlsx2.py            # a planilha')
w('python gen_site2.py            # o site')
w('```')
w('')
w('Depois é só `git add -A && git commit && git push` na pasta `04 - SITE` — o GitHub Pages')
w('republica sozinho.')
w('')
w('## Arquivos')
w('')
w('- `01 - REDE CREDENCIADA/Nossa Saúde/REDE NOSSA SAUDE - CAMPOS GERAIS.xlsx` — rede completa,')
w('  resumo e uma aba por cidade.')
w('- `02 - COMPARATIVOS DE REDE/Rede por cidade/` — **os 9 PDFs por cidade** (é o que vai pro cliente).')
w('- `02 - COMPARATIVOS DE REDE/Rede Nossa Saude - Campos Gerais (9 cidades).pdf` — a região inteira.')
w('- `03 - MATERIAIS ORIGINAIS .../Nossa Saúde/` — PDFs oficiais da operadora e o mapa de cobertura.')
w('- `04 - SITE/` — o site publicado no GitHub Pages.')
w('')
w('---')
w('')
w('Mazza Broker · Alan Vinicius Dall Alba · (41) 99547-6715 · alan.vinicius@mazzabroker.com.br')

open(os.path.join(P01, 'RESUMO.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('OK', os.path.join(P01, 'RESUMO.md'))
