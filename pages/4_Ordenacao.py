"""Módulo 4 – Ordenação: Heap Sort, Quick Sort e Merge Sort."""
import time

import pandas as pd
import streamlit as st

import util
from experimentos import testes_ordenacao as exp
from modulos.gerador_dados import gerar_pedidos
from modulos.heap_sort import heap_sort
from modulos.merge_sort import merge_sort
from modulos.quick_sort import quick_sort

util.configurar("Ordenação", "📊")
util.rodape_backend()
st.title("📊 Módulo 4 – Ordenação: Heap, Quick e Merge Sort")

CAMPOS = {"valor_frete": "Valor do frete (R$)", "peso_kg": "Peso (kg)", "distancia_km": "Distância (km)",
          "prazo_dias": "Prazo (dias)"}

aba_uso, aba_exp, aba_vivo = st.tabs(["🚚 Ordenar pedidos", "🧪 Resultados do experimento", "▶️ Rodar ao vivo"])

# ------------------------------------------------------------------ uso prático
with aba_uso:
    pedidos = util.listar("pedidos")
    c1, c2, c3 = st.columns(3)
    campo = c1.selectbox("Ordenar por", list(CAMPOS), format_func=CAMPOS.get)
    decrescente = c2.toggle("Decrescente", value=True)
    alg = c3.radio("Algoritmo", ["Heap Sort", "Quick Sort", "Merge Sort"], horizontal=True)
    fn = {"Heap Sort": heap_sort, "Quick Sort": quick_sort, "Merge Sort": merge_sort}[alg]
    chave = (lambda p: -p[campo]) if decrescente else (lambda p: p[campo])
    t0 = time.perf_counter()
    ordenados, est = fn(pedidos, chave=chave)
    dt = (time.perf_counter() - t0) * 1000
    m1, m2, m3 = st.columns(3)
    m1.metric("Tempo", f"{dt:.2f} ms")
    m2.metric("Comparações", f"{est['comparacoes']:,}".replace(",", "."))
    m3.metric("Trocas / movimentações", f"{est.get('trocas', est.get('movimentacoes', 0)):,}".replace(",", "."))
    st.dataframe(pd.DataFrame(ordenados), hide_index=True, width="stretch", height=380)

    st.subheader("Mesma lista, três algoritmos")
    comp = []
    for nome, f in (("Heap Sort", heap_sort), ("Quick Sort", quick_sort), ("Merge Sort", merge_sort)):
        t0 = time.perf_counter()
        _, e = f(pedidos, chave=chave)
        comp.append({"Algoritmo": nome, "Tempo (ms)": round((time.perf_counter() - t0) * 1000, 3),
                     "Comparações": e["comparacoes"],
                     "Trocas/movimentações": e.get("trocas", e.get("movimentacoes", 0)),
                     "Estável": "Sim" if nome == "Merge Sort" else "Não",
                     "Memória extra": {"Heap Sort": "O(1)", "Quick Sort": "O(log n)", "Merge Sort": "O(n)"}[nome]})
    st.dataframe(pd.DataFrame(comp), hide_index=True, width="stretch")

# ------------------------------------------------------------------ resultados salvos
def mostrar_resultados(res):
    df = pd.DataFrame(res)
    cen = st.radio("Cenário", exp.CENARIOS, horizontal=True, key=f"cen_{len(res)}")
    sub = df[df["cenario"] == cen]
    metrica = st.radio("Métrica", ["tempo_s", "comparacoes", "trocas_movimentacoes", "memoria_pico_kb"],
                       horizontal=True, key=f"met_{len(res)}",
                       format_func={"tempo_s": "Tempo (s)", "comparacoes": "Comparações",
                                    "trocas_movimentacoes": "Trocas/movimentações",
                                    "memoria_pico_kb": "Memória de pico (KB)"}.get)
    tabela = sub.pivot(index="n", columns="algoritmo", values=metrica)
    st.line_chart(tabela, x_label="n (registros)", y_label=metrica)
    st.dataframe(tabela, width="stretch")
    with st.expander("Tabela completa"):
        st.dataframe(df, hide_index=True, width="stretch")


with aba_exp:
    st.markdown("Mesmos dados para todos os algoritmos · **100, 500, 1.000, 5.000 e 10.000** pedidos · "
                "chave: valor do frete · cenários aleatório, ordenado e inverso.")
    res = util.ler_resultado("ordenacao.csv")
    if res:
        mostrar_resultados(res)
        for img in ("ordenacao_tempo.png", "ordenacao_comparacoes.png"):
            caminho = f"{util.RESULTADOS}/{img}"
            try:
                st.image(caminho, width="stretch")
            except Exception:  # noqa: BLE001
                pass
    else:
        st.warning("Resultados ainda não gerados. Execute `python -m experimentos.executar_todos`.")

# ------------------------------------------------------------------ ao vivo
with aba_vivo:
    st.markdown("Roda o experimento agora, no servidor. O **Quick Sort com pivô no último elemento** é O(n²) em "
                "dados ordenados/inversos – com 10.000 registros pode levar dezenas de segundos.")
    tamanhos = st.multiselect("Tamanhos", exp.TAMANHOS, default=[100, 500, 1000])
    algs = st.multiselect("Algoritmos", list(exp.ALGORITMOS), default=list(exp.ALGORITMOS))
    campo_v = st.selectbox("Chave", list(CAMPOS), format_func=CAMPOS.get, key="campo_vivo")
    if st.button("Executar experimento", type="primary") and tamanhos and algs:
        tamanhos = util.ordenar(tamanhos, chave=lambda x: x)
        barra = st.progress(0.0)
        dados = gerar_pedidos(max(tamanhos), util.grafo(), seed=int(time.time()) % 10000)
        res_vivo = exp.executar(dados, campo_v, tamanhos, exp.CENARIOS, algs, medir_memoria=True,
                                progresso=lambda p, m: barra.progress(p, text=m))
        st.session_state["res_vivo"] = res_vivo
    if "res_vivo" in st.session_state:
        mostrar_resultados(st.session_state["res_vivo"])
