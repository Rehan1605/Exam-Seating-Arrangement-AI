import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UploadPage from './pages/UploadPage'
import ExamDetailsPage from './pages/ExamDetailsPage'
import HallConfigPage from './pages/HallConfigPage'
import ConstraintsPage from './pages/ConstraintsPage'
import PreviewPage from './pages/PreviewPage'
import SuccessPage from './pages/SuccessPage'
import './styles/global.css'

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/exam-details" element={<ExamDetailsPage />} />
        <Route path="/hall-config" element={<HallConfigPage />} />
        <Route path="/constraints" element={<ConstraintsPage />} />
        <Route path="/preview" element={<PreviewPage />} />
        <Route path="/success" element={<SuccessPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
