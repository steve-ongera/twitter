import { useState, useEffect, useCallback } from 'react'
import TweetCard from '../components/TweetCard'
import TweetComposer from '../components/TweetComposer'
import api from '../utils/api'

export default function Home() {
  const [tweets, setTweets] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [tab, setTab] = useState('for_you')

  const fetchFeed = useCallback(async (p = 1, replace = false) => {
    setLoading(true)
    try {
      const res = tab === 'for_you'
        ? await api.getFeed(p)
        : await api.getExplore()
      const results = res.results || res
      setTweets(prev => replace ? results : [...prev, ...results])
      setHasMore(!!res.next)
    } catch {}
    setLoading(false)
  }, [tab])

  useEffect(() => {
    setPage(1)
    fetchFeed(1, true)
  }, [tab, fetchFeed])

  const handleNewTweet = (tweet) => {
    setTweets(prev => [tweet, ...prev])
  }

  const handleDelete = (id) => {
    setTweets(prev => prev.filter(t => t.id !== id))
  }

  const loadMore = () => {
    const next = page + 1
    setPage(next)
    fetchFeed(next)
  }

  return (
    <>
      <header className="feed-header">
        <h1>Home</h1>
      </header>

      <div className="feed-tabs">
        <button
          className={`feed-tab ${tab === 'for_you' ? 'active' : ''}`}
          onClick={() => setTab('for_you')}
        >
          For you
        </button>
        <button
          className={`feed-tab ${tab === 'following' ? 'active' : ''}`}
          onClick={() => setTab('following')}
        >
          Following
        </button>
      </div>

      <TweetComposer onTweet={handleNewTweet} />

      {loading && tweets.length === 0 ? (
        <div className="empty-state">
          <div className="spinner" style={{ margin: '0 auto' }} />
        </div>
      ) : tweets.length === 0 ? (
        <div className="empty-state">
          <h3>No tweets yet</h3>
          <p>Follow some people to see their tweets here.</p>
        </div>
      ) : (
        <>
          {tweets.map(tweet => (
            <TweetCard key={tweet.id} tweet={tweet} onDelete={handleDelete} />
          ))}
          {hasMore && (
            <div style={{ padding: '16px', textAlign: 'center' }}>
              <button className="btn btn-outline" onClick={loadMore} disabled={loading}>
                {loading ? 'Loading…' : 'Load more'}
              </button>
            </div>
          )}
        </>
      )}
    </>
  )
}