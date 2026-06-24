# agente.py
# Implementa a logica do agente inteligente do Mundo de Wumpus.
# O agente so usa: percepcoes da celula atual + base de conhecimento + BFS.
# Ele NUNCA consulta o mapa real do ambiente para decidir seus movimentos.

from busca import vizinhos, bfs_caminho, encontrar_celula_segura_nao_visitada
from conhecimento import BaseConhecimento


class Agente:
    def __init__(self, ambiente):
        self.ambiente = ambiente
        self.tamanho = ambiente.tamanho

        self.posicao = ambiente.posicao_inicial
        self.base = BaseConhecimento(self.posicao)

        # Fila de movimentos planejados (resultado de uma busca BFS).
        # O agente consome essa fila um passo por vez, para a animacao
        # ficar suave na interface.
        self.plano = []

        # Ultima acao executada e ultimas percepcoes, usadas na interface
        self.ultima_acao = "Inicio"
        self.ultimas_percepcoes = {"brisa": False, "cheiro": False, "brilho": False}

        # Permite pedir um disparo manual pela interface (tecla A)
        self.pedir_disparo = False

        # Marca a celula inicial como visitada
        self.base.marcar_visitada(self.posicao)

    # ------------------------------------------------------------------
    # PASSO PRINCIPAL DO AGENTE
    # ------------------------------------------------------------------
    def passo(self):
        """
        Executa um unico passo do agente. Retorna True se o jogo deve
        continuar, ou False se o jogo terminou (sucesso, morte ou bloqueio).
        """
        if self.base.jogo_finalizado:
            return False

        # 1) Se ja temos um plano de movimentos, segue executando-o
        if self.plano:
            self._mover_para(self.plano.pop(0))
            self._processar_percepcoes_atuais()
            return self._verificar_fim_de_jogo()

        # 2) Sem plano: le percepcoes e atualiza conhecimento
        self._processar_percepcoes_atuais()
        if self._verificar_fim_de_jogo() is False:
            return False

        # 3) Decide o que fazer a seguir
        acao = self._decidir_proxima_acao()

        if acao == "disparo":
            self._processar_percepcoes_atuais()
            return self._verificar_fim_de_jogo()

        if acao == "plano":
            return True

        # Se mesmo apos decidir nao ha plano, o agente esta bloqueado
        if not self.plano and not self.base.jogo_finalizado:
            self.base.jogo_finalizado = True
            self.base.mensagem_final = "Bloqueado: nenhum caminho seguro conhecido."
            self.base.registrar_log("Agente bloqueado, sem caminho seguro conhecido.")
            self.ultima_acao = "Bloqueado"
            return False

        return True

    def solicitar_disparo(self):
        """Pede que o agente tente disparar a flecha no proximo passo."""
        self.pedir_disparo = True

    def tentar_disparo_manual(self):
        """
        Tenta um disparo imediato, usado pela interface (tecla A).
        Se o disparo acontecer, atualiza a percepcao atual logo em seguida.
        """
        if self.base.jogo_finalizado:
            return False
        self.solicitar_disparo()
        disparou = self._tentar_disparo_inteligente(manual=True)
        if disparou:
            self._processar_percepcoes_atuais()
            self._verificar_fim_de_jogo()
        return disparou

    # ------------------------------------------------------------------
    # PERCEPCAO E ATUALIZACAO DA BASE DE CONHECIMENTO
    # ------------------------------------------------------------------
    def _processar_percepcoes_atuais(self):
        """Le as percepcoes da celula atual e atualiza a base de conhecimento."""
        percepcoes = self.ambiente.obter_percepcoes(self.posicao)
        self.ultimas_percepcoes = percepcoes

        self.base.marcar_visitada(self.posicao)

        texto = f"Posicao {self.posicao}: "
        partes = []
        if percepcoes["brisa"]:
            partes.append("Brisa")
        if percepcoes["cheiro"]:
            partes.append("Cheiro")
        if percepcoes["brilho"]:
            partes.append("Brilho")
        if not partes:
            partes.append("Nada")
        texto += ", ".join(partes)
        self.base.registrar_log(texto)

        # Verifica se encontrou o ouro
        if percepcoes["brilho"] and not self.base.ouro_encontrado:
            self.base.ouro_encontrado = True
            self.base.registrar_log("Ouro encontrado! Iniciando retorno.")

        # Aplica as regras de inferencia nos vizinhos da celula atual
        self._inferir_vizinhos(percepcoes)

    def _inferir_vizinhos(self, percepcoes):
        """
        Aplica as regras simples de inferencia sobre os vizinhos da
        posicao atual, marcando-os como seguros ou suspeitos.
        """
        for viz in vizinhos(self.posicao, self.tamanho):
            # Celulas ja seguras continuam seguras (prioridade maxima)
            if self.base.eh_segura(viz):
                continue

            if not percepcoes["brisa"] and not percepcoes["cheiro"]:
                # Sem brisa e sem cheiro: vizinho e totalmente seguro
                self.base.marcar_segura(viz)
                continue

            if not percepcoes["brisa"]:
                # Sem brisa: vizinho seguro contra poço
                self.base.suspeitas_poco.discard(viz)
            else:
                # Com brisa: vizinho suspeito de poço
                self.base.marcar_suspeita_poco(viz)

            if not percepcoes["cheiro"]:
                # Sem cheiro: vizinho seguro contra Wumpus
                self.base.suspeitas_wumpus.discard(viz)
            else:
                # Com cheiro: vizinho suspeito de Wumpus
                self.base.marcar_suspeita_wumpus(viz)

            # Se nao ficou suspeito de nada, e seguro
            if viz not in self.base.suspeitas_poco and viz not in self.base.suspeitas_wumpus:
                self.base.marcar_segura(viz)

    # ------------------------------------------------------------------
    # DECISAO DA PROXIMA ACAO
    # ------------------------------------------------------------------
    def _decidir_proxima_acao(self):
        """
        Decide o proximo conjunto de movimentos (plano) com base no
        estado atual da base de conhecimento, usando BFS.
        """
        if self.base.ouro_encontrado and not self.base.modo_retorno:
            self.base.modo_retorno = True

        if self.base.modo_retorno:
            # Tenta voltar para a posicao inicial usando celulas seguras
            caminho = bfs_caminho(
                self.posicao, self.base.posicao_inicial,
                self.base.seguras, self.tamanho
            )
            if caminho and len(caminho) > 1:
                self.plano = caminho[1:]
                self.ultima_acao = "Retornando ao inicio"
                self.base.registrar_log("Decisao: retornar ao inicio pelo caminho seguro.")
                return "plano"
            return None

        # Se houver uma flecha disponivel e um alvo confiavel, tenta disparar.
        if self._tentar_disparo_inteligente():
            return "disparo"

        # Ainda explorando: procura a celula segura mais proxima ainda nao visitada
        caminho = encontrar_celula_segura_nao_visitada(
            self.posicao, self.base.seguras, self.base.visitadas, self.tamanho
        )
        if caminho and len(caminho) > 1:
            self.plano = caminho[1:]
            destino = caminho[-1]
            self.ultima_acao = f"Explorando ate {destino}"
            self.base.registrar_log(f"Decisao: explorar ate {destino} (caminho seguro).")
            return "plano"

        return None

    def _direcao_entre(self, origem, destino):
        """Retorna a direcao em linha reta entre duas posicoes alinhadas."""
        if origem[0] == destino[0]:
            if destino[1] > origem[1]:
                return "direita"
            if destino[1] < origem[1]:
                return "esquerda"
        if origem[1] == destino[1]:
            if destino[0] > origem[0]:
                return "baixo"
            if destino[0] < origem[0]:
                return "cima"
        return None

    def _tentar_disparo_inteligente(self, manual=False):
        """
        Tenta usar a flecha quando houver um unico alvo suspeito alinhado.
        Retorna True se houve disparo, False caso contrario.
        """
        if self.base.flechas <= 0 or not self.ambiente.wumpus_vivo:
            self.pedir_disparo = False
            return False

        alvos = []
        for suspeita in sorted(self.base.suspeitas_wumpus):
            direcao = self._direcao_entre(self.posicao, suspeita)
            if direcao is not None:
                alvos.append((direcao, suspeita))

        if len(alvos) != 1:
            if manual:
                if not alvos:
                    self.base.registrar_log("Disparo pedido, mas nao ha alvo alinhado.")
                else:
                    self.base.registrar_log("Disparo pedido, mas ha mais de um alvo alinhado.")
                self.ultima_acao = "Disparo indisponivel"
            self.pedir_disparo = False
            return False

        direcao, alvo = alvos[0]
        if not self.base.usar_flecha():
            self.pedir_disparo = False
            return False

        acertou, posicao_acertada = self.ambiente.disparar_flecha(self.posicao, direcao)
        self.pedir_disparo = False

        if acertou and posicao_acertada is not None:
            self.base.wumpus_eliminado = True
            self.base.marcar_segura(posicao_acertada)
            self.base.registrar_log(
                f"Flecha disparada para {direcao} em direcao a {alvo} e Wumpus eliminado em {posicao_acertada}."
            )
            self.ultima_acao = f"Disparo: Wumpus eliminado em {posicao_acertada}"
        else:
            self.base.registrar_log(
                f"Flecha disparada para {direcao} em direcao a {alvo}, mas nao encontrou o Wumpus."
            )
            self.ultima_acao = f"Disparo: erro para {direcao}"
        return True

    # ------------------------------------------------------------------
    # MOVIMENTACAO E FIM DE JOGO
    # ------------------------------------------------------------------
    def _mover_para(self, nova_posicao):
        self.posicao = nova_posicao
        self.base.empilhar_caminho(nova_posicao)
        self.ultima_acao = f"Mover para {nova_posicao}"

    def _verificar_fim_de_jogo(self):
        """
        Verifica se o agente caiu em um perigo ou completou a missao.
        Retorna False se o jogo terminou, True caso contrario.
        """
        perigo = self.ambiente.verificar_perigo(self.posicao)
        if perigo == "poco":
            self.base.jogo_finalizado = True
            self.base.mensagem_final = "O agente caiu em um poço! Fim de jogo."
            self.base.registrar_log("Perigo: o agente caiu em um poço.")
            return False
        if perigo == "wumpus":
            self.base.jogo_finalizado = True
            self.base.mensagem_final = "O agente encontrou o Wumpus! Fim de jogo."
            self.base.registrar_log("Perigo: o agente encontrou o Wumpus.")
            return False

        if (self.base.ouro_encontrado and self.base.modo_retorno
                and self.posicao == self.base.posicao_inicial):
            self.base.jogo_finalizado = True
            self.base.mensagem_final = "Sucesso! O agente pegou o ouro e voltou ao inicio."
            self.base.registrar_log("Missao concluida com sucesso!")
            return False

        return True
