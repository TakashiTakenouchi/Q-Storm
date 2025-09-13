import { api } from './client'

export type LoginResult = { access_token: string; session_id?: string }

export async function loginApi(username: string, password: string): Promise<LoginResult> {
  const body = new URLSearchParams()
  body.set('username', username)
  body.set('password', password)
  const res = await api.post('/v1/auth/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return { access_token: res.data.access_token as string, session_id: res.data.session_id as (string | undefined) }
}

export type RegisterInput = {
  username: string
  email: string
  password: string
  full_name?: string
}

export async function registerApi(input: RegisterInput) {
  const res = await api.post('/v1/users/register', input)
  return res.data
}
