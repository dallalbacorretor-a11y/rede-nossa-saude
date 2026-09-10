# -*- coding: utf-8 -*-
import requests, re, os, sys, json, time
B='https://prestador.nossasaude.com.br'
OUT='pdfs'; os.makedirs(OUT,exist_ok=True)

def sess():
    s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0 Chrome/120'})
    s.get(B+'/rede/rede.php',timeout=60)
    s.post(B+'/comum/RedeCredenciadaBuscaUsuario.php',data={'todos':'x'},timeout=60)
    s.get(B+'/comum/redeCredenciada.php',timeout=60)
    return s

def form(**kw):
    d={'plano':'','nome_prestador':'','tipo_prestador':'','tipoRede':'','estado':'PR','cidade':'','bairro':'','graduacao':'','especialidade':'','area':'','regiao':'','emergencia':'','ordenacao':'porPrestador','cidade_selecionada':'','area_selecionada':'','bairro_selecionado':'','cnpj':'nossasaude'}
    d.update(kw); return d

def get_pdf(s,**kw):
    r=s.post(B+'/comum/imprimirRedeCredenciada.php?idsessao=',data=form(**kw),timeout=180)
    m=re.search(r"document\.location='([^']+)'",r.text)
    if not m: return None
    return s.get(B+'/comum/'+m.group(1),timeout=180).content

CIDADES=['PONTA GROSSA','CASTRO','CARAMBEI','PALMEIRA','TELEMACO BORBA','JAGUARIAIVA','PIRAI DO SUL','PRUDENTOPOLIS','IRATI']

if __name__=='__main__':
    plano=sys.argv[1] if len(sys.argv)>1 else ''
    tag=sys.argv[2] if len(sys.argv)>2 else 'TODOS'
    s=sess()
    for c in CIDADES:
        fn=f'{OUT}/{tag}__{c.replace(" ","_")}.pdf'
        if os.path.exists(fn) and os.path.getsize(fn)>2000:
            print('skip',fn); continue
        try:
            b=get_pdf(s,cidade=c,plano=plano)
        except Exception as e:
            print('ERR',c,e); continue
        if not b: print('NOPDF',c); continue
        open(fn,'wb').write(b); print(c,len(b))
