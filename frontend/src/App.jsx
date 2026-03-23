import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'

import Layout from './components/Layout'
import Home from './pages/Home'
import Explore from './pages/Explore'
import Notifications from './pages/Notifications'
import Messages from './pages/Messages'
import Bookmarks from './pages/Bookmarks'
import Profile from './pages/Profile'
import TweetDetail from './pages/TweetDetail'
import Login from './pages/Login'
import Register from './pages/Register'
import HashtagPage from './pages/HashtagPage'
import SearchPage from './pages/SearchPage'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'

function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="loading-screen"><div className="spinner" /></div>
  return user ? children : <Navigate to="/login" replace />
}

function GuestRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="loading-screen"><div className="spinner" /></div>
  return user ? <Navigate to="/home" replace /> : children
}

export default function App() {
  return (
    <Routes>
      {/* Public auth routes */}
      <Route path="/login" element={<GuestRoute><Login /></GuestRoute>} />
      <Route path="/register" element={<GuestRoute><Register /></GuestRoute>} />

      {/* App layout routes */}
      <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
        <Route index element={<Navigate to="/home" replace />} />
        <Route path="home" element={<Home />} />
        <Route path="explore" element={<Explore />} />
        <Route path="notifications" element={<Notifications />} />
        <Route path="messages" element={<Messages />} />
        <Route path="messages/:username" element={<Messages />} />
        <Route path="bookmarks" element={<Bookmarks />} />
        <Route path="settings" element={<Settings />} />
        <Route path="search" element={<SearchPage />} />
        <Route path=":username" element={<Profile />} />
        <Route path=":username/status/:slug" element={<TweetDetail />} />
        <Route path="hashtag/:slug" element={<HashtagPage />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}