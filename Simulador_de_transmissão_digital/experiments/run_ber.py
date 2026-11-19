"""Experimento A: BER x Eb/N0 de BPSK, QPSK e 16-QAM em AWGN e em canal com rajadas.
Rodar da raiz:  python -m experiments.run_ber
Saída: results/raw/ber_runs.csv (um registro por ensaio) e results/raw/config_A.json."""
import csv
import json
import time
from pathlib import Path

import numpy as np

from src.pipeline import run_chain

CFG = dict(
    base_seed=20261119,
    ebn0_db=list(range(0, 15, 2)),          # 8 valores: 0, 2, ..., 14 dB
    n_bits=1_000_000,                       # bits por ensaio (mínimo exigido: 100 mil)
    reps=10,                                # repetições com sementes diferentes (mínimo: 5)
    channels=["awgn", "burst"],
    mods=["bpsk", "qpsk", "qam16"],
    line="none",                            # sem codificação de linha (isolar o efeito da modulação)
    burst=dict(p_gb=0.01, p_bg=0.1, penalty_db=12.0),
)
OUT = Path("results/raw")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "config_A.json").write_text(json.dumps(CFG, indent=1))
    linhas, t0 = [], time.time()
    for ci, ch in enumerate(CFG["channels"]):
        for mi, mod in enumerate(CFG["mods"]):
            for ei, eb in enumerate(CFG["ebn0_db"]):
                for r in range(CFG["reps"]):
                    # semente = (base, canal, modulação, Eb/N0, repetição): cada ensaio é reproduzível
                    rng = np.random.default_rng([CFG["base_seed"], ci, mi, ei, r])
                    bits = rng.integers(0, 2, CFG["n_bits"], dtype=np.uint8)
                    rx, _ = run_chain(bits, line=CFG["line"], mod=mod, ebn0_db=eb, rng=rng,
                                      channel=ch, burst=CFG["burst"])
                    erros = int(np.count_nonzero(bits != rx))
                    linhas.append(dict(channel=ch, mod=mod, ebn0_db=eb, rep=r,
                                       n_bits=CFG["n_bits"], errors=erros, ber=erros / CFG["n_bits"]))
            print(f"{ch:5s} {mod:5s} ok  ({time.time() - t0:5.1f}s)", flush=True)
    with open(OUT / "ber_runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    print(f"{len(linhas)} ensaios gravados em {OUT / 'ber_runs.csv'}")


if __name__ == "__main__":
    main()
