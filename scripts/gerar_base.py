"""Gera os CSVs de seed em dados/ a partir do CSV público de municípios (IBGE).

Uso:
    python scripts/gerar_base.py caminho/para/municipios.csv [qtd_pedidos]

Fonte das cidades: https://github.com/kelvins/municipios-brasileiros (csv/municipios.csv),
dataset aberto derivado do IBGE (codigo_ibge, nome, latitude, longitude, codigo_uf...).
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modulos.gerador_dados import CAMPOS_PEDIDO, CENTROS_DISTRIBUICAO, gerar_pedidos, gerar_rotas  # noqa: E402
from modulos.grafo import Grafo  # noqa: E402

CODIGO_UF_PR = "41"

CIDADES_PR = [
    "Curitiba", "Ponta Grossa", "Londrina", "Maringá", "Cascavel", "Foz do Iguaçu",
    "Guarapuava", "Paranaguá", "São José dos Pinhais", "Colombo", "Apucarana", "Arapongas",
    "Toledo", "Campo Mourão", "Umuarama", "Pato Branco", "Francisco Beltrão", "Cianorte",
    "Paranavaí", "Telêmaco Borba", "Castro", "União da Vitória", "Irati", "Cornélio Procópio",
    "Jacarezinho", "Santo Antônio da Platina", "Prudentópolis", "Palmas", "Lapa", "Rio Negro",
    "Laranjeiras do Sul", "Medianeira", "Marechal Cândido Rondon", "Ivaiporã", "Jandaia do Sul",
    "Mandaguari", "Rolândia", "Cambé", "Ibiporã", "Bandeirantes", "Wenceslau Braz", "Pitanga",
    "Goioerê", "Assis Chateaubriand", "Palotina", "Dois Vizinhos", "Guaratuba", "Matinhos",
    "Antonina", "Morretes",
]

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")


def ler_cidades(caminho_ibge):
    escolhidas = {}
    with open(caminho_ibge, encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            if linha["codigo_uf"] == CODIGO_UF_PR and linha["nome"] in CIDADES_PR:
                escolhidas[linha["nome"]] = {
                    "codigo_ibge": int(linha["codigo_ibge"]), "nome": linha["nome"],
                    "latitude": float(linha["latitude"]), "longitude": float(linha["longitude"]),
                    "centro_distribuicao": linha["nome"] in CENTROS_DISTRIBUICAO,
                }
    faltando = [c for c in CIDADES_PR if c not in escolhidas]
    if faltando:
        raise SystemExit(f"Cidades não encontradas no CSV: {faltando}")
    return [escolhidas[c] for c in CIDADES_PR]


def salvar(nome, linhas, campos):
    with open(os.path.join(DADOS, nome), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    qtd = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    os.makedirs(DADOS, exist_ok=True)

    cidades = ler_cidades(sys.argv[1])
    rotas = gerar_rotas(cidades, k=5)
    grafo = Grafo.de_rotas([c["nome"] for c in cidades], rotas)
    pedidos = gerar_pedidos(qtd, grafo, seed=2026)

    salvar("cidades.csv", cidades,
           ["codigo_ibge", "nome", "latitude", "longitude", "centro_distribuicao"])
    salvar("rotas.csv", rotas, ["origem", "destino", "distancia_km"])
    salvar("pedidos.csv", pedidos, CAMPOS_PEDIDO)

    atrasados = sum(p["status_entrega"] == "Atrasado" for p in pedidos)
    print(f"cidades: {len(cidades)} | rotas: {len(rotas)} | pedidos: {len(pedidos)} "
          f"(atrasados: {atrasados}, no prazo: {len(pedidos) - atrasados})")


if __name__ == "__main__":
    main()
