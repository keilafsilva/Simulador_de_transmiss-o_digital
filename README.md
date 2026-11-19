# Simulador de transmissão digital

Trabalho II de Redes de Computadores – UNISINOS – Prof. Cristiano Bonato Both

Simulador ponta a ponta em Python de um enlace de comunicação digital:

```
texto ASCII → bits → código de linha → modulação → canal com ruído
            → demodulação → decodificação de linha → bits → texto
```

No final, os bits recebidos são comparados com os enviados para calcular a **taxa de erro de bit (BER)**,
e a **eficiência espectral** de cada configuração é calculada.

**Vídeo de demonstração:** https://drive.google.com/file/d/1QsHu6R8mvYkZ7J1wbaSS5cZqt9ySMFlS/view?usp=sharing

## Autoria e divisão de responsabilidades

| Integrante | Responsabilidades |
|---|---|
| Keila Fernanda da Silva | Todas as etapas: implementação, experimentos, análise, documentação e vídeo |

## Instalação e execução

Requer Python 3.10 ou superior. Todos os comandos são executados dentro da pasta do projeto.

```
pip install -r requirements.txt
python -m pytest -v                            # 8 testes de consistência
```

**Experimentos** (as sementes são fixas, então os resultados se repetem exatamente):

```
python -m experiments.run_linecodes            # 1º experimento: códigos de linha (alguns minutos)
python -m experiments.run_ber                  # 2º experimento: modulações (alguns minutos)
python -m experiments.demo_message             # 3º experimento: mensagem de texto (segundos)
```

**Gráficos e tabelas** (leem os resultados brutos já gerados, rodam em segundos):

```
python -m experiments.plot_ber                 # curvas BER × Eb/N0 com teoria e tabela de compromisso
python -m experiments.plot_constellations      # constelações antes e depois do canal
python -m experiments.plot_linecodes_simples   # 1º experimento em linguagem simples (AWGN e rajadas)
python -m experiments.plot_modulacoes_simples  # 2º experimento em linguagem simples (AWGN e rajadas)
python -m experiments.tabela_simples           # tabela de compromisso em linguagem simples
python -m experiments.tabela_imagem            # tabela de compromisso original como imagem
python -m experiments.plot_mensagem            # 3º experimento em gráfico de barras
```

O `plot_mensagem` usa sementes próprias, então o número de bits errados em cada caso é um pouco diferente
do `demo_message`. Os dois mostram o mesmo efeito.

## Arquitetura (`src/`)

| Módulo | Etapa |
|---|---|
| `ascii_io.py` | Texto ↔ bits (8 bits por caractere, tabela ASCII) |
| `linecode.py` | Manchester e Bifase Mark: codificação, decodificação e contagem de violações |
| `modulation.py` | BPSK, QPSK e 16-QAM com mapeamento Gray e energia média por símbolo igual a 1; demodulação por mínima distância; BER teórica |
| `channel.py` | Canal AWGN (Eb/N0 por bit de informação) e canal com ruído em rajadas (Gilbert-Elliott) |
| `metrics.py` | BER, posição dos bits errados e eficiência espectral nominal |
| `pipeline.py` | `run_chain` e `run_message`: ligam todas as etapas na ordem |

## Parâmetros e convenções

- **Manchester:** bit 1 = chips `01` (sobe no meio do bit); bit 0 = chips `10` (desce no meio).
  Um par `00` ou `11` é uma violação; nesse caso o receptor assume bit 0.
- **Bifase Mark:** sempre há transição no início do bit; o bit 1 tem uma transição extra no meio.
  O receptor decide pelo par de chips: diferentes = bit 1, iguais = bit 0.
- **BPSK:** bit 0 → −1 e bit 1 → +1. QPSK e 16-QAM usam mapeamento Gray (pontos vizinhos diferem em 1 bit).
- **Eb/N0** é definido por bit de informação, para comparar de forma justa modulações e códigos que levam
  quantidades diferentes de bits por símbolo. Com código de linha (taxa 1/2), cada chip recebe metade da energia
  do bit (cerca de 3 dB a menos).
- **AWGN:** a cada símbolo é somado um número aleatório com distribuição gaussiana, cuja variância é definida pelo Eb/N0.
- **Ruído em rajadas (Gilbert-Elliott):** cadeia de Markov com dois estados. P(bom → ruim) = 0,01 e
  P(ruim → bom) = 0,1 por símbolo. O canal fica ruim em 0,01 / (0,01 + 0,1) ≈ 9 % do tempo, em rajadas
  de cerca de 10 símbolos. No estado ruim, o ruído é 12 dB mais forte (cerca de 16 vezes a potência).
- **Eficiência espectral nominal:** bits por símbolo × taxa do código de linha, supondo banda igual à taxa de símbolos.

## Plano experimental

São três experimentos, cada um mudando uma coisa por vez:

| Experimento | O que varia | O que fica fixo | Volume |
|---|---|---|---|
| 1º Códigos de linha | sem código, Manchester, Bifase Mark | BPSK | 8 valores de Eb/N0 (0 a 14 dB) × 200 mil bits × 10 repetições, nos dois canais |
| 2º Modulações | BPSK, QPSK, 16-QAM | sem código de linha | 8 valores de Eb/N0 (0 a 14 dB) × 1 milhão de bits × 10 repetições, nos dois canais |
| 3º Mensagem | modulação, Eb/N0 e canal | frase "Redes de Computadores - UNISINOS - Trabalho II" (46 caracteres, 368 bits) | uma execução por caso, como ilustração |

O mínimo pedido era 8 valores de SNR, 100 mil bits e 5 repetições. A variabilidade entre as repetições aparece
nos gráficos como intervalo de confiança de 95 %.

## Validação

Os 8 testes automáticos (`tests/test_consistency.py`) conferem:

1. Texto → bits → texto devolve o texto original.
2. Manchester e Bifase Mark, codificando e decodificando, devolvem os mesmos bits, sem violações.
3. O Bifase Mark tem transição no início de todo bit.
4. As constelações têm energia média 1 e mapeamento Gray.
5. Sem ruído, as 9 combinações de código de linha e modulação devolvem a mensagem idêntica.
6. Com sinal muito forte (30 dB), a mensagem também chega idêntica nas 9 combinações.
7. No AWGN, a BER simulada fica a menos de 10 % da BER teórica.
8. O canal com rajadas fica no estado ruim cerca de 9 % do tempo, como prevê o modelo.

## Resultados

### 1º experimento: códigos de linha (BPSK)

| Canal | Eb/N0 | Sem código | Manchester | Bifase Mark |
|---|---|---|---|---|
| AWGN | 8 dB | 2,0 × 10⁻⁴ | 6,0 × 10⁻³ | 1,2 × 10⁻² |
| AWGN | 12 dB | 0 | 3,0 × 10⁻⁵ | 6,9 × 10⁻⁵ |
| Rajadas | 12 dB | 7,2 × 10⁻³ | 1,5 × 10⁻² | 2,5 × 10⁻² |

- Os códigos de linha garantem uma transição em todo bit, o que dá sincronismo e elimina a componente DC.
  O custo é que cada bit vira dois chips: a banda dobra e a eficiência cai de 1 para 0,5 bit/s/Hz.
- A BER também piorou, porque cada chip leva metade da energia do bit e o receptor decide chip por chip.
  Com decisão conjunta das duas metades, o Manchester teria a mesma BER que sem código. Essa é uma limitação
  assumida do receptor.
- O Bifase Mark errou cerca do dobro do Manchester: nele, um erro em qualquer uma das metades troca o bit,
  enquanto no Manchester metade desses casos vira violação e é decidida corretamente por acaso.
- Código de linha **não é** código de correção de erros: ele detecta alguns erros (violações), mas não corrige.
  A correção de erros (por exemplo, Hamming) acrescenta bits redundantes e não faz parte deste trabalho.

### 2º experimento: modulações (sem código de linha)

| Modulação | Bits por símbolo | BER no AWGN, 8 dB | BER no AWGN, 12 dB | BER com rajadas, 14 dB |
|---|---|---|---|---|
| BPSK | 1 | 2,0 × 10⁻⁴ | 0 | 3,5 × 10⁻³ |
| QPSK | 2 | 2,0 × 10⁻⁴ | 0 | 3,4 × 10⁻³ |
| 16-QAM | 4 | 9,3 × 10⁻³ | 1,4 × 10⁻⁴ | 8,9 × 10⁻³ |

- No AWGN, BPSK e QPSK têm a mesma BER (o QPSK equivale a dois BPSK independentes, nos eixos I e Q) e chegam a
  1 erro em 1.000 bits com cerca de 8 dB. O 16-QAM precisa de cerca de 12 dB, porque seus 16 pontos ficam mais
  próximos e o ruído confunde um ponto com o vizinho mais facilmente.
- Os pontos simulados coincidem com as curvas teóricas.
- Com rajadas, as curvas quase não descem: os erros vêm do estado ruim, e aumentar o sinal não resolve.
  Nenhuma modulação chega a 1 erro em 1.000 bits, nem com 14 dB.

**Tabela de compromisso (BER × eficiência espectral):**

| Modulação | Eficiência (bit/s/Hz) | Eb/N0 para BER ≤ 10⁻³ no AWGN |
|---|---|---|
| BPSK | 1 | cerca de 8 dB |
| QPSK | 2 | cerca de 8 dB |
| 16-QAM | 4 | cerca de 12 dB |

Mais bits por símbolo aumentam a eficiência, mas exigem um sinal mais forte. Com sinal fraco, o QPSK é a melhor
escolha: erra igual ao BPSK e leva o dobro de bits. Com sinal forte e pouca banda, o 16-QAM leva 4 vezes mais.

### 3º experimento: mensagem

`results/demo_mensagem.txt` mostra a frase recebida em cada caso, com os caracteres e bits afetados.
Com 8 dB no BPSK, a frase chega perfeita. Com 4 dB, o BPSK erra 7 bits e o 16-QAM erra 20, deixando a frase
quase ilegível. Um único bit errado já troca uma letra. No canal com rajadas, os erros se concentram em
trechos da frase.

Com só 368 bits, a mensagem não serve para medir a BER com precisão: ela ilustra o efeito dos erros no texto.
A BER foi medida nos dois primeiros experimentos.

## Conclusões

1. O simulador está validado: sem ruído a mensagem chega idêntica e, com ruído, a BER bate com a teoria.
2. Código de linha dá sincronismo, mas não corrige erros e usa o dobro da banda.
3. Mais bits por símbolo aumentam a eficiência espectral, mas exigem sinal mais forte.
4. Ruído em rajadas é o pior caso: mais potência quase não ajuda, e a solução seria correção de erros com entrelaçamento.

## Estrutura do repositório

```
src/                      módulos do simulador
tests/                    testes de consistência
experiments/              scripts que geram todos os resultados e gráficos
results/raw/              resultados brutos (linecode_runs.csv e ber_runs.csv) e configurações (config_B.json e config_A.json)
results/figs/             gráficos
results/demo_mensagem.txt saída do 3º experimento
```

