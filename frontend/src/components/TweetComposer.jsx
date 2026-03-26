import { useState, useRef } from 'react'
import { useAuth } from '../context/AuthContext'
import Avatar from './Avatar'
import api from '../utils/api'

const MAX = 280

export default function TweetComposer({ onTweet, replyTo = null, placeholder = "What's happening?" }) {
  const { user } = useAuth()
  const [content, setContent] = useState('')
  const [media, setMedia] = useState(null)
  const [mediaPreview, setMediaPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const textRef = useRef()
  const fileRef = useRef()

  const remaining = MAX - content.length
  const canPost = content.trim().length > 0 && remaining >= 0 && !loading

  const handleInput = (e) => {
    setContent(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = e.target.scrollHeight + 'px'
  }

  const handleMedia = (e) => {
    const file = e.target.files[0]
    if (!file) return
    setMedia(file)
    setMediaPreview(URL.createObjectURL(file))
  }

  const removeMedia = () => {
    setMedia(null)
    setMediaPreview(null)
    fileRef.current.value = ''
  }

  const submit = async () => {
    if (!canPost) return
    setLoading(true)
    setError(null)
    try {
      let body
      if (media) {
        body = new FormData()
        body.append('content', content)
        body.append('media', media)
        if (replyTo) body.append('reply_to', replyTo)
      } else {
        body = { content }
        if (replyTo) body.reply_to = replyTo
      }
      const tweet = await api.createTweet(body)
      setContent('')
      setMedia(null)
      setMediaPreview(null)
      if (textRef.current) textRef.current.style.height = 'auto'
      onTweet?.(tweet)
    } catch (err) {
      setError(err.data?.content?.[0] || 'Failed to post tweet.')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') submit()
  }

  const charClass = remaining <= 20 ? (remaining < 0 ? 'danger' : 'warning') : ''

  return (
    <div className="compose-box">
      <Avatar user={user} size="md" />
      <div className="compose-right">
        {replyTo && (
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: 8 }}>
            Replying to tweet
          </div>
        )}
        <textarea
          ref={textRef}
          className="compose-textarea"
          placeholder={placeholder}
          value={content}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          rows={1}
        />

        {mediaPreview && (
          <div className="tweet-media-preview">
            <img src={mediaPreview} alt="Preview" />
            <button className="remove-media" onClick={removeMedia}>
              <i className="ri-close-line" />
            </button>
          </div>
        )}

        {error && (
          <div className="alert alert-error" style={{ padding: '8px 12px', margin: '4px 0' }}>
            <i className="ri-error-warning-line" />{error}
          </div>
        )}

        <div className="compose-toolbar">
          <div className="compose-tools">
            <input ref={fileRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleMedia} />
            <button className="compose-tool" onClick={() => fileRef.current.click()} title="Add image">
              <i className="ri-image-line" />
            </button>
            <button className="compose-tool" title="GIF">
              <i className="ri-file-gif-line" />
            </button>
            <button className="compose-tool" title="Emoji">
              <i className="ri-emotion-line" />
            </button>
          </div>

          <div className="compose-right-actions">
            {content.length > 0 && (
              <>
                <div
                  className={`char-counter ${charClass}`}
                  style={{
                    background: `conic-gradient(${remaining < 0 ? 'var(--color-like)' : remaining <= 20 ? '#ffd400' : 'var(--color-blue)'} ${Math.min(((MAX - remaining) / MAX) * 360, 360)}deg, var(--border) 0deg)`
                  }}
                >
                  {remaining <= 20 && <span style={{ fontSize: '0.7rem' }}>{remaining}</span>}
                </div>
                <div className="compose-divider" />
              </>
            )}
            <button
              className="btn btn-primary btn-sm"
              onClick={submit}
              disabled={!canPost}
            >
              {loading ? 'Posting…' : 'Post'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}