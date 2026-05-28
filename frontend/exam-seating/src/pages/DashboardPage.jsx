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
    </PageContainer>
  )
}

export default DashboardPage
