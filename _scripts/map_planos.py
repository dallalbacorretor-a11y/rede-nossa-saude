# -*- coding: utf-8 -*-
"""Mapeia cada plano da Nossa Saúde para a(s) rede(s) credenciada(s) que ele usa."""
import sys, re, json, time
sys.stdout.reconfigure(encoding='utf-8')
import requests
from scrape import sess, B

OPT = re.compile(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', re.S)


def opcoes(html):
    out = []
    for v, t in OPT.findall(html):
        t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', t)).strip()
        out.append((v.strip(), t))
    return out


def main():
    s = sess()
    pg = s.get(B + '/comum/redeCredenciada.php', timeout=60).content.decode('latin-1')

    def select(sid):
        m = re.search(r'<select[^>]*id="%s"[^>]*>(.*?)</select>' % sid, pg, re.S)
        return opcoes(m.group(1)) if m else []

    planos = [(v, t) for v, t in select('plano') if v]
    estados = [(v, t) for v, t in select('estado') if v]
    print('planos:', len(planos), '| estados:', [e[0] for e in estados])

    mapa = {}
    for i, (pid, ptxt) in enumerate(planos, 1):
        for tent in range(3):
            try:
                r = s.post(B + '/comum/buscaRede.php?idSessao=',
                           data={'plano': pid, 'local': 'rede', 'rede': ''}, timeout=60)
                redes = [(v, t) for v, t in opcoes(r.content.decode('latin-1')) if v]
                break
            except Exception as e:
                print('  retry', pid, e); time.sleep(2); redes = []
        mapa[pid] = {'plano': ptxt, 'redes': redes}
        if i % 40 == 0 or i == len(planos):
            print('%d/%d' % (i, len(planos)))

    json.dump({'planos': planos, 'estados': estados, 'mapa': mapa},
              open('planos_redes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # agrupa planos por conjunto de redes
    grupos = {}
    for pid, d in mapa.items():
        k = tuple(sorted(v for v, _ in d['redes']))
        grupos.setdefault(k, []).append(d['plano'])
    print('\nconjuntos distintos de rede:', len(grupos))
    nomes = {v: t for d in mapa.values() for v, t in d['redes']}
    for k, v in sorted(grupos.items(), key=lambda x: -len(x[1])):
        print('%3d planos  <-  %s' % (len(v), ' + '.join(nomes.get(x, x) for x in k) or '(nenhuma)'))
    print('\nredes distintas citadas:', len(nomes))


if __name__ == '__main__':
    main()
