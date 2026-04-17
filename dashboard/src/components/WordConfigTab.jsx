import { useState, useEffect } from 'react'

export default function WordConfigTab() {
  const [words, setWords] = useState([])
  const [idleRanges, setIdleRanges] = useState({
    v1: { min: -912, max: 854 },
    v2: { min: -514, max: 518 },
    v3: { min: -577, max: 584 }
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // New word form state
  const [newWord, setNewWord] = useState('')
  const [newPriority, setNewPriority] = useState(10)
  const [newConditions, setNewConditions] = useState([{ sensor: 'v1', operator: '>', value: 2000 }])

  const loadWords = async () => {
    try {
      setLoading(true)
      const res = await fetch('http://localhost:8000/words')
      const data = await res.json()
      setWords(data.words || [])
      if (data.idle_ranges) {
        setIdleRanges(data.idle_ranges)
      }
      setError(null)
    } catch (err) {
      setError('Failed to fetch configuration')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadWords()
  }, [])

  const handleIdleChange = (sensor, field, val) => {
    setIdleRanges({
      ...idleRanges,
      [sensor]: {
        ...idleRanges[sensor],
        [field]: Number(val)
      }
    })
  }

  const handleSaveIdle = async () => {
    await saveToServer(idleRanges, words)
  }

  const handleAddCondition = () => {
    setNewConditions([...newConditions, { sensor: 'v1', operator: '>', value: 2000 }])
  }

  const handleConditionChange = (index, field, val) => {
    const updated = [...newConditions]
    if (field === 'value') val = Number(val)
    updated[index][field] = val
    setNewConditions(updated)
  }

  const handleRemoveCondition = (index) => {
    setNewConditions(newConditions.filter((_, i) => i !== index))
  }

  const handleDeleteWord = async (indexToDelete) => {
    const updatedWords = words.filter((_, i) => i !== indexToDelete)
    await saveToServer(idleRanges, updatedWords)
  }

  const handleSaveNewWord = async () => {
    if (!newWord.trim()) return
    const wordObj = {
      word: newWord.toUpperCase(),
      priority: Number(newPriority),
      conditions: newConditions
    }
    const updatedWords = [...words, wordObj]
    await saveToServer(idleRanges, updatedWords)
    
    // Reset form
    setNewWord('')
    setNewPriority(10)
    setNewConditions([{ sensor: 'v1', operator: '>', value: 2000 }])
  }

  const saveToServer = async (idleData, wordsData) => {
    try {
      setLoading(true)
      const res = await fetch('http://localhost:8000/words', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idle_ranges: idleData, words: wordsData })
      })
      if (!res.ok) throw new Error("Failed saving")
      const data = await res.json()
      setWords(data.words || [])
      if (data.idle_ranges) setIdleRanges(data.idle_ranges)
    } catch (err) {
      setError('Failed to save configuration')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-800 rounded-xl mt-8">
      <h2 className="text-2xl font-bold mb-6 text-white">System Configuration</h2>
      
      {error && <div className="bg-red-500/20 text-red-400 p-4 rounded mb-6">{error}</div>}
      
      {/* Idle Threshold Ranges */}
      <div className="bg-gray-900 border border-gray-700 p-6 rounded-lg mb-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-yellow-400">Idle Noise Thresholds</h3>
          <button 
            onClick={handleSaveIdle}
            className="bg-yellow-600 hover:bg-yellow-500 px-4 py-2 rounded text-white font-bold transition"
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Sync Idle Bands'}
          </button>
        </div>
        <p className="text-gray-400 text-sm mb-4">
          If all three sensors fall strictly between these Min/Max numbers concurrently, the backend assumes the user is idle and permanently halts Firebase network synchronization to save costs/bandwidth.
        </p>
        <div className="grid grid-cols-3 gap-4">
          {['v1', 'v2', 'v3'].map((sensor) => (
            <div key={sensor} className="bg-gray-800 p-4 rounded border border-gray-600">
              <h4 className="font-bold text-blue-300 uppercase mb-2">{sensor}</h4>
              <div className="space-y-2">
                <div>
                  <label className="block text-xs text-gray-500">Minimum Bounds</label>
                  <input 
                    type="number"
                    value={idleRanges[sensor]?.min || 0}
                    onChange={(e) => handleIdleChange(sensor, 'min', e.target.value)}
                    className="w-full bg-gray-900 border border-gray-600 text-white rounded p-1 font-mono text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Maximum Bounds</label>
                  <input 
                    type="number"
                    value={idleRanges[sensor]?.max || 0}
                    onChange={(e) => handleIdleChange(sensor, 'max', e.target.value)}
                    className="w-full bg-gray-900 border border-gray-600 text-white rounded p-1 font-mono text-sm"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Existing Words List */}
      <div className="mb-10">
        <h3 className="text-xl font-semibold mb-4 text-gray-300">Active Triggers</h3>
        {loading && words.length === 0 ? (
          <p className="text-gray-400">Loading...</p>
        ) : (
          <div className="space-y-4">
            {words.map((w, idx) => (
              <div key={idx} className="flex justify-between items-center bg-gray-700 p-4 rounded-lg">
                <div>
                  <span className="font-bold text-lg text-blue-400">{w.word}</span>
                  <span className="ml-3 text-sm text-gray-400">Priority: {w.priority}</span>
                  <div className="mt-2 text-sm text-gray-300 space-x-2">
                    {w.conditions.map((c, cdx) => (
                      <span key={cdx} className="bg-gray-800 px-2 py-1 rounded">
                        {c.sensor} {c.operator} {c.value}
                      </span>
                    ))}
                  </div>
                </div>
                <button 
                  onClick={() => handleDeleteWord(idx)}
                  className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded transition"
                >
                  Delete
                </button>
              </div>
            ))}
            {words.length === 0 && <p className="text-gray-400">No words configured.</p>}
          </div>
        )}
      </div>

      {/* Add New Word Form */}
      <div className="bg-gray-900 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-semibold mb-4 text-green-400">Add New Word</h3>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Word Text</label>
            <input 
              className="w-full bg-gray-800 text-white border border-gray-600 rounded p-2"
              value={newWord}
              onChange={e => setNewWord(e.target.value)}
              placeholder="e.g. HELP"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Priority (Lower = Checked First)</label>
            <input 
              type="number"
              className="w-full bg-gray-800 text-white border border-gray-600 rounded p-2"
              value={newPriority}
              onChange={e => setNewPriority(e.target.value)}
            />
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm text-gray-400 mb-2">Conditions (ALL must be true)</label>
          {newConditions.map((cond, idx) => (
            <div key={idx} className="flex space-x-2 mb-2 items-center">
              <select 
                className="bg-gray-800 text-white border border-gray-600 rounded p-2 w-1/4"
                value={cond.sensor}
                onChange={e => handleConditionChange(idx, 'sensor', e.target.value)}
              >
                <option value="v1">v1 (Jaw/Back Ear)</option>
                <option value="v2">v2 (Chin)</option>
                <option value="v3">v3 (Temporal/Ear)</option>
              </select>
              
              <select 
                className="bg-gray-800 text-white border border-gray-600 rounded p-2 w-1/4"
                value={cond.operator}
                onChange={e => handleConditionChange(idx, 'operator', e.target.value)}
              >
                <option value=">">&gt;</option>
                <option value="<">&lt;</option>
                <option value=">=">&gt;=</option>
                <option value="<=">&lt;=</option>
                <option value="==">==</option>
                <option value="!=">!=</option>
              </select>
              
              <input 
                type="number"
                className="bg-gray-800 text-white border border-gray-600 rounded p-2 w-1/3"
                value={cond.value}
                onChange={e => handleConditionChange(idx, 'value', e.target.value)}
              />
              
              <button 
                onClick={() => handleRemoveCondition(idx)}
                className="bg-red-500 hover:bg-red-600 text-white p-2 rounded"
              >
                X
              </button>
            </div>
          ))}
          <button 
            onClick={handleAddCondition}
            className="text-blue-400 text-sm hover:underline mt-1"
          >
            + Add Another Condition
          </button>
        </div>

        <button 
          onClick={handleSaveNewWord}
          className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg mt-2 transition"
          disabled={!newWord.trim() || loading}
        >
          {loading ? 'Saving...' : 'Save New Word'}
        </button>
      </div>
    </div>
  )
}
