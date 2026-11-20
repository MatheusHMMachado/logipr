"""Busca em Profundidade (DFS) – explora um caminho ATÉ O LIMITE antes de voltar
(backtracking), usando RECURSÃO (pilha implícita).

- Não é ótima: o caminho depende da ordem dos vizinhos.
- Tempo: O(V + E) · Espaço: O(V) (pilha de recursão + visitados).
"""
import sys

from modulos.grafo import reconstruir_caminho

sys.setrecursionlimit(10_000)


def dfs(grafo, origem, destino=None):
    visitados = set()
    pai = {}
    ordem = []
    eventos = []  # ("visita", v, prof) / ("backtrack", v, prof) – usado no passo a passo
    ops = {"vertices_expandidos": 0, "arestas_examinadas": 0, "chamadas_recursivas": 0,
           "profundidade_max": 0, "backtracks": 0}

    def visitar(v, prof):
        ops["chamadas_recursivas"] += 1
        ops["profundidade_max"] = max(ops["profundidade_max"], prof)
        visitados.add(v)
        ordem.append(v)
        eventos.append(("visita", v, prof))
        if v == destino:
            return True
        ops["vertices_expandidos"] += 1
        for viz, _peso in grafo.vizinhos(v):
            ops["arestas_examinadas"] += 1
            if viz not in visitados:
                pai[viz] = v
                if visitar(viz, prof + 1):
                    return True
        ops["backtracks"] += 1
        eventos.append(("backtrack", v, prof))
        return False

    encontrado = visitar(origem, 0)
    caminho = reconstruir_caminho(pai, origem, destino) if destino and encontrado else []
    return {
        "algoritmo": "DFS",
        "ordem_visita": ordem,
        "pai": pai,
        "eventos": eventos,
        "caminho": caminho,
        "custo": grafo.custo_caminho(caminho) if caminho else None,
        "operacoes": ops,
    }
