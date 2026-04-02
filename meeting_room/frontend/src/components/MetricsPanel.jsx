export default function MetricsPanel({ metrics }) {
  const entries = Object.entries(metrics || {});

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="panel-eyebrow">Metrics</p>
          <h2>运行指标</h2>
        </div>
      </div>

      <div className="metrics-grid">
        {entries.length === 0 ? (
          <div className="booking-empty">当前还没有指标数据。</div>
        ) : (
          entries.map(([key, value]) => (
            <div key={key} className="metric-card">
              <p>{key}</p>
              <strong>{value}</strong>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
