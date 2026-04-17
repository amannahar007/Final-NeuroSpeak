import { useEffect, useState } from 'react'

export default function WordDisplay({ word }) {
  const [flash, setFlash] = useState(false)
  
  useEffect(() => {
    if (word !== '---') {
      setFlash(true)
      const timer = setTimeout(() => setFlash(false), 800)
      return () => clearTimeout(timer)
    }
  }, [word])
  
  return (
    <div className={`text-center my-12 transition-all duration-300 ${flash ? 'scale-110 opacity-100' : 'scale-100 opacity-80'}`}>
      <div className="text-8xl font-bold text-cyber-blue drop-shadow-[0_0_20px_rgba(0,243,255,0.8)]">
        {word}
      </div>
    </div>
  )
}
