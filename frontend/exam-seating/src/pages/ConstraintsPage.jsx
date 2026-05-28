import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageContainer from '../components/PageContainer'
import StepNavigation from '../components/StepNavigation'
import { generateSeating } from '../services/api'

function ConstraintsPage() {
  const navigate = useNavigate()
  const [constraints, setConstraints] = useState({
    mixDepartments: true,
    respectBlockedSeats: true,
    fillHallEfficiently: true,
    sameSubjectHandling: 'prevent-adjacent',
  })
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')

  const updateConstraint = (field, value) => {
    setConstraints({ ...constraints, [field]: value })
  }

  const handleGenerate = async () => {
    setIsGenerating(true)
    setError('')

    try {
      const data = await generateSeating({ constraints })
      sessionStorage.setItem('latestSeatingArrangement', JSON.stringify(data.arrangement))
      if (data.arrangement?.success === false) {
        sessionStorage.setItem('latestGenerationError', data.arrangement.message)
      } else {
        sessionStorage.removeItem('latestGenerationError')
      }
      navigate('/preview')
    } catch (generateError) {
      setError(generateError.message)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <PageContainer
      eyebrow="Step 4"
      title="Seating Constraints"
      description="Select the core arrangement rules before generating the seating plan."
    >
      <section className="card form-card">
        <div className="options-grid">
          <label className="option-card">
            <input type="checkbox" checked={constraints.mixDepartments} onChange={(event) => updateConstraint('mixDepartments', event.target.checked)} />
            Mix departments
          </label>
          <label className="option-card">
            <input type="checkbox" checked={constraints.respectBlockedSeats} onChange={(event) => updateConstraint('respectBlockedSeats', event.target.checked)} />
            Respect blocked seats
          </label>
          <label className="option-card">
            <input type="checkbox" checked={constraints.fillHallEfficiently} onChange={(event) => updateConstraint('fillHallEfficiently', event.target.checked)} />
            Fill hall efficiently
          </label>
        </div>
      </section>

      <section className="card form-card">
        <div className="section-title">
          <h2>Same Subject Handling</h2>
        </div>
        <div className="radio-stack">
          <label><input type="radio" name="subject-handling" checked={constraints.sameSubjectHandling === 'allow-adjacent'} onChange={() => updateConstraint('sameSubjectHandling', 'allow-adjacent')} /> Allow adjacent</label>
          <label><input type="radio" name="subject-handling" checked={constraints.sameSubjectHandling === 'prevent-adjacent'} onChange={() => updateConstraint('sameSubjectHandling', 'prevent-adjacent')} /> Prevent adjacent</label>
          <label><input type="radio" name="subject-handling" checked={constraints.sameSubjectHandling === 'leave-one-seat-gap'} onChange={() => updateConstraint('sameSubjectHandling', 'leave-one-seat-gap')} /> Leave one seat gap</label>
        </div>
      </section>

      <div className="workflow-footer">
        {error && <p className="error-message">{error}</p>}
        <button className="primary-button" type="button" onClick={handleGenerate} disabled={isGenerating}>
          {isGenerating && <span className="spinner" aria-hidden="true"></span>}
          {isGenerating ? 'Solving CSP...' : 'Generate Seating'}
        </button>
      </div>
      <StepNavigation previous="/hall-config" />
    </PageContainer>
  )
}

export default ConstraintsPage
