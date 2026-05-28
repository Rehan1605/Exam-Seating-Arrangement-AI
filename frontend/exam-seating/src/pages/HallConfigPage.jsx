import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageContainer from '../components/PageContainer'
import StepNavigation from '../components/StepNavigation'
import { saveHalls } from '../services/api'

const createId = () => globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`

const createHall = (hall = {}) => ({
  id: createId(),
  hallName: hall.hallName || '',
  rows: hall.rows || 1,
  cols: hall.cols || 1,
  blockedSeats: hall.blockedSeats || '',
})

function HallConfigPage() {
  const navigate = useNavigate()
  const [halls, setHalls] = useState(() => {
    const savedHalls = sessionStorage.getItem('hallConfiguration')
    if (savedHalls) {
      return JSON.parse(savedHalls).map((hall) => createHall(hall))
    }

    return [
      createHall({ hallName: 'Seminar Hall A', rows: 4, cols: 5, blockedSeats: 'R3C2' }),
      createHall({ hallName: 'Block B - Room 204', rows: 4, cols: 4, blockedSeats: 'R3C3' }),
    ]
  })
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const updateHall = (index, field, value) => {
    setHalls(halls.map((hall, hallIndex) => (
      hallIndex === index ? { ...hall, [field]: value } : hall
    )))
  }

  useEffect(() => {
    const persistedHalls = halls.map(({ hallName, rows, cols, blockedSeats }) => ({
      hallName,
      rows,
      cols,
      blockedSeats,
    }))
    sessionStorage.setItem('hallConfiguration', JSON.stringify(persistedHalls))
  }, [halls])

  const handleSave = async () => {
    setIsSaving(true)
    setMessage('')
    setError('')

    try {
      const payload = halls.map((hall) => ({
        hallName: hall.hallName.trim(),
        rows: Number(hall.rows),
        cols: Number(hall.cols),
        blockedSeats: hall.blockedSeats.trim() === '-' ? '' : hall.blockedSeats.trim(),
      }))
      const data = await saveHalls(payload)
      setMessage(data.message)
      return true
    } catch (saveError) {
      setError(saveError.message)
      return false
    } finally {
      setIsSaving(false)
    }
  }

  const handleSaveAndNext = async () => {
    const saved = await handleSave()
    if (saved) {
      navigate('/constraints')
    }
  }

  return (
    <PageContainer
      eyebrow="Step 3"
      title="Hall Configuration"
      description="Define seating capacity, rows, columns, and blocked seat references."
    >
      <section className="card">
        <div className="section-title">
          <h2>Available Examination Halls</h2>
          <button className="secondary-button" type="button" onClick={() => setHalls([...halls, createHall()])}>
            Add Hall
          </button>
        </div>
        <div className="table-wrap editable-table">
          <table>
            <thead>
              <tr>
                <th>Hall Name</th>
                <th>Rows</th>
                <th>Columns</th>
                <th>Blocked Seats</th>
              </tr>
            </thead>
            <tbody>
              {halls.map((hall, index) => (
                <tr key={hall.id}>
                  <td><input value={hall.hallName} onChange={(event) => updateHall(index, 'hallName', event.target.value)} /></td>
                  <td><input type="number" min="1" value={hall.rows} onChange={(event) => updateHall(index, 'rows', event.target.value)} /></td>
                  <td><input type="number" min="1" value={hall.cols} onChange={(event) => updateHall(index, 'cols', event.target.value)} /></td>
                  <td><input value={hall.blockedSeats} onChange={(event) => updateHall(index, 'blockedSeats', event.target.value)} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="workflow-footer">
          {message && <p className="success-message">{message}</p>}
          {error && <p className="error-message">{error}</p>}
          <button className="primary-button" type="button" onClick={handleSave} disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Save Hall Configuration'}
          </button>
        </div>
      </section>
      <StepNavigation
        previous="/exam-details"
        onNext={handleSaveAndNext}
        nextLabel={isSaving ? 'Saving...' : 'Save & Next'}
        nextDisabled={isSaving}
      />
    </PageContainer>
  )
}

export default HallConfigPage
