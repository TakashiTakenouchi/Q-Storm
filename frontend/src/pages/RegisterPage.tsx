import { FormEvent, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { registerApi } from '../api/auth'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [ok, setOk] = useState<string | null>(null)
  const [touchedUser, setTouchedUser] = useState(false)
  const [touchedEmail, setTouchedEmail] = useState(false)
  const [touchedPass, setTouchedPass] = useState(false)

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  const usernameError = !username.trim() ? 'Username is required' : null
  const emailError = !email.trim() ? 'Email is required' : (!emailRegex.test(email) ? 'Enter a valid email' : null)
  const passwordError = !password ? 'Password is required' : (password.length < 8 ? 'Password must be at least 8 characters' : null)
  const formInvalid = useMemo(() => Boolean(usernameError || emailError || passwordError), [usernameError, emailError, passwordError])

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setTouchedUser(true)
    setTouchedEmail(true)
    setTouchedPass(true)
    if (formInvalid) return
    setError(null)
    setOk(null)
    setLoading(true)
    try {
      await registerApi({ username, email, password, full_name: fullName || undefined })
      setOk('Account created. You can now log in.')
      setTimeout(() => navigate('/'), 800)
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 420 }}>
      <h2>Register</h2>
      <form onSubmit={onSubmit} style={{ display: 'grid', gap: 8 }}>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          onBlur={() => setTouchedUser(true)}
          aria-invalid={touchedUser && !!usernameError}
        />
        {touchedUser && usernameError && <div style={{ color: 'crimson' }}>{usernameError}</div>}
        <input
          placeholder="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onBlur={() => setTouchedEmail(true)}
          aria-invalid={touchedEmail && !!emailError}
        />
        {touchedEmail && emailError && <div style={{ color: 'crimson' }}>{emailError}</div>}
        <input placeholder="Full Name (optional)" value={fullName} onChange={(e) => setFullName(e.target.value)} />
        <input
          placeholder="Password (min 8 chars)"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onBlur={() => setTouchedPass(true)}
          aria-invalid={touchedPass && !!passwordError}
        />
        {touchedPass && passwordError && <div style={{ color: 'crimson' }}>{passwordError}</div>}
        <button type="submit" disabled={loading || formInvalid}>{loading ? 'Creating…' : 'Create Account'}</button>
        {error && <div style={{ color: 'crimson' }}>{error}</div>}
        {ok && <div style={{ color: 'green' }}>{ok}</div>}
      </form>
    </div>
  )
}
