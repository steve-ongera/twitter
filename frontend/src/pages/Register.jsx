import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', display_name: '', password: '', password2: '' })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handle = async (e) => {
    e.preventDefault()
    setLoading(true)
    setErrors({})
    try {
      await register(form)
      navigate('/home')
    } catch (err) {
      setErrors(err.data || { non_field_errors: ['Registration failed.'] })
    } finally {
      setLoading(false)
    }
  }

  const field = (key, label, type = 'text') => (
    <div className="form-group">
      <label>{label}</label>
      <input
        className={`form-input${errors[key] ? ' error' : ''}`}
        type={type}
        value={form[key]}
        onChange={set(key)}
        required
      />
      {errors[key] && <span className="form-error">{errors[key][0]}</span>}
    </div>
  )

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
          <h1>Create your account</h1>

          {errors.non_field_errors && (
            <div className="alert alert-error">
              <i className="ri-error-warning-line" />{errors.non_field_errors[0]}
            </div>
          )}

          {field('username', 'Username')}
          {field('email', 'Email', 'email')}
          {field('display_name', 'Display name')}
          {field('password', 'Password', 'password')}
          {field('password2', 'Confirm password', 'password')}

          <button className="btn btn-dark btn-full" type="submit" disabled={loading}>
            {loading ? 'Creating account…' : 'Sign up'}
          </button>

          <p style={{ textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Already have an account?{' '}
            <Link to="/login" className="text-blue">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  )
}