# -*- coding: utf-8 -*-
"""Etapa 7: devolve o direcionamento interno.

A etapa 3 tirou o "D" no lugar do visto porque, nos Campos Gerais, a Nossa
Saúde não marcava nenhum prestador assim. Em Curitiba marca: o campo
"Observação" da listagem do site (que o PDF de impressão não traz) diz
"Somente por encaminhamento" em Pilar, Cruz Vermelha, INC, Pequeno Príncipe,
Menino Deus, Erasto Gaertner e Erastinho, entre outros.

O mecanismo é o mesmo da Amil e da Paraná Clínicas: `dir` no prestador, "D"
na coluna do plano no site e no PDF, e a legenda explicando o que é.
"""
import io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
AQUI = os.path.dirname(os.path.abspath(__file__))
ALVO = os.path.join(AQUI, 'montar_site.py')
t = io.open(ALVO, encoding='utf-8').read()
n = 0

APOS = chr(39)
ASPAS = APOS * 3


def sub(de, para, vezes=1):
    global t, n
    if t.count(de) != vezes:
        raise SystemExit('esperava %d de %r, achei %d' % (vezes, de[:110], t.count(de)))
    t = t.replace(de, para)
    n += vezes


BLOCO = '\n'.join([
    '',
    '# ------------------------------------------------- direcionamento interno',
    '# Prestador que a operadora só libera por encaminhamento. Marcar com D, e',
    '# não com o visto, é o que evita prometer acesso livre (vem do campo',
    '# "Observação" da listagem oficial; ver notas.py).',
    'app = troca(app, ' + ASPAS + '             (tem ? "&#10003;" : "") + "</td>";' + ASPAS + ',',
    '            ' + ASPAS + '             (tem',
    '               ? ((p.dir || []).indexOf(c.codigo) >= 0',
    '                   ? \'<abbr class="dir" title="A operadora só libera este \'',
    '                     + \'prestador por encaminhamento — o acesso não é \'',
    '                     + \'livre. Passe o cursor no selo ao lado do nome \'',
    '                     + \'para ler a observação da operadora.">D</abbr>\'',
    '                   : "&#10003;")',
    '               : "") + "</td>";' + ASPAS + ')',
    'head = troca(head, ".equipe{cursor:help;border-bottom:1px dotted currentColor}",',
    '             ".equipe{cursor:help;border-bottom:1px dotted currentColor}" +',
    '             "\\n.prod .dir{font:700 11px/1 inherit;text-decoration:none;" +',
    '             "cursor:help;border:1px solid currentColor;border-radius:3px;" +',
    '             "padding:0 3px}")',
    'head = troca(head,',
    '             "o plano específico do cliente.</p>",',
    '             "o plano específico do cliente. <b>D</b> na coluna do plano é "',
    '             "<b>direcionamento interno</b>: o prestador atende, mas por "',
    '             "encaminhamento da operadora, não por acesso livre.</p>")',
    '',
    '# no PDF, o mesmo D no lugar do visto',
    'lib = troca(lib,',
    '            ' + ASPAS + '          if (tem) {',
    '            // circulo em volta do visto, como no material impresso',
    '            p.circulo(x + cols[ci].l / 2, topo + 1.2, 6.2, corPr, true, 0.9);',
    '            visto(p, x + cols[ci].l / 2, topo + 0.2, corPr);',
    '          } else {' + ASPAS + ',',
    '            ' + ASPAS + '          if (tem) {',
    '            // circulo em volta do visto, como no material impresso',
    '            p.circulo(x + cols[ci].l / 2, topo + 1.2, 6.2, corPr, true, 0.9);',
    '            if ((item.dir || []).indexOf(pr.codigo) >= 0) {',
    '              // direcionamento interno: D no lugar do visto',
    '              p.texto(x + cols[ci].l / 2 - p.larguraTexto("D", "sansB", 7) / 2,',
    '                      topo - 1.3, "D", "sansB", 7, corPr);',
    '            } else {',
    '              visto(p, x + cols[ci].l / 2, topo + 0.2, corPr);',
    '            }',
    '          } else {' + ASPAS + ')',
    '',
    '# o selo ao lado do nome: no app da Amil `s` é acreditação (ONA), aqui é',
    '# o aviso de encaminhamento — então o cartão do hospital para de dizer',
    '# "ACRED." e a dica do selo passa a mostrar o texto da operadora.',
    'lib = troca(lib, ' + APOS + '"ACRED.", "sansB", 6.6, OURO);' + APOS + ',',
    '            ' + APOS + '"ENCAM.", "sansB", 6.6, OURO);' + APOS + ')',
    'app = troca(app, ' + APOS + 'esc(p.s.join(", "))' + APOS + ',',
    '            ' + APOS + 'esc((p.obs || p.s).join(" · "))' + APOS + ')',
    '',
])

# entra logo antes da remontagem da página
sub('\n# o nome do arquivo e o que o cliente ve na conversa: operadora e recorte',
    BLOCO + '\n# o nome do arquivo e o que o cliente ve na conversa: operadora e recorte')

# e o aviso do PDF precisa explicar o D
sub('\n'.join([
    "            'var aviso = \"Este material soma todos os planos da Nossa Saúde na \" +\\n'",
    '            \'      "região: se o prestador está aqui, ele é credenciado da operadora " +\\n\'',
    '            \'      "naquela cidade por algum plano. " +\')',
]), '\n'.join([
    "            'var aviso = \"Este material soma todos os planos da Nossa Saúde na \" +\\n'",
    '            \'      "região: se o prestador está aqui, ele é credenciado da operadora " +\\n\'',
    '            \'      "naquela cidade por algum plano. O D no lugar do visto marca " +\\n\'',
    '            \'      "direcionamento interno: a operadora só libera aquele prestador " +\\n\'',
    '            \'      "por encaminhamento. " +\')',
]))

io.open(ALVO, 'w', encoding='utf-8').write(t)
print('etapa 7: %d trocas' % n)
