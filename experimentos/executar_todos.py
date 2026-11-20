"""Roda todos os experimentos e salva tabelas (CSV) e gráficos (PNG) em
experimentos/resultados/. Esses arquivos alimentam a página 5 e o relatório.

Uso:  python -m experimentos.executar_todos
"""
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from experimentos import testes_busca, testes_id3, testes_ordenacao  # noqa: E402
from modulos.gerador_dados import gerar_pedidos  # noqa: E402
from modulos.grafo import Grafo  # noqa: E402
from modulos.repositorio import RepositorioCSV  # noqa: E402

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
CORES = {"Heap Sort": "#2a78c4", "Quick Sort (mediana de 3)": "#2a9d5c",
         "Quick Sort (pivô último)": "#d1495b", "Merge Sort": "#e0a000"}


def salvar_csv(nome, linhas):
    with open(os.path.join(PASTA, nome), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)


def graficos_ordenacao(res):
    for metrica, rotulo, arq in (("tempo_s", "Tempo (s)", "ordenacao_tempo.png"),
                                 ("comparacoes", "Comparações", "ordenacao_comparacoes.png")):
        fig, eixos = plt.subplots(1, 3, figsize=(15, 4.5), sharey=False)
        for ax, cen in zip(eixos, testes_ordenacao.CENARIOS):
            for alg in testes_ordenacao.ALGORITMOS:
                pts = [(r["n"], r[metrica]) for r in res if r["algoritmo"] == alg and r["cenario"] == cen]
                ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", label=alg,
                        color=CORES[alg])
            ax.set_title(f"Dados: {cen}")
            ax.set_xlabel("n (registros)")
            ax.set_ylabel(rotulo)
            ax.set_yscale("log")
            ax.grid(alpha=0.3)
        eixos[0].legend(fontsize=8)
        fig.suptitle(f"{rotulo} × tamanho da entrada (escala log)")
        fig.tight_layout()
        fig.savefig(os.path.join(PASTA, arq), dpi=120)
        plt.close(fig)


def main():
    os.makedirs(PASTA, exist_ok=True)
    repo = RepositorioCSV()
    cidades = [c["nome"] for c in repo.listar("cidades")]
    grafo = Grafo.de_rotas(cidades, repo.listar("rotas"))

    t = time.perf_counter()
    print("1/3 Ordenação ...")
    pedidos = gerar_pedidos(max(testes_ordenacao.TAMANHOS), grafo, seed=7)
    res_ord = testes_ordenacao.executar(
        pedidos, progresso=lambda p, m: print(f"   {p:5.0%} {m}", flush=True))
    salvar_csv("ordenacao.csv", res_ord)
    graficos_ordenacao(res_ord)

    print("2/3 Buscas ...")
    linhas = testes_busca.executar(grafo)
    salvar_csv("busca_detalhado.csv", linhas)
    salvar_csv("busca_resumo.csv", testes_busca.resumo(linhas))

    print("3/3 ID3 ...")
    treino = gerar_pedidos(max(testes_id3.TAMANHOS_TREINO), grafo, seed=11)
    teste = gerar_pedidos(500, grafo, seed=99, inicio_id=900000)
    salvar_csv("id3_volume.csv", testes_id3.executar(treino, teste))
    print(f"Concluído em {time.perf_counter() - t:.1f}s → {PASTA}")


if __name__ == "__main__":
    main()
