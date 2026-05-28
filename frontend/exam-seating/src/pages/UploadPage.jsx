import { useState } from 'react'
import PageContainer from '../components/PageContainer'
import StepNavigation from '../components/StepNavigation'
import { uploadCsv } from '../services/api'

function UploadPage() {
  const [fileName, setFileName] = useState(() => sessionStorage.getItem('uploadedStudentFileName') || 'No file uploaded')
  const [students, setStudents] = useState(() => {
    const savedStudents = sessionStorage.getItem('uploadedStudentPreview')
    return savedStudents ? JSON.parse(savedStudents) : []
  })
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState('')

  const handleUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) {
      return
    }

    setFileName(file.name)
    setIsUploading(true)
    setError('')

    try {
      const data = await uploadCsv(file)
      setStudents(data.preview)
      sessionStorage.setItem('uploadedStudentFileName', file.name)
      sessionStorage.setItem('uploadedStudentPreview', JSON.stringify(data.preview))
    } catch (uploadError) {
      setStudents([])
      sessionStorage.removeItem('uploadedStudentPreview')
      setError(uploadError.message)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <PageContainer
      eyebrow="Step 1"
      title="Upload Student CSV"
      description="Upload student roll numbers, branches, subjects, and course details."
    >
      <section className="card form-card">
        <label className="file-upload">
          <input type="file" accept=".csv" onChange={handleUpload} />
          <span>{isUploading ? 'Uploading...' : 'Choose CSV File'}</span>
          <strong>{fileName}</strong>
        </label>
        {error && <p className="error-message">{error}</p>}
      </section>

      <section className="card">
        <div className="section-title">
          <h2>Student Data Preview</h2>
          <p>{students.length} uploaded records shown</p>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Roll No</th>
                <th>Name</th>
                <th>Branch</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.RollNo}>
                  <td>{student.RollNo}</td>
                  <td>{student.Name}</td>
                  <td>{student.Branch}</td>
                </tr>
              ))}
              {!students.length && (
                <tr>
                  <td colSpan="3">Upload a CSV with RollNo, Name, and Branch columns.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
      <StepNavigation previous="/dashboard" next="/exam-details" nextLabel="Exam Details" />
    </PageContainer>
  )
}

export default UploadPage
