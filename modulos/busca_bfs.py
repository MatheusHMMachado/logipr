"""Busca em Largura (BFS) – explora o grafo NÍVEL POR NÍVEL usando uma FILA (FIFO).

- Ignora os pesos: encontra o caminho com MENOR NÚMERO DE ARESTAS (trechos).
- Tempo: O(V + E) · Espaço: O(V) (fila + visitados + pais).
"""
from collections import deque  # estrutura de fila; a lógica da busca é nossa

from modulos.grafo import reconstruir_caminho


def bfs(grafo, origem, destino=None):
    """Retorna dict com ordem de visita, nível de cada vértice, caminho e contadores.

    Se `destino` for informado, a busca para assim que ele é DESCOBERTO
    (teste de objetivo na geração do nó).
    """
    visitados = {origem}
    nivel = {origem: 0}
    pai = {}
    fila = deque([origem])
    ordem = []
    ops = {"vertices_expandidos": 0, "arestas_examinadas": 0, "operacoes_fila": 1,
           "tamanho_max_fronteira": 1}
    encontrado = destino == origem

    while fila and not encontrado:
        atual = fila.popleft()
        ops["operacoes_fila"] += 1
        ordem.append(atual)
        ops["vertices_expandidos"] += 1
        for viz, _peso in grafo.vizinhos(atual):
            ops["arestas_examinadas"] += 1
            if viz in visitados:
                continue
            visitados.add(viz)
            nivel[viz] = nivel[atual] + 1
            pai[viz] = atual
            fila.append(viz)
            ops["operacoes_fila"] += 1
            if viz == destino:
                ordem.append(viz)
                encontrado = True
                break
        ops["tamanho_max_fronteira"] = max(ops["tamanho_max_fronteira"], len(fila))

    caminho = reconstruir_caminho(pai, origem, destino) if destino and encontrado else []
    return {
        "algoritmo": "BFS",
        "ordem_visita": ordem,
        "nivel": nivel,
        "pai": pai,
        "caminho": caminho,
        "custo": grafo.custo_caminho(caminho) if caminho else None,
        "operacoes": ops,
    }


def niveis(resultado_bfs):
    """Agrupa os vértices por nível: {0: [origem], 1: [...], ...}."""
    grupos = {}
    for v, n in resultado_bfs["nivel"].items():
        grupos.setdefault(n, []).append(v)
    return grupos
