---
title: Explorar
---

# Explorador de datos

Consulta el gasto municipal de forma interactiva. Los gráficos se actualizan en tiempo real según los filtros seleccionados.

```js
const db = await DuckDBClient.of({
  compra_agil:    FileAttachment("data/parquet/compra_agil.parquet"),
  convenio_marco: FileAttachment("data/parquet/convenio_marco.parquet"),
  licitacion:     FileAttachment("data/parquet/licitacion.parquet"),
  trato_directo:  FileAttachment("data/parquet/trato_directo.parquet"),
});

await db.query(`
  CREATE VIEW gasto AS
    SELECT * FROM compra_agil
    UNION ALL SELECT * FROM convenio_marco
    UNION ALL SELECT * FROM licitacion
    UNION ALL SELECT * FROM trato_directo
`);
```

```js
const ALL_MUNIS = (await db.query(
  "SELECT DISTINCT comuna_canonica FROM gasto ORDER BY 1"
)).toArray().map(d => d.comuna_canonica);

const SEMESTRES = (await db.query(
  "SELECT DISTINCT anio_semestre FROM gasto ORDER BY 1"
)).toArray().map(d => d.anio_semestre);

const TIPOS = ["compra_agil", "convenio_marco", "licitacion", "trato_directo"];

const TIPO_LABELS = {
  compra_agil:    "Compra ágil",
  convenio_marco: "Convenio marco",
  licitacion:     "Licitación",
  trato_directo:  "Trato directo",
};

function clpBillions(v) {
  return `$${(v / 1e9).toLocaleString("es-CL", {maximumFractionDigits: 1})} MM`;
}

function normalizeSize(s) {
  return ["Micro", "Pequeña", "Mediana", "Grande"].includes(s) ? s : "Sin clasificar";
}

// Custom pill multi-select — returns a DOM element usable with view()
function makePillSelect(options, {allByDefault = true} = {}) {
  const selected = new Set(allByDefault ? options : []);
  const dispatch = () => root.dispatchEvent(new Event("input", {bubbles: true}));

  const root = document.createElement("div");

  const actions = document.createElement("div");
  actions.className = "pill-actions";
  const allBtn = Object.assign(document.createElement("button"), {textContent: "Todas", className: "pill-action-btn"});
  const noneBtn = Object.assign(document.createElement("button"), {textContent: "Ninguna", className: "pill-action-btn"});
  allBtn.onclick  = () => { options.forEach(o => selected.add(o));    update(); dispatch(); };
  noneBtn.onclick = () => { selected.clear();                          update(); dispatch(); };
  actions.append(allBtn, noneBtn);

  const grid = document.createElement("div");
  grid.className = "pill-grid";

  const pills = new Map();
  for (const opt of options) {
    const btn = document.createElement("button");
    btn.textContent = opt;
    btn.className = "pill" + (selected.has(opt) ? " active" : "");
    btn.onclick = () => {
      selected.has(opt) ? selected.delete(opt) : selected.add(opt);
      btn.classList.toggle("active", selected.has(opt));
      dispatch();
    };
    pills.set(opt, btn);
    grid.append(btn);
  }

  function update() {
    for (const [opt, btn] of pills) btn.classList.toggle("active", selected.has(opt));
  }

  root.append(actions, grid);
  Object.defineProperty(root, "value", {get: () => [...selected]});
  return root;
}

// Custom toggle button group — for modalidad
function makeToggleGroup(options, labels, {allByDefault = true} = {}) {
  const selected = new Set(allByDefault ? options : []);
  const dispatch = () => root.dispatchEvent(new Event("input", {bubbles: true}));

  const root = document.createElement("div");
  root.className = "toggle-group";

  for (const opt of options) {
    const btn = document.createElement("button");
    btn.textContent = labels[opt] ?? opt;
    btn.className = "toggle-btn" + (selected.has(opt) ? " active" : "");
    btn.onclick = () => {
      selected.has(opt) ? selected.delete(opt) : selected.add(opt);
      btn.classList.toggle("active", selected.has(opt));
      dispatch();
    };
    root.append(btn);
  }

  Object.defineProperty(root, "value", {get: () => [...selected]});
  return root;
}

// Linked period range — two selects that prevent start > end
function makePeriodRange(semestres) {
  const root = document.createElement("div");
  root.className = "period-range";
  const dispatch = () => root.dispatchEvent(new Event("input", {bubbles: true}));

  function makeSelect(value) {
    const sel = document.createElement("select");
    sel.className = "period-select";
    for (const s of semestres) sel.add(new Option(s, s));
    sel.value = value;
    return sel;
  }

  const startSel = makeSelect(semestres.at(0));
  const endSel   = makeSelect(semestres.at(-1));
  const sep = Object.assign(document.createElement("span"), {textContent: "→", className: "period-sep"});

  startSel.onchange = () => {
    if (startSel.value > endSel.value) endSel.value = startSel.value;
    dispatch();
  };
  endSel.onchange = () => {
    if (endSel.value < startSel.value) startSel.value = endSel.value;
    dispatch();
  };

  root.append(startSel, sep, endSel);
  Object.defineProperty(root, "value", {get: () => [startSel.value, endSel.value]});
  return root;
}

function buildWhere(munis, tipos, semStart, semEnd) {
  if (munis.length === 0) return "WHERE 1=0";
  const conds = [];
  if (munis.length < ALL_MUNIS.length) {
    const list = munis.map(m => `'${m.replace(/'/g, "''")}'`).join(",");
    conds.push(`comuna_canonica IN (${list})`);
  }
  if (tipos.length > 0 && tipos.length < TIPOS.length) {
    conds.push(`tipo_compra IN (${tipos.map(t => `'${t}'`).join(",")})`);
  }
  conds.push(`anio_semestre >= '${semStart}'`);
  conds.push(`anio_semestre <= '${semEnd}'`);
  return conds.length ? `WHERE ${conds.join(" AND ")}` : "";
}
```

---

## Filtros

<div class="filter-panel">

<div class="filter-block">
<div class="filter-label">Municipalidad</div>

```js
const munis = view(makePillSelect(ALL_MUNIS));
```

</div>

<div class="filter-row">
<div class="filter-block">
<div class="filter-label">Modalidad</div>

```js
const tipos = view(makeToggleGroup(TIPOS, TIPO_LABELS));
```

</div>
<div class="filter-block">
<div class="filter-label">Período</div>

```js
const period = view(makePeriodRange(SEMESTRES));
```

```js
const semStart = period[0];
const semEnd   = period[1];
```

</div>
</div>

</div>

```js
const muniLabel = munis.length === 0
  ? "ninguna comuna"
  : munis.length === ALL_MUNIS.length ? "todas las comunas"
  : munis.length === 1 ? munis[0]
  : `${munis.length} comunas`;

const tipoLabel = tipos.length === 0
  ? "ninguna modalidad"
  : tipos.length === TIPOS.length ? "todas las modalidades"
  : tipos.map(t => TIPO_LABELS[t]).join(", ");
```

<p class="filter-summary">Mostrando <strong>${muniLabel}</strong> · <strong>${tipoLabel}</strong> · <strong>${semStart}</strong> → <strong>${semEnd}</strong></p>

---

## Resumen

```js
const summary = (await db.query(`
  SELECT
    SUM(MontoNetoItemCLP)        AS total,
    COUNT(DISTINCT codigoOC)     AS ordenes,
    COUNT(DISTINCT ProveedorRUT) AS proveedores
  FROM gasto
  ${buildWhere(munis, tipos, semStart, semEnd)}
`)).toArray()[0];
```

<div class="stat-grid">
  <div class="stat-card">
    <div class="stat-label">Gasto total (neto sin IVA)</div>
    <div class="stat-value">${clpBillions(summary.total)}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Órdenes de compra</div>
    <div class="stat-value">${summary.ordenes.toLocaleString("es-CL")}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Proveedores distintos</div>
    <div class="stat-value">${summary.proveedores.toLocaleString("es-CL")}</div>
  </div>
</div>

---

## Gasto en el tiempo

```js
const timeSeries = (await db.query(`
  SELECT
    anio_semestre,
    tipo_compra,
    SUM(MontoNetoItemCLP) AS monto
  FROM gasto
  ${buildWhere(munis, tipos, semStart, semEnd)}
  GROUP BY anio_semestre, tipo_compra
  ORDER BY anio_semestre, tipo_compra
`)).toArray().map(d => ({
  ...d,
  label: TIPO_LABELS[d.tipo_compra] ?? d.tipo_compra,
  fecha: (() => { const [y, s] = d.anio_semestre.split("-"); return new Date(+y, s === "1" ? 0 : 6, 1); })(),
}));
```

```js
Plot.plot({
  width,
  height: 320,
  marginLeft: 70,
  x: { type: "time", label: null },
  y: {
    label: "Miles de millones CLP",
    tickFormat: d => `$${(d / 1e9).toFixed(0)}MM`,
    grid: true,
  },
  color: {
    domain: Object.values(TIPO_LABELS),
    scheme: "tableau10",
    legend: true,
  },
  marks: [
    Plot.lineY(timeSeries, {
      x: "fecha", y: "monto", stroke: "label", strokeWidth: 2,
      tip: {
        format: {
          x: d => d.toLocaleDateString("es-CL", {year: "numeric", month: "long"}),
          y: clpBillions,
          stroke: true,
        },
      },
    }),
    Plot.dot(timeSeries, {x: "fecha", y: "monto", fill: "label", r: 2}),
    Plot.ruleY([0]),
  ],
})
```

---

## Categorías

```js
const categories = (await db.query(`
  SELECT RubroN1, SUM(MontoNetoItemCLP) AS monto
  FROM gasto
  ${buildWhere(munis, tipos, semStart, semEnd)}
  GROUP BY RubroN1
  ORDER BY monto DESC
  LIMIT 15
`)).toArray();
```

```js
Plot.plot({
  width,
  height: 480,
  marginLeft: 300,
  marginRight: 80,
  x: {
    label: "Miles de millones CLP →",
    tickFormat: d => `$${(d / 1e9).toFixed(0)}MM`,
    grid: true,
  },
  y: { label: null },
  marks: [
    Plot.barX(categories, {
      x: "monto", y: "RubroN1", fill: "steelblue",
      sort: { y: "-x" },
      tip: { format: { x: clpBillions, y: true } },
    }),
    Plot.ruleX([0]),
  ],
})
```

---

## Tamaño de proveedor

```js
const SIZE_ORDER = ["Micro", "Pequeña", "Mediana", "Grande", "Sin clasificar"];

const vendorSize = Array.from(
  d3.rollup(
    (await db.query(`
      SELECT TamanoProveedor, SUM(MontoNetoItemCLP) AS monto
      FROM gasto
      ${buildWhere(munis, tipos, semStart, semEnd)}
      GROUP BY TamanoProveedor
    `)).toArray(),
    v => d3.sum(v, d => d.monto),
    d => normalizeSize(d.TamanoProveedor)
  ),
  ([size, monto]) => ({ size, monto })
).sort((a, b) => SIZE_ORDER.indexOf(a.size) - SIZE_ORDER.indexOf(b.size));

const totalVendor = d3.sum(vendorSize, d => d.monto);
```

```js
Plot.plot({
  width,
  height: 240,
  marginLeft: 110,
  marginRight: 100,
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
    Plot.barX(vendorSize, {
      x: "monto", y: "size", fill: "size",
      tip: {
        format: {
          x: d => `${clpBillions(d)} (${d3.format(".1%")(d / totalVendor)})`,
          y: true, fill: false,
        },
      },
    }),
    Plot.ruleX([0]),
  ],
})
```

<style>
/* ── Filter panel ─────────────────────────────── */
.filter-panel {
  background: var(--theme-background-alt);
  border: 1px solid var(--theme-foreground-faintest);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.filter-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  align-items: start;
}
.filter-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.filter-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--theme-foreground-muted);
}

/* ── Municipality pills ───────────────────────── */
.pill-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}
.pill-action-btn {
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid var(--theme-foreground-faint);
  background: transparent;
  color: var(--theme-foreground-muted);
  cursor: pointer;
  font-family: inherit;
  transition: color 0.1s, border-color 0.1s;
}
.pill-action-btn:hover {
  color: var(--theme-foreground);
  border-color: var(--theme-foreground-muted);
}
.pill-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
.pill {
  padding: 3px 10px;
  border-radius: 100px;
  border: 1px solid var(--theme-foreground-faint);
  background: transparent;
  color: var(--theme-foreground-muted);
  font-size: 0.78rem;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.1s;
  white-space: nowrap;
}
.pill:hover { border-color: var(--theme-foreground-muted); color: var(--theme-foreground); }
.pill.active {
  background: var(--theme-foreground);
  border-color: var(--theme-foreground);
  color: var(--theme-background);
}

/* ── Modality toggles ─────────────────────────── */
.toggle-group { display: flex; flex-wrap: wrap; gap: 6px; }
.toggle-btn {
  padding: 5px 14px;
  border-radius: 6px;
  border: 1px solid var(--theme-foreground-faint);
  background: transparent;
  color: var(--theme-foreground-muted);
  font-size: 0.82rem;
  cursor: pointer;
  font-family: inherit;
  font-weight: 500;
  transition: all 0.1s;
}
.toggle-btn:hover { border-color: var(--theme-foreground-muted); color: var(--theme-foreground); }
.toggle-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}

/* ── Period range ─────────────────────────────── */
.period-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.period-select {
  flex: 1;
  padding: 5px 8px;
  border-radius: 6px;
  border: 1px solid var(--theme-foreground-faint);
  background: var(--theme-background);
  color: var(--theme-foreground);
  font-size: 0.82rem;
  font-family: inherit;
  cursor: pointer;
  appearance: auto;
}
.period-select:focus { outline: 2px solid #3b82f6; outline-offset: 1px; }
.period-sep { color: var(--theme-foreground-muted); font-size: 0.85rem; flex-shrink: 0; }

/* ── Filter summary ───────────────────────────── */
.filter-summary {
  font-size: 0.82rem;
  color: var(--theme-foreground-muted);
  margin: 0.25rem 0 0;
}

/* ── Stat cards ───────────────────────────────── */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin: 1.5rem 0;
}
.stat-card {
  background: var(--theme-background-alt);
  border: 1px solid var(--theme-foreground-faintest);
  border-radius: 8px;
  padding: 1.25rem 1.5rem;
}
.stat-label {
  font-size: 0.75rem;
  color: var(--theme-foreground-muted);
  margin-bottom: 0.4rem;
}
.stat-value { font-size: 1.6rem; font-weight: 600; }
</style>
