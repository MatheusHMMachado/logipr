# LogiPR – Roteiro de Apresentação

Projeto Formal N2 · Complexidade de Algoritmos · 20/11/2026

Apresentação de 18 minutos, dentro da faixa exigida de 15 a 20, dividida entre 4 integrantes: Matheus Henrique Marques Machado, Mateus Henrique Soares Silva, Felipe Evangelista Alves da Silva e Iury de Andrade Hilário.

## Divisão da apresentação

Cada bloco segue o tempo mínimo do enunciado. O Matheus Machado abre e fecha, porque a conclusão retoma a pergunta que ele apresentou.

| Tempo | Bloco | Quem apresenta | Slides | Demonstração no sistema |
| --- | --- | --- | --- | --- |
| 0:00–3:00 | Problema e temática | Matheus Machado | 1 a 3 | Página inicial |
| 3:00–7:00 | Base de dados e classificação por Entropia | Mateus Soares | 4 a 6 | Páginas 1 e 2 |
| 7:00–11:00 | BFS, DFS e Dijkstra | Felipe Evangelista | 7 e 8 | Página 3 |
| 11:00–15:00 | Algoritmos de ordenação | Iury Hilário | 9 e 10 | Página 4 |
| 15:00–18:00 | Resultados e análise de complexidade | Matheus Machado | 11 a 14 | Página 5 |

**Quem controla o computador:** quem está falando. Na troca de bloco, o próximo integrante já deixa a página do sistema aberta numa segunda aba.

**Regra de ouro:** todos precisam saber explicar todos os módulos. O professor pode pedir a qualquer integrante que explique um trecho de código ou altere dados ao vivo. A seção final traz as perguntas mais prováveis.

## Matheus Machado – Problema e temática (0:00–3:00)

**Slide 1 – Capa (20 s)**

> “Boa noite. Somos o grupo do LogiPR, um laboratório de logística que junta num só sistema todos os algoritmos da disciplina.” Apresentar os integrantes.

**Slide 2 – O problema (1 min 30 s)**

> “Imagine uma transportadora que atende 50 cidades do Paraná a partir de 5 centros de distribuição: Curitiba, Ponta Grossa, Londrina, Maringá e Cascavel. Todo dia ela precisa responder três perguntas. Esse pedido vai atrasar? Qual a rota mais curta até o cliente? Em que ordem despachar milhares de pedidos?”

> “Nossa pergunta de pesquisa foi: como a escolha do algoritmo muda o desempenho e a qualidade da resposta quando o volume e a organização dos dados mudam?”

Dado de impacto para fechar o slide: *“Só trocando o algoritmo de rota, economizamos em média 1.399 km por entrega.”*

**Slide 3 – Arquitetura e fluxo (1 min 10 s)**

> “As cidades são reais, do IBGE. As rotas ligam cada cidade às 5 mais próximas. Os pedidos são simulados, porque não existe base pública dizendo se uma entrega atrasou.”

> “O sistema é em Python com Streamlit, os dados ficam no Supabase com cópia em CSV, e tudo foi escrito por nós: nada de `sort()` nem biblioteca pronta.”

Demonstração: mostrar a página inicial do sistema (os 4 números do topo e o fluxo dos 5 módulos). Passar a palavra: *“O Mateus Soares vai mostrar a base e como a árvore de decisão prevê atrasos.”*

## Mateus Soares – Base de dados e classificação ID3 (3:00–7:00)

**Slide 4 – Base de dados (1 min)**

> “A base tem 300 pedidos, 50 cidades e 155 rotas. Cada pedido tem distância, peso, veículo, turno, clima, prioridade e o resultado: no prazo ou atrasado. 36% atrasaram.”

Demonstração ao vivo (página 1): cadastrar um pedido de **Curitiba para Londrina, 20 kg, moto, noite, chuvoso**. Mostrar que o sistema calcula sozinho a distância (505,5 km, pelo Dijkstra) e a faixa (Longa). Depois filtrar a tabela por “Atrasado” e, na aba Editar / remover, apagar o pedido de teste. Isso mostra o CRUD completo e mantém os números da página 2 iguais aos dos slides (com um pedido a mais, o sorteio de treino e teste muda).

**Slide 5 – Entropia e ganho (1 min 30 s)**

> “A entropia mede a mistura do conjunto. No treino temos 148 pedidos no prazo e 92 atrasados, e a entropia dá 0,96, perto do máximo de 1. O ganho de informação mede quanto cada atributo reduz essa mistura.”

> “A distância tem ganho 0,200, mais que o dobro do segundo colocado, o veículo, com 0,086. Por isso ela vira a raiz da árvore.”

Demonstração (página 2, aba Entropia e Ganho): mostrar a conta passo a passo de `faixa_distancia`.

**Slide 6 – Árvore e testes (1 min 30 s)**

> “A árvore aprendeu regras como: distância Curta e tempo bom, sempre no prazo; distância Longa e chuva, sempre atrasado. Testamos com 60 pedidos que ela nunca viu: acertou 80%. Chutar sempre a classe mais comum daria 72%.”

Demonstração: aba Classificar novo pedido. Escolher Longa + Moto + Chuvoso e mostrar “Atrasado” com o caminho na árvore. Trocar para Curta + Bom e mostrar “No prazo”.

Passar a palavra: *“Agora o Felipe Evangelista mostra como o sistema escolhe a rota.”*

## Felipe Evangelista – BFS, DFS e Dijkstra (7:00–11:00)

**Slide 7 – O grafo e as duas explorações (2 min)**

> “Cada cidade é um vértice e cada estrada é uma aresta com o peso em km. Guardamos o grafo numa lista de adjacência: 50 vértices e 155 arestas.”

> “BFS e DFS são estratégias de exploração e ignoram os pesos. A BFS usa uma fila e anda por níveis: primeiro as cidades a 1 trecho de Curitiba, depois a 2. A DFS usa recursão e segue um caminho até o fim antes de voltar.”

Demonstração (página 3): origem **Curitiba**, destino **Londrina**. Mostrar no mapa:

- BFS: 4 trechos, 512,3 km.
- DFS: 28 trechos, 2.283,8 km. Ela vai primeiro para Antonina (ordem alfabética) e atravessa o estado inteiro.

Abrir a aba BFS – níveis e depois a aba DFS – recursão, mostrando os retornos (*backtracking*).

**Slide 8 – Dijkstra (2 min)**

> “O Dijkstra é outro tipo de algoritmo: ele acha o caminho de menor custo. Usa uma fila de prioridade, um heap mínimo que nós implementamos, e sempre fixa a cidade com menor distância acumulada.”

> “De Curitiba a Londrina ele fez 5 trechos, um a mais que a BFS, e rodou 505,5 km, 6,8 km a menos. Em 245 consultas, ele achou a rota mais curta em 100% dos casos. A BFS, em 44,9%. A DFS ficou em média 1.399 km acima do ótimo.”

Demonstração: aba Dijkstra – ordem de fixação, mostrando as distâncias crescendo até Londrina. Se sobrar tempo, trocar o destino para outra cidade sugerida pelo professor.

Passar a palavra: *“O Iury Hilário mostra a ordenação dos pedidos.”*

## Iury Hilário – Ordenação (11:00–15:00)

**Slide 9 – Os três algoritmos (1 min 30 s)**

> “O Heap Sort monta um heap máximo no próprio vetor e tira o maior a cada passo, sem memória extra. O Quick Sort divide o vetor em torno de um pivô. O Merge Sort divide ao meio e intercala as metades, e é o único estável dos três.”

> “Testamos o Quick Sort em duas versões: com o pivô no último elemento, a versão clássica, e com a mediana de três.”

Demonstração (página 4, aba Ordenar pedidos): ordenar por valor do frete, decrescente, alternando os três algoritmos. Mostrar que o resultado é o mesmo e que mudam o tempo, as comparações e as trocas.

**Slide 10 – O experimento (2 min 30 s)**

> “Rodamos os quatro com os mesmos dados: 100, 500, 1.000, 5.000 e 10.000 pedidos, em ordem aleatória, já ordenados e invertidos.”

> “O resultado mais forte: com o pivô fixo, ordenar 10.000 pedidos que já estavam ordenados levou 23,6 segundos e fez 49.995.000 comparações, exatamente n vezes n menos 1 dividido por 2. É o pior caso, O(n²). Com a mediana de três, o mesmo teste levou 0,07 segundo.”

> “No gráfico em escala logarítmica, a linha azul sobe com o dobro da inclinação das outras. Isso é n² contra n log n.”

Demonstração: aba Resultados do experimento, cenário Ordenado, métrica Comparações. Se o professor pedir, rodar ao vivo na aba Rodar ao vivo com 100, 500 e 1.000 pedidos (leva poucos segundos).

Passar a palavra: *“O Matheus Machado fecha com a análise de complexidade.”*

## Matheus Machado – Resultados e análise (15:00–18:00)

**Slide 11 – Complexidade (50 s)**

> “A tabela resume o custo de cada algoritmo. Os três de ordenação são O(n log n) no caso médio, mas só o Quick Sort tem pior caso O(n²). Em memória, o Merge Sort usa O(n): nos testes, 156 KB contra 78 KB dos outros. O Dijkstra custa O((V+E) log V), mais que BFS e DFS, por causa da fila de prioridade.”

**Slide 12 – Hipóteses (50 s)**

> “Antes dos testes escrevemos seis hipóteses, e as seis foram confirmadas. Destaque para duas: o Dijkstra achou a rota mais curta mesmo quando ela tinha mais trechos, o que aconteceu em 18% das consultas; e mais dados de treino melhoraram a árvore, de 66% para 76% de acerto.”

**Slide 13 – Conclusão e limitações (50 s)**

> “Para este problema: Dijkstra nas rotas, Merge Sort ou Quick Sort com mediana de três na fila de expedição, e a árvore ID3 para prever atrasos. As limitações: os pedidos são simulados e as distâncias são estimadas pela linha reta vezes 1,3.”

> “A principal lição: resolver o problema não é só achar uma resposta, é escolher o algoritmo certo e justificar com números.”

**Slide 14 – Obrigado (30 s)**

Agradecer e abrir para perguntas. Deixar a página 5 do sistema aberta: ela tem as 8 questões do enunciado respondidas com os dados.

## Preparação e perguntas prováveis

**Checklist antes de apresentar**

- [ ] Conferir os nomes no roteiro e nos slides 1 e 14.
- [ ] Abrir o sistema publicado e testar as 5 páginas no computador da sala. Plano B: rodar localmente com `streamlit run app.py`, que usa os CSVs sem internet.
- [ ] Conferir que a base tem 300 pedidos, sem pedidos de teste esquecidos, para os números baterem com os slides.
- [ ] Ensaiar com cronômetro: o total deve ficar entre 16 e 19 minutos.
- [ ] Cada integrante revisar o arquivo do seu módulo em `modulos/` e saber apontar as linhas principais.

**Perguntas prováveis do professor**

| Pergunta | Quem responde primeiro | Resposta curta | Onde mostrar |
| --- | --- | --- | --- |
| Onde a entropia é calculada? | Mateus Soares | Função `entropia()`: conta cada classe e soma −p·log₂ p | `modulos/entropia.py` |
| Por que o ID3 precisa de faixas? | Mateus Soares | Ele só divide por valores categóricos; números contínuos criariam um ramo por valor | Página 1, aba Estrutura da base |
| Mude um atributo e mostre o efeito | Mateus Soares | Na barra lateral da página 2, tirar `faixa_distancia`: a raiz vira `veiculo` e o acerto cai de 80% para 67% | Página 2 |
| Por que a BFS não acha a rota mais curta? | Felipe Evangelista | Ela conta trechos, não km; só é ótima se todas as arestas tiverem o mesmo peso | Página 3 |
| O que acontece com peso negativo no Dijkstra? | Felipe Evangelista | Ele pode fixar uma cidade cedo demais e errar; o sistema recusa peso negativo | `modulos/grafo.py` |
| Onde está a fila de prioridade? | Felipe Evangelista | Classe `HeapMinimo`, com subir e descer do heap | `modulos/dijkstra.py` |
| Por que o Quick Sort usa uma pilha e não recursão? | Iury Hilário | No pior caso seriam 10.000 chamadas, acima do limite do Python; a lógica é a mesma | `modulos/quick_sort.py` |
| Por que o Merge Sort é estável? | Iury Hilário | No empate, pega primeiro o elemento da metade esquerda | `modulos/merge_sort.py` |
| Calcule os filhos do índice 3 no heap | Iury Hilário | 2·3+1 = 7 e 2·3+2 = 8; o pai é (3−1)/2 = 1 | `modulos/heap_sort.py` |
| Os dados são reais? | Matheus Machado | Cidades sim (IBGE); rotas estimadas; pedidos simulados com regras e semente fixa | Página 1, aba Cidades e rotas |
| Vocês usaram alguma função pronta? | Matheus Machado | Não: `sort()` e `sorted()` aparecem só nos testes, para conferir o resultado | `tests/test_algoritmos.py` |
