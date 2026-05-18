# Metodología

Esta página documenta las decisiones metodológicas detrás de los datos que presenta **Cuentas Claras**. El objetivo es que cualquier persona pueda entender qué se está midiendo, qué se está dejando fuera y por qué.

---

## Fuente de datos

Los datos provienen de [Mercado Público](https://www.mercadopublico.cl), el portal oficial de compras públicas del Estado de Chile, operado por **Chile Compra**. Mercado Público registra todas las transacciones de organismos públicos bajo cuatro modalidades de compra.

El período cubierto es **2015–2025** (por semestre). Los datos se descargaron y consolidaron por municipalidad para las 32 comunas de la **Provincia de Santiago**.

---

## Modalidades de compra

| Modalidad | Descripción | Disponible desde |
|---|---|---|
| **Licitación** | Proceso competitivo formal, abierto a múltiples proveedores | 2015 |
| **Trato directo** | Contratación sin licitación, bajo causales específicas | 2015 |
| **Convenio marco** | Compra a proveedores preseleccionados por Chile Compra | 2015 |
| **Compra ágil** | Compras menores mediante cotización simplificada | 2020 |

La modalidad *compra ágil* no existía antes de 2020. Esta brecha es real y se refleja en los gráficos: la ausencia de datos antes de esa fecha no es un error, sino una característica del sistema.

---

## Municipalidades incluidas

Las 32 comunas de la Provincia de Santiago están incluidas en la plataforma:

Cerrillos · Cerro Navia · Conchalí · El Bosque · Estación Central · Huechuraba · Independencia · La Cisterna · La Florida · La Granja · La Pintana · La Reina · Las Condes · Lo Barnechea · Lo Espejo · Lo Prado · Macul · Maipú · Ñuñoa · Pedro Aguirre Cerda · Peñalolén · Providencia · Pudahuel · Quilicura · Quinta Normal · Recoleta · Renca · San Joaquín · San Miguel · San Ramón · Santiago · Vitacura

---

## Filtro de estado de órdenes

No todas las órdenes de compra representan dinero efectivamente gastado. Solo se incluyen órdenes en los siguientes estados:

| Estado | Significado |
|---|---|
| **Aceptada** | El proveedor aceptó la orden |
| **Recepción conforme** | Los bienes o servicios fueron recibidos y aprobados |

Se excluyen los estados *Enviada a proveedor*, *En proceso* y *Solicitud de cancelación*, que corresponden a compras no confirmadas o canceladas.

---

## Campo de monto

El monto utilizado en todos los cálculos es **`MontoNetoItemCLP`**: el valor neto de cada ítem de la orden, ya convertido a pesos chilenos (CLP).

Este campo es **aditivo**: sumar sus valores a través de filas produce el gasto total correcto. No se usa `MontoTotalOC` porque ese campo repite el total de la orden en cada fila de ítems, lo que generaría doble conteo al sumar.

Los montos son **antes de IVA** (monto neto). No incluyen el impuesto al valor agregado.

---

## Filtro específico para compra ágil

En la modalidad *compra ágil*, múltiples proveedores pueden cotizar para una misma orden. Solo uno es seleccionado. Las filas correspondientes a cotizaciones rechazadas (`ProveedorSeleccionado = NO`) se excluyen, ya que no representan gasto real.

---

## Corporaciones y organismos relacionados

Algunos registros de Mercado Público corresponden a corporaciones municipales (de educación, salud, cultura, etc.) que no son la municipalidad propiamente tal, pero están institucionalmente vinculadas a ella. En esta plataforma, el gasto de estos organismos se **atribuye a la municipalidad madre** para dar una imagen más completa del gasto público comunal.

---

## Limitaciones conocidas

- Los montos son **netos (sin IVA)**, por lo que no reflejan el gasto total con impuestos.
- No se ha aplicado **normalización per cápita**. Las comparaciones entre municipios con poblaciones muy distintas (como Las Condes y La Pintana) deben interpretarse con cuidado.
- Los datos de **alcaldes por período** están en desarrollo y no están disponibles aún en esta versión.
