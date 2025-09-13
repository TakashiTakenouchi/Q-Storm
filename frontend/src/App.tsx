import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'

export default function App() {
  const { token, logout } = useAuth()
  const navigate = useNavigate()

  const onLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', margin: 16 }}>
      <header style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16 }}>
        <h1 style={{ margin: 0, fontSize: 20 }}>Q-Storm Platform</h1>
        <nav style={{ display: 'flex', gap: 12 }}>
          <Link to="/">Login</Link>
          <Link to="/register">Register</Link>
          <Link to="/dashboard">Dashboard</Link>
        </nav>
        <div style={{ marginLeft: 'auto' }}>
          {token ? <button onClick={onLogout}>Logout</button> : null}
        </div>
      </header>
      <Outlet />
    </div>
  )
}
