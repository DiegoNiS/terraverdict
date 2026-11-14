#!/usr/bin/env python3
"""Verificación reproducible de las fuentes de datos de TerraVerdict.

Consulta los catálogos y servicios oficiales y guarda la evidencia en JSON.
No descarga productos completos: comprueba que cada colección existe, su
periodo publicado, que hay datos sobre la cuenca del Chili y que el servicio
responde.

Uso:
    python scripts/verificar_fuentes.py [--salida docs/verificacion/evidencia.json]

Requisitos: Python 3.10+, requests. Opcional: pdftotext (poppler) para leer
el reporte de AUTODEMA.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import json
import math
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import requests

# Caja que cubre la cabecera del sistema regulado del Chili y la ciudad
# (lon_min, lat_min, lon_max, lat_max). Aproximada: se reemplaza por el
# polígono oficial de la ANA en la implementación.
BBOX = "-71.6,-16.5,-70.9,-15.3"
PUNTO_CABECERA = (-71.25, -15.95)  # lon, lat (zona de El Frayle / Pillones)
PUNTO_CIUDAD = (-71.535, -16.4)
CMR = "https://cmr.earthdata.nasa.gov/search/"
TIMEOUT = 90

# (clave, short_name, versión) de colecciones NASA en CMR.
COLECCIONES_CMR = [
    ("imerg_final_mensual", "GPM_3IMERGM", "07"),
    ("imerg_final_diaria", "GPM_3IMERGDF", "07"),
    ("imerg_early_30min", "GPM_3IMERGHHE", "07"),
    ("imerg_late_30min", "GPM_3IMERGHHL", "07"),
    ("merra2_superficie_mensual", "M2TMNXSLV", "5.12.4"),
    ("merra2_flujos_mensual", "M2TMNXFLX", "5.12.4"),
    ("gldas21_noah_mensual", "GLDAS_NOAH025_M", "2.1"),
    ("gldas20_noah_mensual", "GLDAS_NOAH025_M", "2.0"),
    ("fldas_chirps_mensual", "FLDAS_NOAH01_C_GL_M", "001"),
    ("modis_lst_terra_8d", "MOD11A2", "061"),
    ("modis_lst_aqua_8d", "MYD11A2", "061"),
    ("modis_ndvi_terra_16d", "MOD13Q1", "061"),
    ("modis_et_8d", "MOD16A2GF", "061"),
    ("modis_nieve_diaria", "MOD10A1", "61"),
    ("modis_nieve_sin_nubes", "MOD10A1F", "61"),
    ("modis_area_quemada", "MCD64A1", "061"),
    ("viirs_ndvi_16d", "VNP13A1", "002"),
    ("viirs_lst_diaria", "VNP21A1D", "002"),
    ("viirs_nieve_sin_nubes", "VNP10A1F", "2"),
    ("viirs_fuegos_375m", "VNP14IMG", "002"),
    ("smap_l3_9km", "SPL3SMP_E", "006"),
    ("smap_l4_9km_3h", "SPL4SMGP", "008"),
    ("nasadem", "NASADEM_HGT", "001"),
    ("hls_landsat", "HLSL30", "2.0"),
    ("hls_sentinel2", "HLSS30", "2.0"),
    ("icesat2_aguas_interiores", "ATL13", "007"),
    ("swot_lagos_obs", "SWOT_L2_HR_LakeSP_obs_D", "D"),
    ("swot_lagos_prior", "SWOT_L2_HR_LakeSP_prior_D", "D"),
    ("nisar_gcov", "NISAR_L2_GCOV_V1", "1"),
]

PRODUCTOS_APPEEARS = [
    "HLSL30.020", "HLSS30.020", "SPL3SMP_E.006", "SPL4SMGP.008",
    "NASADEM_NC.001", "VNP13A1.002", "VNP21A1D.002", "VNP10A1.002",
    "MOD16A2GF.061", "MOD11A2.061", "MOD13Q1.061", "MOD10A1.061",
    "MCD64A1.061", "ECO_L2T_LSTE.002",
]


def sesion() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = "terraverdict-verificacion/1.0"
    return s


def cmr_coleccion(s: requests.Session, short_name: str, version: str) -> dict[str, Any]:
    r = s.get(CMR + "collections.json",
              params={"short_name": short_name, "version": version, "page_size": 1},
              timeout=TIMEOUT)
    r.raise_for_status()
    entradas = r.json()["feed"]["entry"]
    if not entradas:
        return {"existe": False}
    e = entradas[0]
    g = s.get(CMR + "granules.json",
              params={"collection_concept_id": e["id"], "bounding_box": BBOX,
                      "page_size": 1, "sort_key": "-start_date"},
              timeout=TIMEOUT)
    g.raise_for_status()
    ult = g.json()["feed"]["entry"]
    return {
        "existe": True,
        "titulo": e.get("title"),
        "centro": e.get("data_center"),
        "inicio": (e.get("time_start") or "")[:10],
        "fin": (e.get("time_end") or "")[:10] or "vigente",
        "granulos_sobre_cuenca": int(g.headers.get("CMR-Hits", 0)),
        "ultimo_granulo_cuenca": (ult[0].get("time_start", "")[:10] if ult else None),
    }


def appeears(s: requests.Session) -> dict[str, Any]:
    productos = s.get("https://appeears.earthdatacloud.nasa.gov/api/product",
                      timeout=TIMEOUT).json()
    ids = {p["ProductAndVersion"] for p in productos}
    return {"productos_totales": len(productos),
            "disponibles": {p: p in ids for p in PRODUCTOS_APPEEARS}}


def power(s: requests.Session) -> dict[str, Any]:
    lon, lat = PUNTO_CABECERA
    r = s.get("https://power.larc.nasa.gov/api/temporal/monthly/point",
              params={"parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,ALLSKY_SFC_SW_DWN,RH2M,WS2M",
                      "community": "AG", "longitude": lon, "latitude": lat,
                      "start": 1981, "end": 2024, "format": "JSON"},
              timeout=180)
    r.raise_for_status()
    j = r.json()
    par = j["properties"]["parameter"]
    return {"parametros": {k: len(v) for k, v in par.items()},
            "fuentes": j["header"].get("sources"),
            "elevacion_celda_m": j["geometry"]["coordinates"][2]}


def indices_enso(s: requests.Session) -> dict[str, Any]:
    oni = s.get("https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
                timeout=TIMEOUT).text.strip().splitlines()
    roni = s.get("https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt",
                 timeout=TIMEOUT).text.strip().splitlines()
    knmi = s.get("https://climexp.knmi.nl/data/iersst_nino3.4a.dat",
                 timeout=TIMEOUT).text.strip().splitlines()
    return {"oni_registros": len(oni) - 1, "oni_primero": oni[1].split(),
            "oni_ultimo": oni[-1].split(), "roni_ultimo": roni[-1].split(),
            "knmi_nino34_ultimo": knmi[-1].split()}


def ghcn_arequipa(s: requests.Session) -> dict[str, Any]:
    estaciones = s.get("https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt",
                       timeout=180).text.splitlines()
    lon0, lat0 = PUNTO_CIUDAD
    cercanas = []
    for l in estaciones:
        if not l.startswith("PE"):
            continue
        lat, lon = float(l[12:20]), float(l[21:30])
        d = math.hypot(lat - lat0, (lon - lon0) * math.cos(math.radians(lat0))) * 111.2
        if d < 150:
            cercanas.append({"id": l[0:11], "nombre": l[41:71].strip(), "lat": lat,
                             "lon": lon, "elev_m": float(l[31:37]), "dist_km": round(d)})
    resultado: dict[str, Any] = {"estaciones_a_150km": cercanas, "completitud": {}}
    for est in cercanas:
        raw = s.get(f"https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/{est['id']}.csv.gz",
                    timeout=180).content
        conteo: dict[str, Counter] = defaultdict(Counter)
        for fila in gzip.decompress(raw).decode().splitlines():
            p = fila.split(",")
            if p[2] in ("PRCP", "TMAX", "TMIN"):
                conteo[p[2]][int(p[1][:4])] += 1
        resultado["completitud"][est["id"]] = {
            el: {"anios_con_datos": len(c),
                 "anios_90pct": sorted(a for a, n in c.items() if n >= 330),
                 "rango": [min(c), max(c)] if c else None}
            for el, c in conteo.items()}
    return resultado


def copernicus(s: requests.Session) -> dict[str, Any]:
    lon, lat = PUNTO_CABECERA
    out = {}
    for col in ("SENTINEL-1", "SENTINEL-2"):
        filtro = (f"Collection/Name eq '{col}' and OData.CSC.Intersects("
                  f"area=geography'SRID=4326;POINT({lon} {lat})')")
        r = s.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
                  params={"$filter": filtro, "$top": 1, "$orderby": "ContentDate/Start desc"},
                  timeout=TIMEOUT)
        r.raise_for_status()
        v = r.json().get("value", [])
        out[col] = v[0]["Name"] if v else None
    return out


def autodema(s: requests.Session) -> dict[str, Any]:
    url = "https://www.autodema.gob.pe/wp-content/uploads/2024/03/REPORTE-HIDRICO.pdf"
    r = s.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    info: dict[str, Any] = {"url": url, "tipo": r.headers.get("content-type"),
                            "bytes": len(r.content)}
    if shutil.which("pdftotext"):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(r.content)
            f.flush()
            texto = subprocess.run(["pdftotext", "-layout", f.name, "-"],
                                   capture_output=True, text=True, check=True).stdout
        info["menciona_total_chili"] = "Total Cuenca Chili" in texto
        info["lineas_volumen_util"] = sum("Volumen Útil" in l for l in texto.splitlines())
    return info


def estado_http(s: requests.Session, url: str) -> int:
    return s.get(url, timeout=TIMEOUT).status_code


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default="docs/verificacion/evidencia.json")
    args = ap.parse_args()
    s = sesion()
    evidencia: dict[str, Any] = {
        "generado_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "bbox_cuenca": BBOX, "resultados": {}}

    def correr(clave: str, f: Callable[[], Any]) -> None:
        try:
            evidencia["resultados"][clave] = {"ok": True, "datos": f()}
        except Exception as ex:  # se registra el fallo, no se oculta
            evidencia["resultados"][clave] = {"ok": False, "error": f"{type(ex).__name__}: {ex}"[:300]}
        estado = "OK " if evidencia["resultados"][clave]["ok"] else "ERR"
        print(f"[{estado}] {clave}", file=sys.stderr)

    for clave, sn, ver in COLECCIONES_CMR:
        correr(f"cmr:{clave}", lambda sn=sn, ver=ver: cmr_coleccion(s, sn, ver))
    correr("appeears", lambda: appeears(s))
    correr("nasa_power", lambda: power(s))
    correr("enso", lambda: indices_enso(s))
    correr("ghcn_arequipa", lambda: ghcn_arequipa(s))
    correr("copernicus_sentinel", lambda: copernicus(s))
    correr("autodema_reporte", lambda: autodema(s))
    correr("gibs_wmts", lambda: estado_http(
        s, "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/1.0.0/WMTSCapabilities.xml"))
    correr("giovanni", lambda: estado_http(s, "https://giovanni.gsfc.nasa.gov/giovanni/"))
    correr("firms_api", lambda: estado_http(s, "https://firms.modaps.eosdis.nasa.gov/api/area/"))
    correr("chirps_v3_latam_mensual", lambda: estado_http(
        s, "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/"))
    correr("data_rods_gldas", lambda: estado_http(
        s, "https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi"
           "?variable=GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi0_10cm_inst"
           "&location=GEOM:POINT(-71.25,%20-15.95)&startDate=2020-01-01T00"
           "&endDate=2020-01-02T00&type=asc2"))

    salida = Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(evidencia, ensure_ascii=False, indent=1))
    ok = sum(v["ok"] for v in evidencia["resultados"].values())
    print(f"{ok}/{len(evidencia['resultados'])} verificaciones correctas -> {salida}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
