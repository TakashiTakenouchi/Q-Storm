import { api } from './client'

export type TimeSeriesRequest = {
  session_id: number
  dataset_id?: number
  store?: string
  target_column: string
  aggregation?: 'daily' | 'weekly' | 'monthly'
  date_range?: [string, string]
}

export type TimeSeriesResponse = {
  timestamp: string[]
  series: { name: string; values: number[]; statistics?: { mean?: number; std?: number; min?: number; max?: number; trend?: string } }[]
}

export async function fetchTimeSeries(payload: TimeSeriesRequest): Promise<TimeSeriesResponse> {
  const res = await api.post('/v1/analysis/timeseries', payload)
  return res.data as TimeSeriesResponse
}

export type ParetoRequest = {
  session_id: number
  dataset_id?: number
  store?: string
  analysis_type?: 'product_category'
  period?: string
}

export type ParetoResponse = {
  data: { category: string; value: number; metadata?: { display_name?: string; percentage?: number; cumulative?: number } }[]
  total: number
  vital_few_threshold: number
}

export async function fetchPareto(payload: ParetoRequest): Promise<ParetoResponse> {
  const res = await api.post('/v1/analysis/pareto', payload)
  return res.data as ParetoResponse
}

export type HistogramRequest = { session_id: number; dataset_id?: number; column: string; bins?: number }
export type HistogramResponse = { bins: number[]; counts: number[] }

export async function fetchHistogram(payload: HistogramRequest): Promise<HistogramResponse> {
  const res = await api.post('/v1/analysis/histogram', payload)
  return res.data as HistogramResponse
}
