import React, { useEffect, useState } from 'react'

const API = process.env.REACT_APP_BACKEND_URL || ''

export default function LeadWhatsAppTimeline({ leadId, limit=10 }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(()=>{ if (leadId) load() }, [leadId])

  const load = async () => {
    try {
      setLoading(true)
      setError('')
      const res = await fetch(`${API}/api/whatsapp/lead_timeline/${leadId}?limit=${limit}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setItems(Array.isArray(data.items) ? data.items : [])
    } catch (e) {
      setError(e.message)
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  if (!leadId) return null

  return (
    <div className="mt-3 p-3 border rounded-lg bg-gray-50">
      <div className="flex justify-between items-center mb-2">
        <div className="font-semibold">WhatsApp Timeline (last {limit})</div>
        <button className="text-sm underline" onClick={load} disabled={loading}>{loading ? 'Loading...' : 'Refresh'}</button>
      </div>
      {error && <div className="text-red-600 text-sm mb-2">{error}</div>}
      {items.length === 0 ? (
        <div className="text-sm text-gray-600">No messages linked to this lead yet.</div>
      ) : (
        <div className="space-y-2 max-h-64 overflow-auto">
          {items.map((m)=>{
            const ts = m.timestamp ? new Date(m.timestamp).toLocaleString() : ''
            const dir = m.direction === 'inbound' ? 'In' : 'Out'
            return (
              <div key={m.id} className="p-2 bg-white border rounded">
                <div className="flex justify-between text-xs text-gray-500">
                  <div>{dir}</div>
                  <div>{ts}</div>
                </div>
                <div className="text-sm whitespace-pre-wrap mt-1">{m.text || `[${m.type}]`}</div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
