"""Merge Sort – divisão e conquista.

Tempo:  O(n log n) em todos os casos (o vetor é sempre dividido ao meio).
Espaço: O(n) – vetor auxiliar usado na intercalação.
Estável: sim (em empate, mantém a ordem original).
"""


def merge_sort(dados, chave=lambda x: x):
    """Retorna (lista_ordenada, estatisticas). Não altera a lista original."""
    a = list(dados)
    aux = [None] * len(a)
    est = {"comparacoes": 0, "movimentacoes": 0}
    _merge_sort(a, aux, 0, len(a) - 1, chave, est)
    return a, est


def _merge_sort(a, aux, ini, fim, chave, est):
    if ini >= fim:
        return
    meio = (ini + fim) // 2
    _merge_sort(a, aux, ini, meio, chave, est)
    _merge_sort(a, aux, meio + 1, fim, chave, est)
    _intercalar(a, aux, ini, meio, fim, chave, est)


def _intercalar(a, aux, ini, meio, fim, chave, est):
    for k in range(ini, fim + 1):
        aux[k] = a[k]
    i, j = ini, meio + 1
    for k in range(ini, fim + 1):
        if i > meio:
            a[k] = aux[j]
            j += 1
        elif j > fim:
            a[k] = aux[i]
            i += 1
        else:
            est["comparacoes"] += 1
            if chave(aux[j]) < chave(aux[i]):
                a[k] = aux[j]
                j += 1
            else:  # <= mantém estabilidade
                a[k] = aux[i]
                i += 1
        est["movimentacoes"] += 1
