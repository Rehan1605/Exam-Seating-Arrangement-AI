function ArrangementComparison({ arrangements, selectedId, onSelect, isSelecting }) {
  if (!arrangements?.length) {
    return null
  }

  return (
    <section className="card">
      <div className="section-title">
        <div>
          <h2>Compare Arrangements</h2>
          <p>Select the policy outcome to preview and approve.</p>
        </div>
      </div>
      <div className="arrangement-options">
        {arrangements.map((item) => {
          const selected = item.id === selectedId
          return (
            <button
              className={`arrangement-option ${selected ? 'selected' : ''}`}
              type="button"
              key={item.id}
              onClick={() => onSelect(item.id)}
              disabled={isSelecting}
            >
              <span>{item.label}</span>
              <strong>{item.utilityScore} utility</strong>
              <small>{item.confidence}% confidence</small>
            </button>
          )
        })}
      </div>
    </section>
  )
}

export default ArrangementComparison
