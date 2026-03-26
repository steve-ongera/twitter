import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import TweetCard from '../components/TweetCard'
import api from '../utils/api'

export default function HashtagPage() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [tweets, setTweets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getHashtagTweets(slug)
      .then(res => setTweets(res.results || res))
      .finally(() => setLoading(false))
  }, [slug])

  return (
    <>
      <header className="feed-header">
        <button className="feed-header-back" onClick={() => navigate(-1)}>
          <i className="ri-arrow-left-line" />
        </button>
        <h2>#{slug}</h2>
      </header>

      {loading ? (
        <div className="empty-state"><div className="spinner" style={{ margin: '0 auto' }} /></div>
      ) : tweets.length === 0 ? (
        <div className="empty-state"><h3>No tweets for #{slug}</h3></div>
      ) : (
        tweets.map(t => <TweetCard key={t.id} tweet={t} />)
      )}
    </>
  )
}