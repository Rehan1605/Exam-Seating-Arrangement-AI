import { NavLink, useLocation } from 'react-router-dom'

const links = [
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/upload', label: 'Upload' },
  { path: '/exam-details', label: 'Exam Details' },
  { path: '/hall-config', label: 'Halls' },
  { path: '/constraints', label: 'Constraints' },
  { path: '/preview', label: 'Preview' },
]

function Navbar() {
  const { pathname } = useLocation()

  if (pathname === '/login') {
    return null
  }

  return (
    <header className="navbar">
      <NavLink className="brand" to="/dashboard" aria-label="Go to dashboard">
        <span className="brand-mark">AI</span>
        <span>
          <strong>Exam Seating AI</strong>
          <small>Academic Examination Cell</small>
        </span>
      </NavLink>
      <nav className="nav-links" aria-label="Primary navigation">
        {links.map((link) => (
          <NavLink key={link.path} to={link.path}>
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}

export default Navbar
