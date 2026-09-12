# -*- coding: utf-8 -*-
"""Quem assina o material. Editar `corretor.json` e rodar os geradores de novo.

A corretora é fixa: Mazza Broker. Só os dados do corretor mudam.
"""
import json, os

CORRETORA = 'Mazza Broker'
_AQUI = os.path.dirname(os.path.abspath(__file__))
_PADRAO = {'nome': 'Alan Vinicius Dall Alba', 'cargo': 'Corretor de saúde',
           'telefone': '(41) 99547-6715', 'whatsapp': '5541995476715',
           'email': 'alan.vinicius@mazzabroker.com.br'}


def carregar(caminho=None):
    caminho = caminho or os.path.join(_AQUI, 'corretor.json')
    dados = dict(_PADRAO)
    if os.path.exists(caminho):
        lido = json.load(open(caminho, encoding='utf-8'))
        dados.update({k: v for k, v in lido.items()
                      if k in _PADRAO and isinstance(v, str) and v.strip()})
    dados['corretora'] = CORRETORA
    return dados


C = carregar()
NOME = C['nome']
CARGO = C['cargo']
TEL = C['telefone']
WHATS = C['whatsapp']
MAIL = C['email']
