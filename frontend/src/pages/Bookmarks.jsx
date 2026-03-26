import { useState, useEffect } from 'react'
import TweetCard from '../components/TweetCard'
import api from '../utils/api'

export default function Bookmarks() {
  const [bookmarks, setBookmarks] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchBookmarks = async () => {
    try {
      const res = await api.getBookmarks()
      setBookmarks(res.results || res)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchBookmarks() }, [])

  const clearAll = async () => {
    if (!window.confirm('Clear all bookmarks?')) return
    try {
      await api.clearBookmarks()
      setBookmarks([])
    } catch {}
  }

  const handleDelete = (id) => {
    setBookmarks(prev => prev.filter(b => b.tweet?.id !== id))
  }

  return (
    <>
      <header className="feed-header">
        <h1>Bookmarks</h1>
        {bookmarks.length > 0 && (
          <button
            className="btn btn-outline btn-sm"
            style={{ marginLeft: 'auto' }}
            onClick={clearAll}
          >
            Clear all
          </button>
        )}
      </header>

      {loading ? (
        <div className="empty-state"><div className="spinner" style={{ margin: '0 auto' }} /></div>
      ) : bookmarks.length === 0 ? (
        <div className="empty-state">
          <h3>Save tweets for later</h3>
          <p>Bookmark tweets to easily find them again in the future.</p>
        </div>
      ) : (
        bookmarks.map(b => (
          b.tweet && <TweetCard key={b.id} tweet={b.tweet} onDelete={handleDelete} />
        ))
      )}
    </>
  )
}