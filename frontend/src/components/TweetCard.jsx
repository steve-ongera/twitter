import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Avatar from './Avatar'
import api from '../utils/api'
import { timeAgo, formatCount, formatTweetContent } from '../utils/helpers'

export default function TweetCard({ tweet: initialTweet, showThread = false, onDelete }) {
  const [tweet, setTweet] = useState(initialTweet)
  const { user } = useAuth()
  const navigate = useNavigate()

  if (!tweet) return null

  const isOwner = user?.username === tweet.user?.username

  const handleLike = async (e) => {
    e.stopPropagation()
    if (!user) return navigate('/login')
    const prev = { ...tweet }
    setTweet(t => ({
      ...t,
      is_liked: !t.is_liked,
      likes_count: t.is_liked ? t.likes_count - 1 : t.likes_count + 1,
    }))
    try { await api.likeTweet(tweet.slug) }
    catch { setTweet(prev) }
  }

  const handleRetweet = async (e) => {
    e.stopPropagation()
    if (!user) return navigate('/login')
    const prev = { ...tweet }
    setTweet(t => ({
      ...t,
      is_retweeted: !t.is_retweeted,
      retweets_count: t.is_retweeted ? t.retweets_count - 1 : t.retweets_count + 1,
    }))
    try { await api.retweetTweet(tweet.slug) }
    catch { setTweet(prev) }
  }

  const handleBookmark = async (e) => {
    e.stopPropagation()
    if (!user) return navigate('/login')
    const prev = { ...tweet }
    setTweet(t => ({ ...t, is_bookmarked: !t.is_bookmarked }))
    try { await api.bookmarkTweet(tweet.slug) }
    catch { setTweet(prev) }
  }

  const handleDelete = async (e) => {
    e.stopPropagation()
    if (!window.confirm('Delete this tweet?')) return
    try {
      await api.deleteTweet(tweet.slug)
      onDelete?.(tweet.id)
    } catch {}
  }

  const goToTweet = () => {
    navigate(`/${tweet.user.username}/status/${tweet.slug}`)
  }

  const goToProfile = (e) => {
    e.stopPropagation()
    navigate(`/${tweet.user.username}`)
  }

  const isRetweet = !!tweet.retweet_of

  return (
    <article className="tweet-card" onClick={goToTweet}>
      <div className="tweet-left">
        <div onClick={goToProfile} style={{ cursor: 'pointer' }}>
          <Avatar user={tweet.user} size="md" />
        </div>
        {showThread && <div className="tweet-thread-line" />}
      </div>

      <div className="tweet-right">
        {isRetweet && (
          <div className="retweet-banner">
            <i className="ri-repeat-2-line" />
            <span>{tweet.user.display_name || tweet.user.username} Retweeted</span>
          </div>
        )}

        <div className="tweet-header">
          <span className="tweet-name" onClick={goToProfile}>
            {tweet.user.display_name || tweet.user.username}
          </span>
          {tweet.user.is_verified && (
            <i className="ri-verified-badge-fill tweet-verified" />
          )}
          <span className="tweet-handle">@{tweet.user.username}</span>
          <span className="tweet-dot">·</span>
          <span className="tweet-time">{timeAgo(tweet.created_at)}</span>
        </div>

        {tweet.reply_to_user && (
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: 2 }}>
            Replying to <span className="text-blue">@{tweet.reply_to_user}</span>
          </div>
        )}

        <div
          className="tweet-body"
          dangerouslySetInnerHTML={{ __html: formatTweetContent(tweet.content) }}
        />

        {tweet.media_url && (
          <div className="tweet-image">
            <img src={tweet.media_url} alt="Tweet media" />
          </div>
        )}

        <div className="tweet-actions">
          <button
            className={`tweet-action reply`}
            onClick={(e) => { e.stopPropagation(); navigate(`/${tweet.user.username}/status/${tweet.slug}`) }}
          >
            <i className="ri-chat-1-line" />
            <span>{formatCount(tweet.replies_count)}</span>
          </button>

          <button
            className={`tweet-action retweet ${tweet.is_retweeted ? 'active' : ''}`}
            onClick={handleRetweet}
          >
            <i className="ri-repeat-2-line" />
            <span>{formatCount(tweet.retweets_count)}</span>
          </button>

          <button
            className={`tweet-action like ${tweet.is_liked ? 'active' : ''}`}
            onClick={handleLike}
          >
            <i className={tweet.is_liked ? 'ri-heart-fill' : 'ri-heart-line'} />
            <span>{formatCount(tweet.likes_count)}</span>
          </button>

          <button
            className={`tweet-action bookmark ${tweet.is_bookmarked ? 'active' : ''}`}
            onClick={handleBookmark}
          >
            <i className={tweet.is_bookmarked ? 'ri-bookmark-fill' : 'ri-bookmark-line'} />
            <span>{formatCount(tweet.bookmarks_count)}</span>
          </button>

          <button className="tweet-action" onClick={(e) => e.stopPropagation()}>
            <i className="ri-bar-chart-2-line" />
            <span>{formatCount(tweet.views_count)}</span>
          </button>
        </div>
      </div>

      {isOwner && (
        <button className="tweet-more" onClick={handleDelete} title="Delete tweet">
          <i className="ri-delete-bin-line" />
        </button>
      )}
    </article>
  )
}