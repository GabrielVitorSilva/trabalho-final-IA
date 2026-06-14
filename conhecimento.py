# conhecimento.py
# Base de conhecimento do agente: guarda tudo que o agente "sabe" sobre o mundo
# com base apenas no que ele percebeu até o momento.

class BaseConhecimento:
    def __init__(self, posicao_inicial):
        # Conjunto de posicoes ja visitadas pelo agente
        self.visitadas = set()
        # Conjunto de posicoes que o agente considera seguras
        self.seguras = set()
        # Conjunto de posicoes suspeitas de ter poço
        self.suspeitas_poco = set()
        # Conjunto de posicoes suspeitas de ter Wumpus
        self.suspeitas_wumpus = set()

        # A posicao inicial e sempre segura
        self.seguras.add(posicao_inicial)
        self.posicao_inicial = posicao_inicial

        # Lista (log) com o historico de acoes e percepcoes, na ordem em que ocorreram
        self.log = []

        # Caminho percorrido pelo agente (pilha de posicoes)
        self.caminho_percorrido = [posicao_inicial]

        # Flags de estado do agente
        self.ouro_encontrado = False
        self.modo_retorno = False
        self.jogo_finalizado = False
        self.mensagem_final = ""

    def marcar_visitada(self, pos):
        """Marca uma posicao como visitada e tambem como segura."""
        self.visitadas.add(pos)
        self.marcar_segura(pos)

    def marcar_segura(self, pos):
        """Marca uma posicao como segura. Uma vez segura, continua segura."""
        self.seguras.add(pos)
        # Se estava suspeita, remove a suspeita (segura tem prioridade)
        self.suspeitas_poco.discard(pos)
        self.suspeitas_wumpus.discard(pos)

    def marcar_suspeita_poco(self, pos):
        """Marca uma posicao como suspeita de poço, se ainda nao for segura."""
        if pos not in self.seguras:
            self.suspeitas_poco.add(pos)

    def marcar_suspeita_wumpus(self, pos):
        """Marca uma posicao como suspeita de Wumpus, se ainda nao for segura."""
        if pos not in self.seguras:
            self.suspeitas_wumpus.add(pos)

    def eh_segura(self, pos):
        return pos in self.seguras

    def eh_suspeita(self, pos):
        return pos in self.suspeitas_poco or pos in self.suspeitas_wumpus

    def registrar_log(self, texto):
        """Adiciona uma linha no log de eventos (percepcoes, decisoes, acoes)."""
        self.log.append(texto)
        # Mantem o log com tamanho razoavel para nao crescer infinitamente
        if len(self.log) > 200:
            self.log.pop(0)

    def empilhar_caminho(self, pos):
        self.caminho_percorrido.append(pos)
