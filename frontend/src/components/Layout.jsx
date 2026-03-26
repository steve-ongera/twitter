import { useState, useEffect } from 'react'
import { Outlet, NavLink, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Avatar from './Avatar'
import api from '../utils/api'
import TweetComposer from './TweetComposer'

function NavItem({ to, icon, label, badge }) {
  return (
    <NavLink to={to} className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
      <i className={icon} />
      <span className="nav-label">{label}</span>
      {badge > 0 && <span className="nav-badge">{badge > 99 ? '99+' : badge}</span>}
    </NavLink>
  )
}

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [unread, setUnread] = useState(0)
  const [trends, setTrends] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [composeOpen, setComposeOpen] = useState(false)
  const [searchQ, setSearchQ] = useState('')

  useEffect(() => {
    const fetchSidebar = async () => {
      try {
        const [notifRes, trendRes, suggestRes] = await Promise.allSettled([
          api.getUnreadCount(),
          api.getTrendingHashtags(),
          api.getSuggestions(),
        ])
        if (notifRes.status === 'fulfilled') setUnread(notifRes.value.unread_count)
        if (trendRes.status === 'fulfilled') setTrends(trendRes.value.slice(0, 5))
        if (suggestRes.status === 'fulfilled') setSuggestions(suggestRes.value.slice(0, 3))
      } catch {}
    }
    fetchSidebar()
    const interval = setInterval(async () => {
      try {
        const res = await api.getUnreadCount()
        setUnread(res.unread_count)
      } catch {}
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQ.trim()) navigate(`/search?q=${encodeURIComponent(searchQ.trim())}`)
  }

  const handleNewTweet = () => {
    setComposeOpen(false)
  }

  return (
    <div className="app-layout">
      {/* Left Sidebar */}
      <aside className="sidebar">
        <Link to="/home" className="sidebar-logo">
          <i className="ri-twitter-x-line" />
        </Link>

        <nav className="sidebar-nav">
          <NavItem to="/home" icon="ri-home-5-line" label="Home" />
          <NavItem to="/explore" icon="ri-search-line" label="Explore" />
          <NavItem to="/notifications" icon="ri-notification-3-line" label="Notifications" badge={unread} />
          <NavItem to="/messages" icon="ri-message-3-line" label="Messages" />
          <NavItem to="/bookmarks" icon="ri-bookmark-line" label="Bookmarks" />
          {user && <NavItem to={`/${user.username}`} icon="ri-user-line" label="Profile" />}
          <NavItem to="/settings" icon="ri-settings-3-line" label="Settings" />
        </nav>

        <button className="sidebar-tweet-btn" onClick={() => setComposeOpen(true)}>
          <i className="ri-add-line sidebar-tweet-btn-icon" />
          <span>Post</span>
        </button>

        <div className="sidebar-user" onClick={() => navigate(`/${user?.username}`)}>
          <Avatar user={user} size="md" />
          <div className="sidebar-user-info">
            <div className="name">{user?.display_name || user?.username}</div>
            <div className="handle">@{user?.username}</div>
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); handleLogout() }}
            style={{ marginLeft: 'auto', color: 'var(--text-secondary)', fontSize: '1rem' }}
            title="Logout"
          >
            <i className="ri-logout-box-r-line" />
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Outlet context={{ onNewTweet: handleNewTweet }} />
      </main>

      {/* Right Sidebar */}
      <aside className="right-sidebar">
        <form className="search-bar" onSubmit={handleSearch}>
          <i className="ri-search-line" />
          <input
            value={searchQ}
            onChange={e => setSearchQ(e.target.value)}
            placeholder="Search"
            type="search"
          />
        </form>

        {trends.length > 0 && (
          <div className="widget-box">
            <h2>Trends for you</h2>
            {trends.map(tag => (
              <div key={tag.id} className="trend-item" onClick={() => navigate(`/hashtag/${tag.slug}`)}>
                <span className="trend-category">Trending</span>
                <span className="trend-name">#{tag.name}</span>
                <span className="trend-count">{tag.tweets_count?.toLocaleString()} posts</span>
              </div>
            ))}
          </div>
        )}

        {suggestions.length > 0 && (
          <div className="widget-box">
            <h2>Who to follow</h2>
            {suggestions.map(u => (
              <div key={u.id} className="suggest-item">
                <Avatar user={u} size="md" />
                <div className="suggest-info">
                  <div className="name">
                    {u.display_name || u.username}
                    {u.is_verified && <i className="ri-verified-badge-fill" style={{ color: 'var(--color-blue)', fontSize: '0.9rem' }} />}
                  </div>
                  <div className="handle">@{u.username}</div>
                </div>
                <button
                  className="btn btn-follow btn-sm"
                  onClick={async () => {
                    try {
                      await api.followUser(u.username)
                      setSuggestions(s => s.filter(x => x.id !== u.id))
                    } catch {}
                  }}
                >
                  Follow
                </button>
              </div>
            ))}
          </div>
        )}
      </aside>

      {/* Mobile Bottom Nav */}
      <nav className="mobile-nav">
        <div className="mobile-nav-inner">
          <NavLink to="/home" className={({ isActive }) => `mobile-nav-item${isActive ? ' active' : ''}`}>
            <i className="ri-home-5-line" />
          </NavLink>
          <NavLink to="/explore" className={({ isActive }) => `mobile-nav-item${isActive ? ' active' : ''}`}>
            <i className="ri-search-line" />
          </NavLink>
          <NavLink to="/notifications" className={({ isActive }) => `mobile-nav-item${isActive ? ' active' : ''}`}>
            <i className="ri-notification-3-line" />
            {unread > 0 && <span className="nav-badge">{unread}</span>}
          </NavLink>
          <NavLink to="/messages" className={({ isActive }) => `mobile-nav-item${isActive ? ' active' : ''}`}>
            <i className="ri-message-3-line" />
          </NavLink>
          <NavLink to={`/${user?.username}`} className={({ isActive }) => `mobile-nav-item${isActive ? ' active' : ''}`}>
            <Avatar user={user} size="sm" />
          </NavLink>
        </div>
      </nav>

      {/* Mobile FAB */}
      <button className="mobile-fab" onClick={() => setComposeOpen(true)}>
        <i className="ri-quill-pen-line" />
      </button>

      {/* Compose Modal */}
      {composeOpen && (
        <div className="modal-backdrop" onClick={() => setComposeOpen(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 600 }}>
            <div className="modal-header">
              <button className="modal-close" onClick={() => setComposeOpen(false)}>
                <i className="ri-close-line" />
              </button>
            </div>
            <TweetComposer onTweet={(tweet) => {
              setComposeOpen(false)
              handleNewTweet(tweet)
            }} />
          </div>
        </div>
      )}
    </div>
  )
}