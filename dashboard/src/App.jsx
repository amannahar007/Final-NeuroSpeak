import { useState, useEffect, useRef } from 'react'
import { io } from 'socket.io-client'
import EMGChart from './components/EMGChart'
import WordDisplay from './components/WordDisplay'
import ConnectionStatus from './components/ConnectionStatus'
import WordConfigTab from './components/WordConfigTab'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  
  const [connected, setConnected] = useState(false)
  const [espConnected, setEspConnected] = useState(false)
  const [wordHistory, setWordHistory] = useState([])
  
  // Idle Bounds
  const [idleConfig, setIdleConfig] = useState(null)
  
  // Recording State
  const [isRecording, setIsRecording] = useState(false)
  const [recordStats, setRecordStats] = useState(null)
  
  // Load initial idle config
  useEffect(() => {
    fetch('http://localhost:8000/words')
      .then(r => r.json())
      .then(data => {
        if(data.idle_ranges) {
          setIdleConfig(data.idle_ranges)
        }
      })
      .catch(e => console.error(e))
  }, [])

  const [chartData, setChartData] = useState({
    sensor1: [],
    sensor2: [],
    sensor3: []
  })
  
  const socketRef = useRef(null)
  
  const playAudioCue = (wordText) => {
    // 1. Play Oscillator Beep
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
      const oscillator = audioCtx.createOscillator()
      const gainNode = audioCtx.createGain()
      
      oscillator.type = 'sine'
      oscillator.frequency.setValueAtTime(880, audioCtx.currentTime) // A5 note
      
      gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.1)
      
      oscillator.connect(gainNode)
      gainNode.connect(audioCtx.destination)
      
      oscillator.start()
      oscillator.stop(audioCtx.currentTime + 0.1)
    } catch(e) { console.error("Audio beep failed", e) }

    // 2. Play OS Text To Speech
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel() // Cut off previous speech instantly
      const utterance = new SpeechSynthesisUtterance(wordText)
      utterance.rate = 1.1
      utterance.pitch = 1.05
      window.speechSynthesis.speak(utterance)
    }
  }
  
  useEffect(() => {
    socketRef.current = io('http://localhost:8000')
    
    socketRef.current.on('connect', () => {
      setConnected(true)
    })
    
    socketRef.current.on('disconnect', () => {
      setConnected(false)
      setEspConnected(false)
    })
    
    socketRef.current.on('esp_status', (data) => {
      setEspConnected(data.connected)
    })
    
    // Utilize monotonic counter instead of Clock Time to prevent vertical overlapping
    const frameCount = { current: 0 }
    
    socketRef.current.on('emg_data', (data) => {
      frameCount.current += 1
      // Sliced to 150 points for smooth ~30Hz viewing
      setChartData(prev => ({
        sensor1: [...prev.sensor1.slice(-150), { time: frameCount.current, value: data.v1 }],
        sensor2: [...prev.sensor2.slice(-150), { time: frameCount.current, value: data.v2 }],
        sensor3: [...prev.sensor3.slice(-150), { time: frameCount.current, value: data.v3 }]
      }))
    })
    
    socketRef.current.on('word_detected', (data) => {
      setWordHistory(prev => [{ word: data.word, timestamp: new Date().toLocaleTimeString() }, ...prev].slice(0, 50))
      playAudioCue(data.word)
    })
    
    socketRef.current.on('recording_stats', (stats) => {
      setRecordStats(stats)
      setIsRecording(false)
    })
    
    return () => {
      if (socketRef.current) socketRef.current.disconnect()
    }
  }, [])
  
  const handleStartRecording = () => {
    setIsRecording(true)
    setRecordStats(null)
    if (socketRef.current) socketRef.current.emit('start_recording')
  }

  const handleStopRecording = () => {
    if (socketRef.current) socketRef.current.emit('stop_recording')
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <ConnectionStatus connected={connected} espConnected={espConnected} />
      
      {/* Navigation Tabs */}
      <div className="flex justify-center space-x-4 mb-4">
        <button 
          onClick={() => setActiveTab('dashboard')}
          className={`px-6 py-2 rounded-full font-bold transition ${activeTab === 'dashboard' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
        >
          Real-time Dashboard
        </button>
        <button 
          onClick={() => setActiveTab('config')}
          className={`px-6 py-2 rounded-full font-bold transition ${activeTab === 'config' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
        >
          Words Configuration
        </button>
      </div>

      {activeTab === 'dashboard' ? (
        <>
          <WordDisplay history={wordHistory} />
          
          {/* Recording UI Controls */}
          <div className="mt-8 bg-gray-800 p-6 rounded-xl border border-gray-700 text-center">
            <h3 className="text-xl font-bold mb-4">High-Precision Recording</h3>
            {!isRecording ? (
              <button onClick={handleStartRecording} className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded-full font-bold text-lg animate-pulse transition">
                Start Recording
              </button>
            ) : (
              <button onClick={handleStopRecording} className="bg-gray-600 hover:bg-gray-500 text-white px-8 py-3 rounded-full font-bold text-lg transition">
                ⏹ Stop & Analyze
              </button>
            )}
            
            {recordStats && (
              <div className="mt-6 grid grid-cols-3 gap-4 text-left">
                {['v1', 'v2', 'v3'].map((ch, idx) => (
                  <div key={ch} className="bg-gray-900 p-4 rounded border border-gray-600">
                    <h4 className="text-blue-400 font-bold border-b border-gray-700 pb-2 mb-2">Sensor {idx + 1}</h4>
                    <p className="text-sm text-gray-300">Min: <span className="font-mono text-white">{recordStats[ch].min}</span></p>
                    <p className="text-sm text-gray-300">Max: <span className="font-mono text-white">{recordStats[ch].max}</span></p>
                    <p className="text-sm text-gray-300 mt-2 pt-2 border-t border-gray-700">Envelope (Avg): <span className="font-mono text-green-400 text-lg">{recordStats[ch].envelope}</span></p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 gap-6 mt-8">
            <EMGChart data={chartData.sensor1} title="Sensor 1: Jaw/Back Ear" color="#00f3ff" idleBounds={idleConfig?.v1} />
            <EMGChart data={chartData.sensor2} title="Sensor 2: Chin" color="#ff006e" idleBounds={idleConfig?.v2} />
            <EMGChart data={chartData.sensor3} title="Sensor 3: Temporal/Ear" color="#8b5cf6" idleBounds={idleConfig?.v3} />
          </div>
        </>
      ) : (
        <WordConfigTab />
      )}
    </div>
  )
}

export default App
