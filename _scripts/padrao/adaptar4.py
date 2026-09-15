# -*- coding: utf-8 -*-
"""Etapa 4: com um produto só, a aba "Entre planos" compararia o plano com ele
mesmo e diria 100% — some com ela. O app já prevê produto único no resto."""
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


sub("""io.open(SAI, "w", encoding="utf-8").write(pagina)""",
    '''# ------------------------------------------------ produto unico: sem comparativo
# A aba "Entre planos" existe para confrontar duas redes. Aqui o material soma
# todos os planos numa rede so - ela compararia o plano com ele mesmo.
if len(dados["PR"]["produtos"]) < 2:
    head = troca(head,
                 \'<button type="button" class="aba" data-aba="entre">Entre planos</button>\',
                 \'<button type="button" class="aba" data-aba="entre" id="abaEntre"\'
                 \' hidden>Entre planos</button>\')
    app = troca(app, \'$("dataColeta").textContent = "atualizado em " + D.gerado_em;\',
                \'$("dataColeta").textContent = "atualizado em " + D.gerado_em;\\n\'
                \'    if (D.produtos.length < 2) {\\n\'
                \'      var abaE = $("abaEntre");\\n\'
                \'      if (abaE) abaE.hidden = true;\\n\'
                \'    }\')

io.open(SAI, "w", encoding="utf-8").write(pagina)''')

# o "pagina" precisa ser montado depois do bloco acima
sub('''blob = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
pagina = (head + "\\n<script>window.DADOS_UF=" + blob + ";\\n"
          + lib.split(";\\n", 1)[1] + "</script>\\n<script>" + app + "</script>\\n")
''', '')
sub('''io.open(SAI, "w", encoding="utf-8").write(pagina)''',
    '''blob = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
pagina = (head + "\\n<script>window.DADOS_UF=" + blob + ";\\n"
          + lib.split(";\\n", 1)[1] + "</script>\\n<script>" + app + "</script>\\n")
io.open(SAI, "w", encoding="utf-8").write(pagina)''')

io.open(ALVO, 'w', encoding='utf-8').write(t)
print('etapa 4: %d trocas' % n)
