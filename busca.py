# busca.py
# Implementacao simples de BFS (Busca em Largura) usada pelo agente
# para encontrar caminhos passando apenas por celulas seguras conhecidas.

from collections import deque


def vizinhos(pos, tamanho):
    """Retorna as posicoes vizinhas validas (cima, baixo, esquerda, direita)."""
    linha, coluna = pos
    candidatos = [
        (linha - 1, coluna),
        (linha + 1, coluna),
        (linha, coluna - 1),
        (linha, coluna + 1),
    ]
    validos = []
    for (l, c) in candidatos:
        if 0 <= l < tamanho and 0 <= c < tamanho:
            validos.append((l, c))
    return validos


def bfs_caminho(origem, destino, celulas_permitidas, tamanho):
    """
    Busca em largura entre origem e destino, andando apenas por
    celulas que estao no conjunto 'celulas_permitidas'.
    Retorna uma lista de posicoes representando o caminho (incluindo
    origem e destino), ou None se nao houver caminho.
    """
    if origem == destino:
        return [origem]

    fila = deque()
    fila.append(origem)
    visitado = {origem}
    pai = {origem: None}

    while fila:
        atual = fila.popleft()
        if atual == destino:
            break
        for viz in vizinhos(atual, tamanho):
            if viz in visitado:
                continue
            # so podemos passar por celulas permitidas (seguras),
            # exceto o proprio destino, que sempre pode ser alcancado
            if viz != destino and viz not in celulas_permitidas:
                continue
            visitado.add(viz)
            pai[viz] = atual
            fila.append(viz)

    if destino not in pai:
        return None

    # Reconstroi o caminho a partir do destino, voltando pelos pais
    caminho = []
    passo = destino
    while passo is not None:
        caminho.append(passo)
        passo = pai[passo]
    caminho.reverse()
    return caminho


def encontrar_celula_segura_nao_visitada(origem, seguras, visitadas, tamanho):
    """
    Procura, entre as celulas seguras conhecidas e ainda nao visitadas,
    aquela mais proxima da origem (segundo a BFS) e retorna o caminho
    completo até ela. Retorna None se nao existir nenhuma.
    """
    candidatas = [c for c in seguras if c not in visitadas]
    if not candidatas:
        return None

    melhor_caminho = None
    for destino in candidatas:
        caminho = bfs_caminho(origem, destino, seguras, tamanho)
        if caminho is None:
            continue
        if melhor_caminho is None or len(caminho) < len(melhor_caminho):
            melhor_caminho = caminho

    return melhor_caminho
