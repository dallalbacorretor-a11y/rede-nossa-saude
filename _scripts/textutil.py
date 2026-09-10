# -*- coding: utf-8 -*-
import re

ACRONIMOS = {
 'LTDA','ME','EPP','EIRELI','SA','SS','UTI','UPA','PS','SADT',
 'IDF','SIIM','CADI','MK','FAMA','LAPAC','CIC','CIA','II','III','IV',
 'AMS','CDI','CTI','TC','RM','RX','USG','ORL','UEPG','HC','PA','SPA','CEM','CMO','SOS',
 'CLINIPON','BIOSAVE','ISPAR','ISPON','CLINAN','CICASTRO','PLATO','LAFFER','DAVAUS','VITALLE',
 'OFTALMOCARDIO','DIAGNOSTIX','UROSAUDE','ANESTHEMED','GASTROCLINICA','CLINICENTER','XV','XIX','XXI','XXIII','JR',
}

MINUSCULAS = {'de','da','do','das','dos','e','em','a','o','os','as','na','no','nas','nos','para',
              'com','por','ao','aos','sob','sobre'}

ACENTOS = {
 'analises':'análises','clinicas':'clínicas','clinica':'clínica','clinico':'clínico',
 'medico':'médico','medica':'médica','medicos':'médicos','medicas':'médicas',
 'saude':'saúde','coracao':'coração','sao':'São','misericordia':'misericórdia',
 'diagnostico':'diagnóstico','diagnostica':'diagnóstica','diagnose':'diagnose',
 'obstetricia':'obstetrícia','ortopedico':'ortopédico','ortopedica':'ortopédica',
 'nutricao':'nutrição','cranio':'crânio','toracica':'torácica','plastica':'plástica',
 'pediatrica':'pediátrica','ossea':'óssea','urodinamica':'urodinâmica',
 'reabilitacao':'reabilitação','associacao':'associação','beneficencia':'beneficência',
 'servicos':'serviços','servico':'serviço','gestao':'gestão','laboratorio':'laboratório',
 'cirurgico':'cirúrgico','cirurgica':'cirúrgica','desintometria':'densitometria',
 'jesus':'Jesus','santa':'Santa','casa':'Casa','doutor':'Doutor',
 'jaguariaiva':'Jaguariaíva','carambei':'Carambeí','prudentopolis':'Prudentópolis',
 'telemaco':'Telêmaco','pirai':'Piraí','parana':'Paraná','praca':'Praça',
 'joao':'João','antonio':'Antônio','luis':'Luís','jose':'José','ines':'Inês',
 'rosario':'Rosário','conceicao':'Conceição','candido':'Cândido','otavio':'Otávio',
 'vitoria':'Vitória','bancarios':'Bancários','araucarias':'Araucárias','agua':'Água',
 'pro':'Pró','uniao':'União','industria':'indústria','industrial':'industrial',
 'cesar':'César','vicencia':'Vicência','olimpio':'Olímpio','sebastiao':'Sebastião',
 'cabeca':'Cabeça','pescoco':'Pescoço','barao':'Barão','joaquim':'Joaquim','nicolau':'Nicolau','russia':'Rússia','familia':'Família','sagrado':'Sagrado','olhos':'Olhos','edificio':'Edifício','ildefonso':'Ildefonso','cavalcanti':'Cavalcanti','orfas':'Órfãs','ceas':'CEAS','psyque':'Psyque','equilibre':'Equilibre','excelencia':'Excelência','assistencia':'Assistência','pontagrossense':'Pontagrossense','comercio':'Comércio','geriatria':'Geriatria','urologia':'Urologia','oncologia':'Oncologia','hemoterapia':'Hemoterapia','neurocirurgia':'Neurocirurgia','maxilo':'Maxilo','endoscopia':'Endoscopia','pneumologia':'Pneumologia','infectologia':'Infectologia','ressonancia':'Ressonância','magnetica':'Magnética','ergometrico':'Ergométrico','ergometrica':'Ergométrica','tomografia':'Tomografia','otorrino':'Otorrino','cardiaca':'Cardíaca','torax':'Tórax','abdome':'Abdome','holter':'Holter','eletroencefalografia':'Eletroencefalografia','espirometria':'Espirometria','litotripsia':'Litotripsia','quimioterapia':'Quimioterapia','hemodialise':'Hemodiálise','nefrologica':'Nefrológica','pediatrico':'Pediátrico','obstetrica':'Obstétrica','ambulatorio':'ambulatório','oncologico':'oncológico','geral':'geral',
}

def _word(w, first):
    lw = w.lower()
    base = re.sub(r'[^a-z]', '', lw)
    m = re.match(r'^([^A-Za-z0-9]*)([A-Za-z0-9]+)([^A-Za-z0-9]*)$', w)
    if m and m.group(2).upper() in ACRONIMOS:
        return m.group(1) + m.group(2).upper() + m.group(3)
    if base in ACENTOS:
        v = ACENTOS[base]
        pre = re.match(r'^[^a-zA-Z]*', lw).group(0)
        pos = re.search(r'[^a-zA-Z]*$', lw).group(0)
        v = v[0].upper() + v[1:]
        return pre + v + pos
    if not first and lw in MINUSCULAS:
        return lw
    return lw[:1].upper() + lw[1:]

def titulo(s):
    s = (s or '').strip()
    if not s:
        return ''
    s = re.sub(r'\s+', ' ', s)
    out = []
    for i, w in enumerate(s.split(' ')):
        if re.search(r'\d', w) or ('/' in w and w.isupper() and len(w) <= 5):
            out.append(w)
            continue
        parts = re.split(r'(-)', w)
        out.append(''.join(_word(p, i == 0) if p != '-' else '-' for p in parts))
    r = ' '.join(out)
    r = re.sub(r'\b(Rua|Avenida|Travessa|Alameda|Praça) \1\b', r'\1', r, flags=re.I)
    return r

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    tests = ['HOSPITAL DO CORACAO BOM JESUS', 'SANTA CASA DE MISERICORDIA DE PONTA GROSSA',
             'ANALISES CLINICAS E PATOLOGIA', 'LABORATORIO DE ANALISES CLINICAS DOFF SOTTA',
             'CLINICA SABEDOTTI LTDA - FILIAL', 'INSTITUTO DOUTOR FEITOSA IDF',
             'ISPAR - INSTITUTO SUL PARANAENSE DE RADIOTERAPIA LTDA',
             'RUA NOSSA SENHORA DO ROSARIO, 102', 'FAMA - LABORATORIO DE ANALISES CLINICAS',
             'CENTRO DE FISIOTERAPIA E REABILITACAO MASSUQUETO', 'LAPAC',
             'HOSPITAL MOURA LTDA - MATRIZ', 'RADIOLOGIA E DIAGNOSTICO POR IMAGEM',
             'CIRURGIA DO APARELHO DIGESTIVO', 'JARDIM DOS BANCARIOS', 'AGUA SUJA',
             'DESINTOMETRIA OSSEA', 'CENTRO HOSPITALAR SAO CAMILO']
    for t in tests:
        print('%-56s -> %s' % (t, titulo(t)))
