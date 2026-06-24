# main.py
# Ponto de entrada do programa. Cria o ambiente, o agente e a interface,
# e roda o loop principal do Pygame.
#
# Uso:
#   python main.py
#   python main.py --tamanho 6
#   python main.py --tamanho 5 --pocos 4 --semente 42
#   python main.py --velocidade 5    (passos do agente por segundo)
#
# A janela abre em TELA CHEIA por padrao.
# Controles: F = liga/desliga tela cheia | ESPACO = pausa | A = dispara flecha | R = reinicia | ESC = sair

import sys
import argparse
import pygame

from ambiente import Ambiente
from agente import Agente
from interface import Interface


MODOS = {
    "normal": {"rotulo": "Normal", "num_wumpus": 1, "num_pocos": 3, "wumpus_movel": False},
    "dois_wumpus": {"rotulo": "2 Wumpus", "num_wumpus": 2, "num_pocos": 4, "wumpus_movel": False},
    "movel": {"rotulo": "Movel", "num_wumpus": 1, "num_pocos": 3, "wumpus_movel": True},
    "combo": {"rotulo": "Combo", "num_wumpus": 2, "num_pocos": 4, "wumpus_movel": True},
}


def ler_argumentos():
    parser = argparse.ArgumentParser(description="Mundo de Wumpus - Agente Inteligente")
    parser.add_argument("--tamanho", type=int, default=4, help="Tamanho do mapa (NxN), minimo 4")
    parser.add_argument("--pocos", type=int, default=3, help="Quantidade de poços no mapa")
    parser.add_argument("--semente", type=int, default=None, help="Semente aleatoria (opcional)")
    parser.add_argument("--velocidade", type=float, default=3.0, help="Passos do agente por segundo")
    parser.add_argument("--modo", choices=tuple(MODOS.keys()), default="normal", help="Modo/preset inicial")
    return parser.parse_args()


def criar_jogo(args, modo_ativo):
    """Cria (ou recria) o ambiente e o agente para uma nova partida."""
    preset = MODOS.get(modo_ativo, MODOS["normal"])
    tamanho = max(4, args.tamanho)
    num_pocos = preset["num_pocos"] if preset["num_pocos"] is not None else args.pocos
    ambiente = Ambiente(
        tamanho=tamanho,
        num_pocos=num_pocos,
        semente=args.semente,
        num_wumpus=preset["num_wumpus"],
        wumpus_movel=preset["wumpus_movel"],
    )
    agente = Agente(ambiente)
    return ambiente, agente


def main():
    args = ler_argumentos()
    modo_ativo = args.modo

    ambiente, agente = criar_jogo(args, modo_ativo)
    interface = Interface(ambiente.tamanho, tela_cheia=True)

    relogio = pygame.time.Clock()
    pausado = False

    # Tempo entre passos do agente (em milissegundos), conforme a velocidade
    intervalo_passo = max(50, int(1000 / args.velocidade))
    ultimo_passo = pygame.time.get_ticks()

    executando = True
    while executando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    executando = False
                elif evento.key == pygame.K_SPACE:
                    # Pausa/despausa o agente
                    pausado = not pausado
                elif evento.key == pygame.K_f:
                    # Liga/desliga o modo tela cheia
                    interface.alternar_tela_cheia()
                elif evento.key == pygame.K_a:
                    # Tenta disparar a flecha se houver um alvo confiavel
                    agente.tentar_disparo_manual()
                elif evento.key == pygame.K_r:
                    # Reinicia o jogo mantendo o modo atual.
                    if args.semente is not None:
                        args.semente += 1
                    ambiente, agente = criar_jogo(args, modo_ativo)
                    interface = Interface(ambiente.tamanho, tela_cheia=interface.tela_cheia)
                    pausado = False
                    ultimo_passo = pygame.time.get_ticks()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                acao = interface.tratar_clique(evento.pos)
                if acao:
                    if acao["tipo"] == "acao" and acao["valor"] == "atirar":
                        agente.tentar_disparo_manual()
                    elif acao["tipo"] == "acao" and acao["valor"] == "novo_mapa":
                        if args.semente is not None:
                            args.semente += 1
                        ambiente, agente = criar_jogo(args, modo_ativo)
                        interface = Interface(ambiente.tamanho, tela_cheia=interface.tela_cheia)
                        pausado = False
                        ultimo_passo = pygame.time.get_ticks()
                    elif acao["tipo"] == "modo" and acao["valor"] in MODOS:
                        modo_ativo = acao["valor"]
                        if args.semente is not None:
                            args.semente += 1
                        ambiente, agente = criar_jogo(args, modo_ativo)
                        interface = Interface(ambiente.tamanho, tela_cheia=interface.tela_cheia)
                        pausado = False
                        ultimo_passo = pygame.time.get_ticks()

        agora = pygame.time.get_ticks()
        if not pausado and not agente.base.jogo_finalizado:
            if agora - ultimo_passo >= intervalo_passo:
                agente.passo()
                if ambiente.wumpus_movel and not agente.base.jogo_finalizado:
                    if ambiente.mover_wumpus(agente.posicao):
                        agente._verificar_fim_de_jogo()
                ultimo_passo = agora

        interface.desenhar(ambiente, agente, modo_ativo)
        relogio.tick(60)

    interface.fechar()
    sys.exit()


if __name__ == "__main__":
    main()
