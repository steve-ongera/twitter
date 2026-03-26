import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import TweetCard from '../components/TweetCard'
import Avatar from '../components/Avatar'
import api from '../utils/api'

export default function SearchPage() {
  const [searchParams] = useSearchParams()
  const q = searchParams.get('q') || ''
  const navigate = useNavigate()
  const [tab, setTab] = useState('tweets')
  const [results, setResults] = useState({ tweets: [], users: [], hashtags: [] })
  const [loading, setLoading] = useState(false)
  const [inputQ, setInputQ] = useState(q)

  useEffect(() => {
    if (!q) return
    setLoading(true)
    api.search(q)
      .then(setResults)
      .finally(() => setLoading(false))
  }, [q])

  const handleSearch = (e) => {
    e.preventDefault()
    if (inputQ.trim()) navigate(`/search?q=${encodeURIComponent(inputQ.trim())}`)
  }

  return (
    <>
      <header className="feed-header">
        <form onSubmit={handleSearch} style={{ flex: 1 }}>
          <div className="search-bar" style={{ position: 'static' }}>
            <i className="ri-search-line" />
            <input
              value={inputQ}
              onChange={e => setInputQ(e.target.value)}
              placeholder="Search"
              type="search"
              autoFocus
            />
          </div>
        </form>
      </header>

      {q && (
        <>
          <div className="search-tabs">
            {['tweets', 'users', 'hashtags'].map(t => (
              <button
                key={t}
                className={`search-tab ${tab === t ? 'active' : ''}`}
                onClick={() => setTab(t)}
              >
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>

          {loading ? (
            <div className="empty-state"><div className="spinner" style={{ margin: '0 auto' }} /></div>
          ) : (
            <>
              {tab === 'tweets' && (
                results.tweets?.length === 0
                  ? <div className="empty-state"><h3>No tweets found for "{q}"</h3></div>
                  : results.tweets?.map(t => <TweetCard key={t.id} tweet={t} />)
              )}

              {tab === 'users' && (
                results.users?.length === 0
                  ? <div className="empty-state"><h3>No users found for "{q}"</h3></div>
                  : results.users?.map(u => (
                    <div
                      key={u.id}
                      className="suggest-item"
                      style={{ padding: '16px', cursor: 'pointer', borderBottom: '1px solid var(--border)' }}
                      onClick={() => navigate(`/${u.username}`)}
                    >
                      <Avatar user={u} size="lg" />
                      <div className="suggest-info">
                        <div className="name" style={{ fontSize: '0.938rem' }}>
                          {u.display_name || u.username}
                          {u.is_verified && <i className="ri-verified-badge-fill" style={{ color: 'var(--color-blue)', fontSize: '0.9rem' }} />}
                        </div>
                        <div className="handle">@{u.username}</div>
                        {u.bio && <div style={{ fontSize: '0.875rem', marginTop: 4 }}>{u.bio}</div>}
                      </div>
                    </div>
                  ))
              )}

              {tab === 'hashtags' && (
                results.hashtags?.length === 0
                  ? <div className="empty-state"><h3>No hashtags found for "{q}"</h3></div>
                  : results.hashtags?.map(tag => (
                    <div
                      key={tag.id}
                      className="trend-item"
                      style={{ padding: '16px', cursor: 'pointer', borderBottom: '1px solid var(--border)' }}
                      onClick={() => navigate(`/hashtag/${tag.slug}`)}
                    >
                      <span className="trend-name">#{tag.name}</span>
                      <span className="trend-count">{tag.tweets_count} posts</span>
                    </div>
                  ))
              )}
            </>
          )}
        </>
      )}

      {!q && (
        <div className="empty-state">
          <h3>Search X</h3>
          <p>Try searching for people, topics, or keywords.</p>
        </div>
      )}
    </>
  )
}