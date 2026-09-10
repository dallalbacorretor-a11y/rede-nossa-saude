# -*- coding: utf-8 -*-
import os, sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
from scrape import sess, get_pdf, CIDADES
OUT='pdfs_cg'
rep = json.load(open('rep_planos.json', encoding='utf-8'))
s = sess()
for rid, (pid, ptxt) in rep.items():
    for c in CIDADES:
        fn = '%s/%s__%s.pdf' % (OUT, rid, c.replace(' ', '_'))
        if os.path.exists(fn) and os.path.getsize(fn) > 2000:
            continue
        b = None
        for tent in range(3):
            try:
                b = get_pdf(s, estado='PR', cidade=c, plano=pid)
                if b and b[:4] == b'%PDF':
                    break
            except Exception as e:
                print('  erro', e)
            time.sleep(2); b = None
        if b:
            open(fn, 'wb').write(b); print('%-12s %-16s %7d' % (rid, c, len(b)))
        else:
            print('%-12s %-16s vazio (sem prestador)' % (rid, c))
print('fim')
