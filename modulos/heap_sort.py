"""Heap Sort – usa um heap binário MÁXIMO armazenado no próprio vetor.

Filhos de i: 2i+1 e 2i+2 · Pai de i: (i-1)//2

1. Constrói o heap máximo (heapify de baixo para cima)   → O(n)
2. Troca a raiz (maior) com o último da região não ordenada,
   reduz o heap e reaplica o heapify na raiz               → n × O(log n)

Tempo:  O(n log n) em todos os casos.
Espaço: O(1) – ordena no próprio vetor (in-place).
Estável: não.
"""


def heap_sort(dados, chave=lambda x: x):
    a = list(dados)
    n = len(a)
    est = {"comparacoes": 0, "trocas": 0}

    # 1) construção do heap máximo
    for i in range(n // 2 - 1, -1, -1):
        _heapify(a, n, i, chave, est)

    # 2) extrações sucessivas da raiz
    for fim in range(n - 1, 0, -1):
        a[0], a[fim] = a[fim], a[0]
        est["trocas"] += 1
        _heapify(a, fim, 0, chave, est)
    return a, est


def _heapify(a, n, i, chave, est):
    """Desce o elemento da posição i até restaurar a propriedade do heap."""
    while True:
        maior = i
        esq, dir_ = 2 * i + 1, 2 * i + 2
        if esq < n:
            est["comparacoes"] += 1
            if chave(a[esq]) > chave(a[maior]):
                maior = esq
        if dir_ < n:
            est["comparacoes"] += 1
            if chave(a[dir_]) > chave(a[maior]):
                maior = dir_
        if maior == i:
            return
        a[i], a[maior] = a[maior], a[i]
        est["trocas"] += 1
        i = maior
