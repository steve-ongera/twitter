import { useNavigate } from 'react-router-dom'

export default function NotFound() {
  const navigate = useNavigate()
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', gap: 24, padding: 32, textAlign: 'center' }}>
      <i className="ri-twitter-x-line" style={{ fontSize: '3rem', color: 'var(--text-primary)' }} />
      <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Hmm, this page doesn't exist.</h1>
      <p style={{ color: 'var(--text-secondary)', maxWidth: 380 }}>
        Try searching for something else, or go back to home.
      </p>
      <button className="btn btn-primary" onClick={() => navigate('/home')}>
        Go to Home
      </button>
    </div>
  )
}