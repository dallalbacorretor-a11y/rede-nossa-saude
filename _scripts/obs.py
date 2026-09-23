# -*- coding: utf-8 -*-
"""Colhe o campo "Observação" da rede credenciada.

O PDF de impressão da operadora NÃO traz esse campo — ele só existe na
listagem em HTML (`listaRedeCredenciada.php`), uma observação por
especialidade. É lá que está o "somente por encaminhamento", que é como a
Nossa Saúde marca o prestador de acesso por direcionamento, e também o
horário de atendimento e a faixa etária.

A paginação daquela listagem é estado de sessão (o `pg=` da URL não move
nada), então aqui se consulta **um prestador por vez**, pelo nome exato que
saiu no PDF — assim a resposta cabe na primeira página.
"""
import io, json, os, re, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from scrape import sess, form, B
import parse

CABECA = re.compile(
    r'<strong style="font-size: 14px[^>]*>\s*(?P<nome>.+?)\s*'
    r'\(\s*(?P<reg>[^)]*)\)\s*-\s*(?P<tipo>[^<]*)</strong>', re.S)
OBS = re.compile(r'id=\s*"obs_espec"[^>]*>(?P<t>.*?)</textarea>', re.S)
ESPEC = re.compile(r'<p style="color: navy">(?P<e>[^<]*)</p>')


def limpa(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = (s.replace('&nbsp;', ' ').replace('&amp;', '&')
          .replace('&quot;', '"').replace('&#39;', "'"))
    return re.sub(r'\s+', ' ', s).strip()


def blocos(html):
    """[(nome, registro, [observações]) ...] — um por prestador da página."""
    fora, partes = [], list(CABECA.finditer(html))
    for k, m in enumerate(partes):
        fim = partes[k + 1].start() if k + 1 < len(partes) else len(html)
        corpo = html[m.end():fim]
        obs = [limpa(o.group('t')) for o in OBS.finditer(corpo)]
        fora.append((limpa(m.group('nome')), limpa(m.group('reg')),
                     [o for o in obs if o]))
    return fora


def chave(nome, reg):
    reg = re.sub(r'[^0-9A-Z]', '', (reg or '').upper())
    return (re.sub(r'\s+', ' ', (nome or '').upper()).strip(), reg)


def nomes_do_pdf(caminho):
    """[(nome cru, registro cru)] na ordem do PDF, sem repetir."""
    vistos, fora = set(), []
    for r in parse.parse(caminho):
        k = chave(r['nome'], r['registro'])
        if k not in vistos:
            vistos.add(k)
            fora.append((r['nome'].strip(), r['registro'].strip()))
    return fora


def consulta(s, cidade, nome):
    r = s.post(B + '/comum/listaRedeCredenciada.php?idSessao=',
               data=form(cidade=cidade, nome_prestador=nome), timeout=120)
    return blocos(r.text)


def main(pasta, saida, espera=0.12):
    tudo = json.load(io.open(saida, encoding='utf-8')) if os.path.exists(saida) else {}
    s = sess()
    for f in sorted(os.listdir(pasta)):
        if not f.startswith('TODOS__'):
            continue
        cidade = f[:-4].split('__')[1].replace('_', ' ')
        if cidade in tudo:
            print('%-24s já colhido (%d com observação)' % (cidade, len(tudo[cidade])))
            continue
        alvos = nomes_do_pdf(os.path.join(pasta, f))
        achados, faltou, t0 = {}, [], time.time()
        for i, (nome, reg) in enumerate(alvos):
            k = chave(nome, reg)
            for tent in range(3):
                try:
                    bs = consulta(s, cidade, nome)
                    break
                except Exception as e:
                    print('   erro', nome[:30], e)
                    s = sess()
            else:
                faltou.append(nome)
                continue
            casou = [b for b in bs if chave(b[0], b[1]) == k]
            if not casou:
                faltou.append(nome)
            for _n, _r, obs in casou:
                if obs:
                    achados['%s||%s' % k] = obs
            if espera:
                time.sleep(espera)
            if (i + 1) % 50 == 0:
                print('   %s %d/%d' % (cidade, i + 1, len(alvos)))
        tudo[cidade] = achados
        json.dump(tudo, io.open(saida, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('%-24s %3d prestadores · %3d com observação · %2d sem casar · %5.1fs'
              % (cidade, len(alvos), len(achados), len(faltou), time.time() - t0))
        if faltou:
            print('      sem casar:', '; '.join(f[:34] for f in faltou[:8]))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'cg':
        main('pdfs', 'obs_cg.json')
    else:
        main('pdfs_cwb', 'obs_cwb.json')
