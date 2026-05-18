---
title: Cuentas Claras
---

# ¿En qué gasta tu municipio?

Las municipalidades de la Provincia de Santiago compran miles de productos y servicios cada año: desde medicamentos y materiales de construcción hasta servicios digitales y mobiliario. Toda esa actividad queda registrada en **Mercado Público**, el portal oficial de compras del Estado.

Esta plataforma toma esos datos y los convierte en algo legible: quién gasta cuánto, en qué, y cómo ha cambiado a lo largo del tiempo.

```js
const spending = await FileAttachment("data/spending_by_period.csv").csv({typed: true});
```

```js
// Helpers
function semestreToDate(s) {
  const [year, sem] = s.split("-");
  return new Date(+year, sem === "1" ? 0 : 6, 1);
}

const TIPO_LABELS = {
  compra_agil:    "Compra ágil",
  convenio_marco: "Convenio marco",
  licitacion:     "Licitación",
  trato_directo:  "Trato directo",
};

const TIPO_ORDER = ["licitacion", "trato_directo", "convenio_marco", "compra_agil"];

function clpBillions(v) {
  return `$${(v / 1e9).toLocaleString("es-CL", {maximumFractionDigits: 0})} MM`;
}
```

---

## La escala del gasto

Entre 2015 y 2025, las 32 comunas de la Provincia de Santiago ejecutaron compras públicas por un total de **$4.743 miles de millones** (pesos netos, sin IVA). El gasto ha crecido de forma sostenida, con un salto notable a partir de 2020.

```js
// Aggregate across all municipalities by semestre × tipo_compra
const byModality = d3.flatRollup(
  spending,
  v => d3.sum(v, d => d.monto_neto_clp),
  d => d.anio_semestre,
  d => d.tipo_compra
).map(([semestre, tipo, monto]) => ({
  semestre,
  tipo,
  label: TIPO_LABELS[tipo] ?? tipo,
  monto,
  fecha: semestreToDate(semestre),
}));
```

```js
Plot.plot({
  title: "Gasto total por semestre y modalidad de compra",
  subtitle: "32 comunas · Provincia de Santiago · pesos netos sin IVA",
  width,
  height: 380,
  marginLeft: 70,
  x: { type: "time", label: null },
  y: {
    label: "Miles de millones CLP",
    tickFormat: d => `$${(d / 1e9).toFixed(0)}MM`,
    grid: true,
  },
  color: {
    domain: TIPO_ORDER.map(t => TIPO_LABELS[t]),
    scheme: "tableau10",
    legend: true,
  },
  marks: [
    Plot.areaY(
      byModality,
      Plot.stackY({
        x: "fecha",
        y: "monto",
        fill: "label",
        order: TIPO_ORDER.map(t => TIPO_LABELS[t]),
        tip: {
          format: {
            x: d => d.toLocaleDateString("es-CL", { year: "numeric", month: "long" }),
            y: clpBillions,
          },
        },
      })
    ),
    Plot.ruleX(
      [new Date(2020, 0, 1)],
      { stroke: "var(--theme-foreground-muted)", strokeDasharray: "4 3" }
    ),
    Plot.text(
      [{ fecha: new Date(2020, 0, 1), label: "Inicio compra ágil →" }],
      {
        x: "fecha",
        y: 4e11,
        text: "label",
        textAnchor: "end",
        dx: -6,
        fill: "var(--theme-foreground-muted)",
        fontSize: 11,
      }
    ),
    Plot.ruleY([0]),
  ],
})
```

---

## ¿Cómo compran las municipalidades?

Las compras públicas se realizan a través de cuatro modalidades, cada una con reglas distintas sobre competencia, montos y plazos. La **licitación** es el proceso más formal; el **trato directo** permite contratar sin concurso bajo causales específicas; el **convenio marco** usa proveedores preseleccionados por Chile Compra; y la **compra ágil** es una cotización simplificada para montos menores, disponible desde 2020.

```js
// Relative share per semestre
const totalBySemestre = d3.rollup(
  byModality,
  v => d3.sum(v, d => d.monto),
  d => d.semestre
);

const byModalityShare = byModality.map(d => ({
  ...d,
  share: d.monto / totalBySemestre.get(d.semestre),
}));
```

```js
Plot.plot({
  title: "Composición del gasto por modalidad (% del total semestral)",
  width,
  height: 320,
  marginLeft: 70,
  x: { type: "time", label: null },
  y: {
    label: "Proporción",
    tickFormat: d3.format(".0%"),
    domain: [0, 1],
    grid: true,
  },
  color: {
    domain: TIPO_ORDER.map(t => TIPO_LABELS[t]),
    scheme: "tableau10",
    legend: false,
  },
  marks: [
    Plot.areaY(
      byModalityShare,
      Plot.stackY({
        x: "fecha",
        y: "share",
        fill: "label",
        order: TIPO_ORDER.map(t => TIPO_LABELS[t]),
        tip: {
          format: {
            x: d => d.toLocaleDateString("es-CL", { year: "numeric", month: "long" }),
            y: d3.format(".1%"),
          },
        },
      })
    ),
    Plot.ruleX(
      [new Date(2020, 0, 1)],
      { stroke: "var(--theme-foreground-muted)", strokeDasharray: "4 3" }
    ),
    Plot.ruleY([0]),
  ],
})
```

La aparición de la compra ágil en 2020 no solo añadió una nueva modalidad: redistribuyó el gasto. A partir de ese año, una fracción creciente del total provincial se canaliza por esta vía, desplazando parcialmente al convenio marco y al trato directo.

---

## ¿Qué compran?

Las municipalidades compran de todo. Las categorías más relevantes no son las más obvias: los **servicios de construcción y mantenimiento** lideran ampliamente, seguidos de **servicios de limpieza industrial** y lo que el sistema clasifica como **servicios agrícolas, pesqueros y forestales** —que en contexto urbano corresponde principalmente a mantención de áreas verdes, plazas y arbolado público.

```js
const category = await FileAttachment("data/spending_by_category.csv").csv({typed: true});
```

```js
// Top 12 categories by total spend across all municipalities and semesters
const byCategory = d3.flatRollup(
  category,
  v => d3.sum(v, d => d.monto_neto_clp),
  d => d.RubroN1
)
  .map(([rubro, monto]) => ({ rubro, monto }))
  .sort((a, b) => b.monto - a.monto)
  .slice(0, 12);
```

```js
Plot.plot({
  title: "Top 12 categorías por gasto total acumulado (2015–2025)",
  subtitle: "32 comunas · pesos netos sin IVA",
  width,
  height: 420,
  marginLeft: 320,
  marginRight: 80,
  x: {
    label: "Miles de millones CLP →",
    tickFormat: d => `$${(d / 1e9).toFixed(0)}MM`,
    grid: true,
  },
  y: {
    label: null,
    domain: byCategory.map(d => d.rubro),
  },
  marks: [
    Plot.barX(byCategory, {
      x: "monto",
      y: "rubro",
      fill: "steelblue",
      sort: { y: "-x" },
      tip: {
        format: { x: clpBillions, y: true },
      },
    }),
    Plot.ruleX([0]),
  ],
})
```

---

## ¿A quién le compran?

El sistema de Mercado Público clasifica a los proveedores por tamaño. Más del **40% del gasto provincial** va a empresas **grandes**, aunque las empresas micro, pequeñas y medianas en conjunto representan casi la mitad del total.

```js
const vendorSize = await FileAttachment("data/spending_by_vendor_size.csv").csv({typed: true});
```

```js
const SIZE_ORDER = ["Micro", "Pequeña", "Mediana", "Grande", "Sin clasificar"];

function normalizeSize(s) {
  return ["Micro", "Pequeña", "Mediana", "Grande"].includes(s) ? s : "Sin clasificar";
}

const bySize = d3.flatRollup(
  vendorSize,
  v => d3.sum(v, d => d.monto_neto_clp),
  d => normalizeSize(d.TamanoProveedor)
)
  .map(([size, monto]) => ({ size, monto }))
  .sort((a, b) => SIZE_ORDER.indexOf(a.size) - SIZE_ORDER.indexOf(b.size));

const totalSpend = d3.sum(bySize, d => d.monto);
```

```js
Plot.plot({
  title: "Distribución del gasto por tamaño de proveedor (2015–2025)",
  width,
  height: 280,
  marginLeft: 100,
  marginRight: 80,
  x: {
    label: "Miles de millones CLP →",
    tickFormat: d => `$${(d / 1e9).toFixed(0)}MM`,
    grid: true,
  },
  y: { label: null, domain: SIZE_ORDER },
  color: {
    domain: SIZE_ORDER,
    range: ["#4e9af1", "#5bc0be", "#f4a261", "#e76f51", "#aaa"],
  },
  marks: [
    Plot.barX(bySize, {
      x: "monto",
      y: "size",
      fill: "size",
      tip: {
        format: {
          x: d => `${clpBillions(d)} (${d3.format(".1%")(d / totalSpend)})`,
          y: true,
          fill: false,
        },
      },
    }),
    Plot.ruleX([0]),
  ],
})
```

---

## Las comunas en perspectiva

No todas las municipalidades gastan lo mismo, ni deberían: el presupuesto depende de la población, los ingresos propios y las transferencias del Estado. Este gráfico muestra el gasto total acumulado de cada comuna entre 2015 y 2025, **sin normalizar por población**.

```js
const byMuni = d3.flatRollup(
  spending,
  v => d3.sum(v, d => d.monto_neto_clp),
  d => d.municipalidad
)
  .map(([municipalidad, monto]) => ({ municipalidad, monto }))
  .sort((a, b) => b.monto - a.monto);
```

```js
Plot.plot({
  title: "Gasto total acumulado por municipalidad (2015–2025)",
  subtitle: "Sin normalización per cápita · pesos netos sin IVA",
  width,
  height: 680,
  marginLeft: 150,
  marginRight: 80,
  x: {
    label: "Miles de millones CLP →",
    tickFormat: d => `$${(d / 1e9).toFixed(0)}MM`,
    grid: true,
  },
  y: {
    label: null,
    domain: byMuni.map(d => d.municipalidad),
  },
  marks: [
    Plot.barX(byMuni, {
      x: "monto",
      y: "municipalidad",
      fill: "steelblue",
      sort: { y: "-x" },
      tip: {
        format: { x: clpBillions, y: true },
      },
    }),
    Plot.ruleX([0]),
  ],
})
```

_Los datos de alcaldes por período están en desarrollo. Próximamente esta sección mostrará quién gobernaba cada municipio durante cada tramo del gasto._
