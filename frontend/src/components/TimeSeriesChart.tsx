import Plot from 'react-plotly.js'

type Props = {
  timestamps: string[]
  values: number[]
  name?: string
}

export default function TimeSeriesChart({ timestamps, values, name }: Props) {
  return (
    <Plot
      data={[{ x: timestamps, y: values, type: 'scatter', mode: 'lines+markers', name: name ?? 'Series' }]}
      layout={{ autosize: true, title: name ?? 'Time Series', margin: { t: 40, l: 40, r: 20, b: 40 } }}
      style={{ width: '100%', height: 360 }}
      useResizeHandler
      config={{ displaylogo: false }}
    />
  )
}

