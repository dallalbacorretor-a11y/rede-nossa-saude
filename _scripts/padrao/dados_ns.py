# -*- coding: utf-8 -*-
"""Converte as coletas da Nossa Saúde para o formato que o app padrão espera.

O app (mesmo da Amil e da Paraná Clínicas) lê `window.DADOS_UF = {chave: {...}}`
e mostra um botão por chave quando há mais de uma — é assim que a Amil alterna
entre PR, SC e SP. Aqui as chaves são as duas regiões atendidas.

Em todas elas os planos entram como um produto só: o material soma a rede
inteira da operadora na cidade.
"""
import io, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PAI = os.path.dirname(AQUI)
SAIDA = os.path.join(AQUI, 'dados', 'dados_ns.json')
sys.stdout.reconfigure(encoding='utf-8')

GERADO_EM = {'CG': '10/09/2026', 'CWB': '23/09/2026'}

REGIOES = [
    {'chave': 'CG', 'nome': 'Campos Gerais', 'origem': 'dados_unico.json'},
    {'chave': 'CWB', 'nome': 'Curitiba, RMC e Paranaguá', 'origem': 'dados_cwb.json'},
]

# Sede dos municípios (IBGE), para o mapa de bolhas e o "Perto de".
COORD = {
    # Campos Gerais
    'Ponta Grossa': (-25.095, -50.162), 'Telêmaco Borba': (-24.324, -50.617),
    'Jaguariaíva': (-24.251, -49.706), 'Castro': (-24.791, -50.012),
    'Irati': (-25.468, -50.651), 'Palmeira': (-25.429, -50.007),
    'Carambeí': (-24.915, -50.098), 'Prudentópolis': (-25.213, -50.978),
    'Piraí do Sul': (-24.526, -49.945),
    # Curitiba, RMC e litoral
    'Curitiba': (-25.4284, -49.2733), 'São José dos Pinhais': (-25.5305, -49.2064),
    'Araucária': (-25.5936, -49.4103), 'Fazenda Rio Grande': (-25.6625, -49.3075),
    'Campo Largo': (-25.4589, -49.5278), 'Pinhais': (-25.4447, -49.1925),
    'Colombo': (-25.2917, -49.2242), 'Tijucas do Sul': (-25.9294, -49.1947),
    'Campina Grande do Sul': (-25.3053, -49.0553), 'Lapa': (-25.7708, -49.7158),
    'Rio Negro': (-26.1058, -49.7969), 'Piraquara': (-25.4422, -49.0628),
    'Agudos do Sul': (-25.9906, -49.3339), 'Balsa Nova': (-25.5794, -49.6289),
    'Doutor Ulysses': (-24.5636, -49.4197), 'Paranaguá': (-25.5163, -48.5225),
}

# Ordem de exibição e de precedência. A categoria de hospital precisa começar
# com "Hospitais": o app usa /^Hospitais/ para saber onde não se marca exame
# eletivo.
CATEGORIAS = ['Hospitais', 'Diagnóstico por imagem', 'Laboratórios e análises clínicas',
              'Exames e procedimentos', 'Clínicas e consultórios',
              'Médicos e demais profissionais']
CATS_EXAME = ['Diagnóstico por imagem', 'Laboratórios e análises clínicas',
              'Exames e procedimentos']

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


def fone(t):
    d = re.sub(r'\D', '', t or '')
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


_NAT = None


def _natureza(esp):
    global _NAT
    if _NAT is None:
        sys.path.insert(0, PAI)
        import build_unico
        _NAT = build_unico.natureza
    return _NAT(esp)


def por_categoria(item, cats):
    """Quais especialidades sustentam cada categoria (o app usa nos filtros)."""
    pc = {}
    for c in cats:
        if c in CATS_EXAME:
            esp = [e for e in item['esp_exib'] if DE_NATUREZA.get(_natureza(e)) == c]
        else:
            esp = list(item['esp_exib'])
        pc[c] = sorted(set(esp)) or sorted(set(item['esp_exib']))
    return pc


def monta(regiao):
    base = json.load(io.open(os.path.join(PAI, regiao['origem']), encoding='utf-8'))
    prestadores, centros = [], {}
    for i in base['itens']:
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

    return {
        'gerado_em': GERADO_EM[regiao['chave']], 'uf': regiao['chave'],
        'estado': regiao['nome'], 'nota': '',
        'produtos': PRODUTOS, 'categorias': CATEGORIAS, 'catsExame': CATS_EXAME,
        'centros': centros, 'prestadores': prestadores,
    }, base['cidades']


def main():
    dados = {}
    for r in REGIOES:
        dados[r['chave']], cidades = monta(r)
        p = dados[r['chave']]['prestadores']
        print('%-28s %4d prestadores · %2d cidades · %2d hospitais'
              % (r['nome'], len(p), len(cidades),
                 sum(1 for x in p if x['cat'] == 'Hospitais')))
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(dados, io.open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False)
    print('gravado:', SAIDA, round(os.path.getsize(SAIDA) / 1024), 'KB')


if __name__ == '__main__':
    main()
