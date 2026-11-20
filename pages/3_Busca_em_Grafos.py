"""Módulo 3 – Busca em grafos: BFS, DFS e Dijkstra sobre o mapa de rotas do PR."""
import pandas as pd
import pydeck as pdk
import streamlit as st

import util
from modulos.busca_bfs import bfs, niveis
from modulos.busca_dfs import dfs
from modulos.dijkstra import dijkstra

util.configurar("Busca em grafos", "🗺️")
util.rodape_backend()
st.title("🗺️ Módulo 3 – Busca em grafos: BFS, DFS e Dijkstra")
st.info("**BFS** e **DFS** são *estratégias de exploração* (ignoram os pesos). **Dijkstra** é um algoritmo de "
        "*caminho mínimo* com pesos não negativos. Os três percorrem o **mesmo grafo**, mas resolvem "
        "problemas diferentes.")

g = util.grafo()
nomes = util.nomes_cidades()
coords = util.coordenadas()

c1, c2 = st.columns(2)
origem = c1.selectbox("Origem", nomes, index=nomes.index("Curitiba"))
destino = c2.selectbox("Destino", [n for n in nomes if n != origem],
                       index=[n for n in nomes if n != origem].index("Londrina") if origem != "Londrina" else 0)

r_bfs, r_dfs, r_dij = bfs(g, origem, destino), dfs(g, origem, destino), dijkstra(g, origem, destino)

st.subheader(f"Comparação: {origem} → {destino}")
tabela = []
for r in (r_bfs, r_dfs, r_dij):
    ops = r["operacoes"]
    tabela.append({"Algoritmo": r["algoritmo"], "Trechos": len(r["caminho"]) - 1,
                   "Custo (km)": round(r["custo"], 1), "Vértices visitados": len(r["ordem_visita"]),
                   "Arestas examinadas": ops["arestas_examinadas"],
                   "Caminho": " → ".join(r["caminho"])})
st.dataframe(pd.DataFrame(tabela), hide_index=True, width="stretch")

melhor = r_dij["custo"]
st.markdown(
    f"- **BFS** encontrou o caminho com **menos trechos** ({len(r_bfs['caminho']) - 1}), "
    f"custando {r_bfs['custo'] - melhor:+.1f} km em relação ao ótimo.\n"
    f"- **DFS** seguiu a ordem alfabética dos vizinhos até o limite: {len(r_dfs['caminho']) - 1} trechos, "
    f"{r_dfs['custo'] - melhor:+.1f} km em relação ao ótimo.\n"
    f"- **Dijkstra** garantiu o **menor custo**: **{util.fmt_km(melhor)}**."
)

# ------------------------------------------------------------------ mapa
cores = {"BFS": [42, 120, 196], "DFS": [224, 160, 0], "Dijkstra": [209, 73, 91]}
mostrar = st.multiselect("Caminhos no mapa", list(cores), default=list(cores))
arestas = [{"de": coords[a][::-1], "para": coords[b][::-1]} for a in g.adj for b, _ in g.vizinhos(a) if a < b]
camadas = [pdk.Layer("LineLayer", arestas, get_source_position="de", get_target_position="para",
                     get_color=[150, 150, 150, 90], get_width=1.5)]
deslocamento = {"BFS": -0.02, "DFS": 0.02, "Dijkstra": 0.0}
for r in (r_bfs, r_dfs, r_dij):
    if r["algoritmo"] not in mostrar:
        continue
    d = deslocamento[r["algoritmo"]]
    caminho = [[coords[c][1] + d, coords[c][0] + d] for c in r["caminho"]]
    camadas.append(pdk.Layer("PathLayer", [{"path": caminho, "nome": r["algoritmo"]}], get_path="path",
                             get_color=cores[r["algoritmo"]], width_min_pixels=4, pickable=True))
pontos = [{"pos": [lon, lat], "nome": n, "cor": [209, 73, 91] if n in (origem, destino) else [60, 60, 60]}
          for n, (lat, lon) in coords.items()]
camadas.append(pdk.Layer("ScatterplotLayer", pontos, get_position="pos", get_fill_color="cor",
                         radius_min_pixels=4, pickable=True))
camadas.append(pdk.Layer("TextLayer", pontos, get_position="pos", get_text="nome", get_size=11,
                         get_color=[40, 40, 40], get_alignment_baseline="'bottom'"))
st.pydeck_chart(pdk.Deck(layers=camadas, map_style=None, tooltip={"text": "{nome}"},
                         initial_view_state=pdk.ViewState(latitude=-24.6, longitude=-51.5, zoom=5.6)))
st.caption("🔵 BFS · 🟡 DFS · 🔴 Dijkstra (linhas levemente deslocadas para não se sobreporem)")

# ------------------------------------------------------------------ passo a passo
aba_bfs, aba_dfs, aba_dij, aba_adj = st.tabs(["BFS – níveis", "DFS – recursão", "Dijkstra – ordem de fixação",
                                              "Lista de adjacência"])
with aba_bfs:
    st.markdown("A BFS usa uma **fila (FIFO)**: visita todos os vizinhos a 1 trecho, depois a 2 trechos...")
    completo = bfs(g, origem)
    st.dataframe(pd.DataFrame([{"Nível (trechos)": n, "Cidades": ", ".join(vs)}
                               for n, vs in niveis(completo).items()]), hide_index=True, width="stretch")
    st.caption(f"Ordem de expansão até achar {destino}: " + " → ".join(r_bfs["ordem_visita"]))
with aba_dfs:
    st.markdown("A DFS usa **recursão (pilha)**: desce pelo primeiro vizinho não visitado e volta "
                "(*backtracking*) quando não há saída.")
    st.code("\n".join(("  " * p) + (f"visita {v}" if t == "visita" else f"↩ backtrack de {v}")
                      for t, v, p in r_dfs["eventos"]), language=None)
with aba_dij:
    st.markdown("Dijkstra usa uma **fila de prioridade (heap mínimo)** e fixa as cidades em ordem crescente "
                "de distância acumulada; o destino é fixado com custo mínimo garantido.")
    st.dataframe(pd.DataFrame([{"Ordem": i + 1, "Cidade": v, "Distância acumulada (km)": round(d, 1)}
                               for i, (v, d) in enumerate(r_dij["ordem_com_custo"])]),
                 hide_index=True, width="stretch")
    st.json(r_dij["operacoes"])
with aba_adj:
    st.dataframe(pd.DataFrame([{"Cidade": v, "Vizinhos (km)": ", ".join(f"{w} ({p:.0f})" for w, p in g.vizinhos(v))}
                               for v in nomes]), hide_index=True, width="stretch")
    st.caption(f"{g.num_vertices()} vértices · {g.num_arestas()} arestas · espaço O(V + E)")

# ------------------------------------------------------------------ experimento global
st.subheader("Experimento: 5 CDs × todas as cidades")
resumo = util.ler_resultado("busca_resumo.csv")
if resumo:
    st.dataframe(pd.DataFrame(resumo), hide_index=True, width="stretch")
else:
    st.caption("Execute `python -m experimentos.executar_todos` para gerar este resumo.")
