"""Transforma a tabela de compromisso (CSV) em imagem.
Rodar da pasta simulador:  python -m experiments.tabela_imagem"""
import csv
import matplotlib.pyplot as plt

with open("results/tabela_compromisso.csv", newline="", encoding="utf-8") as f:
    linhas = list(csv.reader(f))
cabecalho, dados = linhas[0], linhas[1:]

fig, ax = plt.subplots(figsize=(2.2 * len(cabecalho), 0.6 * len(dados) + 1.4))
ax.axis("off")
tab = ax.table(cellText=dados, colLabels=cabecalho, loc="center", cellLoc="center")
tab.auto_set_font_size(False)
tab.set_fontsize(11)
tab.scale(1, 2)
for (lin, col), cel in tab.get_celld().items():
    cel.set_edgecolor("#cccccc")
    cel.get_text().set_wrap(True)
    if lin == 0:                                   # cabeçalho
        cel.set_facecolor("#1f4e79")
        cel.get_text().set_color("white")
        cel.get_text().set_fontweight("bold")
        cel.set_height(cel.get_height() * 1.6)
    elif lin % 2 == 0:
        cel.set_facecolor("#eef3f8")
ax.set_title("Compromisso entre eficiência espectral e taxa de erro", fontsize=13,
             fontweight="bold", pad=12)
fig.tight_layout()
fig.savefig("results/figs/tabela_compromisso.png", dpi=150, bbox_inches="tight")
print("Imagem salva em results/figs/tabela_compromisso.png")