# -*- coding: utf-8 -*-
"""As observações da operadora, separadas em "vale para todo mundo" e "só para
um plano".

A Nossa Saúde publica dois tipos de restrição de acesso no mesmo campo:

  "Somente por encaminhamento."                      -> vale para qualquer plano
  "PLANO VIDA CARE / REDE AMETISTA SOMENTE COM ...   -> vale só para aquele plano

Como o material soma todos os planos numa rede só, marcar o segundo caso como
direcionamento pintaria de "D" um terço da rede e mentiria para quem tem outro
plano. Então só o primeiro vira direcionamento; o segundo fica no texto da
observação, que o site mostra ao passar o cursor.
"""
import io, json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))

# a cláusula do plano, quando aparece solta no meio do texto
CLAUSULA = re.compile(
    r'(REDE\s+AME[SD]?TISTA\s*[/|]?\s*)?PLANO\s+VIDA\s+CARE\s*[/|]?\s*'
    r'(REDE\s+AME[SD]?TISTA)?\s*SOMENTE\s+COM\s+ENCAMINHAMENTO\.?', re.I)
# o mesmo plano usado como rótulo de tudo que vem depois ("PLANO VIDA CARE: ...")
ESCOPO = re.compile(r'PLANO\s+VIDA\s+CARE\s*:', re.I)
ENCAM = re.compile(r'encaminh|direcion', re.I)


def registro(s):
    """CNPJ ou conselho reduzido ao que dá para comparar."""
    s = re.sub(r'^\s*CNPJ\s*:?', '', (s or '').upper())
    return re.sub(r'[^0-9A-Z]', '', s)


def geral(texto):
    """A observação restringe o acesso de qualquer plano?"""
    if ESCOPO.search(texto):
        return False          # o que vem depois é daquele plano
    return bool(ENCAM.search(CLAUSULA.sub(' ', texto)))


def carrega(*arquivos):
    """{registro: [observações]} — junta os arquivos de coleta."""
    fora = {}
    for a in arquivos:
        caminho = os.path.join(AQUI, a)
        if not os.path.exists(caminho):
            continue
        for _cidade, prest in json.load(io.open(caminho, encoding='utf-8')).items():
            for k, obs in prest.items():
                reg = registro(k.split('||')[1])
                if reg:
                    fora.setdefault(reg, [])
                    for o in obs:
                        if o not in fora[reg]:
                            fora[reg].append(o)
    return fora


def do_prestador(mapa, cnpj, conselho):
    """(direcionamento?, [observações]) para um prestador dos dados."""
    obs = mapa.get(registro(cnpj)) or mapa.get(registro(conselho)) or []
    return any(geral(o) for o in obs), obs
