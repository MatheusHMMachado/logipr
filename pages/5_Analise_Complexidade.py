"""Módulo 5 – Análise de complexidade e relatório experimental.

As respostas às 8 questões são montadas a partir dos CSVs gerados pelos
experimentos (experimentos/resultados), e não apenas da teoria.
"""
import pandas as pd
import streamlit as st

import util

util.configurar("Análise de complexidade", "📈")
util.rodape_backend()
st.title("📈 Módulo 5 – Análise de complexidade")

ord_ = util.ler_resultado("ordenacao.csv")
busca = util.ler_resultado("busca_resumo.csv")
id3 = util.ler_resultado("id3_volume.csv")
if not (ord_ and busca and id3):
    st.warning("Execute `python -m experimentos.executar_todos` para gerar os resultados.")
    st.stop()

df_ord, df_b, df_id3 = pd.DataFrame(ord_), pd.DataFrame(busca).set_index("Algoritmo"), pd.DataFrame(id3)
N = int(df_ord["n"].max())


def linha(alg, cen, n=N):
    return df_ord[(df_ord["algoritmo"] == alg) & (df_ord["cenario"] == cen) & (df_ord["n"] == n)].iloc[0]


def ms(v):
    return f"{v * 1000:,.1f} ms".replace(",", "X").replace(".", ",").replace("X", ".")


def num(v):
    return f"{int(v):,}".replace(",", ".")


# ------------------------------------------------------------------ Big O
st.subheader("Complexidade teórica dos algoritmos implementados")
st.table(pd.DataFrame([
    ["Entropia", "Classificação", "O(n)", "O(n)", "O(n)", "O(c) contagens"],
    ["Ganho de Informação", "Classificação", "O(n)", "O(n)", "O(n)", "O(n) partições"],
    ["ID3 (construção)", "Classificação", "O(a·n)", "O(a²·n)", "O(a²·n)", "O(n) + árvore"],
    ["BFS", "Exploração", "O(V+E)", "O(V+E)", "O(V+E)", "O(V) fila"],
    ["DFS", "Exploração", "O(V+E)", "O(V+E)", "O(V+E)", "O(V) recursão"],
    ["Dijkstra (heap binário)", "Caminho mínimo", "O((V+E) log V)", "O((V+E) log V)", "O((V+E) log V)", "O(V)"],
    ["Heap Sort", "Ordenação", "O(n log n)", "O(n log n)", "O(n log n)", "O(1)"],
    ["Quick Sort", "Ordenação", "O(n log n)", "O(n log n)", "O(n²)", "O(log n) … O(n)"],
    ["Merge Sort", "Ordenação", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)"],
], columns=["Algoritmo", "Tipo", "Melhor caso", "Caso médio", "Pior caso", "Espaço extra"]))
st.caption("n = registros · a = atributos · c = classes · V = vértices · E = arestas")

# ------------------------------------------------------------------ gráficos-resumo
st.subheader(f"Ordenação com n = {num(N)}")
resumo = df_ord[df_ord["n"] == N].pivot(index="algoritmo", columns="cenario", values="tempo_s")
st.bar_chart(resumo, horizontal=True, x_label="Tempo (s)", stack=False)
st.dataframe(resumo.map(ms), width="stretch")

# ------------------------------------------------------------------ 8 questões
st.subheader("Questões de análise (respondidas com os resultados dos experimentos)")

alg_base = ["Heap Sort", "Quick Sort (mediana de 3)", "Merge Sort"]
medias = {a: df_ord[(df_ord["algoritmo"] == a) & (df_ord["n"] == N)]["tempo_s"].mean() for a in alg_base}
vencedor = min(medias, key=medias.get)
qa = {c: linha("Quick Sort (pivô último)", c) for c in ("Aleatório", "Ordenado", "Inverso")}
qm = {c: linha("Quick Sort (mediana de 3)", c) for c in ("Aleatório", "Ordenado", "Inverso")}
mg = {c: linha("Merge Sort", c) for c in ("Aleatório", "Ordenado", "Inverso")}
hp = {c: linha("Heap Sort", c) for c in ("Aleatório", "Ordenado", "Inverso")}
n2 = N * (N - 1) / 2

with st.expander("1. Qual algoritmo apresentou melhor desempenho nos testes de ordenação?", expanded=True):
    st.markdown(
        f"Com n = {num(N)}, o tempo médio nos três cenários foi: " +
        ", ".join(f"**{a}** {ms(t)}" for a, t in medias.items()) +
        f". O mais rápido foi o **{vencedor}**. O Merge Sort fez o **menor número de comparações** "
        f"({num(mg['Aleatório']['comparacoes'])} no aleatório, contra {num(hp['Aleatório']['comparacoes'])} do Heap). "
        "O Heap Sort foi o mais lento entre os O(n log n) por fazer ~2 comparações por nível do heap e "
        "acessar posições distantes do vetor.")

with st.expander("2. O Quick Sort apresentou comportamento diferente quando os dados já estavam ordenados?"):
    st.markdown(
        f"**Sim, com pivô fixo no último elemento.** Em dados aleatórios levou {ms(qa['Aleatório']['tempo_s'])}; "
        f"em dados **ordenados**, {ms(qa['Ordenado']['tempo_s'])} "
        f"(**{qa['Ordenado']['tempo_s'] / qa['Aleatório']['tempo_s']:,.0f}× mais lento**), com "
        f"**{num(qa['Ordenado']['comparacoes'])} comparações** – exatamente n(n−1)/2 = {num(n2)}, "
        f"a assinatura do O(n²). A profundidade da recursão chegou a {num(qa['Ordenado']['profundidade_max'])} "
        f"(uma partição vazia a cada nível). Com **mediana de três**, o tempo ordenado foi "
        f"{ms(qm['Ordenado']['tempo_s'])} – o pior caso desaparece porque o pivô volta a dividir ao meio.")

with st.expander("3. Por que o Merge Sort mantém sua complexidade O(n log n)?"):
    st.markdown(
        "Porque a divisão **não depende dos dados**: o vetor é sempre partido ao meio, gerando ⌈log₂ n⌉ níveis, "
        "e cada nível intercala n elementos → n·log n. Nos experimentos, as **movimentações foram idênticas** "
        f"nos três cenários ({num(mg['Aleatório']['trocas_movimentacoes'])}) e o tempo ficou entre "
        f"{ms(min(m['tempo_s'] for m in mg.values()))} e {ms(max(m['tempo_s'] for m in mg.values()))}. "
        f"Só as comparações variam (de {num(mg['Inverso']['comparacoes'])} a {num(mg['Aleatório']['comparacoes'])}), "
        "porque quando uma metade se esgota o restante é copiado sem comparar.")

b, d, dj = df_b.loc["BFS"], df_b.loc["DFS"], df_b.loc["Dijkstra"]
with st.expander("4. Qual a diferença entre BFS e DFS em relação à exploração dos vértices?"):
    st.markdown(
        "A **BFS** expande por **níveis** (fila FIFO): primeiro as cidades a 1 trecho, depois a 2... A **DFS** "
        "segue **um caminho até o fim** (recursão/pilha) e só volta em becos sem saída. Em 245 consultas "
        f"(5 CDs × 49 destinos), a BFS achou o caminho com **menos trechos em {b['% rotas com menos trechos']}%** "
        f"dos casos (média {b['Trechos (média)']} trechos), enquanto a DFS fez em média **{d['Trechos (média)']} trechos** "
        f"e {d['Custo km (média)']} km – {d['Excesso vs. ótimo (km, média)']} km a mais que o ótimo. "
        f"A BFS visitou em média {b['Vértices visitados (média)']} vértices antes de parar; a DFS, "
        f"{d['Vértices visitados (média)']}.")

with st.expander("5. Qual o impacto do uso de pesos no algoritmo de Dijkstra?"):
    st.markdown(
        f"Os pesos (km) mudam o critério de expansão: Dijkstra encontrou a rota de **menor km em 100%** das "
        f"consultas (média {dj['Custo km (média)']} km), enquanto a BFS – que só conta trechos – acertou o menor km "
        f"em **{b['% rotas de menor km']}%** e ficou em média {b['Excesso vs. ótimo (km, média)']} km acima. "
        f"Em {100 - dj['% rotas com menos trechos']:.1f}% das consultas o caminho ótimo tinha **mais trechos** que o "
        f"da BFS. O custo é maior: {dj['Arestas examinadas (média)']} arestas examinadas e "
        f"{dj['Tempo (ms, média)']} ms por consulta (BFS: {b['Arestas examinadas (média)']} e {b['Tempo (ms, média)']} ms), "
        "por causa da fila de prioridade O(log V) e por não poder parar na primeira descoberta do destino.")

with st.expander("6. Como o volume de dados influencia os cálculos de Entropia e Ganho de Informação?"):
    p, u = df_id3.iloc[0], df_id3.iloc[-1]
    st.markdown(
        f"Com **{int(p['n_treino'])}** registros, a entropia da raiz foi {p['entropia_raiz']} e a acurácia de teste "
        f"{p['acuracia_teste']:.1%}; com **{int(u['n_treino'])}**, {u['entropia_raiz']} e {u['acuracia_teste']:.1%}. "
        "Com poucos dados, os ganhos oscilam (amostras pequenas geram partições quase puras por acaso → "
        "*overfitting*: acurácia de treino alta e de teste baixa). Com mais dados, os ganhos **estabilizam** perto "
        "dos valores reais e a árvore generaliza melhor. O custo cresce linearmente: o treino passou de "
        f"{p['tempo_treino_ms']} ms para {u['tempo_treino_ms']} ms (O(a²·n)).")
    st.line_chart(df_id3.set_index("n_treino")[["acuracia_treino", "acuracia_teste"]],
                  x_label="registros de treino", y_label="acurácia")
    st.line_chart(df_id3.set_index("n_treino")[[c for c in df_id3.columns if c.startswith("ganho_")]],
                  x_label="registros de treino", y_label="ganho de informação")

with st.expander("7. Qual algoritmo apresentou maior consumo de memória?"):
    mem = df_ord[df_ord["n"] == N].groupby("algoritmo")["memoria_pico_kb"].max()
    st.markdown(
        f"O **Merge Sort**: pico de **{mem['Merge Sort']} KB** com n = {num(N)}, contra "
        f"{mem['Heap Sort']} KB do Heap e {mem['Quick Sort (mediana de 3)']} KB do Quick. A diferença "
        "(≈ n referências) é o vetor auxiliar da intercalação – O(n). Heap Sort é in-place (O(1)) e o Quick "
        "usa só a pilha de partições (O(log n)). O valor-base comum aos três é a cópia da lista de entrada.")
    st.bar_chart(mem, horizontal=True, x_label="KB (pico)")

with st.expander("8. Qual estratégia seria mais adequada para resolver o problema escolhido e por quê?"):
    st.markdown(
        "- **Roteamento:** **Dijkstra** – o objetivo da transportadora é minimizar km/custo, e os pesos são não "
        "negativos. A BFS serve para perguntas de alcance (\"quais cidades estão a até 2 trechos do CD?\"); a DFS, "
        "para explorar conectividade, não para rotas.\n"
        "- **Fila de expedição:** **Merge Sort** quando a ordem precisa ser **estável** (ex.: ordenar por prazo "
        "mantendo a ordem de chegada dos empates) e há memória; **Quick Sort com mediana de 3** quando a prioridade "
        f"é velocidade – foi o mais rápido no aleatório ({ms(qm['Aleatório']['tempo_s'])}). Pivô fixo deve ser "
        "evitado: listas de pedidos frequentemente já chegam ordenadas por data.\n"
        "- **Risco de atraso:** **ID3** – gera regras legíveis para a operação (ex.: *SE distância Longa E veículo "
        "Moto ENTÃO Atrasado*), com acurácia de teste acima da linha de base.")

# ------------------------------------------------------------------ hipóteses
st.subheader("Hipóteses formuladas antes dos experimentos")
hip = [
    ("Quick Sort com pivô fixo degrada para O(n²) em dados ordenados/inversos",
     qa["Ordenado"]["comparacoes"] >= 0.9 * n2),
    ("Merge Sort tem tempo estável nos 3 cenários, mas usa mais memória",
     max(m["tempo_s"] for m in mg.values()) < 3 * min(m["tempo_s"] for m in mg.values())
     and mg["Aleatório"]["memoria_pico_kb"] > hp["Aleatório"]["memoria_pico_kb"]),
    ("Heap Sort é o mais consistente entre cenários",
     max(h["tempo_s"] for h in hp.values()) / min(h["tempo_s"] for h in hp.values()) <=
     max(m["tempo_s"] for m in mg.values()) / min(m["tempo_s"] for m in mg.values())),
    ("BFS encontra a rota com menos trechos, mas nem sempre a de menor km",
     b["% rotas com menos trechos"] == 100 and b["% rotas de menor km"] < 100),
    ("Dijkstra encontra a menor rota mesmo com mais trechos que a BFS",
     dj["% rotas de menor km"] == 100 and dj["% rotas com menos trechos"] < 100),
    ("Mais dados de treino → árvore ID3 generaliza melhor",
     df_id3.iloc[-1]["acuracia_teste"] > df_id3.iloc[0]["acuracia_teste"]),
]
st.dataframe(pd.DataFrame([{"Hipótese": h, "Resultado": "✅ Confirmada" if ok else "❌ Refutada"}
                           for h, ok in hip]), hide_index=True, width="stretch")
