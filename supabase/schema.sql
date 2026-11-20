-- LogiPR – esquema do banco no Supabase (PostgreSQL)
-- Execute no Supabase: SQL Editor → New query → cole este arquivo → Run.

create table if not exists cidades (
    codigo_ibge         integer primary key,
    nome                text    not null unique,
    latitude            double precision not null,
    longitude           double precision not null,
    centro_distribuicao boolean not null default false
);

create table if not exists rotas (
    id           bigint generated always as identity primary key,
    origem       text not null references cidades(nome) on update cascade,
    destino      text not null references cidades(nome) on update cascade,
    distancia_km double precision not null check (distancia_km >= 0),  -- Dijkstra exige pesos ≥ 0
    unique (origem, destino)
);

create table if not exists pedidos (
    id_pedido       text primary key,
    cd_origem       text not null references cidades(nome),
    cidade_destino  text not null references cidades(nome),
    distancia_km    double precision,
    faixa_distancia text check (faixa_distancia in ('Curta', 'Média', 'Longa')),
    peso_kg         double precision check (peso_kg > 0),
    faixa_peso      text check (faixa_peso in ('Leve', 'Médio', 'Pesado')),
    veiculo         text check (veiculo in ('Moto', 'Van', 'Caminhão')),
    turno_saida     text check (turno_saida in ('Manhã', 'Tarde', 'Noite')),
    clima           text check (clima in ('Bom', 'Chuvoso')),
    prioridade      text check (prioridade in ('Normal', 'Expressa')),
    valor_frete     double precision,
    prazo_dias      integer,
    status_entrega  text check (status_entrega in ('No prazo', 'Atrasado'))  -- alvo do ID3
);

-- Segurança: RLS ligado e SEM políticas públicas → a chave "anon" não acessa nada.
-- O app (servidor Streamlit) usa a chave service_role, guardada em st.secrets,
-- que nunca é enviada ao navegador.
alter table cidades enable row level security;
alter table rotas   enable row level security;
alter table pedidos enable row level security;
