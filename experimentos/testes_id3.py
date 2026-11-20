"""Experimento do Módulo 2/5 – efeito do VOLUME de dados sobre Entropia,
Ganho de Informação e qualidade da árvore ID3.

Treina com tamanhos crescentes e testa sempre no mesmo conjunto de teste
(registros nunca usados no treino).
"""
import time

from modulos.classificacao_id3 import ID3
from modulos.entropia import entropia, ganho_informacao
from modulos.gerador_dados import ALVO_ID3, ATRIBUTOS_ID3

TAMANHOS_TREINO = [20, 50, 100, 200, 400, 800, 1600, 3200]


def executar(pedidos_treino, pedidos_teste, tamanhos=TAMANHOS_TREINO,
             min_registros=5, profundidade_max=4):
    linhas = []
    for n in tamanhos:
        treino = pedidos_treino[:n]
        t0 = time.perf_counter()
        modelo = ID3(min_registros=min_registros, profundidade_max=profundidade_max)
        modelo.treinar(treino, ATRIBUTOS_ID3, ALVO_ID3)
        tempo = time.perf_counter() - t0
        aval_teste = modelo.avaliar(pedidos_teste)
        aval_treino = modelo.avaliar(treino)
        est = modelo.estatisticas()
        linha = {
            "n_treino": n,
            "entropia_raiz": round(entropia([r[ALVO_ID3] for r in treino]), 4),
            "atributo_raiz": modelo.raiz.atributo,
            "acuracia_treino": round(aval_treino["acuracia"], 4),
            "acuracia_teste": round(aval_teste["acuracia"], 4),
            "nos": est["nos"], "folhas": est["folhas"], "profundidade": est["profundidade"],
            "calculos_entropia": est["calculos_entropia"],
            "tempo_treino_ms": round(tempo * 1000, 2),
        }
        for a in ATRIBUTOS_ID3:
            linha[f"ganho_{a}"] = round(ganho_informacao(treino, a, ALVO_ID3)[0], 4)
        linhas.append(linha)
    return linhas
