"""Constelações antes e depois do canal (Eb/N0 = 10 dB).
Rodar da raiz:  python -m experiments.plot_constellations"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.channel import gilbert_elliott_states, sigma_from_ebn0
from src.modulation import MODULATIONS
from src.pipeline import BURST_PADRAO

EB, N = 10, 4000


def main():
    rng = np.random.default_rng(7)
    fig, axs = plt.subplots(3, 3, figsize=(10.5, 10), sharex=True, sharey=True)
    for j, (nome, m) in enumerate(MODULATIONS.items()):
        bits = rng.integers(0, 2, N * m.k, dtype=np.uint8)
        tx, _ = m.modulate(bits)
        s = sigma_from_ebn0(EB, m.k)
        awgn = tx + s * (rng.normal(size=N) + 1j * rng.normal(size=N))
        ruim = gilbert_elliott_states(N, BURST_PADRAO["p_gb"], BURST_PADRAO["p_bg"], rng)
        sg = np.where(ruim, s * 10 ** (BURST_PADRAO["penalty_db"] / 20), s)
        rj = tx + sg * (rng.normal(size=N) + 1j * rng.normal(size=N))
        axs[0, j].scatter(tx.real, tx.imag, s=30, color="k")
        axs[1, j].scatter(awgn.real, awgn.imag, s=3, alpha=0.5)
        axs[2, j].scatter(rj.real[~ruim], rj.imag[~ruim], s=3, alpha=0.5, label="estado bom")
        axs[2, j].scatter(rj.real[ruim], rj.imag[ruim], s=3, alpha=0.5, color="tab:red", label="estado ruim")
        axs[0, j].set_title(f"{nome.upper()} – transmitido")
        axs[1, j].set_title(f"AWGN, Eb/N0 = {EB} dB")
        axs[2, j].set_title("Rajadas (vermelho = estado ruim)")
        axs[2, j].legend(fontsize=7, markerscale=4)
    for ax in axs.flat:
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_aspect("equal")
        ax.grid(alpha=0.3)
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)
    fig.supxlabel("I (em fase)")
    fig.supylabel("Q (quadratura)")
    fig.tight_layout()
    Path("results/figs").mkdir(parents=True, exist_ok=True)
    fig.savefig("results/figs/constelacoes.png", dpi=130)
    print("ok")


if __name__ == "__main__":
    main()
