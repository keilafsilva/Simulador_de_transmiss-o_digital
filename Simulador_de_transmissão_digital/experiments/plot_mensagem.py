"""Experimento C em gráfico: quantos bits da mensagem chegam errados em cada caso.
Rodar da pasta simulador:  python -m experiments.plot_mensagem"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from src.pipeline import run_message

MSG = "Redes de Computadores - UNISINOS - Trabalho II"
CASOS = [  # (modulação, canal, Eb/N0, nome no gráfico)
    ("bpsk", "awgn", 8, "BPSK\nAWGN 8 dB"),
    ("bpsk", "awgn", 4, "BPSK\nAWGN 4 dB"),
    ("qpsk", "awgn", 4, "QPSK\nAWGN 4 dB"),
    ("qam16", "awgn", 12, "16-QAM\nAWGN 12 dB"),
    ("qam16", "awgn", 4, "16-QAM\nAWGN 4 dB"),
    ("bpsk", "burst", 8, "BPSK\nRajadas 8 dB"),
]

nomes, n_erros, textos = [], [], []
for i, (mod, canal, eb, nome) in enumerate(CASOS):
    rng = np.random.default_rng([2026, i])           # semente fixa: sempre o mesmo resultado
    tx, rx, texto, _ = run_message(MSG, mod=mod, ebn0_db=eb, rng=rng, channel=canal)
    nomes.append(nome)
    n_erros.append(int((tx != rx).sum()))
    textos.append(texto)

fig, (ax, ax2) = plt.subplots(2, 1, figsize=(11, 8), gridspec_kw={"height_ratios": [3, 2]})
cores = ["#2ca02c" if e == 0 else "#ff7f0e" if e < 10 else "#d62728" for e in n_erros]
barras = ax.bar(nomes, n_erros, color=cores)
for b, e in zip(barras, n_erros):
    ax.text(b.get_x() + b.get_width() / 2, e + 0.3, str(e), ha="center", fontsize=12, fontweight="bold")
ax.set_ylabel(f"Bits errados (de {len(MSG) * 8} enviados)", fontsize=11)
ax.set_title("Experimento C: a mesma frase enviada em condições diferentes",
             fontsize=14, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)

ax2.axis("off")
ax2.text(0, 1, f"Enviado:  {MSG}", fontsize=11, family="monospace", fontweight="bold", va="top")
for j, (nome, texto) in enumerate(zip(nomes, textos)):
    seguro = "".join(c if c.isprintable() else "?" for c in texto)
    ax2.text(0, 0.82 - j * 0.15, f"{nome.replace(chr(10), ' '):<20s} {seguro}",
             fontsize=10.5, family="monospace", va="top")
fig.tight_layout()
Path("results/figs").mkdir(parents=True, exist_ok=True)
fig.savefig("results/figs/mensagem.png", dpi=150)
print("Gráfico salvo em results/figs/mensagem.png")