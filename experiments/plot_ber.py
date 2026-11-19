"""Gráficos BER x Eb/N0 (com intervalo de confiança de 95%) e tabela de compromisso.
Rodar da raiz:  python -m experiments.plot_ber   (depois de run_ber)"""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.metrics import spectral_efficiency
from src.modulation import MODULATIONS, theory_ber

RAW, FIG = Path("results/raw"), Path("results/figs")
T975 = {4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 14: 2.145, 19: 2.093}
NOMES = {"bpsk": "BPSK", "qpsk": "QPSK", "qam16": "16-QAM"}
COR = {"bpsk": "tab:blue", "qpsk": "tab:green", "qam16": "tab:red"}
MARC = {"bpsk": "o", "qpsk": "s", "qam16": "^"}
CANAL = {"awgn": "AWGN", "burst": "Rajadas (Gilbert-Elliott)"}


def carregar():
    d, nb = defaultdict(list), {}
    with open(RAW / "ber_runs.csv") as f:
        for r in csv.DictReader(f):
            k = (r["channel"], r["mod"], int(r["ebn0_db"]))
            d[k].append(float(r["ber"]))
            nb[k] = int(r["n_bits"])
    res = {}
    for k, v in d.items():
        v = np.array(v)
        n = len(v)
        dp = v.std(ddof=1)
        t = T975.get(n - 1, 1.96)                       # t de Student para IC de 95%
        res[k] = dict(mean=v.mean(), std=dp, ci=t * dp / np.sqrt(n), n=n, total=n * nb[k])
    return res


def curva(ax, res, canal, mod, teoria=True):
    ebs = sorted({k[2] for k in res if k[0] == canal and k[1] == mod})
    pts = [res[(canal, mod, e)] for e in ebs]
    x = np.array(ebs, dtype=float)
    m = np.array([p["mean"] for p in pts])
    ci = np.array([p["ci"] for p in pts])
    ub = np.array([3 / p["total"] for p in pts])
    ok = m > 0
    ax.errorbar(x[ok], m[ok], yerr=np.minimum(ci[ok], m[ok] * 0.999), color=COR[mod], marker=MARC[mod],
                ms=5, capsize=3, lw=1.3, label=f"{NOMES[mod]} (simulado)")
    if (~ok).any():                                     # zero erros: regra dos 3 (limite superior de 95%)
        ax.plot(x[~ok], ub[~ok], "v", mfc="none", color=COR[mod], ms=7)
    if teoria:
        xs = np.linspace(x.min(), x.max(), 100)
        ax.semilogy(xs, theory_ber(mod, xs), "--", color=COR[mod], lw=1, alpha=0.7)


def estilo(ax, titulo):
    ax.set_yscale("log")
    ax.set_xlabel("Eb/N0 (dB)")
    ax.set_ylabel("BER")
    ax.set_title(titulo, fontsize=10)
    ax.grid(True, which="both", alpha=0.3)
    ax.set_ylim(1e-7, 1)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    res = carregar()
    for canal in ("awgn", "burst"):
        fig, ax = plt.subplots(figsize=(7, 5))
        for mod in MODULATIONS:
            curva(ax, res, canal, mod)
        ax.plot([], [], "k--", lw=1, label="teoria AWGN")
        ax.plot([], [], "kv", mfc="none", ls="", label="0 erros (limite sup. 95%)")
        estilo(ax, f"BER x Eb/N0 – canal {CANAL[canal]} (barras = IC 95%, 10 repetições × 1 Mbit)")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(FIG / f"ber_{canal}.png", dpi=150)
        plt.close(fig)

    fig, axs = plt.subplots(1, 3, figsize=(13, 4.3), sharey=True)
    for ax, mod in zip(axs, MODULATIONS):
        for canal, cor, mk in (("awgn", "tab:blue", "o"), ("burst", "tab:orange", "s")):
            ebs = sorted({k[2] for k in res if k[0] == canal and k[1] == mod})
            m = np.array([res[(canal, mod, e)]["mean"] for e in ebs])
            ci = np.array([res[(canal, mod, e)]["ci"] for e in ebs])
            ok = m > 0
            ax.errorbar(np.array(ebs)[ok], m[ok], yerr=np.minimum(ci[ok], m[ok] * 0.999), color=cor,
                        marker=mk, capsize=3, label=CANAL[canal])
        estilo(ax, NOMES[mod])
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "awgn_vs_burst.png", dpi=150)
    plt.close(fig)

    # tabela de compromisso BER x eficiência espectral
    ref = [4, 8, 12]
    linhas = [["Modulação", "Eficiência (bit/s/Hz)"]
              + [f"BER AWGN {e} dB" for e in ref] + [f"BER rajadas {e} dB" for e in ref]
              + ["Eb/N0 mín. p/ BER<=1e-3 (AWGN)", "Eb/N0 mín. p/ BER<=1e-3 (rajadas)"]]
    for mod in MODULATIONS:
        l = [NOMES[mod], f"{spectral_efficiency(MODULATIONS[mod].k):.0f}"]
        for canal in ("awgn", "burst"):
            l += [f"{res[(canal, mod, e)]['mean']:.2e}" for e in ref]
        for canal in ("awgn", "burst"):
            ok = [e for e in range(0, 15, 2) if res[(canal, mod, e)]["mean"] <= 1e-3]
            l.append(f"{min(ok)} dB" if ok else "> 14 dB")
        linhas.append(l)
    with open("results/tabela_compromisso.csv", "w", newline="") as f:
        csv.writer(f).writerows(linhas)
    md = ["| " + " | ".join(linhas[0]) + " |", "|" + "---|" * len(linhas[0])]
    md += ["| " + " | ".join(r) + " |" for r in linhas[1:]]
    Path("results/tabela_compromisso.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
