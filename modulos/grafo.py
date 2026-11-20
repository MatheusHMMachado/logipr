"""Grafo não direcionado e ponderado representado por LISTA DE ADJACÊNCIA.

    adj = {
        "Curitiba":     [("Lapa", 72), ("Ponta Grossa", 118), ...],
        "Ponta Grossa": [("Castro", 45), ("Curitiba", 118), ...],
        ...
    }

Espaço: O(V + E). Vizinhos mantidos em ordem alfabética (ordenados com o
nosso próprio Merge Sort), o que torna BFS e DFS determinísticas.
"""
import math

from modulos.merge_sort import merge_sort


class Grafo:
    def __init__(self):
        self.adj = {}

    # ------------------------------------------------------------------ montagem
    def adicionar_vertice(self, v):
        if v not in self.adj:
            self.adj[v] = []

    def adicionar_aresta(self, a, b, peso):
        if peso < 0:
            raise ValueError("Dijkstra exige pesos não negativos")
        self.adicionar_vertice(a)
        self.adicionar_vertice(b)
        if not self.tem_aresta(a, b):
            self.adj[a].append((b, peso))
            self.adj[b].append((a, peso))

    def tem_aresta(self, a, b):
        return any(v == b for v, _ in self.adj.get(a, []))

    def ordenar_vizinhos(self):
        for v in self.adj:
            self.adj[v], _ = merge_sort(self.adj[v], chave=lambda t: t[0])

    @classmethod
    def de_rotas(cls, cidades, rotas):
        """cidades: lista de nomes · rotas: lista de dicts origem/destino/distancia_km."""
        g = cls()
        for c in cidades:
            g.adicionar_vertice(c)
        for r in rotas:
            g.adicionar_aresta(r["origem"], r["destino"], float(r["distancia_km"]))
        g.ordenar_vizinhos()
        return g

    # ------------------------------------------------------------------ consultas
    def vizinhos(self, v):
        return self.adj[v]

    def vertices(self):
        lista, _ = merge_sort(list(self.adj.keys()))
        return lista

    def peso(self, a, b):
        for v, p in self.adj[a]:
            if v == b:
                return p
        return math.inf

    def num_vertices(self):
        return len(self.adj)

    def num_arestas(self):
        return sum(len(v) for v in self.adj.values()) // 2

    def custo_caminho(self, caminho):
        return sum(self.peso(caminho[i], caminho[i + 1]) for i in range(len(caminho) - 1))


def reconstruir_caminho(pai, origem, destino):
    """Segue os ponteiros de pai do destino até a origem."""
    if destino not in pai and destino != origem:
        return []
    caminho = [destino]
    while caminho[-1] != origem:
        caminho.append(pai[caminho[-1]])
    caminho.reverse()
    return caminho


def haversine_km(lat1, lon1, lat2, lon2):
    """Distância em linha reta (km) entre duas coordenadas geográficas."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))
