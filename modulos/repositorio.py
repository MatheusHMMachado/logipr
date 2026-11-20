"""Camada de acesso a dados (CRUD) – Supabase (PostgreSQL) ou CSV local.

- Se as credenciais SUPABASE_URL e SUPABASE_KEY existirem (st.secrets ou
  variáveis de ambiente), usa o Supabase via API REST (PostgREST).
- Caso contrário, usa os CSVs de dados/ (modo offline / fallback).

A camada só armazena e devolve registros; nenhuma ordenação, busca ou
classificação é delegada ao banco – isso é feito pelos nossos algoritmos.
"""
import csv
import os

import requests

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(RAIZ, "dados")

TABELAS = {
    "cidades": {"chave": "nome", "campos": ["codigo_ibge", "nome", "latitude", "longitude",
                                            "centro_distribuicao"]},
    "rotas": {"chave": None, "campos": ["origem", "destino", "distancia_km"]},
    "pedidos": {"chave": "id_pedido", "campos": [
        "id_pedido", "cd_origem", "cidade_destino", "distancia_km", "faixa_distancia",
        "peso_kg", "faixa_peso", "veiculo", "turno_saida", "clima", "prioridade",
        "valor_frete", "prazo_dias", "status_entrega"]},
}

TIPOS = {
    "codigo_ibge": int, "prazo_dias": int,
    "latitude": float, "longitude": float, "distancia_km": float, "peso_kg": float,
    "valor_frete": float,
    "centro_distribuicao": lambda v: v if isinstance(v, bool) else str(v).lower() == "true",
}


def normalizar(registro):
    out = {}
    for k, v in registro.items():
        if v is None or v == "":
            out[k] = v
        elif k in TIPOS:
            out[k] = TIPOS[k](v)
        else:
            out[k] = v
    return out


# ============================================================================ CSV
class RepositorioCSV:
    nome = "CSV local"

    def __init__(self, pasta=PASTA_DADOS):
        self.pasta = pasta

    def _arq(self, tabela):
        return os.path.join(self.pasta, f"{tabela}.csv")

    def listar(self, tabela):
        with open(self._arq(tabela), encoding="utf-8") as f:
            return [normalizar(r) for r in csv.DictReader(f)]

    def _gravar(self, tabela, linhas):
        with open(self._arq(tabela), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=TABELAS[tabela]["campos"])
            w.writeheader()
            w.writerows(linhas)

    def buscar(self, tabela, valor_chave):
        chave = TABELAS[tabela]["chave"]
        for r in self.listar(tabela):
            if str(r[chave]) == str(valor_chave):
                return r
        return None

    def inserir(self, tabela, registro):
        linhas = self.listar(tabela)
        chave = TABELAS[tabela]["chave"]
        if chave and any(str(r[chave]) == str(registro[chave]) for r in linhas):
            raise ValueError(f"Já existe registro com {chave} = {registro[chave]}")
        linhas.append({c: registro.get(c) for c in TABELAS[tabela]["campos"]})
        self._gravar(tabela, linhas)
        return registro

    def inserir_varios(self, tabela, registros):
        linhas = self.listar(tabela)
        linhas.extend({c: r.get(c) for c in TABELAS[tabela]["campos"]} for r in registros)
        self._gravar(tabela, linhas)

    def atualizar(self, tabela, valor_chave, alteracoes):
        chave = TABELAS[tabela]["chave"]
        linhas, achou = self.listar(tabela), False
        for r in linhas:
            if str(r[chave]) == str(valor_chave):
                r.update(alteracoes)
                achou = True
        if not achou:
            raise KeyError(valor_chave)
        self._gravar(tabela, linhas)

    def remover(self, tabela, valor_chave):
        chave = TABELAS[tabela]["chave"]
        linhas = self.listar(tabela)
        novas = [r for r in linhas if str(r[chave]) != str(valor_chave)]
        if len(novas) == len(linhas):
            raise KeyError(valor_chave)
        self._gravar(tabela, novas)


# ======================================================================= SUPABASE
class RepositorioSupabase:
    nome = "Supabase (PostgreSQL)"

    def __init__(self, url, chave_api, timeout=15):
        self.base = url.rstrip("/") + "/rest/v1"
        self.timeout = timeout
        self.headers = {"apikey": chave_api, "Authorization": f"Bearer {chave_api}",
                        "Content-Type": "application/json"}

    def _req(self, metodo, tabela, params=None, json=None, extra=None):
        h = dict(self.headers, **(extra or {}))
        r = requests.request(metodo, f"{self.base}/{tabela}", params=params, json=json,
                             headers=h, timeout=self.timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Supabase {r.status_code}: {r.text}")
        return r.json() if r.text else None

    def listar(self, tabela):
        linhas, inicio, passo = [], 0, 1000
        while True:  # paginação (PostgREST devolve no máx. 1000 linhas por vez)
            lote = self._req("GET", tabela, params={"select": "*"},
                             extra={"Range-Unit": "items", "Range": f"{inicio}-{inicio + passo - 1}"})
            linhas.extend(normalizar(r) for r in lote)
            if len(lote) < passo:
                return linhas
            inicio += passo

    def buscar(self, tabela, valor_chave):
        chave = TABELAS[tabela]["chave"]
        res = self._req("GET", tabela, params={"select": "*", chave: f"eq.{valor_chave}"})
        return normalizar(res[0]) if res else None

    def inserir(self, tabela, registro):
        dados = {c: registro.get(c) for c in TABELAS[tabela]["campos"]}
        self._req("POST", tabela, json=dados, extra={"Prefer": "return=minimal"})
        return registro

    def inserir_varios(self, tabela, registros):
        campos = TABELAS[tabela]["campos"]
        for i in range(0, len(registros), 500):
            lote = [{c: r.get(c) for c in campos} for r in registros[i:i + 500]]
            self._req("POST", tabela, json=lote, extra={"Prefer": "return=minimal"})

    def atualizar(self, tabela, valor_chave, alteracoes):
        chave = TABELAS[tabela]["chave"]
        self._req("PATCH", tabela, params={chave: f"eq.{valor_chave}"}, json=alteracoes,
                  extra={"Prefer": "return=minimal"})

    def remover(self, tabela, valor_chave):
        chave = TABELAS[tabela]["chave"]
        self._req("DELETE", tabela, params={chave: f"eq.{valor_chave}"},
                  extra={"Prefer": "return=minimal"})


# ========================================================================= fábrica
def _credenciais():
    url = os.environ.get("SUPABASE_URL")
    chave = os.environ.get("SUPABASE_KEY")
    if not (url and chave):
        try:
            import streamlit as st
            url = url or st.secrets.get("SUPABASE_URL")
            chave = chave or st.secrets.get("SUPABASE_KEY")
        except Exception:  # sem secrets.toml → modo CSV
            pass
    return url, chave


def obter_repositorio():
    url, chave = _credenciais()
    if url and chave:
        return RepositorioSupabase(url, chave)
    return RepositorioCSV()
