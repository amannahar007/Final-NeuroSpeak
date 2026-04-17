import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, ReferenceLine } from 'recharts'

export default function EMGChart({ data, title, color, idleBounds }) {
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
          <YAxis domain={['auto', 'auto']} />
          {idleBounds && (
            <>
              <ReferenceLine y={idleBounds.max} stroke="red" strokeDasharray="3 3"/>
              <ReferenceLine y={idleBounds.min} stroke="yellow" strokeDasharray="3 3"/>
            </>
          )}
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
