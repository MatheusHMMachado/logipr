"""Módulo 1 – Pesquisa, construção e manipulação da base de dados (CRUD)."""
import pandas as pd
import streamlit as st

import util
from modulos.gerador_dados import CENTROS_DISTRIBUICAO, completar_pedido

util.configurar("Base de dados", "🗃️")
util.rodape_backend()
st.title("🗃️ Módulo 1 – Base de dados")

repo = util.repositorio()
pedidos = util.listar("pedidos")
cidades = util.listar("cidades")
nomes = util.nomes_cidades()

aba_lista, aba_novo, aba_editar, aba_cidades, aba_estrutura = st.tabs(
    ["📋 Consultar pedidos", "➕ Cadastrar", "✏️ Editar / remover", "🗺️ Cidades e rotas",
     "🧱 Estrutura da base"])

# ------------------------------------------------------------------ consulta
with aba_lista:
    c1, c2, c3, c4 = st.columns(4)
    f_cd = c1.multiselect("Centro de distribuição", CENTROS_DISTRIBUICAO)
    f_status = c2.multiselect("Status", ["No prazo", "Atrasado"])
    f_veic = c3.multiselect("Veículo", ["Moto", "Van", "Caminhão"])
    termo = c4.text_input("Buscar (ID ou cidade)")
    filtrados = [p for p in pedidos
                 if (not f_cd or p["cd_origem"] in f_cd)
                 and (not f_status or p["status_entrega"] in f_status)
                 and (not f_veic or p["veiculo"] in f_veic)
                 and (not termo or termo.lower() in (p["id_pedido"] + p["cidade_destino"]).lower())]
    st.caption(f"{len(filtrados)} de {len(pedidos)} pedidos")
    st.dataframe(pd.DataFrame(filtrados), width="stretch", hide_index=True, height=420)

    atrasados = sum(p["status_entrega"] == "Atrasado" for p in pedidos)
    m1, m2, m3 = st.columns(3)
    m1.metric("Pedidos no prazo", len(pedidos) - atrasados)
    m2.metric("Pedidos atrasados", atrasados)
    m3.metric("Distância média", util.fmt_km(sum(p["distancia_km"] for p in pedidos) / len(pedidos)))

# ------------------------------------------------------------------ cadastro
def formulario(prefixo, base=None):
    base = base or {}
    c1, c2 = st.columns(2)
    cd = c1.selectbox("Centro de distribuição (origem)", CENTROS_DISTRIBUICAO,
                      index=CENTROS_DISTRIBUICAO.index(base.get("cd_origem", "Curitiba")),
                      key=f"{prefixo}_cd")
    destinos = [n for n in nomes if n != cd]
    atual = base.get("cidade_destino", destinos[0])
    destino = c2.selectbox("Cidade de destino", destinos,
                           index=destinos.index(atual) if atual in destinos else 0,
                           key=f"{prefixo}_dest")
    c3, c4, c5 = st.columns(3)
    peso = c3.number_input("Peso (kg)", 0.1, 5000.0, float(base.get("peso_kg", 10.0)),
                           key=f"{prefixo}_peso")
    opts = {"veiculo": ["Moto", "Van", "Caminhão"], "turno_saida": ["Manhã", "Tarde", "Noite"],
            "clima": ["Bom", "Chuvoso"], "prioridade": ["Normal", "Expressa"],
            "status_entrega": ["No prazo", "Atrasado"]}
    veiculo = c4.selectbox("Veículo", opts["veiculo"],
                           index=opts["veiculo"].index(base.get("veiculo", "Van")), key=f"{prefixo}_v")
    turno = c5.selectbox("Turno de saída", opts["turno_saida"],
                         index=opts["turno_saida"].index(base.get("turno_saida", "Manhã")),
                         key=f"{prefixo}_t")
    c6, c7, c8 = st.columns(3)
    clima = c6.selectbox("Clima", opts["clima"], index=opts["clima"].index(base.get("clima", "Bom")),
                         key=f"{prefixo}_c")
    prioridade = c7.selectbox("Prioridade", opts["prioridade"],
                              index=opts["prioridade"].index(base.get("prioridade", "Normal")),
                              key=f"{prefixo}_p")
    status = c8.selectbox("Status da entrega (resultado real)", opts["status_entrega"],
                          index=opts["status_entrega"].index(base.get("status_entrega", "No prazo")),
                          key=f"{prefixo}_s")
    return {"cd_origem": cd, "cidade_destino": destino, "peso_kg": round(peso, 2), "veiculo": veiculo,
            "turno_saida": turno, "clima": clima, "prioridade": prioridade, "status_entrega": status}


with aba_novo:
    st.markdown("A **distância** é calculada automaticamente pelo **Dijkstra** sobre o grafo de rotas; "
                "as faixas (Curta/Média/Longa, Leve/Médio/Pesado) e o prazo são derivados dela.")
    with st.form("novo"):
        dados = formulario("novo")
        if st.form_submit_button("Cadastrar pedido", type="primary"):
            novo = completar_pedido(dict(dados, id_pedido=util.proximo_id(pedidos)), util.grafo())
            try:
                repo.inserir("pedidos", novo)
                util.limpar_cache()
                st.success(f"Pedido {novo['id_pedido']} cadastrado · {util.fmt_km(novo['distancia_km'])} "
                           f"({novo['faixa_distancia']}) · frete R$ {novo['valor_frete']:.2f}")
            except Exception as e:  # noqa: BLE001
                st.error(f"Erro ao cadastrar: {e}")

# ------------------------------------------------------------------ edição / remoção
with aba_editar:
    ids = [p["id_pedido"] for p in pedidos]
    escolhido = st.selectbox("Pedido", ids, index=len(ids) - 1 if ids else None)
    if escolhido:
        registro = repo.buscar("pedidos", escolhido)
        st.json(registro, expanded=False)
        with st.form("editar"):
            dados = formulario("edit", registro)
            col_a, col_b = st.columns(2)
            salvar = col_a.form_submit_button("Salvar alterações", type="primary")
            remover = col_b.form_submit_button("Remover pedido")
        if salvar:
            atualizado = completar_pedido(dict(dados, id_pedido=escolhido, valor_frete=None,
                                               prazo_dias=None), util.grafo())
            atualizado.pop("id_pedido")
            repo.atualizar("pedidos", escolhido, atualizado)
            util.limpar_cache()
            st.success(f"Pedido {escolhido} atualizado.")
            st.rerun()
        if remover:
            repo.remover("pedidos", escolhido)
            util.limpar_cache()
            st.warning(f"Pedido {escolhido} removido.")
            st.rerun()

# ------------------------------------------------------------------ cidades
with aba_cidades:
    st.markdown("**Fonte pública:** municípios do IBGE com coordenadas "
                "([kelvins/municipios-brasileiros](https://github.com/kelvins/municipios-brasileiros)). "
                "As rotas ligam cada cidade às 5 mais próximas; distância = Haversine × 1,3 (fator rodoviário).")
    df_c = pd.DataFrame(cidades)
    df_c["cor"] = df_c["centro_distribuicao"].map(lambda cd: "#d1495b" if cd else "#2a78c4")
    df_c["tamanho"] = df_c["centro_distribuicao"].map(lambda cd: 9000 if cd else 4000)
    st.map(df_c, latitude="latitude", longitude="longitude", color="cor", size="tamanho")
    c1, c2 = st.columns(2)
    c1.dataframe(df_c.drop(columns=["cor", "tamanho"]), hide_index=True, width="stretch")
    c2.dataframe(pd.DataFrame(util.listar("rotas")), hide_index=True, width="stretch")

# ------------------------------------------------------------------ estrutura
with aba_estrutura:
    st.markdown(f"**{len(pedidos)} pedidos** (mínimo exigido: 50) · **{len(cidades)} cidades** · "
                f"**{len(util.listar('rotas'))} rotas**")
    st.table(pd.DataFrame([
        ["id_pedido", "texto", "P00001…", "Chave primária"],
        ["cd_origem / cidade_destino", "texto (FK cidades)", "50 cidades do PR", "Grafo (origem/destino)"],
        ["distancia_km", "real", "calculada pelo Dijkstra", "Ordenação"],
        ["faixa_distancia", "categórico", "Curta ≤250 · Média ≤500 · Longa", "ID3"],
        ["peso_kg", "real", "0,5 – 1.500", "Ordenação"],
        ["faixa_peso", "categórico", "Leve ≤30 · Médio ≤300 · Pesado", "ID3"],
        ["veiculo", "categórico", "Moto · Van · Caminhão", "ID3"],
        ["turno_saida", "categórico", "Manhã · Tarde · Noite", "ID3"],
        ["clima", "categórico", "Bom · Chuvoso", "ID3"],
        ["prioridade", "categórico", "Normal · Expressa", "ID3"],
        ["valor_frete", "real (R$)", "15 + 0,9·km·(1+peso/500)·(1,5 se expressa)", "Ordenação"],
        ["prazo_dias", "inteiro", "⌈km/250⌉ + 1 (−1 se expressa)", "Ordenação"],
        ["status_entrega", "categórico", "No prazo · Atrasado", "ALVO do ID3"],
    ], columns=["Atributo", "Tipo", "Domínio", "Uso"]))
    st.info("Os pedidos são **simulados** (não existe base pública com o desfecho da entrega). "
            "O gerador aplica regras plausíveis – distância longa, chuva, turno noturno, moto em trajetos "
            "longos, carga pesada fora de caminhão e prazo expresso aumentam a chance de atraso – "
            "com aleatoriedade e semente fixa. O ID3 **não conhece** essas regras: precisa descobri-las.")
