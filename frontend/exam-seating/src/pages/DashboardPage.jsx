import { Link } from 'react-router-dom'
import PageContainer from '../components/PageContainer'

function DashboardPage() {
  return (
    <PageContainer
      eyebrow="Control Center"
      title="Seating Arrangement Dashboard"
      description="Start the seating arrangement workflow and move through each step in order."
    >
      <section className="card dashboard-start">
        <h2>New Examination Seating Plan</h2>
        <p>Upload students, add exam details, configure halls, choose constraints, and generate the final PDF.</p>
        <Link className="primary-button arrow-button" to="/upload">
          Start Process
          <span aria-hidden="true">&rarr;</span>
        </Link>
      </section>

      <section className="dashboard-info-grid">
        <div className="card architecture-card">
          <h2>AI Architecture</h2>
          <div className="architecture-flow">
            {['Student Data', 'Rule Engine', 'Constraint Engine', 'CSP Solver', 'Utility Evaluator', 'PDF Generator'].map((step, index, steps) => (
              <div key={step}>
                <span>{step}</span>
                {index < steps.length - 1 && <b aria-hidden="true">&darr;</b>}
              </div>
            ))}
          </div>
        </div>

        <div className="card search-card">
          <h2>AI Search Techniques Used</h2>
          <ul>
            <li><strong>Backtracking Search</strong><span>Explores valid student-to-seat assignments.</span></li>
            <li><strong>Constraint Propagation</strong><span>Applies seating rules throughout the search.</span></li>
            <li><strong>Forward Checking</strong><span>Removes invalid future seat choices early.</span></li>
            <li><strong>MRV Heuristic</strong><span>Selects the most constrained student first.</span></li>
            <li><strong>Domain Pruning</strong><span>Reduces the remaining search space.</span></li>
          </ul>
        </div>
      </section>
    </PageContainer>
  )
}

export default DashboardPage
