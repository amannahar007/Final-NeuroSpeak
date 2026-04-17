import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts'

export default function EMGChart({ data, title, color }) {
  return (
    <div className="backdrop-blur-md bg-white/10 rounded-lg p-6 border border-white/20">
      <h3 className="text-lg font-semibold mb-4" style={{ color }}>{title}</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <XAxis 
            dataKey="time" 
            domain={['dataMin', 'dataMax']}
            hide
          />
          <YAxis domain={[0, 4095]} />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke={color} 
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
