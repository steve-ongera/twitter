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

  // ── Guard: bail out early if tweet or tweet.user is missing ───────────────
  if (!tweet || !tweet.user) return null

  const isOwner = user?.username === tweet.user?.username
  const isRetweet = !!tweet.retweet_of

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleLike = async (e) => {
    e.stopPropagation()
    if (!user) return navigate('/login')
    const prev = { ...tweet }
    setTweet(t => ({
      ...t,
      is_liked: !t.is_liked,
      likes_count: t.is_liked ? t.likes_count - 1 : t.likes_count + 1,
    }))
    try {
      await api.likeTweet(tweet.slug)
    } catch {
      setTweet(prev)
    }
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
    try {
      await api.retweetTweet(tweet.slug)
    } catch {
      setTweet(prev)
    }
  }

  const handleBookmark = async (e) => {
    e.stopPropagation()
    if (!user) return navigate('/login')
    const prev = { ...tweet }
    setTweet(t => ({ ...t, is_bookmarked: !t.is_bookmarked }))
    try {
      await api.bookmarkTweet(tweet.slug)
    } catch {
      setTweet(prev)
    }
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

  // ── Derived display values (safe because tweet.user is guaranteed above) ──
  const displayName = tweet.user.display_name || tweet.user.username

  return (
    <article className="tweet-card" onClick={goToTweet}>

      {/* ── Left column: avatar + thread line ── */}
      <div className="tweet-left">
        <div onClick={goToProfile} style={{ cursor: 'pointer' }}>
          <Avatar user={tweet.user} size="md" />
        </div>
        {showThread && <div className="tweet-thread-line" />}
      </div>

      {/* ── Right column: all tweet content ── */}
      <div className="tweet-right">

        {/* Retweet banner — only shown when this tweet is a retweet */}
        {isRetweet && (
          <div className="retweet-banner">
            <i className="ri-repeat-2-line" />
            <span>{displayName} Retweeted</span>
          </div>
        )}

        {/* Header: name · handle · time */}
        <div className="tweet-header">
          <span className="tweet-name" onClick={goToProfile}>
            {displayName}
          </span>
          {tweet.user.is_verified && (
            <i className="ri-verified-badge-fill tweet-verified" />
          )}
          <span className="tweet-handle">@{tweet.user.username}</span>
          <span className="tweet-dot">·</span>
          <span className="tweet-time">{timeAgo(tweet.created_at)}</span>
        </div>

        {/* "Replying to @handle" label */}
        {tweet.reply_to_user && (
          <div className="tweet-reply-label">
            Replying to{' '}
            <span
              className="text-blue"
              onClick={(e) => {
                e.stopPropagation()
                navigate(`/${tweet.reply_to_user}`)
              }}
            >
              @{tweet.reply_to_user}
            </span>
          </div>
        )}

        {/* Tweet body */}
        <div
          className="tweet-body"
          dangerouslySetInnerHTML={{ __html: formatTweetContent(tweet.content) }}
        />

        {/* Media */}
        {tweet.media_url && (
          <div className="tweet-image">
            <img
              src={tweet.media_url}
              alt="Tweet media"
              loading="lazy"
              onClick={(e) => e.stopPropagation()} // prevent nav when clicking image
            />
          </div>
        )}

        {/* Action bar */}
        <div className="tweet-actions">

          {/* Reply */}
          <button
            className="tweet-action reply"
            onClick={(e) => {
              e.stopPropagation()
              navigate(`/${tweet.user.username}/status/${tweet.slug}`)
            }}
            aria-label="Reply"
          >
            <i className="ri-chat-1-line" />
            <span>{formatCount(tweet.replies_count)}</span>
          </button>

          {/* Retweet */}
          <button
            className={`tweet-action retweet ${tweet.is_retweeted ? 'active' : ''}`}
            onClick={handleRetweet}
            aria-label={tweet.is_retweeted ? 'Undo retweet' : 'Retweet'}
            aria-pressed={tweet.is_retweeted}
          >
            <i className="ri-repeat-2-line" />
            <span>{formatCount(tweet.retweets_count)}</span>
          </button>

          {/* Like */}
          <button
            className={`tweet-action like ${tweet.is_liked ? 'active' : ''}`}
            onClick={handleLike}
            aria-label={tweet.is_liked ? 'Unlike' : 'Like'}
            aria-pressed={tweet.is_liked}
          >
            <i className={tweet.is_liked ? 'ri-heart-fill' : 'ri-heart-line'} />
            <span>{formatCount(tweet.likes_count)}</span>
          </button>

          {/* Bookmark */}
          <button
            className={`tweet-action bookmark ${tweet.is_bookmarked ? 'active' : ''}`}
            onClick={handleBookmark}
            aria-label={tweet.is_bookmarked ? 'Remove bookmark' : 'Bookmark'}
            aria-pressed={tweet.is_bookmarked}
          >
            <i className={tweet.is_bookmarked ? 'ri-bookmark-fill' : 'ri-bookmark-line'} />
            <span>{formatCount(tweet.bookmarks_count)}</span>
          </button>

          {/* Views (read-only) */}
          <button
            className="tweet-action views"
            onClick={(e) => e.stopPropagation()}
            aria-label="Views"
            tabIndex={-1}
            style={{ cursor: 'default', pointerEvents: 'none' }}
          >
            <i className="ri-bar-chart-2-line" />
            <span>{formatCount(tweet.views_count)}</span>
          </button>

        </div>
      </div>

      {/* Delete button — only visible to the tweet owner */}
      {isOwner && (
        <button
          className="tweet-more"
          onClick={handleDelete}
          title="Delete tweet"
          aria-label="Delete tweet"
        >
          <i className="ri-delete-bin-line" />
        </button>
      )}

    </article>
  )
}