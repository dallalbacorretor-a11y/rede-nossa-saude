# -*- coding: utf-8 -*-
"""Etapa 2 da adaptação: o que ainda é da Paraná Clínicas vira Nossa Saúde.

As buscas mexem em trechos de código dentro de strings, então `\\n` aqui é
barra-invertida-n de verdade (dois caracteres). BN monta isso sem depender de
escape, que o shell come no caminho.
"""
import io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
AQUI = os.path.dirname(os.path.abspath(__file__))
ALVO = os.path.join(AQUI, 'montar_site.py')

BN = chr(92) + 'n'          # o par \n dentro das strings do gerador
Q = chr(39)                 # aspas simples
t = io.open(ALVO, encoding='utf-8').read()
n = 0


def sub(de, para, vezes=1):
    global t, n
    if t.count(de) != vezes:
        raise SystemExit('esperava %d de %r, achei %d' % (vezes, de[:110], t.count(de)))
    t = t.replace(de, para)
    n += vezes


def linhas(*ls):
    """Remonta um bloco de código-em-string do gerador."""
    return (BN + Q + '\n            ' + Q).join(ls)


# ------------------------------------------------- um produto só: uma cor só
sub('var COR = { "Paraná Clínicas": "var(--marca-texto)" };',
    'var COR = { "Nossa Saúde": "var(--marca-texto)" };', 3)
sub('var COR_GRAFICO = { "Paraná Clínicas": "#a80a32" };',
    'var COR_GRAFICO = { "Nossa Saúde": "#e6411c" };')
sub('  var VAR_PLANO = { p400: "var(--plano-a)", p600: "var(--plano-b)",' + BN + Q +
    '\n            ' + Q + '                    cim: "var(--plano-c)" };',
    '  var VAR_PLANO = { ns: "var(--plano-a)" };')

# ------------------------------------------------ quadros e seções do PDF
sub(linhas('    var hospG = daCategoria("Hospitais gerais");',
           '    var hospE = daCategoria("Hospitais especializados");',
           '    var cim = daCategoria("Unidades próprias CIM");',
           '    var medCim = daCategoria("Médicos dos CIM");',
           '    var imagem = daCategoria("Diagnóstico por imagem");',
           '    var lab = daCategoria("Laboratórios e análises clínicas");',
           '    var terapias = daCategoria("Terapias");',
           '    var cons = daCategoria("Clínicas e policlínicas")',
           '                 .concat(daCategoria("Consultórios"));'),
    linhas('    var hosp = daCategoria("Hospitais");',
           '    var imagem = daCategoria("Diagnóstico por imagem");',
           '    var lab = daCategoria("Laboratórios e análises clínicas");',
           '    var proc = daCategoria("Exames e procedimentos");',
           '    var cons = daCategoria("Clínicas e consultórios");',
           '    var prof = daCategoria("Médicos e demais profissionais");'))

sub(linhas('    rel.numeros([',
           '      [hospG.length, "Hospitais gerais"],',
           '      [hospE.length, "Hospitais especializados"],',
           '      [imagem.length, "Centros de diagnóstico por imagem"],',
           '      [lab.length, "Laboratórios de análises clínicas"],',
           '      [cim.length + medCim.length, "Atendimento nos CIM"],',
           '      [cons.length, "Clínicas e consultórios"],',
           '      [lista.length, "Prestadores no total"]',
           '    ].filter(function (n) { return n[0]; }));'),
    linhas('    rel.numeros([',
           '      [hosp.length, "Hospitais para internação"],',
           '      [imagem.length, "Centros de diagnóstico por imagem"],',
           '      [lab.length, "Laboratórios de análises clínicas"],',
           '      [proc.length, "Exames e procedimentos"],',
           '      [cons.length, "Clínicas e consultórios"],',
           '      [prof.length, "Médicos e demais profissionais"],',
           '      [lista.length, "Prestadores no total"]',
           '    ].filter(function (n) { return n[0]; }));'))

sub(linhas('    secao("Hospitais gerais", hospG);',
           '    secao("Hospitais especializados", hospE);',
           '    secao("Unidades próprias CIM", cim);'),
    '    secao("Hospitais e internação", hosp);')

sub(linhas('    secao("Terapias", terapias);',
           '    secao("Médicos que atendem nos CIM", medCim);'),
    linhas('    secao("Clínicas e consultórios", cons);',
           '    secao("Médicos e demais profissionais", prof);'))

# --------------------------------------------------- quadros do panorama
sub(linhas('    var hospitais = daCat("Hospitais gerais");',
           '    var hospEsp = daCat("Hospitais especializados");',
           '    var imagem = daCat("Diagnóstico por imagem");',
           '    var exames = daCat("Laboratórios e análises clínicas",',
           '                       "Exames e procedimentos", "Oncologia");',
           '    var cim = daCat("Unidades próprias CIM", "Médicos dos CIM");',
           '    var consultorios = daCat("Clínicas e policlínicas", "Consultórios",',
           '                             "Terapias");'),
    linhas('    var hospitais = daCat("Hospitais");',
           '    var imagem = daCat("Diagnóstico por imagem");',
           '    var exames = daCat("Laboratórios e análises clínicas",',
           '                       "Exames e procedimentos");',
           '    var medicos = daCat("Médicos e demais profissionais");',
           '    var consultorios = daCat("Clínicas e consultórios");'))

sub(linhas('      [hospitais, "hospitais gerais"],',
           '      [hospEsp, "hospitais especializados"],',
           '      [imagem, "centros de imagem"],',
           '      [exames, "laboratórios e exames"],',
           '      [cim, "atendimento nos CIM"],',
           '      [consultorios, "clínicas e consultórios"]'),
    linhas('      [hospitais, "hospitais"],',
           '      [imagem, "centros de imagem"],',
           '      [exames, "laboratórios e exames"],',
           '      [consultorios, "clínicas e consultórios"],',
           '      [medicos, "médicos e profissionais"]'))

sub('    var refs = hospG.concat(hospE);', '    var refs = hosp;')
sub('"Os hospitais de maior cobertura na sua rede — os gerais primeiro, '
    "'\n            '" + 'que são onde a internação acontece.");',
    '"Os hospitais da rede na região — é onde a internação acontece.");')

io.open(ALVO, 'w', encoding='utf-8').write(t)
print('etapa 2: %d trocas' % n)
