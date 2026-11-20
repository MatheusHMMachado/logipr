"""Quick Sort – divisão e conquista com particionamento (esquema de Lomuto).

Tempo:  O(n log n) no melhor caso e no caso médio; O(n²) no pior caso
        (partições muito desiguais, ex.: pivô = último elemento com dados
        já ordenados ou em ordem inversa).
Espaço: O(log n) de pilha no caso médio; O(n) no pior caso.
Estável: não.

Estratégias de pivô:
  - "ultimo":   pivô fixo no último elemento (versão clássica, expõe o pior caso)
  - "mediana3": mediana entre primeiro, meio e último (evita o pior caso com
                dados ordenados/invertidos)

A recursão foi substituída por uma pilha explícita, porque no pior caso a
profundidade chegaria a n (10.000) e estouraria o limite de recursão do
Python. A lógica continua sendo exatamente a do Quick Sort recursivo.
"""


def quick_sort(dados, chave=lambda x: x, pivo="mediana3"):
    a = list(dados)
    est = {"comparacoes": 0, "trocas": 0, "profundidade_max": 0}
    pilha = [(0, len(a) - 1, 1)]
    while pilha:
        ini, fim, prof = pilha.pop()
        if ini >= fim:
            continue
        if prof > est["profundidade_max"]:
            est["profundidade_max"] = prof
        if pivo == "mediana3":
            _mediana_de_tres(a, ini, fim, chave, est)
        p = _particionar(a, ini, fim, chave, est)
        # empilha a maior partição primeiro → a menor é processada antes
        if p - ini > fim - p:
            pilha.append((ini, p - 1, prof + 1))
            pilha.append((p + 1, fim, prof + 1))
        else:
            pilha.append((p + 1, fim, prof + 1))
            pilha.append((ini, p - 1, prof + 1))
    return a, est


def _trocar(a, i, j, est):
    if i != j:
        a[i], a[j] = a[j], a[i]
        est["trocas"] += 1


def _mediana_de_tres(a, ini, fim, chave, est):
    """Coloca a mediana de (ini, meio, fim) na posição fim (vira o pivô)."""
    meio = (ini + fim) // 2
    est["comparacoes"] += 3
    if chave(a[meio]) < chave(a[ini]):
        _trocar(a, meio, ini, est)
    if chave(a[fim]) < chave(a[ini]):
        _trocar(a, fim, ini, est)
    if chave(a[meio]) < chave(a[fim]):
        _trocar(a, meio, fim, est)


def _particionar(a, ini, fim, chave, est):
    pivo = chave(a[fim])
    i = ini - 1
    for j in range(ini, fim):
        est["comparacoes"] += 1
        if chave(a[j]) <= pivo:
            i += 1
            _trocar(a, i, j, est)
    _trocar(a, i + 1, fim, est)
    return i + 1
