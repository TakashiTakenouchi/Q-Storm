import { useRef, useState } from 'react'
import { uploadFile, UploadResult } from '../api/data'
import { tError } from '../i18n'

type Props = {
  onUploaded: (result: UploadResult) => void
  sessionId?: string | null
}

export default function DataUpload({ onUploaded, sessionId }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [datasetName, setDatasetName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onChoose = async () => {
    const file = inputRef.current?.files?.[0]
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const res = await uploadFile(file, sessionId ?? undefined, undefined, datasetName || undefined)
      onUploaded(res)
      setDatasetName('')
    } catch (err: any) {
      setError(tError(err?.response?.status, err?.response?.data?.detail))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <input
        placeholder="Dataset name (optional)"
        value={datasetName}
        onChange={(e) => setDatasetName(e.target.value)}
      />
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={(e) => {
          const f = e.target.files?.[0]
          if (f) {
            const base = f.name.replace(/\.[^/.]+$/, '')
            setDatasetName(base)
          }
        }}
      />
      <button onClick={onChoose} disabled={loading}>{loading ? 'Uploading…' : 'Upload'}</button>
      {error && <div style={{ color: 'crimson' }}>{error}</div>}
    </div>
  )
}
