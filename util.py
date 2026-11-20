"""Funções compartilhadas pelas páginas Streamlit (cache, grafo, formatação)."""
import csv
import os

import streamlit as st

from modulos.grafo import Grafo
from modulos.merge_sort import merge_sort
from modulos.repositorio import obter_repositorio

RAIZ = os.path.dirname(os.path.abspath(__file__))
RESULTADOS = os.path.join(RAIZ, "experimentos", "resultados")


def configurar(titulo, icone="🚚"):
    st.set_page_config(page_title=f"LogiPR · {titulo}", page_icon=icone, layout="wide")


@st.cache_resource
def repositorio():
    return obter_repositorio()


@st.cache_data(ttl=300, show_spinner="Carregando dados...")
def listar(tabela):
    return repositorio().listar(tabela)


def limpar_cache():
    listar.clear()
    grafo.clear()


@st.cache_resource
def grafo():
    cidades = [c["nome"] for c in listar("cidades")]
    return Grafo.de_rotas(cidades, listar("rotas"))


def nomes_cidades():
    return grafo().vertices()  # já ordenadas pelo nosso Merge Sort


def coordenadas():
    return {c["nome"]: (c["latitude"], c["longitude"]) for c in listar("cidades")}


def proximo_id(pedidos):
    maior = 0
    for p in pedidos:
        num = p["id_pedido"][1:]
        if num.isdigit():
            maior = max(maior, int(num))
    return f"P{maior + 1:05d}"


def ordenar(lista, chave):
    saida, _ = merge_sort(lista, chave=chave)
    return saida


def ler_resultado(nome):
    caminho = os.path.join(RESULTADOS, nome)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    for linha in linhas:
        for k, v in linha.items():
            if v == "":
                linha[k] = None
                continue
            try:
                linha[k] = float(v) if any(c in v for c in ".e") else int(v)
            except (ValueError, TypeError):
                pass
    return linhas


def rodape_backend():
    st.sidebar.caption(f"Armazenamento: **{repositorio().nome}**")


def fmt_km(v):
    return f"{v:,.1f} km".replace(",", "X").replace(".", ",").replace("X", ".")
