import Plot from 'react-plotly.js'

type Item = { category: string; value: number; metadata?: { display_name?: string; percentage?: number; cumulative?: number } }

type Props = { data: Item[] }

export default function ParetoChart({ data }: Props) {
  const labels = data.map(d => d.metadata?.display_name ?? d.category)
  const values = data.map(d => d.value)
  const cumulative = data.map(d => d.metadata?.cumulative ?? 0)

  return (
    <Plot
      data={[
        { x: labels, y: values, type: 'bar', name: 'Value', yaxis: 'y1' },
        { x: labels, y: cumulative, type: 'scatter', mode: 'lines+markers', name: 'Cumulative %', yaxis: 'y2' }
      ]}
      layout={{
        autosize: true,
        title: 'Pareto',
        margin: { t: 40, l: 40, r: 40, b: 100 },
        yaxis: { title: 'Value' },
        yaxis2: { title: 'Cumulative %', overlaying: 'y', side: 'right', range: [0, 100] },
        xaxis: { tickangle: -45 }
      }}
      style={{ width: '100%', height: 360 }}
      useResizeHandler
      config={{ displaylogo: false }}
    />
  )
}

