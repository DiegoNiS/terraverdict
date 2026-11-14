#!/usr/bin/env python3
"""Análisis preliminar con datos reales: cabecera del sistema regulado del Chili.

Fuentes (descargadas en cada ejecución, sin datos inventados):
  * NASA POWER, serie mensual por punto (T2M y PRECTOTCORR; fuente MERRA-2).
  * NOAA CPC, índice ONI (El Niño-Oscilación del Sur).

Cálculos:
  1. Series anuales: temperatura media anual (T2M) y lluvia de la temporada
     húmeda dic-mar (PRECTOTCORR), por año hidrológico.
  2. Tendencia de Theil-Sen por década con IC al 90 %, Mann-Kendall clásico y
     con corrección por autocorrelación (Hamed-Rao).
  3. Filtro ENSO: regresión serie ~ tiempo + ONI(dic-ene-feb) y correlación.
  4. Ventanas: todas las ventanas de 20 años o más; % con el mismo signo.
  5. Detectabilidad (Weatherhead et al., 1998): años necesarios para detectar
     la pendiente observada con el ruido observado.

Limitación declarada: un solo producto (POWER/MERRA-2) en un solo punto. Sin
la prueba de independencia, ningún resultado puede calificar como "robusto"
según las reglas del proyecto: todos se reportan como preliminares.

Uso: python scripts/analisis_preliminar.py [--salida docs/verificacion/analisis_preliminar.json]
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import json
from pathlib import Path

import numpy as np
import pymannkendall as mk
import requests
from scipy import stats

LON, LAT = -71.25, -15.95  # cabecera (zona de El Frayle / Pillones), aproximado
INICIO, FIN = 1981, 2024
VENTANA_MIN = 20


def descargar_power() -> tuple[dict, dict]:
    r = requests.get(
        "https://power.larc.nasa.gov/api/temporal/monthly/point",
        params={"parameters": "T2M,PRECTOTCORR", "community": "AG",
                "longitude": LON, "latitude": LAT, "start": INICIO, "end": FIN,
                "format": "JSON"}, timeout=180)
    r.raise_for_status()
    j = r.json()
    return j["properties"]["parameter"], {
        "unidades": {k: v.get("units") for k, v in j.get("parameters", {}).items()},
        "fuentes": j["header"].get("sources"),
        "elevacion_celda_m": j["geometry"]["coordinates"][2]}


def descargar_oni() -> dict[int, float]:
    """ONI de la estación DJF, indexado por el año de enero-febrero."""
    txt = requests.get("https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
                       timeout=60).text.strip().splitlines()[1:]
    return {int(p[1]): float(p[3]) for p in (l.split() for l in txt) if p[0] == "DJF"}


def mensual(par: dict, nombre: str) -> dict[tuple[int, int], float]:
    out = {}
    for k, v in par[nombre].items():
        anio, mes = int(k[:4]), int(k[4:])
        if mes <= 12 and v not in (-999, -999.0):
            out[(anio, mes)] = float(v)
    return out


def tendencia(nombre: str, anios: np.ndarray, x: np.ndarray, oni: dict[int, float]) -> dict:
    res: dict = {"variable": nombre, "n": int(len(x)),
                 "periodo": [int(anios[0]), int(anios[-1])],
                 "serie": {int(a): round(float(v), 3) for a, v in zip(anios, x)}}
    pend, ord0, lo, hi = stats.theilslopes(x, anios, alpha=0.90)
    res["sen_por_decada"] = round(10 * pend, 4)
    res["ic90_por_decada"] = [round(10 * lo, 4), round(10 * hi, 4)]
    m0, mh = mk.original_test(x), mk.hamed_rao_modification_test(x)
    res["mk_p"] = round(float(m0.p), 4)
    res["mk_hamed_rao_p"] = round(float(mh.p), 4)
    # Regla conservadora del proyecto: se usa el mayor p de las variantes.
    res["p_conservador"] = max(res["mk_p"], res["mk_hamed_rao_p"])

    # Filtro ENSO
    o = np.array([oni.get(int(a), np.nan) for a in anios])
    ok = ~np.isnan(o)
    X = np.column_stack([np.ones(ok.sum()), anios[ok] - anios[ok].mean(), o[ok]])
    beta, *_ = np.linalg.lstsq(X, x[ok], rcond=None)
    resid = x[ok] - X @ beta
    dof = ok.sum() - 3
    s2 = resid @ resid / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    t_b = beta[1] / np.sqrt(cov[1, 1])
    res["enso"] = {
        "r_pearson_con_oni_djf": round(float(stats.pearsonr(x[ok], o[ok])[0]), 3),
        "p_pearson": round(float(stats.pearsonr(x[ok], o[ok])[1]), 4),
        "pendiente_sin_enso_por_decada": round(10 * float(beta[1]), 4),
        "p_pendiente_sin_enso": round(float(2 * stats.t.sf(abs(t_b), dof)), 4),
        "coef_oni": round(float(beta[2]), 4),
    }

    # Ventanas
    signo = np.sign(pend)
    mismos, sig, total = 0, 0, 0
    for i in range(len(x)):
        for j in range(i + VENTANA_MIN - 1, len(x)):
            p_ij = stats.theilslopes(x[i:j + 1], anios[i:j + 1])[0]
            total += 1
            mismos += np.sign(p_ij) == signo
            sig += mk.original_test(x[i:j + 1]).p < 0.10
    res["ventanas"] = {"n_ventanas": total, "pct_mismo_signo": round(100 * mismos / total, 1),
                       "pct_significativas_p010": round(100 * sig / total, 1)}

    # Detectabilidad (Weatherhead et al., 1998)
    r_full = x - (ord0 + pend * anios)
    phi = float(np.corrcoef(r_full[:-1], r_full[1:])[0, 1])
    sigma = float(np.std(r_full, ddof=1))
    if pend != 0:
        n_star = ((3.3 * sigma / abs(pend)) * np.sqrt((1 + phi) / (1 - phi))) ** (2 / 3)
        res["detectabilidad"] = {"sigma_ruido": round(sigma, 4), "phi_ar1": round(phi, 3),
                                 "anios_necesarios": round(float(n_star), 1),
                                 "anios_disponibles": int(len(x))}
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default="docs/verificacion/analisis_preliminar.json")
    args = ap.parse_args()
    par, meta = descargar_power()
    oni = descargar_oni()
    t2m, pr = mensual(par, "T2M"), mensual(par, "PRECTOTCORR")

    # Temperatura media anual
    anios_t = np.array([a for a in range(INICIO, FIN + 1) if all((a, m) in t2m for m in range(1, 13))])
    temp = np.array([np.mean([t2m[(a, m)] for m in range(1, 13)]) for a in anios_t])

    # Lluvia dic-mar por año hidrológico (dic del año anterior + ene-mar). PRECTOTCORR
    # mensual de POWER viene en mm/día: se multiplica por los días del mes.
    def total_temporada(a: int) -> float | None:
        meses = [(a - 1, 12), (a, 1), (a, 2), (a, 3)]
        if not all(k in pr for k in meses):
            return None
        return sum(pr[k] * calendar.monthrange(*k)[1] for k in meses)

    anios_p = np.array([a for a in range(INICIO + 1, FIN + 1) if total_temporada(a) is not None])
    lluvia = np.array([total_temporada(int(a)) for a in anios_p])

    salida = {
        "generado_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "punto": {"lon": LON, "lat": LAT}, "fuente_power": meta,
        "advertencia": ("Un solo producto (POWER/MERRA-2) en un punto; sin prueba de "
                        "independencia ni de sensor. Resultados preliminares."),
        "temperatura_media_anual_C": tendencia("T2M media anual (°C)", anios_t, temp, oni),
        "lluvia_dic_mar_mm": tendencia("PRECTOTCORR dic-mar (mm)", anios_p, lluvia, oni),
        "lluvia_dic_mar_resumen": {"media_mm": round(float(lluvia.mean()), 1),
                                   "min_mm": round(float(lluvia.min()), 1),
                                   "anio_min": int(anios_p[lluvia.argmin()]),
                                   "max_mm": round(float(lluvia.max()), 1),
                                   "anio_max": int(anios_p[lluvia.argmax()])},
    }
    Path(args.salida).parent.mkdir(parents=True, exist_ok=True)
    Path(args.salida).write_text(json.dumps(salida, ensure_ascii=False, indent=1))
    print(json.dumps(salida, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
