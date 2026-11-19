"""Tabela de compromisso em linguagem simples, salva como imagem.
Rodar da pasta simulador:  python -m experiments.tabela_simples"""
import csv
from collections import defaultdict
import matplotlib.pyplot as plt

erros, bits = defaultdict(int), defaultdict(int)
with open("results/raw/ber_runs.csv", newline="") as f:
    leitor = csv.reader(f)
    next(leitor)                                   # pula o cabeçalho
    for lin in leitor:
        chave = (lin[0], lin[1], float(lin[2]))    # canal, modulação, Eb/N0
        bits[chave] += int(lin[4])
        erros[chave] += int(lin[5])

def em_palavras(canal, mod, eb):
    """Transforma a taxa de erro em '1 erro a cada X bits'."""
    e, n = erros[(canal, mod, eb)], bits[(canal, mod, eb)]
    if e == 0:
        return f"nenhum erro\nem {n:,} bits".replace(",", ".")
    x = round(n / e, -1) if n / e < 1000 else round(n / e, -2)
    return f"1 erro a cada\n{int(x):,} bits".replace(",", ".")

MODS = [("bpsk", "BPSK", "1"), ("qpsk", "QPSK", "2"), ("qam16", "16-QAM", "4")]
cab = ["Modulação", "Bits por\nsímbolo",
       "AWGN\n8 dB", "AWGN\n12 dB", "Rajadas\n8 dB", "Rajadas\n12 dB"]
dados = [[nome, b,
          em_palavras("awgn", m, 8.0), em_palavras("awgn", m, 12.0),
          em_palavras("burst", m, 8.0), em_palavras("burst", m, 12.0)] for m, nome, b in MODS]

fig, ax = plt.subplots(figsize=(14, 4.4))
ax.axis("off")
tab = ax.table(cellText=dados, colLabels=cab, loc="upper center", cellLoc="center",
               colWidths=[0.11, 0.09, 0.2, 0.2, 0.2, 0.2])
tab.auto_set_font_size(False)
tab.set_fontsize(12)
tab.scale(1, 3.2)
for (lin, col), cel in tab.get_celld().items():
    cel.set_edgecolor("#cccccc")
    if lin == 0:
        cel.set_facecolor("#1f4e79")
        cel.get_text().set_color("white")
        cel.get_text().set_fontweight("bold")
    elif lin % 2 == 0:
        cel.set_facecolor("#eef3f8")
ax.set_title("Compromisso entre velocidade e taxa de erro", fontsize=15,
             fontweight="bold", pad=10)
fig.text(0.5, 0.04,
         "BPSK e QPSK têm a mesma taxa de erro, mas o QPSK leva o dobro de bits por símbolo.\n"
         "O 16-QAM leva 4 vezes mais bits que o BPSK, mas precisa de sinal mais forte.\n"
         "No canal com rajadas, aumentar o sinal quase não reduz os erros.",
         ha="center", fontsize=12, color="#333333")
fig.savefig("results/figs/tabela_simples.png", dpi=150, bbox_inches="tight")
print("Imagem salva em results/figs/tabela_simples.png")