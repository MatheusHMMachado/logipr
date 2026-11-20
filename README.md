# 🚚 LogiPR – Laboratório Inteligente de Logística e Entregas

Projeto Formal N2 – **Complexidade de Algoritmos**.
Sistema que integra **Entropia/ID3, BFS, DFS, Dijkstra, Heap Sort, Quick Sort e Merge Sort** sobre uma base de logística do Paraná, com experimentos e análise Big O.

Todos os algoritmos foram implementados pelo grupo em `modulos/`. O sistema não usa `sort()`, `sorted()` nem bibliotecas de grafos ou de aprendizado de máquina.

## Estrutura
```
app.py                      página inicial (Streamlit)
pages/                      1 página por módulo (Base, ID3, Grafos, Ordenação, Análise)
modulos/                    algoritmos + acesso a dados + gerador da base
experimentos/               scripts de experimento e resultados (CSV + PNG)
dados/                      seed CSV: 50 cidades (IBGE), 155 rotas, 300 pedidos
supabase/schema.sql         tabelas do banco
scripts/                    geração da base e carga no Supabase
tests/                      pytest (46 testes)
```

## Rodar localmente
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```
Sem credenciais, o app usa os CSVs de `dados/` automaticamente.

```bash
pytest -q                               # testes dos algoritmos
python -m experimentos.executar_todos   # refaz os experimentos (~2 min)
```

## Banco de dados (Supabase)
1. Crie um projeto em <https://supabase.com> (plano gratuito).
2. Abra **SQL Editor**, cole `supabase/schema.sql` e clique em **Run**.
3. Em **Project Settings → API**, copie a **Project URL** e a chave **service_role**.
4. Carregue os dados uma vez (PowerShell):
   ```powershell
   $env:SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
   $env:SUPABASE_KEY = "sua-chave-service_role"
   python scripts/popular_supabase.py
   ```
5. Para rodar local com o banco, copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencha. Esse arquivo está no `.gitignore`.

A chave `service_role` fica apenas no servidor Streamlit e nunca é enviada ao navegador. As tabelas têm RLS ativo e nenhuma política pública, então a chave `anon` não acessa os dados.

## Deploy (Streamlit Community Cloud)
1. Suba esta pasta para um repositório no GitHub.
2. Em <https://share.streamlit.io>, clique em **Create app**, escolha o repositório e informe o *Main file* `app.py`. Em **Advanced settings**, escolha **Python 3.12**.
3. Em **Advanced settings → Secrets**, cole:
   ```toml
   SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
   SUPABASE_KEY = "sua-chave-service_role"
   ```
4. Clique em **Deploy**. Cada novo `git push` atualiza o app.

## Fontes de dados
- **Cidades:** municípios do IBGE com coordenadas, do dataset aberto [kelvins/municipios-brasileiros](https://github.com/kelvins/municipios-brasileiros), filtrado para 50 cidades do PR.
- **Rotas:** cada cidade é ligada às 5 mais próximas. A distância é Haversine × 1,3 (fator rodoviário). O grafo resultante é conexo.
- **Pedidos:** simulados por `modulos/gerador_dados.py`, com regras de negócio, aleatoriedade e semente fixa. Não existe base pública com o desfecho das entregas.

Para regerar a base:
```bash
python scripts/gerar_base.py caminho/municipios.csv 300
```
