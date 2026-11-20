"""Entropia e Ganho de Informação (base do ID3).

Entropia(S)        = − Σ p_i · log2(p_i)
Ganho(S, A)        = Entropia(S) − Σ_v (|S_v| / |S|) · Entropia(S_v)

Entropia 0 → conjunto puro (uma só classe); 1 → duas classes meio a meio.
Custo: O(n) para a entropia de n registros; O(n) por atributo para o ganho.
"""
import math


def contar(valores):
    cont = {}
    for v in valores:
        cont[v] = cont.get(v, 0) + 1
    return cont


def entropia(rotulos):
    n = len(rotulos)
    if n == 0:
        return 0.0
    h = 0.0
    for qtd in contar(rotulos).values():
        p = qtd / n
        h -= p * math.log2(p)
    return h


def particionar(registros, atributo):
    grupos = {}
    for r in registros:
        grupos.setdefault(r[atributo], []).append(r)
    return grupos


def ganho_informacao(registros, atributo, alvo):
    """Retorna (ganho, detalhes) – detalhes mostra a conta passo a passo."""
    h_total = entropia([r[alvo] for r in registros])
    n = len(registros)
    detalhes = {"entropia_total": h_total, "particoes": []}
    restante = 0.0
    for valor, subconj in particionar(registros, atributo).items():
        rot = [r[alvo] for r in subconj]
        h = entropia(rot)
        peso = len(subconj) / n
        restante += peso * h
        detalhes["particoes"].append({
            "valor": valor, "qtd": len(subconj), "contagem": contar(rot),
            "entropia": h, "peso": peso, "contribuicao": peso * h,
        })
    detalhes["entropia_media_ponderada"] = restante
    ganho = h_total - restante
    detalhes["ganho"] = ganho
    return ganho, detalhes


def formula_entropia(rotulos):
    """Texto da conta, ex.: −(30/50)·log2(30/50) − (20/50)·log2(20/50) = 0.971"""
    n = len(rotulos)
    termos = [f"({q}/{n})·log2({q}/{n})" for q in contar(rotulos).values()]
    return "−" + " − ".join(termos) + f" = {entropia(rotulos):.4f}"
