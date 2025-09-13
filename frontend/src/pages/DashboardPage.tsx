import { FormEvent, useMemo, useState } from 'react'
import DataUpload from '../components/DataUpload'
import TimeSeriesChart from '../components/TimeSeriesChart'
import ParetoChart from '../components/ParetoChart'
import HistogramChart from '../components/HistogramChart'
import { fetchTimeSeries, fetchPareto, fetchHistogram, TimeSeriesResponse } from '../api/analysis'
import { useAuth } from '../context/AuthContext'
import { listSessions, listDatasets, renameDataset, SessionInfo, DatasetInfo } from '../api/data'
import { tError } from '../i18n'

export default function DashboardPage() {
  const { sessionId: authSessionId } = useAuth()
  const [localSessionId, setLocalSessionId] = useState<string | null>(null)
  const [datasetId, setDatasetId] = useState<string | null>(null)
  const [sessions, setSessions] = useState<SessionInfo[]>([])
  const [datasets, setDatasets] = useState<DatasetInfo[]>([])
  const [renaming, setRenaming] = useState(false)
  const [renameValue, setRenameValue] = useState('')
  const [renameError, setRenameError] = useState<string | null>(null)
  const [columns, setColumns] = useState<string[]>([])
  const [store, setStore] = useState<string>('')
  const [targetColumn, setTargetColumn] = useState<string>('Total_Sales')
  const [histColumn, setHistColumn] = useState<string>('Total_Sales')
  const [aggregation, setAggregation] = useState<'daily' | 'weekly' | 'monthly'>('monthly')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [tsData, setTsData] = useState<TimeSeriesResponse | null>(null)
  const [paretoData, setParetoData] = useState<any | null>(null)
  const [histData, setHistData] = useState<any | null>(null)
  const sessionId = authSessionId ?? localSessionId
  const canRun = useMemo(() => !!sessionId && !!targetColumn, [sessionId, targetColumn])

  const onUploaded = (res: { session_id: string; dataset_id: string; columns: string[] }) => {
    setLocalSessionId(res.session_id)
    setDatasetId(res.dataset_id)
    setColumns(res.columns)
    if (res.columns.includes('Total_Sales')) setTargetColumn('Total_Sales')
    else setTargetColumn(res.columns[0])
    setHistColumn(res.columns[0])
    // Update selectors
    const sid = Number(res.session_id)
    listDatasets(sid).then(setDatasets).catch(() => {})
  }

  const runAnalysis = async (e: FormEvent) => {
    e.preventDefault()
    const sidStr = authSessionId ?? localSessionId
    if (!sidStr) return
    const sid = Number(sidStr)
    const did = datasetId ? Number(datasetId) : undefined
    setLoading(true)
    setError(null)
    try {
      const ts = await fetchTimeSeries({ session_id: sid, dataset_id: did, store: store || undefined, target_column: targetColumn, aggregation })
      const pa = await fetchPareto({ session_id: sid, dataset_id: did, store: store || undefined, analysis_type: 'product_category' })
      const hi = await fetchHistogram({ session_id: sid, dataset_id: did, column: histColumn, bins: 20 })
      setTsData(ts)
      setParetoData(pa)
      setHistData(hi)
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  // Load sessions for authenticated user
  React.useEffect(() => {
    if (authSessionId) {
      listSessions().then(setSessions).catch(() => {})
    }
  }, [authSessionId])

  // Load datasets when session changes
  React.useEffect(() => {
    if (sessionId) {
      listDatasets(Number(sessionId)).then(setDatasets).catch(() => setDatasets([]))
    } else {
      setDatasets([])
    }
  }, [sessionId])

  React.useEffect(() => {
    if (datasetId) {
      const current = datasets.find(d => String(d.id) === String(datasetId))
      if (current) setRenameValue(current.name)
    }
  }, [datasetId, datasets])

  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <section>
        <h2>Data Upload</h2>
        <DataUpload onUploaded={onUploaded} sessionId={sessionId ?? null} />
        {(authSessionId || localSessionId) && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 8 }}>
            <label>Session:</label>
            {authSessionId ? (
              <select value={sessionId ?? ''} onChange={e => { setLocalSessionId(e.target.value); setDatasetId(null) }}>
                {sessions.map(s => (
                  <option key={s.id} value={s.id}>{s.id} ({new Date(s.created_at).toLocaleString()})</option>
                ))}
              </select>
            ) : (
              <code>{localSessionId}</code>
            )}

            <label>Dataset:</label>
            <select value={datasetId ?? ''} onChange={e => { setDatasetId(e.target.value); setRenaming(false); setRenameError(null) }}>
              <option value="" disabled>Select dataset</option>
              {datasets.map(d => (
                <option key={d.id} value={d.id}>{d.name} ({new Date(d.created_at).toLocaleString()})</option>
              ))}
            </select>
            {datasetId && !renaming && (
              <button type="button" onClick={() => { setRenaming(true); setRenameError(null) }}>Rename</button>
            )}
            {datasetId && renaming && (
              <span style={{ display: 'inline-flex', gap: 6, alignItems: 'center' }}>
                <input value={renameValue} onChange={(e) => setRenameValue(e.target.value)} />
                <button type="button" onClick={async () => {
                  try {
                    setRenameError(null)
                    await renameDataset(Number(datasetId), renameValue)
                    if (sessionId) {
                      const list = await listDatasets(Number(sessionId))
                      setDatasets(list)
                    }
                    setRenaming(false)
                  } catch (err: any) {
                    setRenameError(tError(err?.response?.status, err?.response?.data?.detail))
                  }
                }}>Save</button>
                <button type="button" onClick={() => { setRenaming(false); setRenameError(null) }}>Cancel</button>
                {renameError && <span style={{ color: 'crimson', marginLeft: 8 }}>{renameError}</span>}
              </span>
            )}
          </div>
        )}
      </section>

      <section>
        <h2>Analysis Inputs</h2>
        <form onSubmit={runAnalysis} style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center' }}>
          <input placeholder="Store (optional)" value={store} onChange={(e) => setStore(e.target.value)} />
          <select value={targetColumn} onChange={(e) => setTargetColumn(e.target.value)}>
            {columns.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={histColumn} onChange={(e) => setHistColumn(e.target.value)}>
            {columns.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={aggregation} onChange={(e) => setAggregation(e.target.value as any)}>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
          <button type="submit" disabled={!canRun || loading}>{loading ? 'Running…' : 'Run Analysis'}</button>
          {error && <span style={{ color: 'crimson' }}>{error}</span>}
        </form>
      </section>

      {tsData && (
        <section>
          <h2>Time Series</h2>
          <TimeSeriesChart timestamps={tsData.timestamp} values={tsData.series[0]?.values ?? []} name={tsData.series[0]?.name} />
        </section>
      )}

      {paretoData && (
        <section>
          <h2>Pareto</h2>
          <ParetoChart data={paretoData.data} />
        </section>
      )}

      {histData && (
        <section>
          <h2>Histogram</h2>
          <HistogramChart bins={histData.bins} counts={histData.counts} />
        </section>
      )}
    </div>
  )
}
