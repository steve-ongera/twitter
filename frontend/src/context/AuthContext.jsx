import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchMe = useCallback(async () => {
    const { access } = api.getTokens()
    if (!access) { setLoading(false); return }
    try {
      const data = await api.me()
      setUser(data)
    } catch {
      api.clearTokens()
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchMe() }, [fetchMe])

  const login = async (credentials) => {
    const data = await api.login(credentials)
    api.setTokens(data.access, data.refresh)
    setUser(data.user)
    return data
  }

  const register = async (credentials) => {
    const data = await api.register(credentials)
    api.setTokens(data.access, data.refresh)
    setUser(data.user)
    return data
  }

  const logout = async () => {
    const { refresh } = api.getTokens()
    try { await api.logout(refresh) } catch {}
    api.clearTokens()
    setUser(null)
  }

  const updateUser = (updates) => setUser(prev => ({ ...prev, ...updates }))

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateUser, refetchUser: fetchMe }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)