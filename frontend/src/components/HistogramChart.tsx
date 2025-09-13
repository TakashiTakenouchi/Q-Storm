import Plot from 'react-plotly.js'

type Props = { bins: number[]; counts: number[] }

export default function HistogramChart({ bins, counts }: Props) {
  // Plotly histogram wants bin edges; we plot as bar chart for explicit control
  const centers: number[] = []
  for (let i = 0; i < bins.length - 1; i++) centers.push((bins[i] + bins[i + 1]) / 2)

  return (
    <Plot
      data={[{ x: centers, y: counts, type: 'bar', name: 'Counts' }]}
      layout={{ autosize: true, title: 'Histogram', margin: { t: 40, l: 40, r: 20, b: 40 } }}
      style={{ width: '100%', height: 300 }}
      useResizeHandler
      config={{ displaylogo: false }}
    />
  )
}

