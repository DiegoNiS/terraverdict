# Verificación de fuentes de datos

> **Fecha de verificación:** 14 de noviembre de 2026.
> **Método:** consultas reales a los catálogos y servicios oficiales con [`scripts/verificar_fuentes.py`](../../scripts/verificar_fuentes.py). La evidencia cruda está en [`evidencia.json`](evidencia.json). Cualquiera puede repetirla:
>
> ```bash
> python scripts/verificar_fuentes.py --salida docs/verificacion/evidencia.json
> ```
>
> **Resultado:** 37 de 40 comprobaciones correctas. Los tres servicios que no respondieron desde el entorno de verificación (Giovanni, la API de FIRMS y *data rods*) se marcan como **no verificados**, no como disponibles.

## 1. Niveles de verificación

| Símbolo | Significado |
|---|---|
| ✅ **V1** | Verificado con consulta real: la colección existe en el catálogo oficial, tiene periodo publicado y tiene datos sobre la cuenca del Chili |
| 🟦 **V2** | Verificado con consulta real al servicio (responde y entrega datos), sin descargar productos completos |
| 📄 **D** | Verificado solo con documentación oficial (búsqueda web); no se consultó el servicio |
| ⚠️ **P** | Pendiente: no se pudo verificar o la verificación falló |
| ❌ | Descartado para el uso previsto, con motivo |

## 2. Matriz de verificación

Caja de la cuenca usada en las consultas: lon −71,6 a −70,9; lat −16,5 a −15,3 (cabecera del sistema regulado y la ciudad). Los conteos de gránulos son los que devolvió el catálogo CMR de NASA para esa caja.

### 2.1 Colecciones NASA (catálogo CMR)

| Variable | Colección (versión) | Centro | Periodo publicado | Gránulos sobre la cuenca | Último dato sobre la cuenca | Estado |
|---|---|---|---|---|---|---|
| Lluvia (final, mensual) | GPM_3IMERGM (07) | GES DISC | 1998-01 → 2025-09 | 333 | 2025-09 | ✅ V1 |
| Lluvia (final, diaria) | GPM_3IMERGDF (07) | GES DISC | 1998-01 → 2025-09 | 10 135 | 2025-09-30 | ✅ V1 |
| Lluvia (casi tiempo real, 30 min) | GPM_3IMERGHHE (07) | GES DISC | 1998-01 → vigente | 506 136 | **2026-11-14** | ✅ V1 |
| Lluvia (tardía, 30 min) | GPM_3IMERGHHL (07) | GES DISC | 1998-01 → vigente | 506 116 | 2026-11-14 | ✅ V1 |
| Temperatura, humedad, viento | M2TMNXSLV (5.12.4) | GES DISC | 1980-01 → vigente | 561 | 2026-09 | ✅ V1 |
| Lluvia y flujos de superficie | M2TMNXFLX (5.12.4) | GES DISC | 1980-01 → vigente | 561 | 2026-09 | ✅ V1 |
| Balance hídrico (modelo) | GLDAS_NOAH025_M (2.1) | GES DISC | 2000-01 → vigente | 319 | 2026-07 | ✅ V1 |
| Balance hídrico (serie larga) | GLDAS_NOAH025_M (2.0) | GES DISC | 1948-01 → 2014-12 | 804 | 2014-12 | ✅ V1 |
| Balance forzado con CHIRPS | FLDAS_NOAH01_C_GL_M (001) | GES DISC | 1982-01 → vigente | 537 | 2026-09 | ✅ V1 |
| Temperatura de superficie (Terra) | MOD11A2 (061) | LP DAAC | 2000-02 → vigente | 1 226 | 2026-11-01 | ✅ V1 |
| Temperatura de superficie (Aqua) | MYD11A2 (061) | LP DAAC | 2002-07 → vigente | 1 119 | 2026-11-01 | ✅ V1 |
| Vegetación (NDVI/EVI 250 m) | MOD13Q1 (061) | LP DAAC | 2000-02 → vigente | 614 | 2026-10-16 | ✅ V1 |
| Evapotranspiración | MOD16A2GF (061) | LP DAAC | 2000-01 → vigente | 1 196 | **2025-12-27** | ✅ V1 |
| Nieve (diaria) | MOD10A1 (61) | NSIDC | 2000-02 → vigente | 9 588 | 2026-11-12 | ✅ V1 |
| Nieve sin nubes | MOD10A1F (61) | NSIDC | 2000-02 → vigente | 9 757 | 2026-11-12 | ✅ V1 |
| Área quemada | MCD64A1 (061) | LP DAAC | 2000-11 → vigente | 311 | 2026-09 | ✅ V1 |
| Vegetación (VIIRS, continuidad) | VNP13A1 (002) | LP DAAC | 2012-01 → vigente | 680 | 2026-10-24 | ✅ V1 |
| Temperatura de superficie (VIIRS) | VNP21A1D (002) | LP DAAC | 2012-01 → vigente | 5 325 | 2026-11-01 | ✅ V1 |
| Nieve (VIIRS, sin nubes) | VNP10A1F (2) | NSIDC | 2012-01 → vigente | 5 397 | 2026-11-03 | ✅ V1 |
| Fuegos activos (375 m) | VNP14IMG (002) | LP DAAC | 2012-01 → vigente | 13 896 | 2026-11-01 | ✅ V1 |
| Humedad del suelo (9 km, diaria) | SPL3SMP_E (006) | NSIDC | 2015-03 → vigente | 4 167 | 2026-11-12 | ✅ V1 |
| Humedad del suelo y raíces (modelo + SMAP) | SPL4SMGP (008) | NSIDC | 2015-03 → vigente | 33 961 | 2026-11-10 | ✅ V1 |
| Terreno 30 m | NASADEM_HGT (001) | LP DAAC | febrero de 2000 | 4 teselas | — | ✅ V1 |
| Reflectancia armonizada (Landsat) | HLSL30 (2.0) | LP DAAC | 2013-04 → vigente | 2 406 | 2026-10-30 | ✅ V1 |
| Reflectancia armonizada (Sentinel-2) | HLSS30 (2.0) | LP DAAC | 2015-11 → vigente | 4 379 | 2026-11-04 | ✅ V1 |
| Altura de aguas interiores | ATL13 (007) | NSIDC | 2018-10 → vigente | 216 | 2026-09-21 | ✅ V1 (cruce con cada represa: ⚠️ P) |
| Lagos y embalses: altura, área, almacenamiento | SWOT_L2_HR_LakeSP_obs_D (D) | PO.DAAC | 2022-12 → vigente | 1 361 | 2026-11-10 | ✅ V1 (presencia de cada represa en la base de lagos: ⚠️ P) |
| Radar NISAR (retrodispersión) | NISAR_L2_GCOV_V1 (1) | ASF | 2025-10 → vigente | **6** | 2026-11-01 | ✅ V1, ❌ para tendencias |

### 2.2 Servicios NASA, NOAA y aliados

| Servicio | Qué se comprobó | Resultado | Estado |
|---|---|---|---|
| **AppEEARS** (NASA) | Catálogo de productos | 193 productos; están los 14 requeridos (HLS, SMAP L3/L4, NASADEM, VIIRS, MODIS, MCD64A1, ECOSTRESS) | 🟦 V2 |
| **NASA POWER** | Serie mensual 1981–2024 en la cabecera | 7 parámetros × 572 registros; fuente MERRA-2; elevación de la celda 4232 m | 🟦 V2 |
| **NOAA CPC: ONI y RONI** | Descarga de los índices | 921 registros desde DJF 1950; **ONI ASO 2026 = +2,46; RONI ASO 2026 = +1,97** | 🟦 V2 |
| **KNMI Climate Explorer: Niño3.4** | Descarga de la serie ERSST | Último valor sep. 2026 = +2,86 (anomalía de la propia serie) | 🟦 V2 |
| **NOAA NCEI GHCN-Daily** (catálogo de Climate Data Online) | Estaciones a menos de 150 km y su completitud | Una estación: **PE000084752 Arequipa** (2520 m, 8 km de la ciudad); ver sección 4 | 🟦 V2 |
| **Copernicus Data Space: Sentinel-1 y 2** | Productos sobre la cabecera | S1C IW GRD del 11-11-2026; S2B L1C/L2A del 09-11-2026 | 🟦 V2 |
| **CHIRPS v3** (UCSB CHC) | Directorio mensual de América Latina | Responde | 🟦 V2 |
| **NASA GIBS** (imágenes de Worldview) | Capacidades WMTS | 1330 capas | 🟦 V2 |
| **AUTODEMA, reporte hídrico** | Descarga y lectura del PDF del 13-03-2024 | Volumen útil, caudal afluente, descarga y lluvia por represa; total Chili 373,30 hm³ | 🟦 V2 (archivo histórico: ⚠️ P) |
| **Giovanni** (NASA) | Página del servicio | Conexión reiniciada desde el entorno de verificación (respondió en una prueba previa, falló en la final) | ⚠️ P |
| **API de FIRMS** | Punto de acceso | Conexión reiniciada; requiere además una clave gratuita (MAP_KEY) | ⚠️ P |
| ***Data rods* de hidrología** (GES DISC) | Serie de GLDAS por punto | Conexión reiniciada | ⚠️ P |
| **JAXA G-Portal (GSMaP)** | Portal | Redirige a un dominio no habilitado; requiere registro | ⚠️ P (opcional) |
| **SWOT, información de la CSA** | Documentación | El producto LakeSP versión D estima el cambio de almacenamiento ([PO.DAAC](https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_LakeSP_obs_D)) | 📄 D |
| **RCM** (CSA) | Documentación | Productos de archivo abiertos de 16 m o más gruesos ([CSA](https://data.asc-csa.gc.ca/en/dataset/64927856-8o0t-5u1o-987izna480aa45)); cobertura sobre Arequipa no verificada | 📄 D / ⚠️ P |
| **Landsat 5/7/8/9 Collection 2** (USGS) | Gránulos en CMR | La colección existe (desde 1982), pero CMR **no expone gránulos** sobre la cuenca. El acceso a 1984–2012 es por EarthExplorer/M2M (cuenta USGS) | 📄 D / ⚠️ P |

## 3. Licencias y condiciones de uso

| Fuente | Licencia o política | Restricción relevante | Fuente de la verificación |
|---|---|---|---|
| Datos de NASA (GES DISC, LP DAAC, NSIDC, PO.DAAC, ASF) | Política de datos abiertos de NASA: uso completo y sin restricciones | Citar el producto y su DOI | [Earthdata](https://www.earthdata.nasa.gov/learn/use-data/data-use-policy) · 📄 |
| Landsat (USGS) | Dominio público | Citar | 📄 (política conocida de USGS) |
| Copernicus Sentinel | Acceso libre, completo y abierto (Reglamento UE 377/2014) | Al modificar: *"Contains modified Copernicus Sentinel data [año]"*; uso justo en descargas masivas | [Licencia Sentinel](https://ewds.climate.copernicus.eu/licences/ec-sentinel) · 📄 |
| CHIRPS v3 | Dominio público (renuncia de derechos) y CC BY 4.0 | Citar el DOI 10.15780/G2JQ0P | [CHC](https://chc.ucsb.edu/node/497) · 📄 |
| NOAA (ONI, RONI, GHCN) | Datos del Gobierno de EE. UU., uso libre | Citar | 📄 |
| KNMI Climate Explorer | Uso libre con registro para funciones completas | Respetar las condiciones de cada serie | 📄 |
| HydroSHEDS / HydroRIVERS | Uso libre científico y comercial; v2 con CC BY 4.0 | Confirmar la versión y la atribución | [HydroSHEDS](https://hydrosheds.org/terms-of-use) · 📄 (fuentes secundarias contradictorias) |
| PISCOp V2.1 (SENAMHI) | CC BY-NC-ND | **No distribuir derivados**: solo validación interna | Repositorio de SENAMHI · 📄 |
| Reportes de AUTODEMA | Documentos públicos de una entidad estatal | Sin licencia explícita: citar y usar para validación | ⚠️ P |
| GSMaP (JAXA) | Requiere registro y aceptar términos | No verificado | ⚠️ P |

## 4. Hallazgos de la verificación (datos reales)

1. **La lluvia final de IMERG llega con más de un año de rezago respecto de hoy.** El último mes final publicado es septiembre de 2025. Para los meses recientes solo existen las versiones Early y Late, que tienen otra calibración. **Consecuencia:** las tendencias usan solo IMERG Final, y las versiones rápidas se reservan para la anticipación (turbidez y temporada). Mezclarlas en una misma serie introduciría un salto artificial.
2. **La evapotranspiración MOD16A2GF se publica una vez al año.** El último dato es de diciembre de 2025.
3. **La estación de tierra de Arequipa está muy incompleta.** La estación GHCN PE000084752 tiene lluvia entre 1973 y 2025, pero solo **14 años con al menos el 90 % de días con dato**, y **ninguno desde 2010**. La temperatura máxima no tiene **ningún** año completo. **Consecuencia:** no sirve como serie continua para tendencias. Sí sirve para validar puntualmente, y es una evidencia cuantitativa del vacío de datos de tierra.
4. **NISAR todavía no tiene historia.** Hay 6 gránulos GCOV sobre la cuenca, todos desde octubre de 2026. Es útil para monitorear el presente, no para tendencias.
5. **El Niño fuerte está en curso.** ONI ASO 2026 = +2,46 y RONI = +1,97 (NOAA CPC). Esto coincide con el inicio de la temporada de lluvias 2026–27.
6. **La celda de POWER/MERRA-2 tiene una elevación media de 4232 m.** Representa la cabecera, no la ciudad (2335–2520 m). Las variables de temperatura necesitan corrección por altitud con NASADEM antes de compararlas con estaciones.
7. **Los reportes de AUTODEMA traen más de lo esperado:** caudal afluente, descarga y lluvia local de cada represa. Si se consigue el archivo histórico, son verdad terrestre para calibrar el modelo de las represas.

## 5. Incompatibilidades identificadas

| # | Incompatibilidad | Efecto si se ignora | Tratamiento |
|---|---|---|---|
| I1 | Resoluciones muy distintas: IMERG 0,1° (~11 km), MERRA-2 0,5° × 0,625°, SMAP 9 km, MODIS 250 m–1 km, HLS 30 m | Comparar escalas distintas como si fueran iguales | Agregar todo a la unidad de análisis (subcuenca o bofedal) con ponderación por área; declarar la escala de cada indicador |
| I2 | IMERG Final, Late y Early tienen calibraciones distintas | Saltos artificiales en la serie | Tendencias solo con Final; Early y Late solo para anticipación |
| I3 | Cambio de constelación en IMERG (TRMM → GPM, junio de 2014) y de sensor en Landsat (TM → ETM+ → OLI) | Tendencias falsas | Prueba de sensor del Sello de Confianza; armonización de Landsat (Roy et al., 2016) |
| I4 | Deriva de órbita de Terra desde febrero de 2020 (hora de paso más temprana) | Sesgo en la tendencia de temperatura de superficie | Contraste con Aqua y VIIRS; la prueba de sensor incluye un quiebre en 2020 |
| I5 | Periodos distintos: SMAP desde 2015, VIIRS desde 2012, HLS desde 2013, SWOT desde 2022 | Comparar tendencias de periodos distintos | Cada indicador lleva su periodo; las tendencias de largo plazo usan solo productos con 20 años o más |
| I6 | MERRA-2, GLDAS y FLDAS comparten insumos (forzantes atmosféricos) | Contar como independientes fuentes que no lo son | Grafo de procedencia: las confirmaciones se cuentan por familias |
| I7 | PISCOp no permite derivados | Riesgo legal | Solo validación interna; no se publica nada derivado de PISCOp |

## 6. Vacíos de información

| Vacío | Impacto | Cómo se cubre |
|---|---|---|
| Archivo histórico diario de los reportes de AUTODEMA | Sin él, el modelo de las represas se calibra solo con datos satelitales | Pedirlo a AUTODEMA; digitalizar con la IA verificada (sección 7b del diseño técnico) |
| Polígonos oficiales de las represas y de las subcuencas (incluidos los trasvases) | Agregaciones aproximadas | Polígonos de la ANA o máscara de agua HLS del máximo histórico |
| Presencia de cada represa en la base de lagos de SWOT | El cambio de almacenamiento directo podría no estar disponible para todas | Descargar la base de lagos (PLD) y cruzarla en la hora 0 |
| Series diarias de turbidez de SEDAPAR | La alerta de turbidez queda como prototipo | Solicitud formal a SEDAPAR |
| Estaciones de SENAMHI en la cabecera | Poca verdad terrestre de lluvia en altura | Lluvia local de los reportes de AUTODEMA; solicitud a SENAMHI |
| Landsat 1984–2012 | No se verificó el acceso automatizado | EarthExplorer/M2M con cuenta USGS; JRC Global Surface Water como alternativa |
| Una segunda familia independiente para la temperatura del aire | El sello de la tendencia de temperatura queda incompleto | ERA5 (no verificado en este entorno) o estaciones de SENAMHI |
