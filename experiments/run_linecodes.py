"""Experimento B: codificações de linha (nenhuma, Manchester, Bifase Mark) sobre BPSK, em AWGN e rajadas.
Rodar da raiz:  python -m experiments.run_linecodes
Saída: results/raw/linecode_runs.csv, results/raw/config_B.json, results/figs/linecodes.png
e results/tabela_linecodes.md"""
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.pipeline import run_chain

CFG = dict(base_seed=20261120, ebn0_db=list(range(0, 15, 2)), n_bits=200_000, reps=10,
           channels=["awgn", "burst"], lines=["none", "manchester", "bifase_mark"], mod="bpsk",
           burst=dict(p_gb=0.01, p_bg=0.1, penalty_db=12.0))
RAW, FIG = Path("results/raw"), Path("results/figs")
NOME = {"none": "Sem código de linha", "manchester": "Manchester", "bifase_mark": "Bifase Mark"}
T975 = 2.262   # t de Student, 9 graus de liberdade (10 repetições)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    (RAW / "config_B.json").write_text(json.dumps(CFG, indent=1))
    linhas = []
    for ci, ch in enumerate(CFG["channels"]):
        for li, line in enumerate(CFG["lines"]):
            for ei, eb in enumerate(CFG["ebn0_db"]):
                for r in range(CFG["reps"]):
                    rng = np.random.default_rng([CFG["base_seed"], ci, li, ei, r])
                    bits = rng.integers(0, 2, CFG["n_bits"], dtype=np.uint8)
                    rx, viol = run_chain(bits, line=line, mod=CFG["mod"], ebn0_db=eb, rng=rng,
                                         channel=ch, burst=CFG["burst"])
                    e = int(np.count_nonzero(bits != rx))
                    linhas.append(dict(channel=ch, line=line, ebn0_db=eb, rep=r, n_bits=CFG["n_bits"],
                                       errors=e, ber=e / CFG["n_bits"], violations=viol))
    with open(RAW / "linecode_runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)

    ag = defaultdict(list)
    for l in linhas:
        ag[(l["channel"], l["line"], l["ebn0_db"])].append((l["ber"], l["violations"] / l["n_bits"]))

    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, ch in zip(axs, CFG["channels"]):
        for line in CFG["lines"]:
            x, m, ci = [], [], []
            for eb in CFG["ebn0_db"]:
                v = np.array([a for a, _ in ag[(ch, line, eb)]])
                if v.mean() > 0:
                    x.append(eb)
                    m.append(v.mean())
                    ci.append(T975 * v.std(ddof=1) / np.sqrt(len(v)))
            m, ci = np.array(m), np.array(ci)
            ax.errorbar(x, m, yerr=np.minimum(ci, m * 0.999), marker="o", ms=4, capsize=3, label=NOME[line])
        ax.set_yscale("log")
        ax.set_ylim(1e-6, 1)
        ax.grid(True, which="both", alpha=0.3)
        ax.set_xlabel("Eb/N0 por bit de informação (dB)")
        ax.set_title(f"BPSK – canal {'AWGN' if ch == 'awgn' else 'com rajadas'} (IC 95%, 10 × 200 kbit)",
                     fontsize=10)
        ax.legend(fontsize=8)
    axs[0].set_ylabel("BER")
    fig.tight_layout()
    fig.savefig(FIG / "linecodes.png", dpi=150)

    md = ["| Canal | Código de linha | Eb/N0 | BER média | Violações por bit |", "|---|---|---|---|---|"]
    for ch in CFG["channels"]:
        for line in CFG["lines"]:
            for eb in (4, 8, 12):
                v = np.array(ag[(ch, line, eb)])
                md.append(f"| {ch} | {NOME[line]} | {eb} dB | {v[:, 0].mean():.2e} | {v[:, 1].mean():.2e} |")
    Path("results/tabela_linecodes.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
