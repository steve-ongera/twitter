import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handle = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await login(form)
      navigate('/home')
    } catch (err) {
      setError(err.data?.non_field_errors?.[0] || err.data?.detail || 'Invalid credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-left">
        <i className="ri-twitter-x-line" />
      </div>
      <div className="auth-right">
        <form className="auth-form" onSubmit={handle}>
          <div className="auth-logo">
            <i className="ri-twitter-x-line" />
          </div>
          <h1>Sign in to X</h1>

          {error && (
            <div className="alert alert-error">
              <i className="ri-error-warning-line" />{error}
            </div>
          )}

          <div className="form-group">
            <label>Username</label>
            <input
              className="form-input"
              value={form.username}
              onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
              required
              autoFocus
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              className="form-input"
              type="password"
              value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              required
            />
          </div>

          <button className="btn btn-dark btn-full" type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>

          <div className="auth-divider">or</div>

          <p style={{ textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Don't have an account?{' '}
            <Link to="/register" className="text-blue">Sign up</Link>
          </p>
        </form>
      </div>
    </div>
  )
}