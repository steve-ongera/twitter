import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import TweetCard from '../components/TweetCard'
import api from '../utils/api'

export default function Explore() {
  const [tweets, setTweets] = useState([])
  const [trends, setTrends] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQ, setSearchQ] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const fetch = async () => {
      try {
        const [tweetsRes, trendsRes] = await Promise.allSettled([
          api.getExplore(),
          api.getTrendingHashtags(),
        ])
        if (tweetsRes.status === 'fulfilled') setTweets(tweetsRes.value.results || tweetsRes.value)
        if (trendsRes.status === 'fulfilled') setTrends(trendsRes.value)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQ.trim()) navigate(`/search?q=${encodeURIComponent(searchQ.trim())}`)
  }

  return (
    <>
      <header className="feed-header">
        <h1>Explore</h1>
      </header>

      <div className="explore-search-bar">
        <form onSubmit={handleSearch} className="search-bar" style={{ position: 'static' }}>
          <i className="ri-search-line" />
          <input
            value={searchQ}
            onChange={e => setSearchQ(e.target.value)}
            placeholder="Search"
            type="search"
          />
        </form>
      </div>

      {trends.length > 0 && (
        <div style={{ borderBottom: '1px solid var(--border)' }}>
          <div style={{ padding: '16px', fontWeight: 800, fontSize: '1.125rem' }}>Trending</div>
          <div style={{ display: 'flex', gap: 12, padding: '0 16px 16px', flexWrap: 'wrap' }}>
            {trends.map(tag => (
              <button
                key={tag.id}
                className="btn btn-outline btn-sm"
                onClick={() => navigate(`/hashtag/${tag.slug}`)}
              >
                #{tag.name}
                <span style={{ color: 'var(--text-secondary)', fontWeight: 400 }}>
                  &nbsp;{tag.tweets_count}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <div className="empty-state"><div className="spinner" style={{ margin: '0 auto' }} /></div>
      ) : tweets.length === 0 ? (
        <div className="empty-state"><h3>Nothing to explore</h3></div>
      ) : (
        tweets.map(t => <TweetCard key={t.id} tweet={t} />)
      )}
    </>
  )
}