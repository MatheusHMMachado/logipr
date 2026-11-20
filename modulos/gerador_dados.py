"""Geração da base de dados do LogiPR.

- CIDADES: dado REAL (IBGE – nome, código, latitude, longitude), filtrado para o PR.
- ROTAS:   derivadas do dado real. Cada cidade é ligada às k cidades mais
           próximas; distância = Haversine × fator rodoviário (≈1,3, razão média
           entre distância por estrada e em linha reta).
- PEDIDOS: SIMULADOS com regras de negócio + aleatoriedade (semente fixa →
           reprodutível). Não há base pública com o desfecho "no prazo/atrasado".
"""
import math
import random

from modulos.dijkstra import dijkstra
from modulos.grafo import Grafo, haversine_km
from modulos.merge_sort import merge_sort

CENTROS_DISTRIBUICAO = ["Curitiba", "Ponta Grossa", "Londrina", "Maringá", "Cascavel"]

FATOR_RODOVIARIO = 1.3

ATRIBUTOS_ID3 = ["faixa_distancia", "faixa_peso", "veiculo", "turno_saida", "clima", "prioridade"]
ALVO_ID3 = "status_entrega"

CAMPOS_PEDIDO = ["id_pedido", "cd_origem", "cidade_destino", "distancia_km", "faixa_distancia",
                 "peso_kg", "faixa_peso", "veiculo", "turno_saida", "clima", "prioridade",
                 "valor_frete", "prazo_dias", "status_entrega"]


# ------------------------------------------------------------------ rotas
def gerar_rotas(cidades, k=3):
    """cidades: lista de dicts com nome, latitude, longitude."""
    pares = set()
    rotas = []

    def ligar(a, b):
        chave = (a["nome"], b["nome"]) if a["nome"] < b["nome"] else (b["nome"], a["nome"])
        if chave in pares:
            return
        pares.add(chave)
        km = haversine_km(a["latitude"], a["longitude"], b["latitude"], b["longitude"])
        rotas.append({"origem": chave[0], "destino": chave[1],
                      "distancia_km": round(km * FATOR_RODOVIARIO, 1)})

    for c in cidades:
        dists = [(haversine_km(c["latitude"], c["longitude"], o["latitude"], o["longitude"]), o)
                 for o in cidades if o is not c]
        dists, _ = merge_sort(dists, chave=lambda t: t[0])
        for _, o in dists[:k]:
            ligar(c, o)

    # garante grafo conexo: une componentes pelo par de cidades mais próximo
    while True:
        comps = _componentes(cidades, rotas)
        if len(comps) == 1:
            break
        a_comp, melhor = comps[0], None
        for c in cidades:
            if c["nome"] not in a_comp:
                continue
            for o in cidades:
                if o["nome"] in a_comp:
                    continue
                d = haversine_km(c["latitude"], c["longitude"], o["latitude"], o["longitude"])
                if melhor is None or d < melhor[0]:
                    melhor = (d, c, o)
        ligar(melhor[1], melhor[2])
    return rotas


def _componentes(cidades, rotas):
    g = Grafo.de_rotas([c["nome"] for c in cidades], rotas)
    vistos, comps = set(), []
    for v in g.adj:
        if v in vistos:
            continue
        comp, pilha = set(), [v]
        while pilha:
            u = pilha.pop()
            if u in comp:
                continue
            comp.add(u)
            pilha.extend(w for w, _ in g.vizinhos(u) if w not in comp)
        vistos |= comp
        comps.append(comp)
    return comps


# ------------------------------------------------------------------ pedidos
def faixa_distancia(km):
    return "Curta" if km <= 250 else ("Média" if km <= 500 else "Longa")


def faixa_peso(kg):
    return "Leve" if kg <= 30 else ("Médio" if kg <= 300 else "Pesado")


def _escolher(rng, opcoes):
    """opcoes: lista de (valor, probabilidade)."""
    x, acum = rng.random(), 0.0
    for valor, p in opcoes:
        acum += p
        if x < acum:
            return valor
    return opcoes[-1][0]


def probabilidade_atraso(fd, fp, veiculo, turno, clima, prioridade):
    """Regra de negócio usada na SIMULAÇÃO (o ID3 não a conhece – precisa descobri-la)."""
    score = {"Curta": 0.0, "Média": 1.0, "Longa": 2.0}[fd]
    score += 1.6 if clima == "Chuvoso" else 0.0
    score += {"Manhã": 0.0, "Tarde": 0.4, "Noite": 1.0}[turno]
    score += 1.4 if (veiculo == "Moto" and fd != "Curta") else 0.0
    score += 1.0 if (fp == "Pesado" and veiculo != "Caminhão") else 0.0
    score += 0.8 if prioridade == "Expressa" else 0.0
    return 1 / (1 + math.exp(-1.7 * (score - 2.7)))


def gerar_pedidos(n, grafo, seed=42, inicio_id=1):
    rng = random.Random(seed)
    dist_cd = {cd: dijkstra(grafo, cd)["dist"] for cd in CENTROS_DISTRIBUICAO}
    destinos = [v for v in grafo.vertices()]
    pedidos = []
    for i in range(n):
        cd = CENTROS_DISTRIBUICAO[rng.randrange(len(CENTROS_DISTRIBUICAO))]
        destino = cd
        while destino == cd:
            destino = destinos[rng.randrange(len(destinos))]
        km = round(dist_cd[cd][destino], 1)

        fp = _escolher(rng, [("Leve", 0.45), ("Médio", 0.35), ("Pesado", 0.20)])
        peso = {"Leve": rng.uniform(0.5, 30), "Médio": rng.uniform(30.1, 300),
                "Pesado": rng.uniform(300.1, 1500)}[fp]
        veiculo = _escolher(rng, {
            "Leve": [("Moto", 0.5), ("Van", 0.4), ("Caminhão", 0.1)],
            "Médio": [("Moto", 0.1), ("Van", 0.6), ("Caminhão", 0.3)],
            "Pesado": [("Van", 0.2), ("Caminhão", 0.8)],
        }[fp])
        turno = _escolher(rng, [("Manhã", 0.45), ("Tarde", 0.35), ("Noite", 0.20)])
        clima = _escolher(rng, [("Bom", 0.7), ("Chuvoso", 0.3)])
        prioridade = _escolher(rng, [("Normal", 0.7), ("Expressa", 0.3)])
        fd = faixa_distancia(km)

        p = probabilidade_atraso(fd, fp, veiculo, turno, clima, prioridade)
        status = "Atrasado" if rng.random() < p else "No prazo"
        prazo = max(1, math.ceil(km / 250) + 1 - (1 if prioridade == "Expressa" else 0))
        frete = 15 + km * 0.9 * (1 + peso / 500) * (1.5 if prioridade == "Expressa" else 1.0)

        pedidos.append({
            "id_pedido": f"P{inicio_id + i:05d}", "cd_origem": cd, "cidade_destino": destino,
            "distancia_km": km, "faixa_distancia": fd, "peso_kg": round(peso, 2),
            "faixa_peso": fp, "veiculo": veiculo, "turno_saida": turno, "clima": clima,
            "prioridade": prioridade, "valor_frete": round(frete, 2), "prazo_dias": prazo,
            "status_entrega": status,
        })
    return pedidos


def completar_pedido(pedido, grafo):
    """Calcula distância (Dijkstra), faixas e prazo de um pedido cadastrado manualmente."""
    res = dijkstra(grafo, pedido["cd_origem"], pedido["cidade_destino"])
    km = round(res["custo"], 1) if res["custo"] is not None else 0.0
    pedido["distancia_km"] = km
    pedido["faixa_distancia"] = faixa_distancia(km)
    pedido["faixa_peso"] = faixa_peso(float(pedido["peso_kg"]))
    pedido.setdefault("prazo_dias",
                      max(1, math.ceil(km / 250) + 1 - (1 if pedido["prioridade"] == "Expressa" else 0)))
    if not pedido.get("valor_frete"):
        pedido["valor_frete"] = round(15 + km * 0.9 * (1 + float(pedido["peso_kg"]) / 500) *
                                      (1.5 if pedido["prioridade"] == "Expressa" else 1.0), 2)
    return pedido
