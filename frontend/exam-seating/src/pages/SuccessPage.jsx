import { useState } from 'react'
import { Link } from 'react-router-dom'
import PageContainer from '../components/PageContainer'
import { downloadPdf } from '../services/api'

function SuccessPage() {
  const [isDownloading, setIsDownloading] = useState(false)
  const [error, setError] = useState('')

  const handleDownload = async () => {
    setIsDownloading(true)
    setError('')

    try {
      const blob = await downloadPdf()
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'exam_seating_arrangement.pdf'
      link.click()
      URL.revokeObjectURL(url)
    } catch (downloadError) {
      setError(downloadError.message)
    } finally {
      setIsDownloading(false)
    }
  }

  return (
    <PageContainer
      eyebrow="Complete"
      title="Seating Arrangement Generated"
      description="The hall-wise examination seating plan is ready for download."
    >
      <section className="card success-card">
        <div className="success-icon">OK</div>
        <h2>PDF report generated successfully</h2>
        <p>Download the approved seating arrangement or return to the dashboard for another session.</p>
        {error && <p className="error-message">{error}</p>}
        <div className="button-row">
          <button className="primary-button" type="button" onClick={handleDownload} disabled={isDownloading}>
            {isDownloading ? 'Downloading...' : 'Download PDF'}
          </button>
          <Link className="secondary-button" to="/dashboard">Back to Dashboard</Link>
        </div>
      </section>
    </PageContainer>
  )
}

export default SuccessPage
