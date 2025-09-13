import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { loginApi } from '../api/auth'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [touchedUser, setTouchedUser] = useState(false)
  const [touchedPass, setTouchedPass] = useState(false)

  const usernameError = !username.trim() ? 'Username is required' : null
  const passwordError = !password ? 'Password is required' : null
  const formInvalid = Boolean(usernameError || passwordError)

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setTouchedUser(true)
    setTouchedPass(true)
    setError(null)
    setLoading(true)
    try {
      const { access_token, session_id } = await loginApi(username, password)
      login(access_token, session_id ?? null)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 360 }}>
      <h2>Login</h2>
      <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          onBlur={() => setTouchedUser(true)}
          aria-invalid={touchedUser && !!usernameError}
        />
        {touchedUser && usernameError && <div style={{ color: 'crimson' }}>{usernameError}</div>}
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onBlur={() => setTouchedPass(true)}
          aria-invalid={touchedPass && !!passwordError}
        />
        {touchedPass && passwordError && <div style={{ color: 'crimson' }}>{passwordError}</div>}
        <button type="submit" disabled={loading || formInvalid}>{loading ? 'Logging in…' : 'Login'}</button>
        {error && <div style={{ color: 'crimson' }}>{error}</div>}
      </form>
      <p style={{ opacity: 0.8, marginTop: 8 }}>
        New here? <Link to="/register">Create an account</Link>.
      </p>
    </div>
  )
}
