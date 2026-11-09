import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

// Series colours are theme tokens (see styles.css), so the chart always matches the app.
const SERIES = ["var(--series-1)", "var(--series-2)", "var(--series-3)"];
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Dates read as MM/YY when every point is a month start, otherwise DD/MM; other labels stay as they are.
function tickFormatter(rows, x) {
  const dates = rows.map((row) => row[x]);
  if (!dates.every((value) => ISO_DATE.test(value))) return (value) => String(value);
  const monthly = dates.every((value) => value.endsWith("-01"));
  return (value) => {
    const [year, month, day] = String(value).split("-");
    return monthly ? `${month}/${year.slice(2)}` : `${day}/${month}`;
  };
}

const number = (value) => (typeof value === "number" ? value.toLocaleString("vi-VN", { maximumFractionDigits: 2 }) : "–");

function ChartTooltip({ active, payload, label, y_label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tip">
      <div className="chart-tip-label">{label}</div>
      {payload.map((item) => (
        <div key={item.dataKey} className="chart-tip-row">
          <i style={{ background: item.color }} />
          <span>{payload.length > 1 ? item.name : (y_label || item.name)}</span>
          <strong>{number(item.value)}</strong>
        </div>
      ))}
    </div>
  );
}

function DataTable({ spec }) {
  return (
    <details className="details">
      <summary>Bảng số liệu ({spec.rows.length} dòng)</summary>
      <div className="table-scroll" tabIndex={0} role="region" aria-label={`Số liệu của biểu đồ ${spec.title}`}>
        <table>
          <thead><tr>{[spec.x, ...spec.y].map((name) => <th key={name} scope="col">{name}</th>)}</tr></thead>
          <tbody>{spec.rows.map((row, index) => (
            <tr key={index}>{[spec.x, ...spec.y].map((name) => <td key={name}>{name === spec.x ? String(row[name]) : number(row[name])}</td>)}</tr>
          ))}</tbody>
        </table>
      </div>
    </details>
  );
}

export default function Chart({ spec }) {
  const animate = !reducedMotion();
  const multi = spec.y.length > 1;
  const Plot = spec.kind === "line" ? LineChart : BarChart;
  const format = tickFormatter(spec.rows, spec.x);
  const axis = { tick: { fill: "var(--ink-muted)", fontSize: 12 }, tickLine: false, axisLine: { stroke: "var(--line-strong)" } };
  return (
    <figure className="chart">
      <figcaption>{spec.title}{spec.y_label && <span className="muted"> · {spec.y_label}</span>}</figcaption>
      <div className="chart-plot" role="img" aria-label={`Biểu đồ ${spec.kind === "line" ? "đường" : "cột"}: ${spec.title}. Xem bảng số liệu bên dưới.`}>
        <ResponsiveContainer width="100%" height={260}>
          <Plot data={spec.rows} margin={{ top: 8, right: 20, bottom: spec.x_label ? 18 : 4, left: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--line)" />
            <XAxis dataKey={spec.x} {...axis} tickFormatter={format} interval="preserveStartEnd" minTickGap={28} tickMargin={8}
              label={spec.x_label ? { value: spec.x_label, position: "insideBottom", offset: -14, fill: "var(--ink-muted)", fontSize: 12 } : undefined} />
            <YAxis {...axis} axisLine={false} width={44} tickFormatter={number} domain={spec.kind === "line" ? ["auto", "auto"] : [0, "auto"]} />
            <Tooltip content={<ChartTooltip y_label={spec.y_label} />} cursor={{ fill: "var(--line)", stroke: "var(--line-strong)" }} isAnimationActive={false} />
            {multi && <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12, color: "var(--ink-soft)" }} />}
            {spec.y.map((name, index) => spec.kind === "line"
              ? <Line key={name} dataKey={name} stroke={SERIES[index]} strokeWidth={2} dot={spec.rows.length <= 40 ? { r: 3, fill: SERIES[index], stroke: "var(--panel-solid)", strokeWidth: 2 } : false}
                  activeDot={{ r: 5 }} connectNulls={false} isAnimationActive={animate} />
              : <Bar key={name} dataKey={name} fill={SERIES[index]} radius={[4, 4, 0, 0]} maxBarSize={36} isAnimationActive={animate} />)}
          </Plot>
        </ResponsiveContainer>
      </div>
      <DataTable spec={spec} />
    </figure>
  );
}
