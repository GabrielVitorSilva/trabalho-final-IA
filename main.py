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


def ler_argumentos():
    parser = argparse.ArgumentParser(description="Mundo de Wumpus - Agente Inteligente")
    parser.add_argument("--tamanho", type=int, default=4, help="Tamanho do mapa (NxN), minimo 4")
    parser.add_argument("--pocos", type=int, default=3, help="Quantidade de poços no mapa")
    parser.add_argument("--semente", type=int, default=None, help="Semente aleatoria (opcional)")
    parser.add_argument("--velocidade", type=float, default=3.0, help="Passos do agente por segundo")
    return parser.parse_args()


def criar_jogo(args):
    """Cria (ou recria) o ambiente e o agente para uma nova partida."""
    tamanho = max(4, args.tamanho)
    ambiente = Ambiente(tamanho=tamanho, num_pocos=args.pocos, semente=args.semente)
    agente = Agente(ambiente)
    return ambiente, agente


def main():
    args = ler_argumentos()

    ambiente, agente = criar_jogo(args)
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
                    # Reinicia o jogo. Se uma semente foi passada por
                    # argumento, soma 1 a cada reinicio (gera um mapa novo,
                    # mas de forma previsivel/reprodutivel). Sem semente,
                    # o novo mapa e totalmente aleatorio.
                    if args.semente is not None:
                        args.semente += 1
                    ambiente, agente = criar_jogo(args)
                    pausado = False

        agora = pygame.time.get_ticks()
        if not pausado and not agente.base.jogo_finalizado:
            if agora - ultimo_passo >= intervalo_passo:
                agente.passo()
                ultimo_passo = agora

        interface.desenhar(ambiente, agente)
        relogio.tick(60)

    interface.fechar()
    sys.exit()


if __name__ == "__main__":
    main()
