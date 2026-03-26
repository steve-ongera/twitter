import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Avatar from '../components/Avatar'
import TweetCard from '../components/TweetCard'
import api from '../utils/api'
import { formatCount } from '../utils/helpers'

export default function Profile() {
  const { username } = useParams()
  const { user: me, updateUser } = useAuth()
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [tweets, setTweets] = useState([])
  const [tab, setTab] = useState('tweets')
  const [loading, setLoading] = useState(true)
  const [tweetLoading, setTweetLoading] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const [followLoading, setFollowLoading] = useState(false)
  const [editData, setEditData] = useState({})

  const isMe = me?.username === username

  useEffect(() => {
    setLoading(true)
    setTweets([])
    setTab('tweets')
    api.getUser(username)
      .then(p => { setProfile(p); setEditData({ display_name: p.display_name, bio: p.bio, location: p.location, website: p.website }) })
      .catch(() => navigate('/404'))
      .finally(() => setLoading(false))
  }, [username, navigate])

  useEffect(() => {
    if (!profile) return
    const fetchContent = async () => {
      setTweetLoading(true)
      try {
        if (tab === 'tweets') {
          const res = await api.getUserTweets(username)
          setTweets(res.results || res)
        } else if (tab === 'likes') {
          const res = await api.getUserLikes(username)
          setTweets(res.results || res)
        }
      } finally {
        setTweetLoading(false)
      }
    }
    fetchContent()
  }, [tab, profile, username])

  const handleFollow = async () => {
    setFollowLoading(true)
    try {
      if (profile.is_following) {
        await api.unfollowUser(username)
        setProfile(p => ({ ...p, is_following: false, followers_count: p.followers_count - 1 }))
      } else {
        await api.followUser(username)
        setProfile(p => ({ ...p, is_following: true, followers_count: p.followers_count + 1 }))
      }
    } catch {}
    setFollowLoading(false)
  }

  const handleEditSave = async () => {
    try {
      const res = await api.updateMe(editData)
      setProfile(p => ({ ...p, ...res }))
      updateUser(res)
      setEditOpen(false)
    } catch {}
  }

  const handleDelete = (id) => {
    setTweets(prev => prev.filter(t => t.id !== id))
  }

  if (loading) return <div className="empty-state"><div className="spinner" style={{ margin: '0 auto' }} /></div>
  if (!profile) return null

  return (
    <>
      <header className="feed-header">
        <button className="feed-header-back" onClick={() => navigate(-1)}>
          <i className="ri-arrow-left-line" />
        </button>
        <div>
          <h2>{profile.display_name || profile.username}</h2>
          <div style={{ fontSize: '0.813rem', color: 'var(--text-secondary)' }}>
            {formatCount(profile.tweets_count)} posts
          </div>
        </div>
      </header>

      {/* Banner */}
      <div className="profile-banner">
        {profile.banner_url && <img src={profile.banner_url} alt="Banner" />}
      </div>

      <div className="profile-info-section">
        <div className="profile-top-row">
          <div className="profile-avatar-wrap">
            <Avatar user={profile} size="xxl" />
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 8 }}>
            {isMe ? (
              <button className="btn btn-outline btn-sm" onClick={() => setEditOpen(true)}>
                Edit profile
              </button>
            ) : (
              <>
                <button className="btn btn-outline btn-sm" onClick={() => navigate(`/messages/${username}`)}>
                  <i className="ri-message-3-line" />
                </button>
                <button
                  className={`btn btn-sm ${profile.is_following ? 'btn-following' : 'btn-follow'}`}
                  onClick={handleFollow}
                  disabled={followLoading}
                >
                  {profile.is_following
                    ? <><span className="following-text">Following</span></>
                    : 'Follow'}
                </button>
              </>
            )}
          </div>
        </div>

        <div className="profile-name">
          {profile.display_name || profile.username}
          {profile.is_verified && <i className="ri-verified-badge-fill verified-badge" />}
        </div>
        <div className="profile-handle">@{profile.username}</div>

        {profile.bio && <div className="profile-bio">{profile.bio}</div>}

        <div className="profile-meta">
          {profile.location && <span><i className="ri-map-pin-line" />{profile.location}</span>}
          {profile.website && (
            <span>
              <i className="ri-link" />
              <a href={profile.website} target="_blank" rel="noopener noreferrer" className="text-blue">
                {profile.website.replace(/^https?:\/\//, '')}
              </a>
            </span>
          )}
        </div>

        <div className="profile-stats">
          <a onClick={() => {}} style={{ cursor: 'pointer' }}>
            <strong>{formatCount(profile.following_count)}</strong>
            <span style={{ color: 'var(--text-secondary)' }}>Following</span>
          </a>
          <a onClick={() => {}} style={{ cursor: 'pointer' }}>
            <strong>{formatCount(profile.followers_count)}</strong>
            <span style={{ color: 'var(--text-secondary)' }}>Followers</span>
          </a>
        </div>
      </div>

      <div className="feed-tabs">
        {['tweets', 'likes'].map(t => (
          <button
            key={t}
            className={`feed-tab ${tab === t ? 'active' : ''}`}
            onClick={() => setTab(t)}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tweetLoading ? (
        <div className="empty-state"><div className="spinner" style={{ margin: '0 auto' }} /></div>
      ) : tweets.length === 0 ? (
        <div className="empty-state">
          <h3>No {tab} yet</h3>
        </div>
      ) : (
        tweets.map(t => <TweetCard key={t.id} tweet={t} onDelete={handleDelete} />)
      )}

      {/* Edit Modal */}
      {editOpen && (
        <div className="modal-backdrop" onClick={() => setEditOpen(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <button className="modal-close" onClick={() => setEditOpen(false)}>
                <i className="ri-close-line" />
              </button>
              <h2 style={{ fontWeight: 800, fontSize: '1.125rem' }}>Edit profile</h2>
              <button className="btn btn-dark btn-sm" style={{ marginLeft: 'auto' }} onClick={handleEditSave}>
                Save
              </button>
            </div>
            <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 16 }}>
              {[
                { key: 'display_name', label: 'Display name' },
                { key: 'bio', label: 'Bio', multiline: true },
                { key: 'location', label: 'Location' },
                { key: 'website', label: 'Website' },
              ].map(field => (
                <div key={field.key} className="form-group">
                  <label>{field.label}</label>
                  {field.multiline ? (
                    <textarea
                      className="form-input"
                      value={editData[field.key] || ''}
                      onChange={e => setEditData(d => ({ ...d, [field.key]: e.target.value }))}
                      rows={3}
                      style={{ resize: 'vertical' }}
                    />
                  ) : (
                    <input
                      className="form-input"
                      value={editData[field.key] || ''}
                      onChange={e => setEditData(d => ({ ...d, [field.key]: e.target.value }))}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  )
}