"""Árvore de Decisão – algoritmo ID3 (Quinlan, 1986), implementado do zero.

ID3(S, atributos):
    se todos os registros de S têm a mesma classe → folha com essa classe
    se não restam atributos (ou S abaixo do mínimo) → folha com a classe majoritária
    A ← atributo de MAIOR GANHO DE INFORMAÇÃO
    para cada valor v de A:
        filho_v ← ID3(S_v, atributos − {A})   (S_v vazio → folha majoritária)

Custo de construção: O(a² · n) no pior caso (a = nº de atributos, n = registros):
em cada nível o ganho de até a atributos é calculado sobre os n registros.
Classificação de um registro: O(profundidade) ≤ O(a).
"""
from modulos.entropia import contar, entropia, ganho_informacao, particionar


class No:
    def __init__(self, atributo=None, classe=None, registros=0, distribuicao=None,
                 entropia=0.0, ganho=None):
        self.atributo = atributo        # None → folha
        self.classe = classe            # classe majoritária no nó
        self.filhos = {}                # valor do atributo → No
        self.registros = registros
        self.distribuicao = distribuicao or {}
        self.entropia = entropia
        self.ganho = ganho

    @property
    def folha(self):
        return self.atributo is None


def _majoritaria(rotulos):
    cont = contar(rotulos)
    melhor, qtd = None, -1
    for classe, q in cont.items():
        if q > qtd:
            melhor, qtd = classe, q
    return melhor


class ID3:
    def __init__(self, min_registros=2, profundidade_max=None):
        self.min_registros = min_registros
        self.profundidade_max = profundidade_max
        self.raiz = None
        self.alvo = None
        self.atributos = []
        self.passos = []  # log de ganhos calculados em cada nó (para o relatório)
        self.calculos_entropia = 0

    # ---------------------------------------------------------------- treino
    def treinar(self, registros, atributos, alvo):
        self.alvo, self.atributos = alvo, list(atributos)
        self.dominio = {a: list(contar([r[a] for r in registros]).keys()) for a in atributos}
        self.passos, self.calculos_entropia = [], 0
        self.raiz = self._construir(registros, list(atributos), 0, "raiz")
        return self

    def _construir(self, registros, atributos, prof, caminho):
        rotulos = [r[self.alvo] for r in registros]
        h = entropia(rotulos)
        self.calculos_entropia += 1
        no = No(classe=_majoritaria(rotulos), registros=len(registros),
                distribuicao=contar(rotulos), entropia=h)

        if h == 0 or not atributos or len(registros) < self.min_registros or \
                (self.profundidade_max is not None and prof >= self.profundidade_max):
            return no

        ganhos = {}
        melhor, melhor_ganho = None, -1.0
        for a in atributos:  # empate → primeiro atributo da lista
            g, _ = ganho_informacao(registros, a, self.alvo)
            self.calculos_entropia += 1 + len(self.dominio[a])
            ganhos[a] = g
            if g > melhor_ganho:
                melhor, melhor_ganho = a, g
        self.passos.append({"no": caminho, "registros": len(registros), "entropia": h,
                            "ganhos": ganhos, "escolhido": melhor})

        if melhor_ganho <= 0:
            return no

        no.atributo, no.ganho = melhor, melhor_ganho
        restantes = [a for a in atributos if a != melhor]
        grupos = particionar(registros, melhor)
        for valor in self.dominio[melhor]:
            sub = grupos.get(valor, [])
            if not sub:
                no.filhos[valor] = No(classe=no.classe, registros=0)
            else:
                no.filhos[valor] = self._construir(sub, restantes, prof + 1,
                                                   f"{caminho} → {melhor}={valor}")
        return no

    # ---------------------------------------------------------------- uso
    def classificar(self, registro, explicar=False):
        no, trilha = self.raiz, []
        while not no.folha:
            valor = registro.get(no.atributo)
            trilha.append(f"{no.atributo} = {valor}")
            if valor not in no.filhos:  # valor desconhecido → majoritária do nó
                break
            no = no.filhos[valor]
        return (no.classe, trilha) if explicar else no.classe

    def avaliar(self, registros):
        """Acurácia e matriz de confusão sobre registros de teste."""
        classes = list(contar([r[self.alvo] for r in registros]).keys())
        for c in self.raiz.distribuicao:
            if c not in classes:
                classes.append(c)
        matriz = {real: {prev: 0 for prev in classes} for real in classes}
        acertos = 0
        for r in registros:
            prev = self.classificar(r)
            matriz[r[self.alvo]][prev] = matriz[r[self.alvo]].get(prev, 0) + 1
            acertos += prev == r[self.alvo]
        return {"acuracia": acertos / len(registros) if registros else 0.0,
                "acertos": acertos, "total": len(registros), "matriz": matriz}

    # ---------------------------------------------------------------- inspeção
    def regras(self):
        """Lista de regras SE ... ENTÃO ... (uma por folha)."""
        saida = []

        def percorrer(no, conds):
            if no.folha:
                if no.registros > 0:
                    se = " E ".join(conds) if conds else "(sempre)"
                    saida.append({"regra": f"SE {se} ENTÃO {self.alvo} = {no.classe}",
                                  "classe": no.classe, "suporte": no.registros,
                                  "distribuicao": no.distribuicao})
                return
            for valor, filho in no.filhos.items():
                percorrer(filho, conds + [f"{no.atributo} = {valor}"])

        percorrer(self.raiz, [])
        return saida

    def estatisticas(self):
        nos = folhas = prof = 0

        def percorrer(no, d):
            nonlocal nos, folhas, prof
            nos += 1
            prof = max(prof, d)
            if no.folha:
                folhas += 1
            for f in no.filhos.values():
                percorrer(f, d + 1)

        percorrer(self.raiz, 0)
        return {"nos": nos, "folhas": folhas, "profundidade": prof,
                "calculos_entropia": self.calculos_entropia}

    def para_dot(self):
        """Árvore no formato Graphviz DOT (renderizada pelo Streamlit)."""
        linhas = ['digraph ID3 {', 'node [fontname="Helvetica", fontsize=10];',
                  'edge [fontname="Helvetica", fontsize=9];']
        cont = [0]

        def nid():
            cont[0] += 1
            return f"n{cont[0]}"

        def percorrer(no):
            i = nid()
            dist = ", ".join(f"{k}: {v}" for k, v in no.distribuicao.items())
            if no.folha:
                cor = "#d4edda" if no.classe == "No prazo" else "#f8d7da"
                linhas.append(f'{i} [shape=box, style="rounded,filled", fillcolor="{cor}", '
                              f'label="{no.classe}\\n({dist or "sem registros"})"];')
            else:
                linhas.append(f'{i} [shape=ellipse, style=filled, fillcolor="#dbe9f6", '
                              f'label="{no.atributo}\\nH={no.entropia:.3f} · G={no.ganho:.3f}\\n'
                              f'n={no.registros}"];')
                for valor, filho in no.filhos.items():
                    j = percorrer(filho)
                    linhas.append(f'{i} -> {j} [label="{valor}"];')
            return i

        percorrer(self.raiz)
        linhas.append("}")
        return "\n".join(linhas)
