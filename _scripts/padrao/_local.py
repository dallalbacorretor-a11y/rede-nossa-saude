# -*- coding: utf-8 -*-
"""Caminhos fixos, para os scripts rodarem de qualquer diretorio.

Mesmo arranjo dos outros estudos: importar isto antes de abrir qualquer
arquivo. RAIZ e onde o index.html e gravado.
"""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, 'saida')
DADOS = os.path.join(AQUI, 'dados')
BASE = os.path.join(AQUI, 'base')
os.chdir(AQUI)
os.makedirs(DADOS, exist_ok=True)
os.makedirs(RAIZ, exist_ok=True)
