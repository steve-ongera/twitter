import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import TweetCard from '../components/TweetCard'
import TweetComposer from '../components/TweetComposer'
import api from '../utils/api'

export default function TweetDetail() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getThread(slug)
      .then(setData)
      .catch(() => navigate('/404'))
      .finally(() => setLoading(false))
  }, [slug, navigate])

  const handleReply = (reply) => {
    setData(d => ({ ...d, replies: [reply, ...d.replies] }))
  }

  const handleDelete = (id) => {
    setData(d => ({ ...d, replies: d.replies.filter(r => r.id !== id) }))
  }

  if (loading) return <div className="empty-state"><div className="spinner" style={{ margin: '0 auto' }} /></div>
  if (!data) return null

  return (
    <>
      <header className="feed-header">
        <button className="feed-header-back" onClick={() => navigate(-1)}>
          <i className="ri-arrow-left-line" />
        </button>
        <h2>Post</h2>
      </header>

      <TweetCard tweet={data.tweet} showThread={data.replies.length > 0} />

      {user && (
        <TweetComposer
          onTweet={handleReply}
          replyTo={data.tweet.id}
          placeholder={`Reply to @${data.tweet.user.username}…`}
        />
      )}

      {data.replies.map(r => <TweetCard key={r.id} tweet={r} onDelete={handleDelete} />)}
    </>
  )
}