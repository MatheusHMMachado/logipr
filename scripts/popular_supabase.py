"""Envia os CSVs de dados/ para o Supabase (rodar uma vez, após executar schema.sql).

Uso (PowerShell):
    $env:SUPABASE_URL = "https://xxxx.supabase.co"
    $env:SUPABASE_KEY = "<service_role key>"
    python scripts/popular_supabase.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modulos.repositorio import RepositorioCSV, RepositorioSupabase  # noqa: E402


def main():
    url, chave = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
    if not (url and chave):
        raise SystemExit("Defina SUPABASE_URL e SUPABASE_KEY.")
    csv_repo, sb = RepositorioCSV(), RepositorioSupabase(url, chave)
    for tabela in ["cidades", "rotas", "pedidos"]:  # ordem respeita as chaves estrangeiras
        linhas = csv_repo.listar(tabela)
        if sb.listar(tabela):
            print(f"{tabela}: já possui dados – pulando")
            continue
        sb.inserir_varios(tabela, linhas)
        print(f"{tabela}: {len(linhas)} registros enviados")


if __name__ == "__main__":
    main()
