import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function LoginPage() {
  const navigate = useNavigate()
  const [credentials, setCredentials] = useState({ username: '', password: '' })

  const handleSubmit = (event) => {
    event.preventDefault()
    navigate('/dashboard')
  }

  return (
    <main className="login-layout">
      <section className="login-panel">
        <div className="login-copy">
          <span className="brand-mark large">AI</span>
          <p className="eyebrow">Examination Seating System</p>
          <h1>AI-Based Examination Seating Arrangement</h1>
          <p>
            Plan conflict-aware, hall-wise seating arrangements for academic examinations with a clear approval workflow.
          </p>
        </div>
        <form className="card login-card" onSubmit={handleSubmit}>
          <h2>Coordinator Login</h2>
          <label>
            Username
            <input
              type="text"
              value={credentials.username}
              onChange={(event) => setCredentials({ ...credentials, username: event.target.value })}
              placeholder="exam.admin"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={credentials.password}
              onChange={(event) => setCredentials({ ...credentials, password: event.target.value })}
              placeholder="Enter password"
            />
          </label>
          <button className="primary-button" type="submit">Login</button>
        </form>
      </section>
    </main>
  )
}

export default LoginPage
