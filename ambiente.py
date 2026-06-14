# ambiente.py
# Representa o "mundo" do Wumpus: a matriz NxN com poços, Wumpus e ouro.
# Tambem e responsavel por gerar o mundo aleatoriamente, mas garantindo
# que ele seja sempre solucionavel (existe caminho seguro até o ouro e de volta).

import random
from busca import vizinhos, bfs_caminho


class Ambiente:
    def __init__(self, tamanho=4, num_pocos=3, semente=None):
        self.tamanho = tamanho
        self.num_pocos = num_pocos
        self.rng = random.Random(semente)

        # Gera o mundo repetidamente até encontrar um que seja valido (solucionavel)
        while True:
            self._gerar_mundo()
            if self._mundo_eh_valido():
                break

    # ------------------------------------------------------------------
    # GERACAO DO MUNDO
    # ------------------------------------------------------------------
    def _gerar_mundo(self):
        """Sorteia as posicoes do agente, ouro, Wumpus e poços."""
        tamanho = self.tamanho

        # Posicao inicial do agente: sempre o canto (0,0), que sera garantido seguro
        self.posicao_inicial = (0, 0)

        # Lista com todas as celulas, exceto a inicial
        todas_celulas = [
            (l, c) for l in range(tamanho) for c in range(tamanho)
            if (l, c) != self.posicao_inicial
        ]
        self.rng.shuffle(todas_celulas)

        # Sorteia a posicao do ouro
        self.ouro = todas_celulas.pop()

        # Sorteia a posicao do Wumpus (nao pode ser a inicial nem o ouro,
        # e nao pode ser vizinho da posicao inicial, para o inicio ser seguro)
        vizinhos_inicio = set(vizinhos(self.posicao_inicial, tamanho))
        candidatos_wumpus = [c for c in todas_celulas if c not in vizinhos_inicio]
        if not candidatos_wumpus:
            candidatos_wumpus = todas_celulas
        self.wumpus = candidatos_wumpus[0]
        todas_celulas.remove(self.wumpus)

        # Sorteia as posicoes dos poços (nao podem ser a inicial nem vizinhas dela)
        candidatos_pocos = [c for c in todas_celulas if c not in vizinhos_inicio]
        self.rng.shuffle(candidatos_pocos)
        qtd = min(self.num_pocos, len(candidatos_pocos))
        self.pocos = set(candidatos_pocos[:qtd])

    def _mundo_eh_valido(self):
        """
        Verifica se existe um caminho do inicio até o ouro formado apenas
        por celulas "limpas" (sem poço e sem Wumpus em nenhuma celula
        vizinha). Isso e mais forte do que apenas "sem perigo na celula":
        garante que, ao andar por esse caminho, o agente vai sentir
        "Nada" (sem brisa, sem cheiro) em cada celula e, pela regra de
        inferencia, vai poder marcar a proxima celula do caminho como
        segura ANTES de andar para ela. Ou seja, o caminho e descobrivel
        pelo agente usando apenas suas regras de inferencia, sem sorte.

        O gerador usa o mapa real apenas para essa validacao -- o agente
        nunca tem acesso a essa informacao.
        """
        celulas_limpas = set()
        for l in range(self.tamanho):
            for c in range(self.tamanho):
                pos = (l, c)
                if pos in self.pocos or pos == self.wumpus:
                    continue
                # uma celula e "limpa" se nenhum vizinho dela e perigo
                limpa = True
                for viz in vizinhos(pos, self.tamanho):
                    if viz in self.pocos or viz == self.wumpus:
                        limpa = False
                        break
                if limpa:
                    celulas_limpas.add(pos)

        if self.posicao_inicial not in celulas_limpas:
            return False
        if self.ouro not in celulas_limpas:
            return False

        caminho = bfs_caminho(
            self.posicao_inicial, self.ouro, celulas_limpas, self.tamanho
        )
        return caminho is not None

    # ------------------------------------------------------------------
    # PERCEPCOES E REGRAS DO JOGO
    # ------------------------------------------------------------------
    def obter_percepcoes(self, pos):
        """
        Retorna um dicionario com as percepcoes da celula 'pos':
        - brisa: True se ha poço em alguma celula adjacente
        - cheiro: True se o Wumpus esta em alguma celula adjacente
        - brilho: True se o ouro esta nesta celula
        """
        brisa = False
        cheiro = False
        for viz in vizinhos(pos, self.tamanho):
            if viz in self.pocos:
                brisa = True
            if viz == self.wumpus:
                cheiro = True

        brilho = (pos == self.ouro)

        return {"brisa": brisa, "cheiro": cheiro, "brilho": brilho}

    def verificar_perigo(self, pos):
        """Retorna 'poco', 'wumpus' ou None, indicando se a posicao e letal."""
        if pos in self.pocos:
            return "poco"
        if pos == self.wumpus:
            return "wumpus"
        return None
