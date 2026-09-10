# -*- coding: utf-8 -*-
import os, sys, collections
import common as C

sys.stdout.reconfigure(encoding='utf-8')
d = C.carregar()
VN, FORA = d['vncg'], d['fora']
L = []
w = L.append

tot = sum(len(VN[c]) for c in C.CIDADES)
n_cat = {k: sum(1 for c in C.CIDADES for r in VN[c] if r['categoria'] == k) for k in C.CATS}

w('# RESUMO — Rede credenciada Nossa Saúde · %s' % C.PRODUTO_LONGO)
w('')
w('**Operadora:** %s (CNPJ %s) · **Produto:** %s · **UF:** PR' % (C.OPERADORA, C.OPER_CNPJ, C.PRODUTO))
w('**Consulta:** %s · **Fonte:** buscador oficial `prestador.nossasaude.com.br/rede/rede.php`' % C.DATA_REF)
w('')
w('> %s' % C.AVISO)
w('')
w('## Como a rede foi levantada')
w('')
w('1. Entrada pelo site da operadora: **Rede Credenciada → "Listar todas as redes"**, que abre')
w('   `comum/redeCredenciada.php` (a URL direta redireciona para a home sem a sessão criada nesse passo).')
w('2. Filtro **Estado = PR** + **Cidade** (uma por vez, as 9 cidades do mapa de cobertura) +')
w('   **Plano = VIDA NOVA CG**.')
w('3. Botão *Imprimir* (`comum/imprimirRedeCredenciada.php`) devolve o PDF oficial completo, sem')
w('   paginação — é o arquivo guardado em `03 - MATERIAIS ORIGINAIS`. A listagem em tela pagina de 5')
w('   em 5 e é bem mais lenta de varrer.')
w('4. Os PDFs foram parseados (`pdfplumber`) para xlsx / PDFs de apresentação / HTML.')
w('')
w('## Achado importante: os 12 planos VIDA NOVA CG têm a MESMA rede')
w('')
w('Foram baixadas e comparadas as redes dos 12 códigos da linha, prestador a prestador, em Ponta')
w('Grossa (a cidade com mais rede): **diferença zero**. Individual/familiar, empresarial e adesão,')
w('QC ou QP, coparticipação 30% ou 50% — todos enxergam exatamente os mesmos credenciados.')
w('Por isso o material tem **uma coluna só de rede**, e não uma coluna por plano.')
w('')
w('| Código | Plano | Contratação | Registro ANS |')
w('|---|---|---|---|')
for cod, nome, tipo, ans in C.PLANOS:
    w('| %s | %s | %s | %s |' % (cod, nome, tipo, ans))
w('')
w('Legenda: **QC** = quarto coletivo (enfermaria) · **QP** = quarto privativo (apartamento) ·')
w('**CCP30 / CCP50** = coparticipação de 30% ou 50% · **L200** = Líder 200.')
w('')
w('## A rede em números')
w('')
w('| Cidade | Hospitais | Clínicas | Labs e Imagem | Profissionais | Total |')
w('|---|---:|---:|---:|---:|---:|')
for cid in C.CIDADES:
    n = [sum(1 for r in VN[cid] if r['categoria'] == k) for k in C.CATS]
    w('| %s | %d | %d | %d | %d | **%d** |' % (cid, n[0], n[1], n[2], n[3], len(VN[cid])))
w('| **TOTAL** | **%d** | **%d** | **%d** | **%d** | **%d** |'
  % (n_cat[C.CATS[0]], n_cat[C.CATS[1]], n_cat[C.CATS[2]], n_cat[C.CATS[3]], tot))
w('')
w('## Hospitais e pronto-socorro por cidade')
w('')
for cid in C.CIDADES:
    hs = [r for r in VN[cid] if r['categoria'] == C.CATS[0]]
    if hs:
        for r in sorted(hs, key=lambda x: x['nome_exib'].lower()):
            end = (C.enderecos_txt(r) or ['—'])[0]
            w('- **%s** — %s (%s) · %s · %s' % (cid, r['nome_exib'], r['tipo'], end,
                                                ' · '.join(C.tels(r)) or 'sem telefone'))
    else:
        w('- **%s** — sem hospital credenciado na cidade; referência hospitalar em Ponta Grossa.' % cid)
w('')
w('## Pontos de atenção para a venda')
w('')
w('- **Ponta Grossa concentra a rede**: %d dos %d prestadores (%.0f%%). Cliente de Carambeí, Piraí do'
  % (len(VN['Ponta Grossa']), tot, 100.0 * len(VN['Ponta Grossa']) / tot))
w('  Sul, Castro e Palmeira resolve consulta e exame simples na cidade, mas depende de Ponta Grossa')
w('  para hospital e especialidade.')
w('- **Sem hospital credenciado na cidade:** Castro, Carambeí, Jaguariaíva e Piraí do Sul.')
w('- **Telêmaco Borba:** o **Hospital Moura** aparece na rede geral da Nossa Saúde mas **não** no')
w('  VIDA NOVA CG. O hospital do produto na cidade é o **Instituto Doutor Feitosa (IDF)**.')
w('  Vale conferir antes de prometer.')
w('- Labs e imagem estão bem distribuídos: só Carambeí e Piraí do Sul têm apenas 1 ponto cada.')
w('')
w('## Credenciados fora do VIDA NOVA CG')
w('')
w('Constam na rede geral da operadora nestas cidades, mas não aparecem no filtro do produto —')
w('não prometer ao cliente deste plano.')
w('')
for cid in C.CIDADES:
    if FORA[cid]:
        w('- **%s** — %s' % (cid, ', '.join('%s (%s)' % (r['nome_exib'], r['tipo'])
                                            for r in sorted(FORA[cid], key=lambda x: x['nome_exib'].lower()))))
w('')
w('## Arquivos gerados')
w('')
w('- `01 - REDE CREDENCIADA/Nossa Saúde/REDE NOSSA SAUDE - VIDA NOVA CG - CAMPOS GERAIS.xlsx`')
w('  — resumo, rede completa, uma aba por cidade e a aba dos que ficam fora do produto.')
w('- `02 - COMPARATIVOS DE REDE/NOSSA SAUDE - VIDA NOVA CG - CLIENTES (Principais).pdf`')
w('  — hospitais, clínicas e laboratórios, sem médicos pessoa física. É o que vai para o cliente.')
w('- `02 - COMPARATIVOS DE REDE/NOSSA SAUDE - VIDA NOVA CG - Apresentacao COMPLETA.pdf`')
w('  — tudo, com os profissionais agrupados por especialidade dentro de cada cidade.')
w('- `02 - COMPARATIVOS DE REDE/REDE NOSSA SAUDE - VIDA NOVA CG (interativo).html`')
w('  — página com busca por prestador, cidade, especialidade e categoria.')
w('- `03 - MATERIAIS ORIGINAIS .../Nossa Saúde/` — os PDFs oficiais da operadora (VIDA NOVA CG e')
w('  TODOS OS PLANOS, por cidade) e o mapa de cobertura.')
w('')
w('---')
w('')
w('Mazza Broker · %s · %s · %s' % (C.CORRETOR, C.CORRETOR_TEL, C.CORRETOR_MAIL))

destino = os.path.join(C.P01, 'RESUMO.md')
open(destino, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('OK', destino)
