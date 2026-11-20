"""Dijkstra – caminho de MENOR CUSTO em grafos com pesos NÃO NEGATIVOS.

Diferente de BFS/DFS (estratégias de exploração), Dijkstra é um algoritmo de
caminhos mínimos: sempre expande o vértice com a menor distância acumulada
conhecida, usando uma fila de prioridade (heap binário mínimo próprio).

Tempo: O((V + E) log V) com heap binário · Espaço: O(V).
"""
import math


class HeapMinimo:
    """Fila de prioridade implementada como heap binário mínimo em vetor."""

    def __init__(self):
        self.v = []
        self.operacoes = 0  # comparações + trocas dentro do heap

    def __len__(self):
        return len(self.v)

    def inserir(self, prioridade, item):
        self.v.append((prioridade, item))
        i = len(self.v) - 1
        while i > 0:
            p = (i - 1) // 2
            self.operacoes += 1
            if self.v[i][0] < self.v[p][0]:
                self.v[i], self.v[p] = self.v[p], self.v[i]
                i = p
            else:
                break

    def remover_min(self):
        topo = self.v[0]
        ultimo = self.v.pop()
        if self.v:
            self.v[0] = ultimo
            i, n = 0, len(self.v)
            while True:
                menor, e, d = i, 2 * i + 1, 2 * i + 2
                if e < n:
                    self.operacoes += 1
                    if self.v[e][0] < self.v[menor][0]:
                        menor = e
                if d < n:
                    self.operacoes += 1
                    if self.v[d][0] < self.v[menor][0]:
                        menor = d
                if menor == i:
                    break
                self.v[i], self.v[menor] = self.v[menor], self.v[i]
                i = menor
        return topo


def dijkstra(grafo, origem, destino=None):
    dist = {v: math.inf for v in grafo.adj}
    dist[origem] = 0.0
    pai = {}
    explorados = set()
    heap = HeapMinimo()
    heap.inserir(0.0, origem)
    ordem = []  # (vértice, distância) na ordem em que foram fixados
    ops = {"vertices_expandidos": 0, "arestas_examinadas": 0, "relaxamentos": 0,
           "insercoes_heap": 1, "remocoes_heap": 0, "entradas_obsoletas": 0}

    while heap:
        d, u = heap.remover_min()
        ops["remocoes_heap"] += 1
        if u in explorados:  # entrada antiga (já havia caminho melhor)
            ops["entradas_obsoletas"] += 1
            continue
        explorados.add(u)
        ordem.append((u, d))
        if u == destino:  # teste na EXPANSÃO → custo mínimo garantido
            break
        ops["vertices_expandidos"] += 1
        for v, w in grafo.vizinhos(u):
            ops["arestas_examinadas"] += 1
            if v in explorados:
                continue
            nd = d + w
            if nd < dist[v]:  # RELAXAMENTO
                dist[v] = nd
                pai[v] = u
                heap.inserir(nd, v)
                ops["relaxamentos"] += 1
                ops["insercoes_heap"] += 1

    ops["operacoes_heap"] = heap.operacoes
    caminho = []
    if destino is not None and dist.get(destino, math.inf) < math.inf:
        caminho = [destino]
        while caminho[-1] != origem:
            caminho.append(pai[caminho[-1]])
        caminho.reverse()
    return {
        "algoritmo": "Dijkstra",
        "ordem_visita": [v for v, _ in ordem],
        "ordem_com_custo": ordem,
        "dist": dist,
        "pai": pai,
        "caminho": caminho,
        "custo": dist.get(destino) if caminho else None,
        "operacoes": ops,
    }
