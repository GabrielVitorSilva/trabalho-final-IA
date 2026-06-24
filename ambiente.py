# ambiente.py
# Representa o "mundo" do Wumpus: a matriz NxN com poços, Wumpus e ouro.
# Tambem e responsavel por gerar o mundo aleatoriamente, mas garantindo
# que ele seja sempre solucionavel (existe caminho seguro até o ouro e de volta).

import random
from busca import vizinhos, bfs_caminho


class Ambiente:
    def __init__(self, tamanho=4, num_pocos=3, semente=None, num_wumpus=1, wumpus_movel=False):
        self.tamanho = tamanho
        self.num_pocos = num_pocos
        self.num_wumpus = max(1, num_wumpus)
        self.wumpus_movel = wumpus_movel
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

        # Sorteia as posicoes dos Wumpus (nao podem ser a inicial nem o ouro,
        # e nao podem ser vizinhos da posicao inicial, para o inicio ser seguro)
        vizinhos_inicio = set(vizinhos(self.posicao_inicial, tamanho))
        candidatos_wumpus = [c for c in todas_celulas if c not in vizinhos_inicio]
        if len(candidatos_wumpus) < self.num_wumpus:
            candidatos_wumpus = list(todas_celulas)
        self.rng.shuffle(candidatos_wumpus)
        qtd_wumpus = min(self.num_wumpus, len(candidatos_wumpus))
        self.wumpus_posicoes = set(candidatos_wumpus[:qtd_wumpus])
        for pos in self.wumpus_posicoes:
            if pos in todas_celulas:
                todas_celulas.remove(pos)
        self.posicoes_wumpus_mortos = set()
        self._atualizar_resumo_wumpus()

        # Sorteia as posicoes dos poços (nao podem ser a inicial nem vizinhas dela)
        candidatos_pocos = [c for c in todas_celulas if c not in vizinhos_inicio]
        self.rng.shuffle(candidatos_pocos)
        qtd = min(self.num_pocos, len(candidatos_pocos))
        self.pocos = set(candidatos_pocos[:qtd])

    def _atualizar_resumo_wumpus(self):
        """Mantem atributos de compatibilidade com o restante do projeto."""
        self.wumpus_vivo = bool(self.wumpus_posicoes)
        self.wumpus = next(iter(sorted(self.wumpus_posicoes)), None)
        self.posicao_wumpus_morto = next(iter(sorted(self.posicoes_wumpus_mortos)), None)

    def tem_wumpus_em(self, pos):
        """Retorna True se houver um Wumpus vivo naquela celula."""
        return pos in self.wumpus_posicoes

    def matar_wumpus(self, pos=None):
        """Elimina um Wumpus vivo e registra a posicao onde ele morreu."""
        if not self.wumpus_posicoes:
            return False
        alvo = pos
        if alvo is None:
            alvo = next(iter(sorted(self.wumpus_posicoes)))
        if alvo not in self.wumpus_posicoes:
            return False
        self.wumpus_posicoes.remove(alvo)
        self.posicoes_wumpus_mortos.add(alvo)
        self._atualizar_resumo_wumpus()
        return True

    def disparar_flecha(self, origem, direcao):
        """
        Dispara uma flecha em linha reta a partir de 'origem'.
        A flecha percorre a linha ate a borda; se encontrar o Wumpus vivo,
        ele e eliminado.
        Retorna um par (acertou, posicao_acertada).
        """
        deslocamentos = {
            "cima": (-1, 0),
            "baixo": (1, 0),
            "esquerda": (0, -1),
            "direita": (0, 1),
        }
        if direcao not in deslocamentos:
            return False, None

        dl, dc = deslocamentos[direcao]
        l, c = origem
        while True:
            l += dl
            c += dc
            if not (0 <= l < self.tamanho and 0 <= c < self.tamanho):
                return False, None
            if (l, c) in self.wumpus_posicoes:
                self.matar_wumpus((l, c))
                return True, (l, c)

    def mover_wumpus(self, posicao_agente=None):
        """
        Move cada Wumpus vivo uma casa aleatoria, se o modo dinamico estiver
        ativo. Retorna True se algum Wumpus encostou na posicao do agente.
        """
        if not self.wumpus_movel or not self.wumpus_posicoes:
            return False

        vivos_atuais = list(self.wumpus_posicoes)
        self.rng.shuffle(vivos_atuais)
        novos_vivos = set()
        colidiu_com_agente = False

        for pos in vivos_atuais:
            if pos in self.posicoes_wumpus_mortos:
                continue
            candidatos = []
            ocupacoes = novos_vivos | (self.wumpus_posicoes - {pos}) | self.pocos | {self.posicao_inicial, self.ouro}
            for viz in vizinhos(pos, self.tamanho):
                if viz in ocupacoes:
                    continue
                candidatos.append(viz)
            if candidatos:
                novo = self.rng.choice(candidatos)
            else:
                novo = pos
            novos_vivos.add(novo)
            if posicao_agente is not None and novo == posicao_agente:
                colidiu_com_agente = True

        self.wumpus_posicoes = novos_vivos
        self._atualizar_resumo_wumpus()
        return colidiu_com_agente

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
                if pos in self.pocos or pos in self.wumpus_posicoes:
                    continue
                # uma celula e "limpa" se nenhum vizinho dela e perigo
                limpa = True
                for viz in vizinhos(pos, self.tamanho):
                    if viz in self.pocos or viz in self.wumpus_posicoes:
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
            if viz in self.wumpus_posicoes:
                cheiro = True

        brilho = (pos == self.ouro)

        return {"brisa": brisa, "cheiro": cheiro, "brilho": brilho}

    def verificar_perigo(self, pos):
        """Retorna 'poco', 'wumpus' ou None, indicando se a posicao e letal."""
        if pos in self.pocos:
            return "poco"
        if pos in self.wumpus_posicoes:
            return "wumpus"
        return None
