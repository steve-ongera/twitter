import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function Settings() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [theme, setTheme] = useState(() => document.documentElement.getAttribute('data-theme') || 'dark')

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    document.documentElement.setAttribute('data-theme', next)
    localStorage.setItem('theme', next)
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <>
      <header className="feed-header">
        <button className="feed-header-back" onClick={() => navigate(-1)}>
          <i className="ri-arrow-left-line" />
        </button>
        <h2>Settings</h2>
      </header>

      <div className="settings-list">
        <div className="settings-item" onClick={toggleTheme}>
          <div className="settings-item-left">
            <span className="label">
              <i className={`ri-${theme === 'dark' ? 'sun' : 'moon'}-line`} style={{ marginRight: 8 }} />
              {theme === 'dark' ? 'Light mode' : 'Dark mode'}
            </span>
            <span className="desc">Switch to {theme === 'dark' ? 'light' : 'dark'} theme</span>
          </div>
          <div className={`toggle ${theme === 'light' ? 'on' : ''}`} />
        </div>

        <div className="settings-item" onClick={() => navigate(`/${user?.username}`)}>
          <div className="settings-item-left">
            <span className="label"><i className="ri-user-line" style={{ marginRight: 8 }} />Your profile</span>
            <span className="desc">@{user?.username}</span>
          </div>
          <i className="ri-arrow-right-s-line" style={{ color: 'var(--text-secondary)' }} />
        </div>

        <div className="settings-item" onClick={() => navigate('/bookmarks')}>
          <div className="settings-item-left">
            <span className="label"><i className="ri-bookmark-line" style={{ marginRight: 8 }} />Bookmarks</span>
            <span className="desc">Saved tweets</span>
          </div>
          <i className="ri-arrow-right-s-line" style={{ color: 'var(--text-secondary)' }} />
        </div>

        <div className="settings-item" onClick={handleLogout} style={{ color: 'var(--color-like)' }}>
          <div className="settings-item-left">
            <span className="label" style={{ color: 'var(--color-like)' }}>
              <i className="ri-logout-box-r-line" style={{ marginRight: 8 }} />Log out
            </span>
            <span className="desc" style={{ color: 'var(--text-secondary)' }}>@{user?.username}</span>
          </div>
        </div>
      </div>
    </>
  )
}