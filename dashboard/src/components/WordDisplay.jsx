import { useEffect, useState } from 'react'

export default function WordDisplay({ history }) {
  const [flash, setFlash] = useState(false)
  
  const mostRecentWord = history.length > 0 ? history[0].word : '---'
  
  useEffect(() => {
    if (mostRecentWord !== '---') {
      setFlash(true)
      const timer = setTimeout(() => setFlash(false), 800)
      return () => clearTimeout(timer)
    }
  }, [history])
  
  return (
    <div className="text-center my-8">
      {/* Latest Glowing Word */}
      <div className={`transition-all duration-300 ${flash ? 'scale-110 opacity-100' : 'scale-100 opacity-80'}`}>
        <div className="text-7xl font-bold text-cyber-blue drop-shadow-[0_0_20px_rgba(0,243,255,0.8)]">
          {mostRecentWord}
        </div>
      </div>
      
      {/* Word Chronological History List */}
      {history.length > 0 && (
        <div className="mt-8 mx-auto max-w-sm text-left bg-gray-800/50 p-4 rounded-xl border border-gray-700/50 h-48 overflow-y-auto">
          <h4 className="text-sm text-gray-400 font-bold mb-2 uppercase flex items-center">
            <span className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>
            Detection Feed
          </h4>
          <ul className="space-y-2">
            {history.map((entry, idx) => (
              <li key={idx} className={`flex justify-between items-center px-3 py-2 rounded ${idx === 0 ? 'bg-blue-600/30' : 'bg-transparent text-gray-400'}`}>
                <span className={`font-bold ${idx === 0 ? 'text-blue-400 text-lg' : ''}`}>{entry.word}</span>
                <span className="text-xs font-mono">{entry.timestamp}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
