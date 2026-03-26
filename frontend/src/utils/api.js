const BASE_URL = 'http://localhost:8000/api'

function getTokens() {
  return {
    access: localStorage.getItem('access_token'),
    refresh: localStorage.getItem('refresh_token'),
  }
}

function setTokens(access, refresh) {
  localStorage.setItem('access_token', access)
  if (refresh) localStorage.setItem('refresh_token', refresh)
}

function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

async function refreshAccessToken() {
  const { refresh } = getTokens()
  if (!refresh) throw new Error('No refresh token')
  const res = await fetch(`${BASE_URL}/auth/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })
  if (!res.ok) { clearTokens(); throw new Error('Session expired') }
  const data = await res.json()
  setTokens(data.access)
  return data.access
}

async function request(path, options = {}, retry = true) {
  const { access } = getTokens()
  const headers = { ...options.headers }
  if (access) headers['Authorization'] = `Bearer ${access}`
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })

  if (res.status === 401 && retry) {
    try {
      const newAccess = await refreshAccessToken()
      headers['Authorization'] = `Bearer ${newAccess}`
      const retried = await fetch(`${BASE_URL}${path}`, { ...options, headers })
      if (!retried.ok) {
        const err = await retried.json().catch(() => ({}))
        throw Object.assign(new Error('Request failed'), { data: err, status: retried.status })
      }
      return retried.status === 204 ? null : retried.json()
    } catch {
      clearTokens()
      window.location.href = '/login'
      throw new Error('Session expired')
    }
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw Object.assign(new Error('Request failed'), { data: err, status: res.status })
  }
  return res.status === 204 ? null : res.json()
}

const api = {
  get: (path) => request(path, { method: 'GET' }),
  post: (path, body) => request(path, {
    method: 'POST',
    body: body instanceof FormData ? body : JSON.stringify(body),
  }),
  patch: (path, body) => request(path, {
    method: 'PATCH',
    body: body instanceof FormData ? body : JSON.stringify(body),
  }),
  delete: (path) => request(path, { method: 'DELETE' }),

  // Auth
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  me: () => api.get('/auth/me/'),
  updateMe: (data) => request('/auth/me/', {
    method: 'PATCH',
    body: data instanceof FormData ? data : JSON.stringify(data),
  }),

  // Users
  getUser: (username) => api.get(`/users/${username}/`),
  followUser: (username) => api.post(`/users/${username}/follow/`),
  unfollowUser: (username) => api.post(`/users/${username}/unfollow/`),
  getUserTweets: (username, page = 1) => api.get(`/users/${username}/tweets/?page=${page}`),
  getUserLikes: (username, page = 1) => api.get(`/users/${username}/likes/?page=${page}`),
  getUserFollowers: (username) => api.get(`/users/${username}/followers/`),
  getUserFollowing: (username) => api.get(`/users/${username}/following/`),
  getSuggestions: () => api.get('/users/suggestions/'),
  searchUsers: (q) => api.get(`/users/?search=${encodeURIComponent(q)}`),

  // Tweets
  getFeed: (page = 1) => api.get(`/tweets/feed/?page=${page}`),
  getExplore: () => api.get('/tweets/explore/'),
  getTweet: (slug) => api.get(`/tweets/${slug}/`),
  getThread: (slug) => api.get(`/tweets/${slug}/thread/`),
  createTweet: (data) => request('/tweets/', {
    method: 'POST',
    body: data instanceof FormData ? data : JSON.stringify(data),
  }),
  deleteTweet: (slug) => api.delete(`/tweets/${slug}/`),
  likeTweet: (slug) => api.post(`/tweets/${slug}/like/`),
  bookmarkTweet: (slug) => api.post(`/tweets/${slug}/bookmark/`),
  retweetTweet: (slug) => api.post(`/tweets/${slug}/retweet/`),
  searchTweets: (q) => api.get(`/tweets/?search=${encodeURIComponent(q)}`),

  // Hashtags
  getTrendingHashtags: () => api.get('/hashtags/trending/'),
  getHashtagTweets: (slug, page = 1) => api.get(`/hashtags/${slug}/tweets/?page=${page}`),

  // Bookmarks
  getBookmarks: (page = 1) => api.get(`/bookmarks/?page=${page}`),
  clearBookmarks: () => api.delete('/bookmarks/clear_all/'),

  // Notifications
  getNotifications: (page = 1) => api.get(`/notifications/?page=${page}`),
  markAllRead: () => api.post('/notifications/mark_all_read/'),
  markRead: (id) => api.post(`/notifications/${id}/mark_read/`),
  getUnreadCount: () => api.get('/notifications/unread_count/'),

  // Messages
  getConversations: () => api.get('/messages/conversations/'),
  getMessages: (username) => api.get(`/messages/with_user/?username=${username}`),
  sendMessage: (data) => api.post('/messages/', data),

  // Search
  search: (q, type = 'all') => api.get(`/search/?q=${encodeURIComponent(q)}&type=${type}`),

  setTokens,
  clearTokens,
  getTokens,
}

export default api