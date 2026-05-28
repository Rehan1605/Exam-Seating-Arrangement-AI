import { useEffect, useState } from 'react'
import PageContainer from '../components/PageContainer'
import StepNavigation from '../components/StepNavigation'

const createId = () => globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`

const createSubject = (subject = {}) => ({
  id: createId(),
  branch: subject.branch || '',
  subject: subject.subject || '',
  courseCode: subject.courseCode || '',
})

function ExamDetailsPage() {
  const [examInfo, setExamInfo] = useState(() => {
    const savedInfo = sessionStorage.getItem('examMetadata')
    return savedInfo ? JSON.parse(savedInfo) : {
      examName: 'End Semester Examination',
      date: '2026-06-12',
      session: 'Morning',
      examTime: '10:00 AM - 1:00 PM',
    }
  })
  const [subjects, setSubjects] = useState([
    createSubject({ branch: 'CSE', subject: 'Artificial Intelligence', courseCode: 'CS501' }),
    createSubject({ branch: 'ECE', subject: 'Digital Systems', courseCode: 'EC403' }),
  ])

  const updateSubject = (index, field, value) => {
    setSubjects(subjects.map((row, rowIndex) => (
      rowIndex === index ? { ...row, [field]: value } : row
    )))
  }

  const updateExamInfo = (field, value) => {
    setExamInfo({ ...examInfo, [field]: value })
  }

  useEffect(() => {
    sessionStorage.setItem('examMetadata', JSON.stringify(examInfo))
  }, [examInfo])

  return (
    <PageContainer
      eyebrow="Step 2"
      title="Exam Details"
      description="Create the examination identity and map branches to papers."
    >
      <section className="card form-card">
        <div className="form-grid">
          <label>Exam Name<input type="text" value={examInfo.examName} onChange={(event) => updateExamInfo('examName', event.target.value)} /></label>
          <label>Date<input type="date" value={examInfo.date} onChange={(event) => updateExamInfo('date', event.target.value)} /></label>
          <label>Session<input type="text" value={examInfo.session} onChange={(event) => updateExamInfo('session', event.target.value)} /></label>
          <label>Exam Time<input type="text" value={examInfo.examTime} onChange={(event) => updateExamInfo('examTime', event.target.value)} /></label>
        </div>
      </section>

      <section className="card">
        <div className="section-title">
          <h2>Subject Mapping</h2>
          <button className="secondary-button" type="button" onClick={() => setSubjects([...subjects, createSubject()])}>
            Add Row
          </button>
        </div>
        <div className="table-wrap editable-table">
          <table>
            <thead>
              <tr>
                <th>Branch</th>
                <th>Subject</th>
                <th>Course Code</th>
              </tr>
            </thead>
            <tbody>
              {subjects.map((row, index) => (
                <tr key={row.id}>
                  <td><input value={row.branch} onChange={(event) => updateSubject(index, 'branch', event.target.value)} /></td>
                  <td><input value={row.subject} onChange={(event) => updateSubject(index, 'subject', event.target.value)} /></td>
                  <td><input value={row.courseCode} onChange={(event) => updateSubject(index, 'courseCode', event.target.value)} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <StepNavigation previous="/upload" next="/hall-config" nextLabel="Hall Configuration" />
    </PageContainer>
  )
}

export default ExamDetailsPage
