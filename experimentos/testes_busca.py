"""Experimento do Módulo 3 – BFS × DFS × Dijkstra sobre o mesmo grafo.

Para cada centro de distribuição e cada cidade de destino, executa os três
algoritmos e compara: nº de trechos, custo em km e operações realizadas.
"""
import time

from modulos.busca_bfs import bfs
from modulos.busca_dfs import dfs
from modulos.dijkstra import dijkstra
from modulos.gerador_dados import CENTROS_DISTRIBUICAO


def executar(grafo, origens=CENTROS_DISTRIBUICAO):
    linhas = []
    for origem in origens:
        for destino in grafo.vertices():
            if destino == origem:
                continue
            for nome, fn in (("BFS", bfs), ("DFS", dfs), ("Dijkstra", dijkstra)):
                t0 = time.perf_counter()
                r = fn(grafo, origem, destino)
                tempo = time.perf_counter() - t0
                ops = r["operacoes"]
                linhas.append({
                    "origem": origem, "destino": destino, "algoritmo": nome,
                    "trechos": len(r["caminho"]) - 1, "custo_km": round(r["custo"], 1),
                    "vertices_visitados": len(r["ordem_visita"]),
                    "arestas_examinadas": ops["arestas_examinadas"],
                    "tempo_ms": tempo * 1000,
                })
    return linhas


def resumo(linhas):
    """Agrega por algoritmo e compara com o ótimo do Dijkstra."""
    otimo = {(l["origem"], l["destino"]): l["custo_km"] for l in linhas if l["algoritmo"] == "Dijkstra"}
    min_trechos = {}
    for l in linhas:
        k = (l["origem"], l["destino"])
        min_trechos[k] = min(min_trechos.get(k, 10 ** 9), l["trechos"])
    agg = {}
    for l in linhas:
        a = agg.setdefault(l["algoritmo"], {"algoritmo": l["algoritmo"], "consultas": 0,
                                            "trechos": 0, "custo": 0.0, "visitados": 0,
                                            "arestas": 0, "tempo": 0.0, "otimo_km": 0,
                                            "min_trechos": 0, "excesso_km": 0.0})
        k = (l["origem"], l["destino"])
        a["consultas"] += 1
        a["trechos"] += l["trechos"]
        a["custo"] += l["custo_km"]
        a["visitados"] += l["vertices_visitados"]
        a["arestas"] += l["arestas_examinadas"]
        a["tempo"] += l["tempo_ms"]
        a["otimo_km"] += abs(l["custo_km"] - otimo[k]) < 0.05
        a["min_trechos"] += l["trechos"] == min_trechos[k]
        a["excesso_km"] += l["custo_km"] - otimo[k]
    saida = []
    for a in agg.values():
        n = a["consultas"]
        saida.append({
            "Algoritmo": a["algoritmo"], "Consultas": n,
            "Trechos (média)": round(a["trechos"] / n, 2),
            "Custo km (média)": round(a["custo"] / n, 1),
            "Excesso vs. ótimo (km, média)": round(a["excesso_km"] / n, 1),
            "% rotas de menor km": round(100 * a["otimo_km"] / n, 1),
            "% rotas com menos trechos": round(100 * a["min_trechos"] / n, 1),
            "Vértices visitados (média)": round(a["visitados"] / n, 1),
            "Arestas examinadas (média)": round(a["arestas"] / n, 1),
            "Tempo (ms, média)": round(a["tempo"] / n, 3),
        })
    return saida
