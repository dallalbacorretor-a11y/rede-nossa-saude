# -*- coding: utf-8 -*-
import re, io, os, json, unicodedata
import pdfplumber

SKIP = ('NOSSA SAUDE OPERADORA DE PLANOS','Rede Credenciada','Filtros:','Tipo: ','Estado: ',
        'Cidade: ','Bairro: ','Graduação: ','Especialidade: ','Tipo de rede: ','Área de atuação: ',
        'Plano: ')
PAGE = re.compile(r'^Page \d+/\d+$')
PAGEX = re.compile(r'\s*Page \d+/\d+\s*$')
CORPO = re.compile(r'^-\s*(?P<nome>.+?)\s*\(\s*(?P<reg>(?:C[A-Z]{2,8})[^)]*)\)\s*(?:-\s*(?P<rqe>.+))?$')
HDR  = re.compile(r'^(?P<nome>.+?)\s*\(\s*(?P<reg>(?:CNPJ|C[A-Z]{2,8})[^)]*)\)\s*-\s*(?P<tipo>[^()]{3,60})$')
CEPL = re.compile(r'^(?P<bairro>.*?)\s*-\s*(?P<cidade>[^-]+?)\s*-\s*(?P<uf>[A-Z]{2})\s*-\s*CEP:\s*(?P<cep>[\d\-]+)\s*$')

def pdf_lines(path):
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            for ln in (p.extract_text() or '').split('\n'):
                ln = PAGEX.sub('', ln.strip()).strip()
                if not ln or PAGE.match(ln) or ln.startswith(SKIP):
                    continue
                yield ln

def parse(path):
    recs, cur = [], None
    lines = list(pdf_lines(path))
    i = 0
    while i < len(lines):
        ln = lines[i]
        mc0 = CORPO.match(ln)
        if mc0 and cur is not None:
            cur['corpo_clinico'].append({'nome': mc0.group('nome').strip(),
                                         'registro': mc0.group('reg').strip(),
                                         'rqe': (mc0.group('rqe') or '').strip()})
            i += 1
            continue
        m = HDR.match(ln)
        if m:
            cur = {'nome': m.group('nome').strip(), 'registro': m.group('reg').strip(),
                   'tipo': m.group('tipo').strip(), 'fantasia': '', 'especialidades': [],
                   'enderecos': [], 'corpo_clinico': []}
            recs.append(cur)
            i += 1
            # optional fantasia line (only for CNPJ providers)
            if cur['registro'].startswith('CNPJ') and i < len(lines) and not lines[i].startswith('Tel:') \
               and not HDR.match(lines[i]):
                cur['fantasia'] = lines[i].strip(); i += 1
            continue
        if cur is None:
            i += 1; continue
        if ln.startswith('Tel:'):
            tel = ln[4:].strip()
            end = {'tel': tel, 'logradouro': '', 'bairro': '', 'cidade': '', 'uf': '', 'cep': ''}
            j = i + 1
            partes = []
            while j < len(lines) and not lines[j].startswith('Tel:') and not HDR.match(lines[j])                   and not CORPO.match(lines[j]):
                mc = CEPL.match(lines[j])
                if mc:
                    end.update(bairro=mc.group('bairro').strip(), cidade=mc.group('cidade').strip(),
                               uf=mc.group('uf'), cep=mc.group('cep'))
                    j += 1
                    break
                partes.append(lines[j]); j += 1
            end['logradouro'] = ' '.join(partes).strip()
            cur['enderecos'].append(end)
            i = j
            continue
        # specialty line
        cur['especialidades'].append(ln)
        i += 1
    return recs

HOSP = {'Hospital geral','Hospital e Maternidade','Hospital dia','Hospital Especializado',
        'Hospital Ortopedico','Hospital Psiquiatrico','Pronto atendimento','Pronto Atendimento'}
LAB  = {'Laboratório','Clínica de imagens','Serviço de diagnose e terapia','Clínica / Laboratório'}
CLIN = {'Clínica','Clínica especializada','Empresa médica','Clínica odontológica','Cooperativa de anestesistas'}

def categoria(tipo):
    if tipo in HOSP: return 'Hospitais e Pronto-Socorro'
    if tipo in LAB:  return 'Laboratórios e Imagem'
    if tipo in CLIN: return 'Clínicas e Centros Médicos'
    return 'Profissionais (médicos e demais)'

def norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'[^A-Za-z0-9 ]', ' ', s).upper()
    return re.sub(r'\s+', ' ', s).strip()

if __name__ == '__main__':
    import sys
    tot = 0
    for f in sorted(os.listdir('pdfs')):
        if not f.startswith('TODOS'): continue
        r = parse('pdfs/' + f)
        tot += len(r)
        tipos = {}
        for x in r: tipos[x['tipo']] = tipos.get(x['tipo'], 0) + 1
        bad = [x for x in r if not x['enderecos']]
        print(f, len(r), 'sem-end:', len(bad))
        print('   ', tipos)
    print('TOTAL', tot)
