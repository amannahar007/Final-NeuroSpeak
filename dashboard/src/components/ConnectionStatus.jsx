export default function ConnectionStatus({ connected, espConnected }) {
  return (
    <div className="fixed top-4 right-4 flex space-x-2">
      <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
        connected 
          ? 'bg-green-500/20 text-green-400 border border-green-400' 
          : 'bg-red-500/20 text-red-400 border border-red-400'
      }`}>
        {connected ? '● Backend: UP' : '● Backend: DOWN'}
      </div>
      <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
        espConnected 
          ? 'bg-blue-500/20 text-blue-400 border border-blue-400' 
          : 'bg-yellow-500/20 text-yellow-500 border border-yellow-500'
      }`}>
        {espConnected ? '● ESP32: CONNECTED' : '● ESP32: WAITING'}
      </div>
    </div>
  )
}
