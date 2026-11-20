"""Experimento obrigatório do Módulo 4 – comparação Heap × Quick × Merge Sort.

Mesmos dados para todos os algoritmos · tamanhos 100 a 10.000 · cenários
aleatório / já ordenado / ordem inversa · mede tempo, comparações,
trocas/movimentações e pico de memória (tracemalloc).
"""
import time
import tracemalloc

from modulos.heap_sort import heap_sort
from modulos.merge_sort import merge_sort
from modulos.quick_sort import quick_sort

TAMANHOS = [100, 500, 1000, 5000, 10000]
CENARIOS = ["Aleatório", "Ordenado", "Inverso"]

ALGORITMOS = {
    "Heap Sort": lambda d, k: heap_sort(d, chave=k),
    "Quick Sort (mediana de 3)": lambda d, k: quick_sort(d, chave=k, pivo="mediana3"),
    "Quick Sort (pivô último)": lambda d, k: quick_sort(d, chave=k, pivo="ultimo"),
    "Merge Sort": lambda d, k: merge_sort(d, chave=k),
}


def preparar_cenario(dados, cenario, chave):
    if cenario == "Aleatório":
        return list(dados)
    ordenado, _ = merge_sort(dados, chave=chave)
    return ordenado if cenario == "Ordenado" else ordenado[::-1]


def esta_ordenado(lista, chave):
    return all(chave(lista[i]) <= chave(lista[i + 1]) for i in range(len(lista) - 1))


def medir(nome, dados, chave, medir_memoria=True):
    fn = ALGORITMOS[nome]
    t0 = time.perf_counter()
    saida, est = fn(dados, chave)
    tempo = time.perf_counter() - t0
    if not esta_ordenado(saida, chave):
        raise AssertionError(f"{nome} não ordenou corretamente")
    pico = None
    if medir_memoria:  # passada separada para o tracemalloc não distorcer o tempo
        tracemalloc.start()
        fn(dados, chave)
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    return {
        "algoritmo": nome,
        "tempo_s": tempo,
        "comparacoes": est.get("comparacoes", 0),
        "trocas_movimentacoes": est.get("trocas", est.get("movimentacoes", 0)),
        "memoria_pico_kb": round(pico / 1024, 1) if pico is not None else None,
        "profundidade_max": est.get("profundidade_max"),
    }


def executar(pedidos, chave_campo="valor_frete", tamanhos=TAMANHOS, cenarios=CENARIOS,
             algoritmos=None, medir_memoria=True, progresso=None):
    """pedidos: lista com pelo menos max(tamanhos) registros."""
    chave = lambda p: p[chave_campo]  # noqa: E731
    algoritmos = algoritmos or list(ALGORITMOS)
    resultados = []
    total = len(tamanhos) * len(cenarios) * len(algoritmos)
    feito = 0
    for n in tamanhos:
        base = pedidos[:n]
        for cen in cenarios:
            dados = preparar_cenario(base, cen, chave)
            for alg in algoritmos:
                r = medir(alg, dados, chave, medir_memoria)
                r.update({"n": n, "cenario": cen, "chave": chave_campo})
                resultados.append(r)
                feito += 1
                if progresso:
                    progresso(feito / total, f"{alg} · n={n} · {cen}")
    return resultados
