# interface.py
# Responsavel por toda a parte grafica usando Pygame:
# desenha o grid do mundo, o agente, e o painel lateral com informacoes.
#
# Todos os "icones" (Wumpus, ouro, agente) sao desenhados na hora com
# formas geometricas do proprio Pygame -- nao usamos nenhuma imagem
# externa, para manter o projeto simples e sem dependencias extras.

import math
import pygame

# Largura do painel lateral, em pixels
LARGURA_PAINEL = 360

# ----------------------------------------------------------------------
# PALETA DE CORES
# ----------------------------------------------------------------------
# Fundo (gradiente escuro azulado, simulado com duas cores)
COR_FUNDO_TOPO = (24, 28, 46)
COR_FUNDO_BASE = (12, 14, 24)

# Cores das celulas do grid
COR_NAO_VISITADA = (58, 64, 86)         # azul acinzentado escuro
COR_NAO_VISITADA_BORDA = (78, 86, 112)
COR_VISITADA = (94, 168, 224)           # azul claro vibrante
COR_SEGURA = (88, 196, 134)             # verde esmeralda
COR_SUSPEITA_POCO = (240, 165, 60)      # laranja
COR_SUSPEITA_WUMPUS = (224, 80, 90)     # vermelho coral
COR_OURO = (255, 209, 84)               # dourado
COR_OURO_BRILHO = (255, 240, 180)
COR_INICIAL = (255, 255, 255)           # branco
COR_AGENTE = (152, 110, 240)            # roxo vibrante
COR_GRADE = (18, 20, 32)

# Cores do texto e do painel
COR_TEXTO = (235, 238, 245)
COR_TEXTO_FRACO = (160, 170, 190)
COR_PAINEL_FUNDO = (20, 22, 38)
COR_PAINEL_CARD = (32, 36, 58)
COR_PAINEL_BORDA = (60, 66, 96)
COR_DESTAQUE = (255, 209, 84)           # dourado, usado em titulos
COR_OK = (110, 220, 150)
COR_ALERTA = (235, 110, 110)


def cor_intermediaria(cor_a, cor_b, fator):
    """Mistura duas cores (r,g,b) de acordo com 'fator' entre 0 e 1."""
    return tuple(
        int(cor_a[i] + (cor_b[i] - cor_a[i]) * fator) for i in range(3)
    )


class Interface:
    def __init__(self, tamanho_mundo, tela_cheia=True):
        pygame.init()
        self.tamanho_mundo = tamanho_mundo
        self.tela_cheia = tela_cheia

        self._criar_janela()

        self.fonte = pygame.font.SysFont("arial", 17)
        self.fonte_pequena = pygame.font.SysFont("arial", 13)
        self.fonte_titulo = pygame.font.SysFont("arial", 19, bold=True)
        self.fonte_grande = pygame.font.SysFont("arial", 26, bold=True)

        # Contador usado para pequenas animacoes (pulsar do agente, brilho do ouro)
        self.tempo_animacao = 0

    def _criar_janela(self):
        """Cria a janela do jogo, em tela cheia ou em modo normal."""
        if self.tela_cheia:
            self.tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.tela = pygame.display.set_mode((1100, 750))

        pygame.display.set_caption("Mundo de Wumpus - Agente Inteligente")

        self.largura_tela, self.altura_tela = self.tela.get_size()

        # Calcula o tamanho de cada celula do grid para caber na area
        # disponivel (largura total menos o painel lateral), com uma
        # pequena margem ao redor do tabuleiro
        self.margem = 16
        largura_disponivel = self.largura_tela - LARGURA_PAINEL - self.margem * 2
        altura_disponivel = self.altura_tela - self.margem * 2
        self.tamanho_celula = min(
            largura_disponivel // self.tamanho_mundo,
            altura_disponivel // self.tamanho_mundo,
        )
        self.tamanho_celula = max(28, self.tamanho_celula)

        # Pre-renderiza o fundo em gradiente (so precisa ser feito de novo
        # quando a janela muda de tamanho)
        self._fundo = self._criar_fundo_gradiente()

    def alternar_tela_cheia(self):
        """Liga/desliga o modo tela cheia (tecla F)."""
        self.tela_cheia = not self.tela_cheia
        self._criar_janela()

    # ------------------------------------------------------------------
    # FUNDO
    # ------------------------------------------------------------------
    def _criar_fundo_gradiente(self):
        """Cria uma superficie com um gradiente vertical simples."""
        fundo = pygame.Surface((self.largura_tela, self.altura_tela))
        altura = self.altura_tela
        for y in range(altura):
            fator = y / max(1, altura - 1)
            cor = cor_intermediaria(COR_FUNDO_TOPO, COR_FUNDO_BASE, fator)
            pygame.draw.line(fundo, cor, (0, y), (self.largura_tela, y))
        return fundo

    # ------------------------------------------------------------------
    def desenhar(self, ambiente, agente):
        self.tempo_animacao += 1
        self.tela.blit(self._fundo, (0, 0))
        self._desenhar_grid(ambiente, agente)
        self._desenhar_painel(ambiente, agente)
        pygame.display.flip()

    # ------------------------------------------------------------------
    # GRID DO MUNDO
    # ------------------------------------------------------------------
    def _desenhar_grid(self, ambiente, agente):
        base = agente.base
        tamanho = ambiente.tamanho
        t = self.tamanho_celula

        for linha in range(tamanho):
            for coluna in range(tamanho):
                pos = (linha, coluna)
                x = self.margem + coluna * t
                y = self.margem + linha * t
                rect = pygame.Rect(x, y, t, t)

                # Escolhe a cor de fundo da celula com base no conhecimento do agente
                cor = COR_NAO_VISITADA
                cor_borda = COR_NAO_VISITADA_BORDA
                if pos in base.visitadas:
                    cor = COR_VISITADA
                    cor_borda = cor_intermediaria(cor, (255, 255, 255), 0.3)
                elif pos in base.seguras:
                    cor = COR_SEGURA
                    cor_borda = cor_intermediaria(cor, (255, 255, 255), 0.3)
                elif pos in base.suspeitas_poco and pos in base.suspeitas_wumpus:
                    cor = COR_SUSPEITA_WUMPUS
                    cor_borda = cor_intermediaria(cor, (255, 255, 255), 0.3)
                elif pos in base.suspeitas_poco:
                    cor = COR_SUSPEITA_POCO
                    cor_borda = cor_intermediaria(cor, (255, 255, 255), 0.3)
                elif pos in base.suspeitas_wumpus:
                    cor = COR_SUSPEITA_WUMPUS
                    cor_borda = cor_intermediaria(cor, (255, 255, 255), 0.3)

                # Celula com cantos arredondados, para um visual mais suave
                pygame.draw.rect(self.tela, cor, rect, border_radius=8)
                pygame.draw.rect(self.tela, cor_borda, rect, width=2, border_radius=8)

                # Marca a posicao inicial com uma borda dourada grossa
                if pos == ambiente.posicao_inicial:
                    pygame.draw.rect(self.tela, COR_INICIAL, rect, width=3, border_radius=8)
                    rotulo = self.fonte_pequena.render("INICIO", True, (40, 40, 40))
                    self.tela.blit(rotulo, (x + 6, y + t - 18))

                # Mostra o ouro apenas se o agente ja visitou a celula (ja viu o brilho)
                if pos == ambiente.ouro and pos in base.visitadas:
                    self._desenhar_ouro(rect)

                # Desenha o agente na sua posicao atual
                if pos == agente.posicao:
                    self._desenhar_agente(rect)

                # Se o Wumpus foi eliminado, mostra a "carcaca" na celula onde
                # ele morreu, para evidenciar o uso da flecha.
                if not ambiente.wumpus_vivo and pos == ambiente.posicao_wumpus_morto:
                    self._desenhar_wumpus_morto(rect)

                # Mostra coordenadas pequenas no canto da celula (ajuda na apresentacao)
                texto_pos = self.fonte_pequena.render(f"{linha},{coluna}", True, (255, 255, 255))
                texto_pos.set_alpha(90)
                self.tela.blit(texto_pos, (x + 5, y + 4))

                # Desenha um pequeno "monstro" do Wumpus nas celulas suspeitas
                # de Wumpus, para deixar o perigo visualmente reconhecivel
                if pos in base.suspeitas_wumpus and pos not in base.visitadas:
                    self._desenhar_wumpus_mini(rect)

                # Desenha um simbolo de poço (~) nas celulas suspeitas de poço
                if pos in base.suspeitas_poco and pos not in base.visitadas:
                    self._desenhar_poco_mini(rect)

    # ------------------------------------------------------------------
    # "ICONES" DESENHADOS NA HORA (sem imagens externas)
    # ------------------------------------------------------------------
    def _desenhar_ouro(self, rect):
        """Desenha uma pilha de moedas douradas, com um leve brilho pulsante."""
        cx, cy = rect.center
        t = rect.width
        pulso = (math.sin(self.tempo_animacao * 0.12) + 1) / 2  # 0..1
        raio_brilho = int(t * 0.42 + pulso * 3)

        # Brilho de fundo (circulo translucido)
        brilho = pygame.Surface((raio_brilho * 2, raio_brilho * 2), pygame.SRCALPHA)
        pygame.draw.circle(brilho, (*COR_OURO_BRILHO, 70), (raio_brilho, raio_brilho), raio_brilho)
        self.tela.blit(brilho, (cx - raio_brilho, cy - raio_brilho))

        # "Moedas" -- tres circulos dourados sobrepostos
        raio_moeda = max(4, t // 7)
        offsets = [(-raio_moeda, raio_moeda // 2), (raio_moeda, raio_moeda // 2), (0, -raio_moeda // 2)]
        for ox, oy in offsets:
            pygame.draw.circle(self.tela, COR_OURO, (cx + ox, cy + oy), raio_moeda)
            pygame.draw.circle(self.tela, (180, 140, 30), (cx + ox, cy + oy), raio_moeda, 2)

    def _desenhar_agente(self, rect):
        """Desenha o agente como um robozinho roxo simples, com 'olhos'."""
        cx, cy = rect.center
        t = rect.width
        raio = t // 3

        # Leve pulsacao para dar sensacao de "vivo"
        pulso = (math.sin(self.tempo_animacao * 0.2) + 1) / 2
        raio_atual = int(raio + pulso * 2)

        # Sombra suave
        sombra = pygame.Surface((raio_atual * 2 + 6, raio_atual * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(sombra, (0, 0, 0, 60), sombra.get_rect().center, raio_atual + 2)
        self.tela.blit(sombra, (cx - raio_atual - 3, cy - raio_atual - 3 + 3))

        # Corpo do agente
        pygame.draw.circle(self.tela, COR_AGENTE, (cx, cy), raio_atual)
        pygame.draw.circle(self.tela, (255, 255, 255), (cx, cy), raio_atual, 2)

        # "Olhos"
        olho_raio = max(2, raio_atual // 4)
        deslocamento = raio_atual // 2
        pygame.draw.circle(self.tela, (255, 255, 255), (cx - deslocamento, cy - 2), olho_raio)
        pygame.draw.circle(self.tela, (255, 255, 255), (cx + deslocamento, cy - 2), olho_raio)
        pygame.draw.circle(self.tela, (30, 20, 50), (cx - deslocamento, cy - 2), max(1, olho_raio // 2))
        pygame.draw.circle(self.tela, (30, 20, 50), (cx + deslocamento, cy - 2), max(1, olho_raio // 2))

    def _desenhar_wumpus_mini(self, rect):
        """Desenha um pequeno "rosto de monstro" representando o Wumpus suspeito."""
        cx, cy = rect.center
        t = rect.width
        raio = t // 4

        # Cabeca do monstro (forma arredondada escura avermelhada)
        pygame.draw.circle(self.tela, (90, 20, 25), (cx, cy), raio)

        # Chifres (dois triangulos no topo)
        ponta_y = cy - raio
        for sinal in (-1, 1):
            base_x = cx + sinal * (raio // 2)
            pygame.draw.polygon(
                self.tela,
                (60, 10, 15),
                [(base_x - 3, ponta_y + 3), (base_x + 3, ponta_y + 3), (base_x + sinal * 2, ponta_y - 6)],
            )

        # Olhos brilhantes (amarelos)
        olho_raio = max(2, raio // 3)
        pygame.draw.circle(self.tela, (255, 220, 80), (cx - raio // 2, cy - 1), olho_raio)
        pygame.draw.circle(self.tela, (255, 220, 80), (cx + raio // 2, cy - 1), olho_raio)
        pygame.draw.circle(self.tela, (30, 0, 0), (cx - raio // 2, cy - 1), max(1, olho_raio // 2))
        pygame.draw.circle(self.tela, (30, 0, 0), (cx + raio // 2, cy - 1), max(1, olho_raio // 2))

    def _desenhar_wumpus_morto(self, rect):
        """Desenha um Wumpus abatido, em tons acinzentados, para marcar o acerto."""
        cx, cy = rect.center
        t = rect.width
        raio = t // 4

        pygame.draw.circle(self.tela, (90, 90, 100), (cx, cy), raio)
        pygame.draw.line(self.tela, (210, 210, 220), (cx - raio // 2, cy - raio // 2), (cx + raio // 2, cy + raio // 2), 2)
        pygame.draw.line(self.tela, (210, 210, 220), (cx - raio // 2, cy + raio // 2), (cx + raio // 2, cy - raio // 2), 2)
        pygame.draw.circle(self.tela, (160, 160, 170), (cx - raio // 2, cy - 1), max(1, raio // 4))
        pygame.draw.circle(self.tela, (160, 160, 170), (cx + raio // 2, cy - 1), max(1, raio // 4))

    def _desenhar_poco_mini(self, rect):
        """Desenha um pequeno simbolo de ondas (~) representando um poço suspeito."""
        cx, cy = rect.center
        largura = rect.width // 2
        x0 = cx - largura // 2
        pontos = []
        for i in range(largura + 1):
            x = x0 + i
            y = cy + int(4 * math.sin((i / largura) * math.pi * 2 + self.tempo_animacao * 0.1))
            pontos.append((x, y))
        if len(pontos) >= 2:
            pygame.draw.lines(self.tela, (60, 40, 20), False, pontos, 3)

    # ------------------------------------------------------------------
    # PAINEL LATERAL
    # ------------------------------------------------------------------
    def _desenhar_painel(self, ambiente, agente):
        base = agente.base
        x0 = self.largura_tela - LARGURA_PAINEL

        # Fundo do painel
        painel_rect = pygame.Rect(x0, 0, LARGURA_PAINEL, self.altura_tela)
        pygame.draw.rect(self.tela, COR_PAINEL_FUNDO, painel_rect)
        pygame.draw.line(self.tela, COR_PAINEL_BORDA, (x0, 0), (x0, self.altura_tela), 2)

        margem = 18
        largura_card = LARGURA_PAINEL - margem * 2
        y = margem

        # ---- Titulo --------------------------------------------------
        titulo = self.fonte_grande.render("MUNDO DE WUMPUS", True, COR_DESTAQUE)
        self.tela.blit(titulo, (x0 + margem, y))
        y += titulo.get_height() + 4
        subtitulo = self.fonte_pequena.render("Agente inteligente baseado em conhecimento", True, COR_TEXTO_FRACO)
        self.tela.blit(subtitulo, (x0 + margem, y))
        y += subtitulo.get_height() + 14

        # ---- Card: percepcoes -----------------------------------------
        p = agente.ultimas_percepcoes
        linhas_percepcoes = [
            (f"Brisa", p["brisa"]),
            (f"Cheiro", p["cheiro"]),
            (f"Brilho", p["brilho"]),
        ]
        y = self._desenhar_card_percepcoes(x0 + margem, y, largura_card, "PERCEPCOES ATUAIS", linhas_percepcoes)
        y += 12

        # ---- Card: status ----------------------------------------------
        linhas_status = [
            f"Posicao atual: {agente.posicao}",
            f"Ultima acao: {agente.ultima_acao}",
            f"Ouro encontrado: {'Sim' if base.ouro_encontrado else 'Nao'}",
            f"Modo retorno: {'Sim' if base.modo_retorno else 'Nao'}",
            f"Flechas disponiveis: {base.flechas}",
            f"Wumpus vivo: {'Sim' if ambiente.wumpus_vivo else 'Nao'}",
        ]
        y = self._desenhar_card_texto(x0 + margem, y, largura_card, "STATUS DO AGENTE", linhas_status)
        y += 12

        # ---- Card: contadores (com legenda de cores) -------------------
        y = self._desenhar_card_contadores(x0 + margem, y, largura_card, base)
        y += 12

        # ---- Card: resultado (se o jogo terminou) -----------------------
        if base.jogo_finalizado:
            cor_resultado = COR_OK if "Sucesso" in base.mensagem_final else COR_ALERTA
            y = self._desenhar_card_resultado(x0 + margem, y, largura_card, base.mensagem_final, cor_resultado)
            y += 12

        # ---- Log de eventos ----------------------------------------------
        self._desenhar_log(x0 + margem, y, largura_card, base.log)

    # ------------------------------------------------------------------
    def _titulo_card(self, x, y, largura, titulo):
        """Desenha o cabecalho de um card e retorna o y onde o conteudo deve comecar."""
        rotulo = self.fonte_titulo.render(titulo, True, COR_DESTAQUE)
        self.tela.blit(rotulo, (x + 12, y + 8))
        # Linha decorativa abaixo do titulo
        linha_y = y + 8 + rotulo.get_height() + 4
        pygame.draw.line(self.tela, COR_PAINEL_BORDA, (x + 12, linha_y), (x + largura - 12, linha_y), 1)
        return linha_y + 8

    def _desenhar_card_percepcoes(self, x, y, largura, titulo, itens):
        altura = 8 + self.fonte_titulo.get_height() + 4 + 8 + 34 + 10
        rect = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(self.tela, COR_PAINEL_CARD, rect, border_radius=10)
        pygame.draw.rect(self.tela, COR_PAINEL_BORDA, rect, width=1, border_radius=10)

        y_conteudo = self._titulo_card(x, y, largura, titulo)

        # Desenha cada percepcao como uma "pílula" colorida (ativa/inativa)
        n = len(itens)
        espaco = largura - 24
        largura_pilula = espaco // n - 8
        xi = x + 12
        for nome, ativo in itens:
            cor_fundo = COR_OK if ativo else (50, 54, 78)
            cor_texto = (20, 30, 20) if ativo else COR_TEXTO_FRACO
            pilula = pygame.Rect(xi, y_conteudo, largura_pilula, 30)
            pygame.draw.rect(self.tela, cor_fundo, pilula, border_radius=15)
            texto = self.fonte.render(nome, True, cor_texto)
            self.tela.blit(texto, (pilula.centerx - texto.get_width() // 2, pilula.centery - texto.get_height() // 2))
            xi += largura_pilula + 8

        return y + altura

    def _desenhar_card_texto(self, x, y, largura, titulo, linhas):
        altura_conteudo = len(linhas) * 22
        altura = 8 + self.fonte_titulo.get_height() + 4 + 8 + altura_conteudo + 8
        rect = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(self.tela, COR_PAINEL_CARD, rect, border_radius=10)
        pygame.draw.rect(self.tela, COR_PAINEL_BORDA, rect, width=1, border_radius=10)

        y_conteudo = self._titulo_card(x, y, largura, titulo)
        for linha in linhas:
            texto = self.fonte.render(linha, True, COR_TEXTO)
            self.tela.blit(texto, (x + 12, y_conteudo))
            y_conteudo += 22

        return y + altura

    def _desenhar_card_contadores(self, x, y, largura, base):
        # Cada item: (rotulo, valor, cor da legenda)
        itens = [
            ("Visitadas", len(base.visitadas), COR_VISITADA),
            ("Seguras", len(base.seguras), COR_SEGURA),
            ("Suspeitas de poço", len(base.suspeitas_poco), COR_SUSPEITA_POCO),
            ("Suspeitas de Wumpus", len(base.suspeitas_wumpus), COR_SUSPEITA_WUMPUS),
            ("Flechas", base.flechas, COR_DESTAQUE),
        ]
        altura_conteudo = len(itens) * 26
        altura = 8 + self.fonte_titulo.get_height() + 4 + 8 + altura_conteudo + 8
        rect = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(self.tela, COR_PAINEL_CARD, rect, border_radius=10)
        pygame.draw.rect(self.tela, COR_PAINEL_BORDA, rect, width=1, border_radius=10)

        y_conteudo = self._titulo_card(x, y, largura, "MAPA DE CORES / CONTADORES")
        for rotulo, valor, cor in itens:
            # Quadradinho colorido (legenda)
            quad = pygame.Rect(x + 12, y_conteudo + 4, 16, 16)
            pygame.draw.rect(self.tela, cor, quad, border_radius=4)
            texto = self.fonte.render(f"{rotulo}: {valor}", True, COR_TEXTO)
            self.tela.blit(texto, (quad.right + 10, y_conteudo))
            y_conteudo += 26

        return y + altura

    def _desenhar_card_resultado(self, x, y, largura, mensagem, cor):
        # Quebra a mensagem em mais de uma linha se for muito longa
        palavras = mensagem.split(" ")
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            teste = (linha_atual + " " + palavra).strip()
            if self.fonte.size(teste)[0] > largura - 24:
                linhas.append(linha_atual)
                linha_atual = palavra
            else:
                linha_atual = teste
        if linha_atual:
            linhas.append(linha_atual)

        altura = 8 + self.fonte_titulo.get_height() + 4 + 8 + len(linhas) * 22 + 22 + 8
        rect = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(self.tela, COR_PAINEL_CARD, rect, border_radius=10)
        pygame.draw.rect(self.tela, cor, rect, width=2, border_radius=10)

        y_conteudo = self._titulo_card(x, y, largura, "RESULTADO")
        for linha in linhas:
            texto = self.fonte.render(linha, True, cor)
            self.tela.blit(texto, (x + 12, y_conteudo))
            y_conteudo += 22
        dica = self.fonte_pequena.render("Pressione R para reiniciar", True, COR_TEXTO_FRACO)
        self.tela.blit(dica, (x + 12, y_conteudo))

        return y + altura

    def _desenhar_log(self, x, y, largura, log):
        """Desenha o card de log, ocupando o espaco restante da tela."""
        altura = self.altura_tela - y - 18
        if altura < 40:
            return
        rect = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(self.tela, COR_PAINEL_CARD, rect, border_radius=10)
        pygame.draw.rect(self.tela, COR_PAINEL_BORDA, rect, width=1, border_radius=10)

        y_conteudo = self._titulo_card(x, y, largura, "LOG DE EVENTOS")
        espaco_restante = (y + altura) - y_conteudo
        max_linhas = max(1, espaco_restante // 19)
        ultimas = log[-max_linhas:]
        for linha_log in ultimas:
            texto = self.fonte_pequena.render("• " + linha_log, True, COR_TEXTO_FRACO)
            self.tela.blit(texto, (x + 12, y_conteudo))
            y_conteudo += 19

    # ------------------------------------------------------------------
    def fechar(self):
        pygame.quit()
