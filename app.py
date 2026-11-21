"""LogiPR – Logística e Entregas (página inicial)."""
import streamlit as st

import util

util.configurar("Início")
util.rodape_backend()

st.title("🚚 LogiPR –  Logística e Entregas")
st.markdown(
    "Projeto Formal N2 · **Complexidade de Algoritmos** · "
    "Classificação, Busca, Ordenação e Análise de Eficiência Computacional"
)

cidades, rotas, pedidos = util.listar("cidades"), util.listar("rotas"), util.listar("pedidos")
g = util.grafo()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Cidades (IBGE)", len(cidades))
c2.metric("Rotas (arestas)", g.num_arestas())
c3.metric("Pedidos cadastrados", len(pedidos))
c4.metric("Centros de distribuição", sum(1 for c in cidades if c["centro_distribuicao"]))

st.subheader("O problema")
st.markdown(
    """
Uma transportadora atende **50 cidades do Paraná** a partir de **5 centros de distribuição**
(Curitiba, Ponta Grossa, Londrina, Maringá e Cascavel). Para operar bem, ela precisa:

1. **Prever** se um pedido será entregue **no prazo** ou com **atraso** → *Árvore de Decisão ID3*;
2. **Explorar** as cidades alcançáveis e **calcular a rota de menor custo** → *BFS, DFS e Dijkstra*;
3. **Organizar** milhares de pedidos por prazo, peso, frete ou distância → *Heap, Quick e Merge Sort*;
4. **Justificar** cada escolha pelo custo computacional medido → *Análise de complexidade (Big O)*.
"""
)

st.subheader("Fluxo integrado do sistema")
st.graphviz_chart(
    """
digraph {
  rankdir=LR; node [shape=box, style="rounded,filled", fillcolor="#eef4fb", fontname="Helvetica"];
  A [label="1. Base de dados\\ncidades · rotas · pedidos\\n(CRUD)"];
  B [label="2. Classificação ID3\\nEntropia · Ganho\\nÁrvore de decisão"];
  C [label="3. Busca em grafos\\nBFS · DFS · Dijkstra"];
  D [label="4. Ordenação\\nHeap · Quick · Merge"];
  E [label="5. Análise\\ntempo · memória\\noperações · Big O"];
  A -> B -> C -> D -> E;
}
"""
)

st.subheader("Navegação")
st.page_link("pages/1_Base_de_Dados.py", label="1 · Base de dados", icon="🗃️")
st.page_link("pages/2_Classificacao_ID3.py", label="2 · Classificação por Entropia (ID3)", icon="🌳")
st.page_link("pages/3_Busca_em_Grafos.py", label="3 · Busca em grafos (BFS, DFS, Dijkstra)", icon="🗺️")
st.page_link("pages/4_Ordenacao.py", label="4 · Ordenação (Heap, Quick, Merge)", icon="📊")
st.page_link("pages/5_Analise_Complexidade.py", label="5 · Análise de complexidade", icon="📈")

with st.expander("Arquitetura e restrições atendidas"):
    st.markdown(
        """
| Camada | Tecnologia |
|---|---|
| Linguagem | Python |
| Interface | Streamlit (uma página por módulo) |
| Armazenamento | Supabase (PostgreSQL) com fallback em CSV |
| Hospedagem | Railway |

**Todos os algoritmos foram implementados pelo grupo** (pasta `modulos/`): Entropia, Ganho de
Informação, ID3, BFS, DFS, Dijkstra (com heap mínimo próprio), Heap Sort, Quick Sort e Merge Sort.
Nenhum `sort()`/`sorted()` nem biblioteca de grafos ou de aprendizado de máquina é usado no sistema.
"""
    )
