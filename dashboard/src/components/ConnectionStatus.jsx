export default function ConnectionStatus({ connected }) {
  return (
    <div className="fixed top-4 right-4">
      <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
        connected 
          ? 'bg-green-500/20 text-green-400 border border-green-400' 
          : 'bg-red-500/20 text-red-400 border border-red-400'
      }`}>
        {connected ? '● CONNECTED' : '● DISCONNECTED'}
      </div>
    </div>
  )
}
