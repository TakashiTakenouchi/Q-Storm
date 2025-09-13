import { api } from './client'

export type UploadResult = {
  session_id: string
  dataset_id: string
  rows: number
  columns: string[]
  preview: Record<string, unknown>[]
}

export async function uploadFile(file: File, existingSessionId?: string, sheetName?: string, datasetName?: string): Promise<UploadResult> {
  const form = new FormData()
  form.append('file', file)
  if (existingSessionId) form.append('session_id', existingSessionId)
  if (sheetName) form.append('sheet_name', sheetName)
  if (datasetName) form.append('name', datasetName)
  const res = await api.post('/v1/data/upload', form)
  return res.data as UploadResult
}

export type SessionInfo = { id: number; created_at: string; expires_at?: string | null }
export async function listSessions(): Promise<SessionInfo[]> {
  const res = await api.get('/v1/data/sessions')
  return res.data as SessionInfo[]
}

export type DatasetInfo = { id: number; name: string; created_at: string; path: string }
export async function listDatasets(sessionId: number): Promise<DatasetInfo[]> {
  const res = await api.get('/v1/data/datasets', { params: { session_id: sessionId } })
  return res.data as DatasetInfo[]
}

export async function renameDataset(datasetId: number, name: string): Promise<{ id: number; name: string }> {
  const res = await api.patch(`/v1/data/datasets/${datasetId}`, { name })
  return res.data as { id: number; name: string }
}
