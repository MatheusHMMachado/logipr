"""Testes automatizados dos algoritmos (pytest).

Valida cada implementação contra resultados conhecidos – inclusive o mapa da
Romênia (Arad → Bucharest), cujos resultados clássicos estão em Russell & Norvig.
"""
import math
import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modulos.busca_bfs import bfs, niveis  # noqa: E402
from modulos.busca_dfs import dfs  # noqa: E402
from modulos.classificacao_id3 import ID3  # noqa: E402
from modulos.dijkstra import HeapMinimo, dijkstra  # noqa: E402
from modulos.entropia import entropia, ganho_informacao  # noqa: E402
from modulos.grafo import Grafo  # noqa: E402
from modulos.heap_sort import heap_sort  # noqa: E402
from modulos.merge_sort import merge_sort  # noqa: E402
from modulos.quick_sort import quick_sort  # noqa: E402
from modulos.repositorio import RepositorioCSV  # noqa: E402

# ----------------------------------------------------------------- ordenação
ORDENADORES = [
    ("heap", lambda d, k=lambda x: x: heap_sort(d, k)),
    ("merge", lambda d, k=lambda x: x: merge_sort(d, k)),
    ("quick_m3", lambda d, k=lambda x: x: quick_sort(d, k, "mediana3")),
    ("quick_ultimo", lambda d, k=lambda x: x: quick_sort(d, k, "ultimo")),
]

CASOS = [[], [1], [2, 1], [5, 5, 5], [3, -1, 2, 0, -1], list(range(50)), list(range(50, 0, -1))]


@pytest.mark.parametrize("nome,fn", ORDENADORES)
@pytest.mark.parametrize("dados", CASOS)
def test_ordena_casos_limite(nome, fn, dados):
    saida, _ = fn(dados)
    esperado = list(dados)
    esperado.sort()  # referência APENAS no teste – nunca no sistema
    assert saida == esperado


@pytest.mark.parametrize("nome,fn", ORDENADORES)
def test_ordena_aleatorio_e_nao_altera_entrada(nome, fn):
    rng = random.Random(1)
    dados = [rng.randint(-1000, 1000) for _ in range(2000)]
    copia = list(dados)
    saida, est = fn(dados)
    assert saida == sorted(copia)
    assert dados == copia
    assert est["comparacoes"] > 0


def test_merge_sort_estavel():
    dados = [("b", 1), ("a", 2), ("c", 1), ("d", 2)]
    saida, _ = merge_sort(dados, chave=lambda t: t[1])
    assert saida == [("b", 1), ("c", 1), ("a", 2), ("d", 2)]


def test_quick_pivo_ultimo_degrada_em_dados_ordenados():
    n = 500
    _, est_ord = quick_sort(list(range(n)), pivo="ultimo")
    _, est_m3 = quick_sort(list(range(n)), pivo="mediana3")
    assert est_ord["comparacoes"] == n * (n - 1) // 2  # O(n²) exato
    assert est_m3["comparacoes"] < est_ord["comparacoes"] / 10


# ----------------------------------------------------------------- grafos
@pytest.fixture
def romenia():
    arestas = [("Arad", "Zerind", 75), ("Arad", "Sibiu", 140), ("Arad", "Timisoara", 118),
               ("Zerind", "Oradea", 71), ("Oradea", "Sibiu", 151), ("Timisoara", "Lugoj", 111),
               ("Lugoj", "Mehadia", 70), ("Mehadia", "Dobreta", 75), ("Dobreta", "Craiova", 120),
               ("Craiova", "Rimnicu Vilcea", 146), ("Craiova", "Pitesti", 138),
               ("Sibiu", "Fagaras", 99), ("Sibiu", "Rimnicu Vilcea", 80),
               ("Rimnicu Vilcea", "Pitesti", 97), ("Fagaras", "Bucharest", 211),
               ("Pitesti", "Bucharest", 101), ("Bucharest", "Giurgiu", 90),
               ("Bucharest", "Urziceni", 85), ("Urziceni", "Hirsova", 98),
               ("Hirsova", "Eforie", 86), ("Urziceni", "Vaslui", 142), ("Vaslui", "Iasi", 92),
               ("Iasi", "Neamt", 87)]
    g = Grafo()
    for a, b, p in arestas:
        g.adicionar_aresta(a, b, p)
    g.ordenar_vizinhos()
    return g


def test_dijkstra_romenia_418(romenia):
    r = dijkstra(romenia, "Arad", "Bucharest")
    assert r["custo"] == 418
    assert r["caminho"] == ["Arad", "Sibiu", "Rimnicu Vilcea", "Pitesti", "Bucharest"]


def test_bfs_romenia_menos_trechos(romenia):
    r = bfs(romenia, "Arad", "Bucharest")
    assert r["caminho"] == ["Arad", "Sibiu", "Fagaras", "Bucharest"]
    assert r["custo"] == 450


def test_bfs_niveis(romenia):
    r = bfs(romenia, "Arad")
    assert niveis(r)[1] == ["Sibiu", "Timisoara", "Zerind"]
    assert len(r["ordem_visita"]) == 20


def test_dfs_romenia(romenia):
    r = dfs(romenia, "Arad", "Bucharest")
    assert r["caminho"][0] == "Arad" and r["caminho"][-1] == "Bucharest"
    assert len(dfs(romenia, "Arad")["ordem_visita"]) == 20  # visita todos


def test_dijkstra_nunca_pior_que_bfs_dfs(romenia):
    for destino in romenia.vertices():
        d = dijkstra(romenia, "Arad", destino)["dist"][destino]
        if destino == "Arad":
            continue
        assert d <= bfs(romenia, "Arad", destino)["custo"] + 1e-9
        assert d <= dfs(romenia, "Arad", destino)["custo"] + 1e-9


def test_peso_negativo_rejeitado():
    with pytest.raises(ValueError):
        Grafo().adicionar_aresta("A", "B", -1)


def test_heap_minimo():
    h = HeapMinimo()
    for p in [5, 3, 8, 1, 9, 2]:
        h.inserir(p, str(p))
    assert [h.remover_min()[0] for _ in range(6)] == [1, 2, 3, 5, 8, 9]


# ----------------------------------------------------------------- entropia / ID3
def test_entropia_valores_classicos():
    assert entropia(["s"] * 10) == 0
    assert entropia(["s", "n"]) == 1
    assert math.isclose(entropia(["s"] * 9 + ["n"] * 5), 0.9403, abs_tol=1e-4)


JOGAR_TENIS = [  # base clássica de Quinlan (Mitchell, 1997)
    ("Ensolarado", "Quente", "Alta", "Fraco", "Não"), ("Ensolarado", "Quente", "Alta", "Forte", "Não"),
    ("Nublado", "Quente", "Alta", "Fraco", "Sim"), ("Chuvoso", "Amena", "Alta", "Fraco", "Sim"),
    ("Chuvoso", "Fria", "Normal", "Fraco", "Sim"), ("Chuvoso", "Fria", "Normal", "Forte", "Não"),
    ("Nublado", "Fria", "Normal", "Forte", "Sim"), ("Ensolarado", "Amena", "Alta", "Fraco", "Não"),
    ("Ensolarado", "Fria", "Normal", "Fraco", "Sim"), ("Chuvoso", "Amena", "Normal", "Fraco", "Sim"),
    ("Ensolarado", "Amena", "Normal", "Forte", "Sim"), ("Nublado", "Amena", "Alta", "Forte", "Sim"),
    ("Nublado", "Quente", "Normal", "Fraco", "Sim"), ("Chuvoso", "Amena", "Alta", "Forte", "Não"),
]
ATR = ["Tempo", "Temperatura", "Umidade", "Vento"]


def _tenis():
    return [dict(zip(ATR + ["Jogar"], linha)) for linha in JOGAR_TENIS]


def test_ganho_informacao_jogar_tenis():
    d = _tenis()
    assert math.isclose(ganho_informacao(d, "Tempo", "Jogar")[0], 0.2467, abs_tol=1e-3)
    assert math.isclose(ganho_informacao(d, "Umidade", "Jogar")[0], 0.1518, abs_tol=1e-3)


def test_id3_jogar_tenis():
    m = ID3(min_registros=1).treinar(_tenis(), ATR, "Jogar")
    assert m.raiz.atributo == "Tempo"
    assert m.raiz.filhos["Nublado"].classe == "Sim"
    assert m.raiz.filhos["Ensolarado"].atributo == "Umidade"
    assert m.raiz.filhos["Chuvoso"].atributo == "Vento"
    assert m.avaliar(_tenis())["acuracia"] == 1.0
    assert m.classificar({"Tempo": "Ensolarado", "Temperatura": "Fria", "Umidade": "Normal",
                          "Vento": "Forte"}) == "Sim"


# ----------------------------------------------------------------- base de dados
def test_base_tem_minimo_50_registros_e_grafo_conexo():
    repo = RepositorioCSV()
    pedidos = repo.listar("pedidos")
    cidades = [c["nome"] for c in repo.listar("cidades")]
    assert len(pedidos) >= 50
    g = Grafo.de_rotas(cidades, repo.listar("rotas"))
    assert len(bfs(g, "Curitiba")["ordem_visita"]) == len(cidades)


def test_crud_csv(tmp_path):
    import shutil
    from modulos.repositorio import PASTA_DADOS
    for t in ("cidades", "rotas", "pedidos"):
        shutil.copy(os.path.join(PASTA_DADOS, f"{t}.csv"), tmp_path)
    repo = RepositorioCSV(str(tmp_path))
    n = len(repo.listar("pedidos"))
    novo = dict(repo.listar("pedidos")[0], id_pedido="TESTE1")
    repo.inserir("pedidos", novo)
    assert repo.buscar("pedidos", "TESTE1")["cd_origem"] == novo["cd_origem"]
    repo.atualizar("pedidos", "TESTE1", {"clima": "Chuvoso"})
    assert repo.buscar("pedidos", "TESTE1")["clima"] == "Chuvoso"
    repo.remover("pedidos", "TESTE1")
    assert len(repo.listar("pedidos")) == n
    with pytest.raises(ValueError):
        repo.inserir("pedidos", repo.listar("pedidos")[0])
