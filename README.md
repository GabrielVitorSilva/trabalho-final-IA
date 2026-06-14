# Mundo de Wumpus - Agente Inteligente (Trabalho de IA)

## 1. Descrição do projeto

Este projeto implementa o clássico problema do **Mundo de Wumpus**, utilizado
para ensinar agentes baseados em conhecimento na disciplina de Inteligência
Artificial. Um agente explora um tabuleiro NxN desconhecido, percebe pistas
locais (brisa, cheiro e brilho), monta uma base de conhecimento sobre o
ambiente, evita perigos (poços e o Wumpus), encontra o ouro e retorna ao
ponto de partida.

A interface gráfica foi feita com **Pygame**, mostrando o tabuleiro, o
agente se movendo, as células visitadas/seguras/suspeitas e um painel
lateral com percepções, ações e log de eventos.

## 2. Objetivos do trabalho

- Demonstrar um agente baseado em regras e inferência lógica simples.
- Mostrar como uma base de conhecimento é construída incrementalmente
  apenas com percepções locais.
- Utilizar busca em largura (BFS) para planejar caminhos seguros.
- Apresentar de forma visual e didática o funcionamento do agente.

## 3. Requisitos de instalação

- Python 3.8 ou superior
- Biblioteca `pygame`

## 4. Como instalar as dependências

```bash
pip install -r requirements.txt
```

## 5. Como executar

```bash
python3 main.py
```

### Argumentos opcionais

```bash
python main.py --tamanho 6 --pocos 4 --semente 42 --velocidade 3
```

- `--tamanho`: dimensão do tabuleiro NxN (mínimo 4, padrão 4)
- `--pocos`: quantidade de poços no mapa (padrão 3)
- `--semente`: semente aleatória, para reproduzir o mesmo mapa (opcional)
- `--velocidade`: quantos passos o agente executa por segundo (padrão 3)

### Tela cheia

O jogo abre em **tela cheia** por padrão, ocupando toda a resolução do
monitor. O grid e o painel lateral se ajustam automaticamente ao tamanho
da tela.

### Controles durante a execução

- `F`: liga/desliga o modo tela cheia
- `ESPAÇO`: pausa/retoma o agente
- `R`: reinicia o jogo com um novo mapa (se `--semente` foi usado, a
  semente é incrementada em 1 a cada reinício, de forma previsível)
- `ESC` ou fechar a janela: encerra o programa

## 6. Como alterar o tamanho do mapa

Basta passar o argumento `--tamanho`, por exemplo:

```bash
python main.py --tamanho 8
```

O mínimo permitido é 4x4, conforme exigido pelo enunciado.

## 7. Lógica do agente (explicação simples)

O agente **não conhece o mapa completo**. Em cada célula, ele só sabe o que
percebe naquele exato momento:

- **Brisa**: pode haver um poço em alguma célula vizinha.
- **Cheiro**: pode haver o Wumpus em alguma célula vizinha.
- **Brilho**: o ouro está na célula atual.

Com base nessas percepções, o agente atualiza sua **base de conhecimento**
e decide o próximo movimento usando **busca em largura (BFS)**, andando
sempre por células que ele já considera seguras. O agente **nunca se move
de forma aleatória**.

### Regras de inferência usadas

- Sem brisa e sem cheiro → todos os vizinhos desconhecidos são marcados
  como **seguros**.
- Sem brisa → vizinhos ficam livres da suspeita de poço.
- Sem cheiro → vizinhos ficam livres da suspeita de Wumpus.
- Com brisa → vizinhos desconhecidos ficam **suspeitos de poço**.
- Com cheiro → vizinhos desconhecidos ficam **suspeitos de Wumpus**.
- Uma célula que já foi marcada como segura **nunca volta a ser suspeita**.

## 8. Base de conhecimento

A base de conhecimento (`conhecimento.py`) guarda:

- `visitadas`: conjunto de posições já visitadas.
- `seguras`: conjunto de posições consideradas seguras.
- `suspeitas_poco` e `suspeitas_wumpus`: conjuntos de posições suspeitas.
- `caminho_percorrido`: lista com a sequência de posições visitadas.
- `log`: histórico textual de percepções, decisões e ações.
- `ouro_encontrado` e `modo_retorno`: flags de estado da missão.

## 9. Mecanismo de inferência e estratégia

1. O agente começa na posição inicial (sempre segura, sem Wumpus e sem poço).
2. Lê as percepções da célula atual e atualiza a base de conhecimento.
3. Aplica as regras de inferência nos vizinhos da célula atual.
4. Usa **BFS** para encontrar o caminho mais curto, por células seguras,
   até a célula segura ainda não visitada mais próxima.
5. Se sentir **brilho**, marca o ouro como encontrado e entra em **modo de
   retorno**.
6. Em modo de retorno, usa **BFS** para voltar à posição inicial por
   células seguras.
7. O jogo termina com sucesso quando o agente retorna ao início com o
   ouro encontrado.
8. Se, em algum momento, não existir mais nenhum caminho seguro conhecido
   para uma célula nova (ou para o retorno), o agente exibe a mensagem
   **"Bloqueado: nenhum caminho seguro conhecido"** e para, sem travar o
   programa. Isso pode ocorrer porque o agente, por segurança, só anda em
   células que tem certeza de serem seguras — em alguns mapas isso pode
   significar que o caminho até o ouro passa por uma célula apenas
   "suspeita", e o agente prudente prefere não arriscar.

## 10. Geração do mundo

O ambiente (`ambiente.py`) gera o mapa aleatoriamente, mas **valida**
internamente (usando o mapa real, que o agente não vê) se existe um
caminho do início até o ouro passando apenas por **células "limpas"**
(células que não têm poço nem Wumpus em nenhum vizinho). Se o mapa
sorteado não atender a essa condição, ele é **regenerado**
automaticamente até ser válido.

Essa validação é mais forte do que apenas "existe caminho sem perigo":
ela garante que, ao andar célula a célula por esse caminho, o agente vai
sempre sentir "Nada" (sem brisa, sem cheiro) e, pela própria regra de
inferência, vai conseguir marcar a próxima célula do caminho como segura
**antes** de pisar nela. Ou seja, o caminho até o ouro (e a volta) é
sempre **descobrível pelo agente usando só as regras de inferência**,
sem depender de sorte.

Garantias da geração:

- A posição inicial é sempre `(0,0)`.
- Não há poço nem Wumpus na posição inicial nem em suas células vizinhas.
- Existe pelo menos um caminho de células "limpas" do início até o ouro,
  que o agente consegue descobrir e percorrer com suas regras normais.

## 11. Roteiro de apresentação para o professor

1. Executar `python main.py` e mostrar o tabuleiro sendo gerado.
2. Apontar a posição inicial (borda branca) e explicar que ela é sempre
   segura.
3. Deixar o agente andar e mostrar, no painel lateral, as percepções
   (brisa/cheiro/brilho) em cada célula.
4. Mostrar como células ficam **verdes** (seguras), **laranja** (suspeita
   de poço) e **vermelhas** (suspeita de Wumpus) conforme o agente explora.
5. Explicar que o agente usa BFS para escolher a próxima célula segura
   mais próxima — destacar o log de decisões no painel.
6. Quando o agente encontrar o ouro (círculo dourado), mostrar a mudança
   para "Modo retorno: Sim".
7. Mostrar o agente retornando à posição inicial e a mensagem de sucesso.
8. (Opcional) Usar `R` para reiniciar com outro mapa, e `--semente` para
   reproduzir um mapa específico.

## 12. Limitações da solução

- O agente é conservador: só se move por células que tem certeza de serem
  seguras. Graças à validação do gerador de mundo (item 10), sempre existe
  um caminho até o ouro e de volta que o agente consegue inferir como
  seguro, então a mensagem de "bloqueado" não deve ocorrer em condições
  normais — ela existe apenas como salvaguarda para não travar o programa.
- Não há mecanismo de flecha, combate ou Wumpus móvel (fora do escopo).
- A inferência é local (apenas vizinhos diretos), sem lógica proposicional
  mais avançada (ex.: combinação de múltiplas pistas de células distantes).

## 13. Possíveis extensões futuras

- Inferência mais avançada, combinando pistas de várias células para
  reduzir suspeitas (ex.: lógica proposicional completa).
- Permitir que o agente arrisque uma célula suspeita quando não houver
  alternativa, calculando probabilidades.
- Adicionar flecha para eliminar o Wumpus.
- Permitir múltiplos itens de ouro ou múltiplos Wumpus.
- Salvar estatísticas de várias execuções para comparar desempenho.

## 14. Estrutura dos arquivos

- `main.py`: ponto de entrada, loop principal do Pygame.
- `ambiente.py`: representação e geração do mundo.
- `agente.py`: lógica de decisão do agente.
- `conhecimento.py`: base de conhecimento do agente.
- `busca.py`: implementação do BFS.
- `interface.py`: desenho da interface gráfica.
- `requirements.txt`: dependências do projeto.
