# -*- coding: utf-8 -*-
"""Converte a coleta da Nossa Saúde para o formato que o app padrão da casa espera.

O app (mesmo da Amil e da Paraná Clínicas) lê `window.DADOS_UF = {"PR": {...}}`.
Aqui os planos entram como um produto só — é assim que o material foi definido.
"""
import io, json, os, re, sys, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIGEM = os.path.join(os.path.dirname(AQUI), 'dados_unico.json')
SAIDA = os.path.join(AQUI, 'dados', 'dados_ns.json')
sys.stdout.reconfigure(encoding='utf-8')

GERADO_EM = '10/09/2026'
REGIAO = 'Campos Gerais'

COORD = {
    'Ponta Grossa': (-25.095, -50.162), 'Telêmaco Borba': (-24.324, -50.617),
    'Jaguariaíva': (-24.251, -49.706), 'Castro': (-24.791, -50.012),
    'Irati': (-25.468, -50.651), 'Palmeira': (-25.429, -50.007),
    'Carambeí': (-24.915, -50.098), 'Prudentópolis': (-25.213, -50.978),
    'Piraí do Sul': (-24.526, -49.945),
}

# Ordem de exibição e de precedência. A categoria de hospital precisa começar
# com "Hospitais": o app usa /^Hospitais/ para saber onde não se marca exame
# eletivo.
CATEGORIAS = ['Hospitais', 'Diagnóstico por imagem', 'Laboratórios e análises clínicas',
              'Exames e procedimentos', 'Clínicas e consultórios',
              'Médicos e demais profissionais']
CATS_EXAME = ['Diagnóstico por imagem', 'Laboratórios e análises clínicas',
              'Exames e procedimentos']

# natureza do exame (vinda do build_unico) -> categoria do app
DE_NATUREZA = {
    'Diagnóstico por imagem': 'Diagnóstico por imagem',
    'Análises clínicas e patologia': 'Laboratórios e análises clínicas',
    'Endoscopia e procedimentos': 'Exames e procedimentos',
    'Exames funcionais': 'Exames e procedimentos',
}
CAT_PROF = 'Profissionais (médicos e demais)'
CAT_CLIN = 'Clínicas e Centros Médicos'

PRODUTOS = [{
    'codigo': 'ns', 'rotulo': 'Nossa Saúde', 'acomodacao': 'todos os planos',
    'linha': 'Nossa Saúde', 'cor': '#E6411C', 'ans': '',
    'nome': 'Nossa Saúde — todos os planos',
}]


def maiusc(s):
    return (s or '').upper()


def so_digitos(t):
    return re.sub(r'\D', '', t or '')


def fone(t):
    d = so_digitos(t)
    if len(d) == 11:
        return '%s-%s-%s' % (d[:2], d[2:7], d[7:])
    if len(d) == 10:
        return '%s-%s-%s' % (d[:2], d[2:6], d[6:])
    return (t or '').strip()


def categorias_do(item):
    """Todas as categorias em que o prestador aparece, na ordem de precedência."""
    fora = []
    if item['internacao']:
        fora.append('Hospitais')
    for nat in item['naturezas']:
        c = DE_NATUREZA.get(nat)
        if c and c not in fora:
            fora.append(c)
    if not fora or item['categoria'] == CAT_CLIN:
        alvo = ('Médicos e demais profissionais' if item['categoria'] == CAT_PROF
                else 'Clínicas e consultórios')
        if alvo not in fora:
            fora.append(alvo)
    return sorted(fora, key=CATEGORIAS.index)


def por_categoria(item, cats):
    """Quais especialidades sustentam cada categoria (o app usa nos filtros)."""
    pc = {}
    for c in cats:
        if c in CATS_EXAME:
            esp = [e for e in item['esp_exib']
                   if DE_NATUREZA.get(_natureza(e)) == c]
        else:
            esp = list(item['esp_exib'])
        pc[c] = sorted(set(esp)) or sorted(set(item['esp_exib']))
    return pc


_NAT = None


def _natureza(esp):
    """Refaz o mapa especialidade -> natureza usando o vocabulário do build_unico."""
    global _NAT
    if _NAT is None:
        sys.path.insert(0, os.path.dirname(AQUI))
        import build_unico
        _NAT = build_unico.natureza
    return _NAT(esp)


def main():
    base = json.load(io.open(ORIGEM, encoding='utf-8'))
    itens, cidades_ordem = base['itens'], base['cidades']

    prestadores, centros = [], {}
    for i in itens:
        cidade = i['cidade']
        lat, lon = COORD[cidade]
        cats = categorias_do(i)
        bairros = [b for b in dict.fromkeys(e['bairro'] for e in i['enderecos']) if b]
        ends = [e for e in dict.fromkeys(e['logradouro'] for e in i['enderecos']) if e]
        tels = []
        for e in i['enderecos']:
            for t in re.split(r'\s*/\s*', e.get('tel') or ''):
                t = fone(t)
                if t and t not in tels:
                    tels.append(t)
        prestadores.append({
            'n': maiusc(i['nome_exib']),
            'c': i['cnpj'] or i['conselho'],
            'cid': [maiusc(cidade)], 'cr': [maiusc(cidade)],
            'pp': {maiusc(cidade): ['ns']}, 'p': ['ns'], 'dir': [],
            'b': [maiusc(b) for b in bairros],
            'e': [maiusc(e) for e in ends],
            't': tels, 'mail': [], 'acess': False,
            'eq': [[m['nome'], m['registro'], ''] for m in i['corpo_clinico']],
            'cat': cats[0], 'cats': cats,
            'esp': [maiusc(e) for e in i['esp_exib']],
            'pc': {c: [maiusc(e) for e in v] for c, v in por_categoria(i, cats).items()},
            's': [], 'xy': [lat, lon],
        })
        chave = 'CENTRO|' + maiusc(cidade)
        centros.setdefault(chave, [lat, lon, 0])
        centros[chave][2] += 1

    dados = {'PR': {
        'gerado_em': GERADO_EM, 'uf': 'PR', 'estado': REGIAO, 'nota': '',
        'produtos': PRODUTOS, 'categorias': CATEGORIAS, 'catsExame': CATS_EXAME,
        'centros': centros, 'prestadores': prestadores,
    }}
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(dados, io.open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False)
    print('prestadores:', len(prestadores), '| centros:', len(centros))
    from collections import Counter
    for c, n in Counter(p['cat'] for p in prestadores).most_common():
        print('  %-34s %4d' % (c, n))
    print('gravado:', SAIDA, round(os.path.getsize(SAIDA) / 1024), 'KB')


if __name__ == '__main__':
    main()
