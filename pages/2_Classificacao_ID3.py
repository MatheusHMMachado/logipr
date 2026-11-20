"""Módulo 2 – Classificação por Entropia, Ganho de Informação e Árvore ID3."""
import random

import pandas as pd
import streamlit as st

import util
from modulos.classificacao_id3 import ID3
from modulos.entropia import contar, entropia, formula_entropia, ganho_informacao
from modulos.gerador_dados import ALVO_ID3, ATRIBUTOS_ID3

util.configurar("Classificação ID3", "🌳")
util.rodape_backend()
st.title("🌳 Módulo 2 – Classificação por Entropia (ID3)")
st.markdown(f"**Variável classificada:** `{ALVO_ID3}` (No prazo / Atrasado) · "
            f"**Atributos:** {', '.join(f'`{a}`' for a in ATRIBUTOS_ID3)}")

pedidos = util.listar("pedidos")

with st.sidebar:
    st.header("Parâmetros")
    pct_treino = st.slider("% para treino", 50, 90, 80, 5)
    atributos = st.multiselect("Atributos usados", ATRIBUTOS_ID3, ATRIBUTOS_ID3)
    prof_max = st.slider("Profundidade máxima", 1, 6, 4)
    min_reg = st.slider("Mínimo de registros para dividir", 1, 20, 5)
    semente = st.number_input("Semente do embaralhamento", 0, 9999, 42)

if not atributos:
    st.warning("Selecione ao menos um atributo.")
    st.stop()

# divisão treino/teste (embaralhamento Fisher-Yates com semente → reprodutível)
dados = list(pedidos)
rng = random.Random(semente)
for i in range(len(dados) - 1, 0, -1):
    j = rng.randint(0, i)
    dados[i], dados[j] = dados[j], dados[i]
corte = int(len(dados) * pct_treino / 100)
treino, teste = dados[:corte], dados[corte:]

modelo = ID3(min_registros=min_reg, profundidade_max=prof_max).treinar(treino, atributos, ALVO_ID3)
aval = modelo.avaliar(teste)
est = modelo.estatisticas()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Treino", len(treino))
c2.metric("Teste (nunca vistos)", len(teste))
c3.metric("Acurácia no teste", f"{aval['acuracia']:.1%}")
c4.metric("Nós / folhas", f"{est['nos']} / {est['folhas']}")
c5.metric("Profundidade", est["profundidade"])

aba_calc, aba_arvore, aba_regras, aba_teste, aba_novo = st.tabs(
    ["🧮 Entropia e Ganho", "🌳 Árvore", "📜 Regras", "✅ Testes", "🔮 Classificar novo pedido"])

# ------------------------------------------------------------------ cálculos
with aba_calc:
    rot = [r[ALVO_ID3] for r in treino]
    st.subheader("1. Entropia do conjunto de treino")
    cont = contar(rot)
    st.markdown(f"Distribuição: {', '.join(f'**{k}**: {v}' for k, v in cont.items())} (total {len(rot)})")
    st.latex(r"H(S) = -\sum_i p_i \log_2 p_i")
    st.code(f"H(S) = {formula_entropia(rot)}", language=None)

    st.subheader("2. Ganho de Informação de cada atributo (nó raiz)")
    st.latex(r"Ganho(S,A) = H(S) - \sum_{v} \frac{|S_v|}{|S|} H(S_v)")
    linhas, detalhes = [], {}
    for a in atributos:
        g, det = ganho_informacao(treino, a, ALVO_ID3)
        detalhes[a] = det
        linhas.append({"Atributo": a, "Entropia média ponderada": round(det["entropia_media_ponderada"], 4),
                       "Ganho": round(g, 4)})
    linhas = util.ordenar(linhas, chave=lambda l: -l["Ganho"])
    st.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch")
    st.bar_chart(pd.DataFrame(linhas).set_index("Atributo")["Ganho"], horizontal=True)
    st.success(f"**Atributo mais relevante:** `{modelo.raiz.atributo}` "
               f"(ganho = {modelo.raiz.ganho:.4f}) → escolhido como raiz da árvore.")

    st.subheader("3. Detalhe da conta por atributo")
    atr = st.selectbox("Atributo", atributos, index=atributos.index(modelo.raiz.atributo)
                       if modelo.raiz.atributo in atributos else 0)
    det = detalhes[atr]
    st.dataframe(pd.DataFrame([{
        "Valor": p["valor"], "Registros": p["qtd"],
        "Distribuição": ", ".join(f"{k}: {v}" for k, v in p["contagem"].items()),
        "H(S_v)": round(p["entropia"], 4), "|S_v|/|S|": round(p["peso"], 4),
        "Contribuição": round(p["contribuicao"], 4)} for p in det["particoes"]]),
        hide_index=True, width="stretch")
    st.code(f"Ganho({atr}) = {det['entropia_total']:.4f} − {det['entropia_media_ponderada']:.4f} "
            f"= {det['ganho']:.4f}", language=None)

    with st.expander("Ganhos calculados em todos os nós internos (passo a passo do ID3)"):
        for p in modelo.passos:
            st.markdown(f"**{p['no']}** · n={p['registros']} · H={p['entropia']:.4f} → "
                        f"escolhido **{p['escolhido']}**")
            st.caption(" · ".join(f"{a}: {g:.4f}" for a, g in p["ganhos"].items()))

# ------------------------------------------------------------------ árvore
with aba_arvore:
    st.graphviz_chart(modelo.para_dot(), width="stretch")
    st.caption(f"H = entropia do nó · G = ganho do atributo escolhido · n = registros no nó · "
               f"{est['calculos_entropia']} cálculos de entropia na construção.")

# ------------------------------------------------------------------ regras
with aba_regras:
    regras = modelo.regras()
    st.markdown(f"**{len(regras)} regras** extraídas (uma por folha com registros):")
    st.dataframe(pd.DataFrame([{"Regra": r["regra"], "Suporte": r["suporte"],
                                "Distribuição": ", ".join(f"{k}: {v}" for k, v in r["distribuicao"].items())}
                               for r in regras]), hide_index=True, width="stretch")

# ------------------------------------------------------------------ testes
with aba_teste:
    st.subheader("Matriz de confusão (registros de teste)")
    st.dataframe(pd.DataFrame(aval["matriz"]).T.rename_axis("Real \\ Previsto"), width="stretch")
    base = max(contar([r[ALVO_ID3] for r in teste]).values()) / len(teste) if teste else 0
    st.markdown(f"Acurácia: **{aval['acuracia']:.1%}** ({aval['acertos']}/{aval['total']}) · "
                f"Linha de base (chutar sempre a classe mais comum): **{base:.1%}**")
    st.dataframe(pd.DataFrame([{
        "Pedido": r["id_pedido"], **{a: r[a] for a in atributos},
        "Real": r[ALVO_ID3], "Previsto": modelo.classificar(r),
        "Acertou": "✅" if modelo.classificar(r) == r[ALVO_ID3] else "❌"} for r in teste]),
        hide_index=True, width="stretch", height=350)

# ------------------------------------------------------------------ novo
with aba_novo:
    st.markdown("Informe as características de um pedido **novo** e veja a classificação e o caminho na árvore.")
    dominios = {"faixa_distancia": ["Curta", "Média", "Longa"], "faixa_peso": ["Leve", "Médio", "Pesado"],
                "veiculo": ["Moto", "Van", "Caminhão"], "turno_saida": ["Manhã", "Tarde", "Noite"],
                "clima": ["Bom", "Chuvoso"], "prioridade": ["Normal", "Expressa"]}
    cols = st.columns(3)
    entrada = {a: cols[i % 3].selectbox(a, dominios[a], key=f"nv_{a}") for i, a in enumerate(ATRIBUTOS_ID3)}
    classe, trilha = modelo.classificar(entrada, explicar=True)
    (st.success if classe == "No prazo" else st.error)(f"Classificação: **{classe}**")
    st.markdown("Caminho percorrido: " + (" → ".join(f"`{t}`" for t in trilha) or "raiz é folha"))
