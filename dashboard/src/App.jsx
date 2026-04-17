import { useState, useEffect, useRef } from 'react'
import { io } from 'socket.io-client'
import EMGChart from './components/EMGChart'
import WordDisplay from './components/WordDisplay'
import ConnectionStatus from './components/ConnectionStatus'

function App() {
  const [connected, setConnected] = useState(false)
  const [detectedWord, setDetectedWord] = useState('---')
  const [chartData, setChartData] = useState({
    sensor1: [],
    sensor2: [],
    sensor3: []
  })
  const socketRef = useRef(null)
  
  useEffect(() => {
    // Initialize Socket.io connection
    socketRef.current = io('http://localhost:8000')
    
    socketRef.current.on('connect', () => {
      console.log('Socket.io connected')
      setConnected(true)
    })
    
    socketRef.current.on('disconnect', () => {
      console.log('Socket.io disconnected')
      setConnected(false)
    })
    
    socketRef.current.on('emg_data', (data) => {
      // Update chart data with rolling window (5 seconds @ 30Hz = ~150 points)
      setChartData(prev => ({
        sensor1: [...prev.sensor1.slice(-150), { time: Date.now(), value: data.v1 }],
        sensor2: [...prev.sensor2.slice(-150), { time: Date.now(), value: data.v2 }],
        sensor3: [...prev.sensor3.slice(-150), { time: Date.now(), value: data.v3 }]
      }))
    })
    
    socketRef.current.on('word_detected', (data) => {
      console.log('Word detected:', data.word)
      setDetectedWord(data.word)
    })
    
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect()
      }
    }
  }, [])
  
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <ConnectionStatus connected={connected} />
      <WordDisplay word={detectedWord} />
      <div className="grid grid-cols-1 gap-6 mt-8">
        <EMGChart data={chartData.sensor1} title="Sensor 1: Jaw/Back Ear" color="#00f3ff" />
        <EMGChart data={chartData.sensor2} title="Sensor 2: Chin" color="#ff006e" />
        <EMGChart data={chartData.sensor3} title="Sensor 3: Temporal/Ear" color="#8b5cf6" />
      </div>
    </div>
  )
}

export default App
