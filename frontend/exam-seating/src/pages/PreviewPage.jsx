import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AiEvaluationPanel from '../components/AiEvaluationPanel'
import ArrangementComparison from '../components/ArrangementComparison'
import PageContainer from '../components/PageContainer'
import SeatingGrid from '../components/SeatingGrid'
import { generatePdf, regenerateSeating, selectArrangement } from '../services/api'

function PreviewPage() {
  const navigate = useNavigate()
  const [arrangement, setArrangement] = useState(() => {
    const savedArrangement = sessionStorage.getItem('latestSeatingArrangement')
    return savedArrangement ? JSON.parse(savedArrangement) : null
  })
  const [generationFailure, setGenerationFailure] = useState(() => sessionStorage.getItem('latestGenerationError') || '')
  const [currentHall, setCurrentHall] = useState(0)
  const [isRegenerating, setIsRegenerating] = useState(false)
  const [isSelecting, setIsSelecting] = useState(false)
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false)
  const [error, setError] = useState('')

  const alternatives = useMemo(() => arrangement?.arrangements || [], [arrangement])
  const selectedId = arrangement?.selectedArrangementId || arrangement?.id
  const activeArrangement = useMemo(
    () => alternatives.find((item) => item.id === selectedId) || arrangement,
    [alternatives, arrangement, selectedId],
  )
  const halls = useMemo(() => activeArrangement?.halls || [], [activeArrangement])
  const hall = halls[currentHall]

  const handleRegenerate = async () => {
    setIsRegenerating(true)
    setError('')

    try {
      const savedConstraints = sessionStorage.getItem('latestConstraints')
      const constraints = savedConstraints ? JSON.parse(savedConstraints) : {}
      const data = await regenerateSeating({ constraints })
      sessionStorage.setItem('latestSeatingArrangement', JSON.stringify(data.arrangement))
      setArrangement(data.arrangement)
      setCurrentHall(0)
      if (data.arrangement?.success === false) {
        sessionStorage.setItem('latestGenerationError', data.arrangement.message)
        setGenerationFailure(data.arrangement.message)
      } else {
        sessionStorage.removeItem('latestGenerationError')
        setGenerationFailure('')
      }
    } catch (regenerateError) {
      setError(regenerateError.message)
    } finally {
      setIsRegenerating(false)
    }
  }

  const handleSelectArrangement = async (arrangementId) => {
    if (arrangementId === selectedId) {
      return
    }
    setIsSelecting(true)
    setError('')
    try {
      await selectArrangement(arrangementId)
      const nextArrangement = {
        ...arrangement,
        selectedArrangementId: arrangementId,
      }
      setArrangement(nextArrangement)
      sessionStorage.setItem('latestSeatingArrangement', JSON.stringify(nextArrangement))
      setCurrentHall(0)
    } catch (selectionError) {
      setError(selectionError.message)
    } finally {
      setIsSelecting(false)
    }
  }

  const handleApprovePdf = async () => {
    setIsGeneratingPdf(true)
    setError('')

    try {
      const savedMetadata = sessionStorage.getItem('examMetadata')
      const metadata = savedMetadata ? JSON.parse(savedMetadata) : {}
      await generatePdf({ metadata })
      navigate('/success')
    } catch (pdfError) {
      setError(pdfError.message)
    } finally {
      setIsGeneratingPdf(false)
    }
  }

  if (!arrangement || !halls.length) {
    return (
      <PageContainer
        eyebrow="Step 5"
        title="Hall-Wise Seating Preview"
        description="Generate a seating arrangement before opening the preview."
      >
        <section className="card empty-state">
          <h2>No seating arrangement found</h2>
          <p>Upload students, save hall configuration, and generate seating from the Constraints page.</p>
          <Link className="primary-button" to="/constraints">Go to Constraints</Link>
        </section>
      </PageContainer>
    )
  }

  if (arrangement.success === false) {
    return (
      <PageContainer
        eyebrow="Step 5"
        title="Hall-Wise Seating Preview"
        description="The CSP solver could not produce a valid arrangement for the current inputs."
      >
        <section className="card empty-state">
          <h2>Generation failed</h2>
          <p className="error-message">{arrangement.failureReason || generationFailure || arrangement.message}</p>
          {arrangement.failureDetails && <p>{arrangement.failureDetails}</p>}
          {arrangement.diagnostics && (
            <div className="failure-diagnostics">
              <span>Students <b>{arrangement.diagnostics.students}</b></span>
              <span>Available Seats <b>{arrangement.diagnostics.availableSeats}</b></span>
              <span>Shortfall <b>{arrangement.diagnostics.shortfall}</b></span>
            </div>
          )}
          <div className="button-row">
            <button className="primary-button" type="button" onClick={handleRegenerate} disabled={isRegenerating}>
              {isRegenerating && <span className="spinner" aria-hidden="true"></span>}
              {isRegenerating ? 'Solving CSP...' : 'Try Regenerate'}
            </button>
            <Link className="secondary-button" to="/constraints">Adjust Constraints</Link>
          </div>
        </section>
      </PageContainer>
    )
  }

  const warnings = activeArrangement.warnings || []
  const showRelaxedWarning = activeArrangement.constraintsRelaxed || warnings.length > 0

  return (
    <PageContainer
      eyebrow="Step 5"
      title="Hall-Wise Seating Preview"
      description="Inspect the generated seating grid and approve it for PDF generation."
      actions={<span className="pill">{currentHall + 1} of {halls.length}</span>}
    >
      <ArrangementComparison
        arrangements={alternatives}
        selectedId={selectedId}
        onSelect={handleSelectArrangement}
        isSelecting={isSelecting}
      />
      <section className="card preview-card">
        <div className="section-title">
          <div>
            <h2>{hall.hallName}</h2>
            <p>{hall.rows} rows x {hall.cols} columns</p>
          </div>
          <button className="secondary-button" type="button" onClick={handleRegenerate} disabled={isRegenerating}>
            {isRegenerating && <span className="spinner spinner-blue" aria-hidden="true"></span>}
            {isRegenerating ? 'Solving CSP...' : 'Regenerate Seating'}
          </button>
        </div>

        {showRelaxedWarning && (
          <div className="warning-banner">
            <strong>Constraint warning</strong>
            <span>{warnings.join(' ') || 'Some seating constraints were relaxed during generation.'}</span>
          </div>
        )}
        {error && <p className="error-message">{error}</p>}
        <SeatingGrid hall={hall} />

        <div className="preview-controls">
          <button
            className="secondary-button"
            type="button"
            disabled={currentHall === 0}
            onClick={() => setCurrentHall(currentHall - 1)}
          >
            Previous Hall
          </button>
          <button
            className="secondary-button"
            type="button"
            disabled={currentHall === halls.length - 1}
            onClick={() => setCurrentHall(currentHall + 1)}
          >
            Next Hall
          </button>
          <button className="primary-button" type="button" onClick={handleApprovePdf} disabled={isGeneratingPdf}>
            {isGeneratingPdf && <span className="spinner" aria-hidden="true"></span>}
            {isGeneratingPdf ? 'Generating PDF...' : 'Approve & Generate PDF'}
          </button>
        </div>
      </section>
      <AiEvaluationPanel arrangement={activeArrangement} />
    </PageContainer>
  )
}

export default PreviewPage
