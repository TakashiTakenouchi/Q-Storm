import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'

type AuthContextType = {
  token: string | null
  sessionId: string | null
  login: (token: string, sessionId?: string | null) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const [sessionId, setSessionId] = useState<string | null>(() => localStorage.getItem('session_id'))

  useEffect(() => {
    if (token) localStorage.setItem('token', token)
    else localStorage.removeItem('token')
  }, [token])

  useEffect(() => {
    if (sessionId) localStorage.setItem('session_id', sessionId)
    else localStorage.removeItem('session_id')
  }, [sessionId])

  const value = useMemo<AuthContextType>(() => ({
    token,
    sessionId,
    login: (t: string, sid?: string | null) => { setToken(t); if (sid) setSessionId(sid) },
    logout: () => { setToken(null); setSessionId(null) }
  }), [token, sessionId])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
