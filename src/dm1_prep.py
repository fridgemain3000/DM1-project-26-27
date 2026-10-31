"""Funzioni di supporto per il Modulo 1 (Data Understanding & Preparation).

Tenute qui per non appesantire il notebook e per riusarle nei moduli successivi.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

# Colonne numeriche che nel CSV contengono valori corrotti (lette come stringhe)
CORRUPTED_COLS = [
    "price_median", "back_legroom_median", "front_legroom_median",
    "fuel_tank_volume_median", "height_median", "length_median", "width_median",
]

TARGET = "seller_rating_class"
TARGET_ORDER = ["low", "medium", "high"]


def load_raw(path):
    """Carica il CSV grezzo (separatore ';')."""
    return pd.read_csv(path, sep=";")


def _candidates(raw):
    """Tutti i numeri ottenibili rimettendo il punto decimale in ogni posizione."""
    digits = raw.replace(".", "").lstrip("0") or "0"
    return [float(digits[:k] + "." + digits[k:]) for k in range(1, len(digits) + 1)]


def repair_corrupted_numeric(s, q_low=0.001, q_high=0.999):
    """Ripara una colonna numerica con valori tipo '38.650.000.000.000.000'.

    I valori leggibili restano invariati. Per quelli corrotti si provano tutte le
    posizioni del punto decimale e si tiene il candidato che cade nel range
    plausibile della colonna [quantile q_low, quantile q_high], calcolato sui soli
    valori leggibili. Zero candidati o più di uno → NaN (non si inventa nulla).

    Restituisce (serie riparata, dizionario con i conteggi).
    """
    clean = pd.to_numeric(s, errors="coerce")
    bad_mask = s.notna() & clean.isna()
    lo, hi = clean.quantile(q_low), clean.quantile(q_high)

    repaired = clean.copy()
    n_ok = n_amb = n_none = 0
    for idx, raw in s[bad_mask].items():
        ok = [x for x in _candidates(str(raw)) if lo <= x <= hi]
        if len(ok) == 1:
            repaired.loc[idx] = ok[0]
            n_ok += 1
        elif len(ok) > 1:
            n_amb += 1
        else:
            n_none += 1

    report = {"corrotti": int(bad_mask.sum()), "riparati": n_ok,
              "ambigui→NaN": n_amb, "senza candidato→NaN": n_none,
              "range plausibile": f"[{lo:g}, {hi:g}]"}
    return repaired, report, bad_mask


def describe_plus(df, cols):
    """describe() esteso con asimmetria, curtosi, zeri, valori distinti e % NaN."""
    d = df[cols].describe(percentiles=[0.01, 0.25, 0.5, 0.75, 0.99]).T
    d["skew"] = df[cols].skew()
    d["kurt"] = df[cols].kurt()
    d["n_zeri"] = (df[cols] == 0).sum()
    d["n_distinti"] = df[cols].nunique()
    d["%NaN"] = df[cols].isna().mean() * 100
    return d


def iqr_bounds(s, k=1.5):
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def iqr_outlier_table(df, cols, ks=(1.5, 3.0)):
    """Numero e % di outlier per colonna secondo la regola k·IQR."""
    rows = {}
    for c in cols:
        s = df[c].dropna()
        row = {}
        for k in ks:
            lo, hi = iqr_bounds(s, k)
            n = int(((s < lo) | (s > hi)).sum())
            row[f"n_out_{k}IQR"] = n
            row[f"%_out_{k}IQR"] = round(100 * n / len(s), 2)
        rows[c] = row
    return pd.DataFrame(rows).T


def cramers_v(x, y):
    """V di Cramér (con correzione di Bergsma) tra due variabili categoriche."""
    table = pd.crosstab(x, y)
    if min(table.shape) < 2:
        return np.nan
    chi2 = chi2_contingency(table, correction=False)[0]
    n = table.values.sum()
    phi2 = chi2 / n
    r, k = table.shape
    phi2corr = max(0.0, phi2 - (k - 1) * (r - 1) / (n - 1))
    rcorr = r - (r - 1) ** 2 / (n - 1)
    kcorr = k - (k - 1) ** 2 / (n - 1)
    return float(np.sqrt(phi2corr / min(kcorr - 1, rcorr - 1)))


def cramers_v_matrix(df, cols):
    m = pd.DataFrame(index=cols, columns=cols, dtype=float)
    for a in cols:
        for b in cols:
            m.loc[a, b] = 1.0 if a == b else cramers_v(df[a], df[b])
    return m


def save_fig(fig, name, folder):
    """Salva la figura in PNG ad alta risoluzione per il report."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    fig.savefig(folder / f"{name}.png", dpi=300, bbox_inches="tight")
