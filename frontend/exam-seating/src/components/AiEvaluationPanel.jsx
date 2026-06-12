const metricLabels = {
  assignments: 'Assignments Attempted',
  backtracks: 'Backtracks',
  pruned: 'Pruned Domains',
  recursiveCalls: 'Recursive Calls',
}

function AiEvaluationPanel({ arrangement }) {
  const metrics = arrangement.metrics || {}
  const quality = arrangement.quality || {}
  const breakdown = arrangement.utilityBreakdown || {}

  return (
    <div className="evaluation-layout">
      <section className="card evaluation-card confidence-card" title="Higher score indicates a higher-quality arrangement according to current evaluation metrics.">
        <p className="eyebrow">AI Confidence Score</p>
        <strong className="score-value">{arrangement.confidence ?? 0}%</strong>
        <p>Estimated arrangement quality under the selected rules.</p>
      </section>

      <section className="card evaluation-card">
        <p className="eyebrow">Utility Score</p>
        <strong className="score-value">{arrangement.utilityScore ?? 0} / 100</strong>
        <div className="compact-list">
          <span>Hall Balance <b>{breakdown.hallBalance ?? 0} / 40</b></span>
          <span>Subject Separation <b>{breakdown.subjectSeparation ?? 0} / 30</b></span>
          <span>Seat Utilization <b>{breakdown.seatUtilization ?? 0} / 20</b></span>
          <span>Unused Seat Efficiency <b>{breakdown.unusedSeatEfficiency ?? 0} / 10</b></span>
        </div>
      </section>

      <section className="card evaluation-card wide-card">
        <h2>Seating Quality Report</h2>
        <div className="quality-grid">
          <span>Hall Balance <b>{quality.hallBalance ?? 0}%</b></span>
          <span>Seat Utilization <b>{quality.utilization ?? 0}%</b></span>
          <span>Subject Separation <b>{quality.separation ?? 0}%</b></span>
          <span>Blocked Seat Compliance <b>{quality.compliance ?? 0}%</b></span>
        </div>
      </section>

      <section className="card evaluation-card">
        <h2>Performance Metrics</h2>
        <div className="compact-list">
          {Object.entries(metricLabels).map(([key, label]) => (
            <span key={key}>{label} <b>{metrics[key] ?? 0}</b></span>
          ))}
          <span>Solve Time <b>{metrics.solveTime ?? 0} sec</b></span>
        </div>
      </section>

      <section className="card evaluation-card trace-card">
        <h2>AI Reasoning Trace</h2>
        <ol className="reasoning-trace">
          {(arrangement.trace || []).map((step, index) => <li key={`${step}-${index}`}>{step}</li>)}
        </ol>
      </section>
    </div>
  )
}

export default AiEvaluationPanel
