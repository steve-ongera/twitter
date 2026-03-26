import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Avatar from '../components/Avatar'
import api from '../utils/api'
import { timeAgo } from '../utils/helpers'

const ICONS = {
  like:    { icon: 'ri-heart-fill',        cls: 'like' },
  retweet: { icon: 'ri-repeat-2-fill',     cls: 'retweet' },
  reply:   { icon: 'ri-chat-1-fill',       cls: 'reply' },
  follow:  { icon: 'ri-user-add-fill',     cls: 'follow' },
  mention: { icon: 'ri-at-line',           cls: 'mention' },
}

function notifText(n) {
  const name = n.sender.display_name || n.sender.username
  switch (n.notification_type) {
    case 'like':    return <><strong>{name}</strong> liked your tweet</>
    case 'retweet': return <><strong>{name}</strong> retweeted your tweet</>
    case 'reply':   return <><strong>{name}</strong> replied to your tweet</>
    case 'follow':  return <><strong>{name}</strong> followed you</>
    case 'mention': return <><strong>{name}</strong> mentioned you</>
    default:        return <><strong>{name}</strong> interacted with you</>
  }
}

export default function Notifications() {
  const [notifs, setNotifs] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await api.getNotifications()
        setNotifs(res.results || res)
        await api.markAllRead()
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  const handleClick = (n) => {
    if (n.tweet) navigate(`/${n.sender.username}/status/${n.tweet.slug}`)
    else navigate(`/${n.sender.username}`)
  }

  return (
    <>
      <header className="feed-header">
        <h1>Notifications</h1>
      </header>

      {loading ? (
        <div className="empty-state"><div className="spinner" style={{ margin: '0 auto' }} /></div>
      ) : notifs.length === 0 ? (
        <div className="empty-state">
          <h3>No notifications yet</h3>
          <p>When someone likes or replies to your tweets, it'll show up here.</p>
        </div>
      ) : (
        notifs.map(n => {
          const { icon, cls } = ICONS[n.notification_type] || ICONS.mention
          return (
            <div
              key={n.id}
              className={`notif-item ${!n.is_read ? 'unread' : ''}`}
              onClick={() => handleClick(n)}
            >
              <div className={`notif-icon ${cls}`}>
                <i className={icon} />
              </div>
              <div className="notif-content">
                <Avatar user={n.sender} size="sm" />
                <div style={{ marginTop: 8 }}>{notifText(n)}</div>
                {n.tweet && (
                  <div className="notif-text" style={{ marginTop: 4 }}>
                    {n.tweet.content?.slice(0, 100)}{n.tweet.content?.length > 100 ? '…' : ''}
                  </div>
                )}
                <div className="notif-time" style={{ marginTop: 4 }}>{timeAgo(n.created_at)}</div>
              </div>
            </div>
          )
        })
      )}
    </>
  )
}