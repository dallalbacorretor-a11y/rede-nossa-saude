# -*- coding: utf-8 -*-
"""Baixa a rede credenciada da Nossa Saúde por (rede credenciada x UF).

Um PDF oficial por combinação, em pdfs_rede/<idRede>__<UF>.pdf.
Retoma de onde parou: arquivos já existentes são pulados.
"""
import os, re, sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
from scrape import sess, get_pdf, B

OUT = 'pdfs_rede'
os.makedirs(OUT, exist_ok=True)
OPT = re.compile(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', re.S)


def catalogo(s):
    pg = s.get(B + '/comum/redeCredenciada.php', timeout=60).content.decode('latin-1')
    def sel(sid):
        m = re.search(r'<select[^>]*id="%s"[^>]*>(.*?)</select>' % sid, pg, re.S)
        out = []
        for v, t in OPT.findall(m.group(1)):
            t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', t)).strip()
            if v.strip():
                out.append((v.strip(), t))
        return out
    return sel('tipoRede1') or sel('tipoRede'), sel('estado')


def main():
    s = sess()
    redes, estados = catalogo(s)
    usadas = set()
    if os.path.exists('planos_redes.json'):
        pr = json.load(open('planos_redes.json', encoding='utf-8'))
        usadas = {v for d in pr['mapa'].values() for v, _ in d['redes']}
    alvo = [(v, t) for v, t in redes if not usadas or v in usadas]
    print('redes no site: %d | usadas por algum plano: %d | alvo: %d'
          % (len(redes), len(usadas), len(alvo)))
    json.dump({'redes': redes, 'estados': estados},
              open('catalogo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    ufs = [u for u in (os.environ.get('UFS') or 'PR').split(',') if u]
    tarefas = [(rid, rtxt, uf) for rid, rtxt in alvo for uf in ufs]
    tarefas += [('TODAS', 'TODAS AS REDES', uf) for uf in ufs]
    print('total de downloads:', len(tarefas))

    falhas = []
    for i, (rid, rtxt, uf) in enumerate(tarefas, 1):
        fn = '%s/%s__%s.pdf' % (OUT, rid, uf)
        if os.path.exists(fn):
            continue
        t0 = time.time()
        ok = False
        for tent in range(3):
            try:
                b = get_pdf(s, estado=uf, cidade='', tipoRede=('' if rid == 'TODAS' else rid))
                if b and b[:4] == b'%PDF':
                    open(fn, 'wb').write(b)
                    ok = True
                    break
                print('   sem pdf (%s/%s) tentativa %d' % (rtxt, uf, tent + 1))
            except Exception as e:
                print('   erro (%s/%s): %s' % (rtxt, uf, e))
            time.sleep(2)
        if ok:
            print('[%3d/%d] %-34s %-3s %7d bytes %5.1fs' % (i, len(tarefas), rtxt, uf,
                                                            os.path.getsize(fn), time.time() - t0))
        else:
            falhas.append((rid, rtxt, uf))
            print('[%3d/%d] %-34s %-3s FALHOU' % (i, len(tarefas), rtxt, uf))
    print('concluido. falhas:', falhas)


if __name__ == '__main__':
    main()
