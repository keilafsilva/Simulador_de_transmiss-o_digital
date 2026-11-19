"""Gráficos simples dos códigos de linha, um para cada canal, com eixos em linguagem fácil.
Rodar da pasta simulador:  python -m experiments.plot_linecodes_simples"""
import csv
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt

CODIGOS = {"none": ("Sem código de linha", "#1f77b4", "o"),
           "manchester": ("Manchester", "#ff7f0e", "s"),
           "bifase_mark": ("Bifase Mark", "#2ca02c", "^")}
CANAIS = {"awgn": "Canal AWGN (ruído comum)", "burst": "Canal com rajadas de ruído"}
NIVEIS = [(1e-1, "1 erro em 10 bits"), (1e-2, "1 erro em 100 bits"),
          (1e-3, "1 erro em 1.000 bits"), (1e-4, "1 erro em 10.000 bits"),
          (1e-5, "1 erro em 100.000 bits"), (1e-6, "1 erro em 1.000.000 bits")]

erros, bits = defaultdict(int), defaultdict(int)
with open("results/raw/linecode_runs.csv", newline="") as f:
    leitor = csv.reader(f)
    next(leitor)                                   # pula o cabeçalho
    for lin in leitor:
        chave = (lin[0], lin[1], float(lin[2]))    # canal, código, Eb/N0
        bits[chave] += int(lin[4])
        erros[chave] += int(lin[5])

Path("results/figs").mkdir(parents=True, exist_ok=True)
for canal, titulo in CANAIS.items():
    fig, ax = plt.subplots(figsize=(9, 5.5))
    menor = 1.0
    for codigo, (nome, cor, marca) in CODIGOS.items():
        pts = sorted((eb, erros[(c, k, eb)] / bits[(c, k, eb)])
                     for (c, k, eb) in bits if c == canal and k == codigo)
        pts = [(x, y) for x, y in pts if y > 0]    # zero erros não aparece em escala log
        menor = min([menor] + [y for _, y in pts])
        ax.semilogy([p[0] for p in pts], [p[1] for p in pts], marker=marca, color=cor,
                    lw=2.2, ms=7, label=nome)
    usados = [n for n in NIVEIS if n[0] >= menor / 10]
    ax.set_yticks([n[0] for n in usados])
    ax.set_yticklabels([n[1] for n in usados], fontsize=10)
    ax.set_ylim(usados[-1][0] / 2, 0.5)
    ax.minorticks_off()
    ax.set_ylabel("Quantos bits chegam errados\n(mais embaixo = melhor)", fontsize=11)
    ax.set_xlabel("Força do sinal em relação ao ruído, Eb/N0 (dB)", fontsize=11)
    ax.text(0.01, -0.13, "← sinal fraco", transform=ax.transAxes, fontsize=10, color="gray")
    ax.text(0.99, -0.13, "sinal forte →", transform=ax.transAxes, fontsize=10, color="gray", ha="right")
    ax.set_title(f"Códigos de linha com BPSK: {titulo}", fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=11, frameon=False)
    fig.tight_layout()
    nome_arq = f"results/figs/linecodes_simples_{'awgn' if canal == 'awgn' else 'rajadas'}.png"
    fig.savefig(nome_arq, dpi=150)
    plt.close(fig)
    print("Gráfico salvo em", nome_arq)