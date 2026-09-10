# -*- coding: utf-8 -*-
import os, sys, collections
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import common as C

sys.stdout.reconfigure(encoding='utf-8')
os.makedirs(C.P01, exist_ok=True)

D = C.carregar()
ITENS, REDES = D['itens'], D['redes']

hx = lambda c: 'FF' + c.lstrip('#')
F_TIT = Font(name='Calibri', size=16, bold=True, color=hx(C.NAVY))
F_SUB = Font(name='Calibri', size=10, color=hx(C.CINZA))
F_HDR = Font(name='Calibri', size=10, bold=True, color='FFFFFFFF')
F_TXT = Font(name='Calibri', size=10)
F_B = Font(name='Calibri', size=10, bold=True)
FILL_HDR = PatternFill('solid', fgColor=hx(C.NAVY))
FILL_ALT = PatternFill('solid', fgColor=hx(C.CINZA_CLARO))
FILL_LAR = PatternFill('solid', fgColor=hx(C.LARANJA))
THIN = Side(style='thin', color=hx(C.BORDA))
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTRO = Alignment(horizontal='center', vertical='center')

COLS = ([('Cidade', 16), ('Categoria', 26), ('Tipo (operadora)', 24), ('Prestador', 44)]
        + [('Rede ' + r['curto'], 13) for r in REDES]
        + [('Razão social / Nome', 44), ('CNPJ', 20), ('Conselho', 18), ('Especialidades', 46),
           ('Endereço', 52), ('Bairro', 20), ('CEP', 12), ('Telefones', 32), ('Corpo clínico', 60)])
NR = len(REDES)
IWRAP = {4 + NR + 3, 4 + NR + 4, 4 + NR + 7, 4 + NR + 8}   # especialidades, endereço, tels, corpo


def cab(ws, titulo, sub):
    ws['A1'] = titulo; ws['A1'].font = F_TIT
    ws['A2'] = sub; ws['A2'].font = F_SUB
    ws['A3'] = C.AVISO; ws['A3'].font = F_SUB
    ws.freeze_panes = 'A6'


def tabela(ws, recs, r0=5):
    for j, (h, w) in enumerate(COLS, start=1):
        c = ws.cell(row=r0, column=j, value=h)
        c.font = F_HDR; c.border = BOX
        c.fill = (PatternFill('solid', fgColor=hx(REDES[j - 5]['cor']))
                  if 5 <= j <= 4 + NR else FILL_HDR)
        c.alignment = CENTRO if 5 <= j <= 4 + NR else Alignment(vertical='center')
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.row_dimensions[r0].height = 22
    r = r0 + 1
    for rec in recs:
        vals = ([rec['cidade'], rec['categoria'], rec['tipo'], rec['nome_exib']]
                + ['✔' if x['id'] in rec['redes'] else '—' for x in REDES]
                + [rec['razao'], rec['cnpj'], rec['conselho'], ' • '.join(rec['esp_exib']),
                   ' | '.join(C.enderecos_txt(rec)),
                   ' | '.join(sorted({e['bairro'] for e in rec['enderecos'] if e['bairro']})),
                   ' | '.join(sorted({e['cep'] for e in rec['enderecos'] if e['cep']})),
                   ' | '.join(C.tels(rec)),
                   ' | '.join('%s (%s)' % (m['nome'], m['registro']) for m in rec['corpo_clinico'])])
        for j, v in enumerate(vals, start=1):
            c = ws.cell(row=r, column=j, value=v)
            c.font = F_TXT; c.border = BOX
            c.alignment = Alignment(vertical='top', wrap_text=(j in IWRAP))
            if r % 2 == 0:
                c.fill = FILL_ALT
            if j == 4:
                c.font = F_B
            elif j == 2:
                c.font = Font(name='Calibri', size=10, bold=True, color=hx(C.CAT_COR[rec['categoria']]))
            elif 5 <= j <= 4 + NR:
                c.alignment = CENTRO
                c.font = Font(name='Calibri', size=11, bold=True,
                              color=hx(REDES[j - 5]['cor']) if v == '✔' else hx(C.CINZA))
        r += 1
    ws.auto_filter.ref = 'A%d:%s%d' % (r0, get_column_letter(len(COLS)), r - 1)
    return r


wb = Workbook()

# ---------------- RESUMO ----------------
ws = wb.active; ws.title = 'RESUMO'
ws['A1'] = 'REDE CREDENCIADA — NOSSA SAÚDE'; ws['A1'].font = Font(size=18, bold=True, color=hx(C.NAVY))
ws['A2'] = 'Campos Gerais / PR · todas as redes e produtos · Mazza Broker'
ws['A2'].font = Font(size=11, bold=True, color=hx(C.LARANJA))
ws['A3'] = C.FONTE; ws['A3'].font = F_SUB
ws['A4'] = C.AVISO; ws['A4'].font = F_SUB
for w, col in zip([30, 15, 15, 17, 17, 14, 14, 14, 14], 'ABCDEFGHI'):
    ws.column_dimensions[col].width = w

r = 6
ws.cell(row=r, column=1, value='PRESTADORES POR CIDADE E CATEGORIA').font = Font(size=12, bold=True, color=hx(C.NAVY))
r += 1
hdr = ['Cidade'] + [C.CAT_CURTA[k] for k in C.CATS] + ['Total'] + ['Rede ' + x['curto'] for x in REDES]
for j, h in enumerate(hdr, start=1):
    c = ws.cell(row=r, column=j, value=h); c.font = F_HDR; c.border = BOX
    c.fill = PatternFill('solid', fgColor=hx(REDES[j - 7]['cor'])) if j >= 7 else FILL_HDR
r += 1
tot = [0] * 4
for cid in C.CIDADES:
    recs = [i for i in ITENS if i['cidade'] == cid]
    n = [sum(1 for x in recs if x['categoria'] == k) for k in C.CATS]
    tot = [a + b for a, b in zip(tot, n)]
    vals = [cid] + n + [len(recs)] + [sum(1 for x in recs if rd['id'] in x['redes']) for rd in REDES]
    for j, v in enumerate(vals, start=1):
        c = ws.cell(row=r, column=j, value=v); c.border = BOX
        c.font = F_B if j in (1, 6) else F_TXT
    r += 1
vals = ['TOTAL'] + tot + [len(ITENS)] + [sum(1 for x in ITENS if rd['id'] in x['redes']) for rd in REDES]
for j, v in enumerate(vals, start=1):
    c = ws.cell(row=r, column=j, value=v); c.font = Font(size=10, bold=True, color='FFFFFFFF')
    c.fill = FILL_LAR; c.border = BOX
r += 3

ws.cell(row=r, column=1, value='AS REDES CREDENCIADAS QUE CHEGAM AOS CAMPOS GERAIS').font = Font(size=12, bold=True, color=hx(C.NAVY))
r += 1
ws.cell(row=r, column=1, value='Cada produto da Nossa Saúde usa uma rede. Planos da mesma rede enxergam '
                               'exatamente os mesmos prestadores — muda acomodação, coparticipação e preço.').font = F_SUB
r += 2
for j, h in enumerate(['Rede', 'Prestadores', 'Planos', 'Observação'], start=1):
    c = ws.cell(row=r, column=j, value=h); c.font = F_HDR; c.fill = FILL_HDR; c.border = BOX
r += 1
for rd in REDES:
    n = sum(1 for x in ITENS if rd['id'] in x['redes'])
    for j, v in enumerate([rd['nome'], n, len(rd['planos']), rd['desc']], start=1):
        c = ws.cell(row=r, column=j, value=v); c.border = BOX
        c.font = Font(name='Calibri', size=10, bold=(j == 1), color=hx(rd['cor']) if j == 1 else hx(C.CINZA) if j == 4 else 'FF111827')
    r += 1
r += 2
ws.cell(row=r, column=1, value='Contato: %s · %s · %s' % (C.CORRETOR, C.CORRETOR_TEL, C.CORRETOR_MAIL)).font = F_SUB

# ---------------- REDE COMPLETA ----------------
ws = wb.create_sheet('REDE COMPLETA')
todos = []
for cid in C.CIDADES:
    todos += C.ordena([i for i in ITENS if i['cidade'] == cid])
cab(ws, 'Rede credenciada Nossa Saúde — Campos Gerais (todas as redes)',
    '%d prestadores · %s' % (len(todos), C.FONTE))
tabela(ws, todos)

# ---------------- por cidade ----------------
for cid in C.CIDADES:
    ws = wb.create_sheet(cid[:31])
    recs = C.ordena([i for i in ITENS if i['cidade'] == cid])
    cab(ws, '%s / PR' % cid, '%d prestadores · %s' % (len(recs), C.FONTE))
    tabela(ws, recs)

# ---------------- diferenças ----------------
AMPLAS = C.redes_amplas(D)
IDS_AMPLAS = {r['id'] for r in AMPLAS}
ws = wb.create_sheet('DIFERENCAS %s' % ' x '.join(r['curto'] for r in AMPLAS))[:31] if False else wb.create_sheet(
    ('DIF ' + ' x '.join(r['curto'] for r in AMPLAS))[:31])
dif = [i for i in todos if len(IDS_AMPLAS & set(i['redes'])) not in (0, len(IDS_AMPLAS))]
cab(ws, 'Onde %s se diferenciam' % ' e '.join('Rede ' + r['curto'] for r in AMPLAS),
    'As duas redes que atendem todas as 9 cidades são quase iguais; estes %d prestadores são a diferença. '
    'Confira a rede do plano do cliente antes de prometer. · %s' % (len(dif), C.FONTE))
tabela(ws, dif)

for rd in REDES:
    if rd['id'] in IDS_AMPLAS:
        continue
    cids = C.cidades_da_rede(D, rd['id'])
    ws = wb.create_sheet(('REDE ' + rd['curto'])[:31])
    recs = C.ordena([i for i in ITENS if rd['id'] in i['redes']])
    cab(ws, 'Rede %s — cobertura reduzida' % rd['curto'],
        '%d prestadores, só em %s. Sem atendimento local em: %s. · %s'
        % (len(recs), ', '.join(cids), ', '.join(c for c in C.CIDADES if c not in cids), C.FONTE))
    tabela(ws, recs)

# ---------------- planos ----------------
ws = wb.create_sheet('PLANOS x REDE')
ws['A1'] = 'Planos da Nossa Saúde e a rede credenciada de cada um'
ws['A1'].font = F_TIT
ws['A2'] = ('Apenas os planos cujas redes alcançam os Campos Gerais. Planos da mesma rede têm '
            'exatamente os mesmos prestadores.')
ws['A2'].font = F_SUB
for w, col in zip([16, 52, 24, 18, 22], 'ABCDE'):
    ws.column_dimensions[col].width = w
r = 4
for j, h in enumerate(['Código', 'Plano', 'Contratação', 'Registro ANS', 'Rede credenciada'], start=1):
    c = ws.cell(row=r, column=j, value=h); c.font = F_HDR; c.fill = FILL_HDR; c.border = BOX
r += 1
linhas = []
for rd in REDES:
    for p in rd['planos']:
        txt = p['txt']
        cod = txt.split(' - ')[0].strip()
        tipo = ('Individual / Familiar' if 'Individual' in txt else
                'Coletivo Empresarial' if 'Empresarial' in txt else
                'Coletivo por Adesão' if 'Ades' in txt else '—')
        ans = txt.split('Registro ANS:')[-1].strip() if 'Registro ANS:' in txt else ''
        nome = txt.split(' - Individual')[0].split(' - Coletivo')[0].replace(cod + ' - ', '').strip(' -') or cod
        linhas.append((cod, nome, tipo, ans, rd))
for cod, nome, tipo, ans, rd in sorted(linhas, key=lambda x: (x[1].lower(), x[0])):
    for j, v in enumerate([cod, nome, tipo, ans, rd['nome']], start=1):
        c = ws.cell(row=r, column=j, value=v); c.border = BOX
        c.font = Font(name='Calibri', size=10, bold=(j in (1, 5)),
                      color=hx(rd['cor']) if j == 5 else 'FF111827')
    r += 1
ws.auto_filter.ref = 'A4:E%d' % (r - 1)
ws.freeze_panes = 'A5'

out = os.path.join(C.P01, 'REDE NOSSA SAUDE - CAMPOS GERAIS (todas as redes).xlsx')
wb.save(out)
print('OK', out, len(todos), 'prestadores /', len(dif), 'com diferença entre redes /', len(linhas), 'planos')

destino_site = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'site', 'arquivos', 'rede-nossa-saude-campos-gerais.xlsx')
if os.path.isdir(os.path.dirname(destino_site)):
    wb.save(destino_site)
    print('   copiado para o site')
