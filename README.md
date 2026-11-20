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

## Deploy (Railway)
A configuração já está no repositório:

| Arquivo | Função |
|---|---|
| `railway.json` | Build com Railpack, comando de start, health check em `/_stcore/health` e reinício automático em caso de falha |
| `.python-version` | Fixa o Python 3.12 no build |
| `Procfile` | Mesmo comando de start, para quem preferir esse formato |
| `requirements.txt` | Dependências instaladas pelo Railway |

O Streamlit escuta a porta que o Railway define em `$PORT`, no endereço `0.0.0.0`.

**Pelo painel (recomendado)**
1. Suba esta pasta (`logipr/`) para um repositório no GitHub. Ela precisa ser a raiz do repositório; se não for, informe `Formal N2/logipr` em **Settings → Root Directory**.
2. Em <https://railway.com>, clique em **New Project → Deploy from GitHub repo** e escolha o repositório.
3. No serviço criado, abra **Variables** e cadastre:
   ```
   SUPABASE_URL = https://SEU-PROJETO.supabase.co
   SUPABASE_KEY = sua-chave-service_role
   ```
4. Em **Settings → Networking**, clique em **Generate Domain** para ganhar o endereço público (`*.up.railway.app`).
5. Cada novo `git push` na branch principal gera um deploy automático.

**Pela linha de comando**
```bash
npm i -g @railway/cli
railway login
railway init
railway up
railway variables --set "SUPABASE_URL=https://SEU-PROJETO.supabase.co" --set "SUPABASE_KEY=sua-chave-service_role"
railway domain
```

**Observações**
- Sem as variáveis do Supabase o app sobe normalmente usando os CSVs. Porém o disco do Railway é apagado a cada deploy, então cadastros feitos nesse modo se perdem. Com o Supabase, os dados persistem.
- A chave `service_role` fica só nas variáveis do servidor e nunca chega ao navegador.
- O Railway cobra pelo uso (há crédito de teste para contas novas). Um app Streamlit pequeno como este consome pouco, mas desligue o serviço depois da apresentação se não for mais usá-lo.

## Fontes de dados
- **Cidades:** municípios do IBGE com coordenadas, do dataset aberto [kelvins/municipios-brasileiros](https://github.com/kelvins/municipios-brasileiros), filtrado para 50 cidades do PR.
- **Rotas:** cada cidade é ligada às 5 mais próximas. A distância é Haversine × 1,3 (fator rodoviário). O grafo resultante é conexo.
- **Pedidos:** simulados por `modulos/gerador_dados.py`, com regras de negócio, aleatoriedade e semente fixa. Não existe base pública com o desfecho das entregas.

Para regerar a base:
```bash
python scripts/gerar_base.py caminho/municipios.csv 300
```
