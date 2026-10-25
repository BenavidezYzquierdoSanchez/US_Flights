# Diccionario de KPI

Frecuencia: actualización por cada carga del JSON; fecha de observación mensual para el cubo. No hay refresco automático del origen. Todas las divisiones sin denominador devuelven vacío.

| KPI | Fórmula | Unidad | Dirección | Referencia |
|---|---|---|---|---|
| Operaciones | Σops | vuelos representados | Contextual | Sin meta |
| Puntualidad OTP | 100 × Σontime / Σops | % | ↑ | 80%: referencia interna, no norma oficial |
| Demora ≥15 | 100 × Σdelayed15 / Σops | % | ↓ | Sin meta validada |
| Demora ≥60 | 100 × Σdelayed60 / Σops | % | ↓ | Subconjunto de demora ≥15 |
| Demora media condicionada | ΣsumDelayMin / Σdelayed15 | min / llegada demorada | ↓ | Según semántica declarada en HTML; confirmar con microdatos |
| Cancelación | 100 × Σcancel / Σops | % | ↓ | Sin meta validada |
| Desvíos | 100 × Σdivert / Σops | % | ↓ | Sin meta validada |
| Cobertura de causas | 100 × Σops con CauseValid / Σops | % | ↑ | 100% deseable como calidad de datos |
