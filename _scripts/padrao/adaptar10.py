# -*- coding: utf-8 -*-
"""Etapa 10: o PDF no padrão Central de Rede (pdf-rede.js + pdfmake).

O motor próprio (PDFWeb + Relatorio, herdado da Paraná Clínicas) cortava
bairro e especialidades com "…", deixava especialidades e cabeçalhos em
cinza claro e embutia Segoe UI e Constantia (fontes da Microsoft) na página.
Aqui ele sai inteiro:

- a página só DESCREVE o documento (pdf_nossa_saude.js, colado no lugar de
  gerarPDF/montarEEntregar e do PDF da aba Entre planos);
- o PDF é montado pelo pdf-rede.js, o mesmo da Amil, do Bradesco e da
  SulAmérica. Ele e o pdfmake.min.js e o fontes-pdf.js ficam na raiz do
  site, copiados sem alteração do rede-amil;
- saem do lib o PDFWeb, o Relatorio e as fontes embutidas. A linha das
  fontes (Segoe UI e Constantia em base64) foi apagada também do
  base/amil_lib.js; o código do Relatorio continua lá porque as etapas 1 a 9
  ainda o reescrevem antes de a etapa 10 cortá-lo.
"""
import io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
AQUI = os.path.dirname(os.path.abspath(__file__))
ALVO = os.path.join(AQUI, 'montar_site.py')
t = io.open(ALVO, encoding='utf-8').read()
n = 0


def sub(de, para, vezes=1):
    global t, n
    if t.count(de) != vezes:
        raise SystemExit('esperava %d de %r, achei %d' % (vezes, de[:110], t.count(de)))
    t = t.replace(de, para)
    n += vezes


BLOCO = r'''# ===================================== 3c) PDF no padrao Central de Rede
# Etapa 10 (adaptar10.py). O PDF sai pelo pdf-rede.js (pdfmake), o gerador da
# Amil, do Bradesco e da SulAmerica: o motor antigo (PDFWeb + Relatorio)
# cortava bairro e especialidades com "..." e embutia Segoe UI e Constantia.
# pdf-rede.js, pdfmake.min.js e fontes-pdf.js ficam na raiz do site, copiados
# sem alteracao do rede-amil; a pagina so descreve o documento.
def recorta(txt, de, ate, novo):
    """Troca o trecho [de, ate). Os dois marcadores existem uma vez so."""
    global trocas
    if txt.count(de) != 1 or txt.count(ate) != 1 or txt.index(ate) <= txt.index(de):
        raise SystemExit("recorta: esperava um %r antes de um %r" % (de[:60], ate[:60]))
    trocas += 1
    return txt[:txt.index(de)] + novo + txt[txt.index(ate):]


# a descricao do documento entra no lugar do motor antigo
app = recorta(app, "  function gerarPDFEntre() {\n", "  function montarSelects() {\n", "")
app = recorta(app, "  function gerarPDF() {\n", "  /* Zera todo filtro escolhido.",
              L(os.path.join(_local.AQUI, "pdf_nossa_saude.js")))
# PDFWeb, Relatorio e as fontes da Microsoft saem do lib (a linha das fontes
# ja foi tirada do base/amil_lib.js; se voltar numa copia nova, sai aqui)
if "window.FONTES=" in lib:
    lib = recorta(lib, "window.FONTES=", "window.CORRETOR=", "")
_corte = lib.index("/* pdf_web.js")
if "global.Relatorio = Relatorio;" not in lib[_corte:]:
    raise SystemExit("o motor antigo (Relatorio) mudou de lugar")
lib = lib[:_corte]
trocas += 1
# o gerador e externo: o pdf-rede.js carrega pdfmake e fontes no primeiro PDF
head = head + '<script src="pdf-rede.js"></script>\n'
for _resto in ("Relatorio", "PDFWeb", "window.FONTES", "entregarBinario"):
    if _resto in app or _resto in lib:
        raise SystemExit("sobrou referencia ao motor antigo: " + _resto)
'''

MARCA = '# ============================================================== 4) monta\n'
sub(MARCA, BLOCO + '\n' + MARCA)

io.open(ALVO, 'w', encoding='utf-8').write(t)
print('etapa 10: %d trocas' % n)
