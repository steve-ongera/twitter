import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Avatar from '../components/Avatar'
import api from '../utils/api'
import { timeAgo } from '../utils/helpers'

export default function Messages() {
  const { username } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [conversations, setConversations] = useState([])
  const [messages, setMessages] = useState([])
  const [activeUser, setActiveUser] = useState(null)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef()

  useEffect(() => {
    api.getConversations().then(res => setConversations(res)).catch(() => {})
  }, [])

  useEffect(() => {
    if (username) {
      api.getUser(username).then(setActiveUser).catch(() => {})
      loadMessages(username)
    }
  }, [username])

  const loadMessages = async (uname) => {
    try {
      const res = await api.getMessages(uname)
      setMessages(res)
    } catch {}
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || !activeUser) return
    setLoading(true)
    try {
      const msg = await api.sendMessage({ recipient: activeUser.id, content: input })
      setMessages(prev => [...prev, msg])
      setInput('')
      if (!conversations.find(c => c.username === activeUser.username)) {
        setConversations(prev => [activeUser, ...prev])
      }
    } catch {}
    setLoading(false)
  }

  const openConversation = (u) => {
    setActiveUser(u)
    navigate(`/messages/${u.username}`)
    loadMessages(u.username)
  }

  return (
    <>
      <header className="feed-header">
        <h1>Messages</h1>
      </header>

      <div className="messages-layout" style={{ height: 'calc(100vh - 53px)' }}>
        {/* Conversation list */}
        <div className="conv-list">
          {conversations.length === 0 ? (
            <div className="empty-state" style={{ padding: 32 }}>
              <p>No conversations yet</p>
            </div>
          ) : (
            conversations.map(u => (
              <div
                key={u.id}
                className={`conv-item ${activeUser?.username === u.username ? 'active' : ''}`}
                onClick={() => openConversation(u)}
              >
                <Avatar user={u} size="md" />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 700, fontSize: '0.938rem' }}>
                    {u.display_name || u.username}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }} className="truncate">
                    @{u.username}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Chat area */}
        <div className="chat-area">
          {activeUser ? (
            <>
              <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 12 }}>
                <Avatar user={activeUser} size="md" />
                <div>
                  <div style={{ fontWeight: 700 }}>{activeUser.display_name || activeUser.username}</div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>@{activeUser.username}</div>
                </div>
              </div>

              <div className="chat-messages">
                {messages.map(msg => {
                  const isSent = msg.sender.username === user?.username
                  return (
                    <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', alignItems: isSent ? 'flex-end' : 'flex-start' }}>
                      <div className={`message-bubble ${isSent ? 'sent' : 'received'}`}>
                        {msg.content}
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: '2px 4px' }}>
                        {timeAgo(msg.created_at)}
                      </span>
                    </div>
                  )
                })}
                <div ref={bottomRef} />
              </div>

              <form className="chat-input-bar" onSubmit={sendMessage}>
                <input
                  className="chat-input"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder={`Message @${activeUser.username}`}
                />
                <button
                  className="btn btn-primary btn-sm"
                  type="submit"
                  disabled={!input.trim() || loading}
                >
                  <i className="ri-send-plane-fill" />
                </button>
              </form>
            </>
          ) : (
            <div className="empty-state" style={{ margin: 'auto' }}>
              <h3>Your messages</h3>
              <p>Select a conversation or start a new one.</p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}