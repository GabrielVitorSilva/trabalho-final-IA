# interface.py
# Responsavel por toda a parte grafica usando Pygame:
# desenha o grid do mundo, o agente, e o painel lateral com informacoes.

import pygame

# Largura do painel lateral, em pixels
LARGURA_PAINEL = 320

# Cores (R, G, B)
COR_FUNDO = (30, 30, 30)
COR_NAO_VISITADA = (120, 120, 120)      # cinza
COR_VISITADA = (173, 216, 230)          # azul claro
COR_SEGURA = (144, 238, 144)            # verde
COR_SUSPEITA_POCO = (255, 165, 0)       # laranja
COR_SUSPEITA_WUMPUS = (220, 20, 60)     # vermelho
COR_OURO = (255, 215, 0)                # dourado
COR_INICIAL = (255, 255, 255)           # branco
COR_AGENTE = (75, 0, 130)               # roxo (indigo)
COR_GRADE = (0, 0, 0)
COR_TEXTO = (255, 255, 255)


class Interface:
    def __init__(self, tamanho_mundo, tela_cheia=True):
        pygame.init()
        self.tamanho_mundo = tamanho_mundo
        self.tela_cheia = tela_cheia

        self._criar_janela()

        self.fonte = pygame.font.SysFont("arial", 16)
        self.fonte_pequena = pygame.font.SysFont("arial", 13)
        self.fonte_titulo = pygame.font.SysFont("arial", 18, bold=True)

    def _criar_janela(self):
        """Cria a janela do jogo, em tela cheia ou em modo normal."""
        if self.tela_cheia:
            self.tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.tela = pygame.display.set_mode((1000, 700))

        pygame.display.set_caption("Mundo de Wumpus - Agente Inteligente")

        self.largura_tela, self.altura_tela = self.tela.get_size()

        # Calcula o tamanho de cada celula do grid para caber na area
        # disponivel (largura total menos o painel lateral)
        largura_disponivel = self.largura_tela - LARGURA_PAINEL
        self.tamanho_celula = min(
            largura_disponivel // self.tamanho_mundo,
            self.altura_tela // self.tamanho_mundo,
        )
        self.tamanho_celula = max(30, self.tamanho_celula)

    def alternar_tela_cheia(self):
        """Liga/desliga o modo tela cheia (tecla F)."""
        self.tela_cheia = not self.tela_cheia
        self._criar_janela()

    def desenhar(self, ambiente, agente):
        self.tela.fill(COR_FUNDO)
        self._desenhar_grid(ambiente, agente)
        self._desenhar_painel(ambiente, agente)
        pygame.display.flip()

    # ------------------------------------------------------------------
    def _desenhar_grid(self, ambiente, agente):
        base = agente.base
        tamanho = ambiente.tamanho

        for linha in range(tamanho):
            for coluna in range(tamanho):
                pos = (linha, coluna)
                x = coluna * self.tamanho_celula
                y = linha * self.tamanho_celula
                rect = pygame.Rect(x, y, self.tamanho_celula, self.tamanho_celula)

                # Escolhe a cor de fundo da celula com base no conhecimento do agente
                cor = COR_NAO_VISITADA
                if pos in base.visitadas:
                    cor = COR_VISITADA
                elif pos in base.seguras:
                    cor = COR_SEGURA
                elif pos in base.suspeitas_poco and pos in base.suspeitas_wumpus:
                    cor = COR_SUSPEITA_WUMPUS  # combina, usa vermelho como prioridade visual
                elif pos in base.suspeitas_poco:
                    cor = COR_SUSPEITA_POCO
                elif pos in base.suspeitas_wumpus:
                    cor = COR_SUSPEITA_WUMPUS

                pygame.draw.rect(self.tela, cor, rect)
                pygame.draw.rect(self.tela, COR_GRADE, rect, 1)

                # Marca a posicao inicial com uma borda branca grossa
                if pos == ambiente.posicao_inicial:
                    pygame.draw.rect(self.tela, COR_INICIAL, rect, 4)

                # Mostra o ouro apenas se o agente ja sentiu o brilho ali
                # (so desenhamos se o agente ja visitou e percebeu brilho nessa posicao)
                if pos == ambiente.ouro and pos in base.visitadas:
                    centro = rect.center
                    pygame.draw.circle(self.tela, COR_OURO, centro, self.tamanho_celula // 4)

                # Desenha o agente na sua posicao atual
                if pos == agente.posicao:
                    centro = rect.center
                    pygame.draw.circle(self.tela, COR_AGENTE, centro, self.tamanho_celula // 3)

                # Mostra coordenadas pequenas no canto da celula (ajuda na apresentacao)
                texto_pos = self.fonte_pequena.render(f"{linha},{coluna}", True, (50, 50, 50))
                self.tela.blit(texto_pos, (x + 4, y + 4))

    # ------------------------------------------------------------------
    def _desenhar_painel(self, ambiente, agente):
        base = agente.base
        x0 = ambiente.tamanho * self.tamanho_celula + 10
        y = 10

        def escrever(texto, fonte=None, cor=COR_TEXTO):
            nonlocal y
            fonte = fonte or self.fonte
            superficie = fonte.render(texto, True, cor)
            self.tela.blit(superficie, (x0, y))
            y += superficie.get_height() + 4

        escrever("MUNDO DE WUMPUS", self.fonte_titulo)
        y += 6

        escrever("Percepcoes atuais:", self.fonte_titulo)
        p = agente.ultimas_percepcoes
        escrever(f"  Brisa:  {'Sim' if p['brisa'] else 'Nao'}")
        escrever(f"  Cheiro: {'Sim' if p['cheiro'] else 'Nao'}")
        escrever(f"  Brilho: {'Sim' if p['brilho'] else 'Nao'}")
        y += 6

        escrever("Status:", self.fonte_titulo)
        escrever(f"  Posicao: {agente.posicao}")
        escrever(f"  Ultima acao: {agente.ultima_acao}")
        escrever(f"  Ouro encontrado: {'Sim' if base.ouro_encontrado else 'Nao'}")
        escrever(f"  Modo retorno: {'Sim' if base.modo_retorno else 'Nao'}")
        y += 6

        escrever("Contadores:", self.fonte_titulo)
        escrever(f"  Visitadas: {len(base.visitadas)}")
        escrever(f"  Seguras: {len(base.seguras)}")
        escrever(f"  Suspeitas poço: {len(base.suspeitas_poco)}")
        escrever(f"  Suspeitas Wumpus: {len(base.suspeitas_wumpus)}")
        y += 6

        if base.jogo_finalizado:
            escrever("RESULTADO:", self.fonte_titulo)
            escrever(f"  {base.mensagem_final}")
            escrever("  Pressione R para reiniciar")
            y += 6

        # Log de eventos (mostra as ultimas linhas que cabem na tela)
        escrever("Log de eventos:", self.fonte_titulo)
        espaco_restante = self.altura_tela - y
        max_linhas = max(1, espaco_restante // 18)
        ultimas = base.log[-max_linhas:]
        for linha_log in ultimas:
            escrever("  " + linha_log, self.fonte_pequena)

    # ------------------------------------------------------------------
    def fechar(self):
        pygame.quit()
