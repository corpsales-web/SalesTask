import React, { useEffect, useState } from 'react'

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL

export default function HRMSPanel(){
  const [today, setToday] = useState({ checked_in: false, checkin_time: null, checkout_time: null })
  const [summary, setSummary] = useState([])
  const [loading, setLoading] = useState(false)

  const load = async()=>{
    try{
      setLoading(true)
      const r1 = await fetch(`${API}/api/hrms/today`)
      const d1 = await r1.json()
      setToday(d1||{})
      const r2 = await fetch(`${API}/api/hrms/summary?days=7`)
      const d2 = await r2.json()
      setSummary(Array.isArray(d2?.items)? d2.items : [])
    }catch(e){ console.warn('hrms load', e) } finally{ setLoading(false) }
  }
  useEffect(()=>{ load() },[])

  const checkin = async()=>{
    try{
      await fetch(`${API}/api/hrms/checkin`, { method:'POST' })
      await load()
      try{ window.dispatchEvent(new CustomEvent('crm:notify', { detail: { title: 'Checked In', message:'Attendance recorded', type:'hrms', priority:'low', channel:['push'] } })) }catch{}
    }catch{ alert('Check-in failed') }
  }
  const checkout = async()=>{
    try{
      await fetch(`${API}/api/hrms/checkout`, { method:'POST' })
      await load()
      try{ window.dispatchEvent(new CustomEvent('crm:notify', { detail: { title: 'Checked Out', message:'Good day!', type:'hrms', priority:'low', channel:['push'] } })) }catch{}
    }catch{ alert('Check-out failed') }
  }

  return (
    <div className="space-y-4">
      <div className="bg-white border rounded p-3 flex items-center gap-2">
        <div className="text-sm">Today: {today.checked_in? 'Checked-in' : 'Not checked-in'}</div>
        <button className="primary" onClick={checkin} disabled={today.checked_in}>Check-in</button>
        <button className="ghost" onClick={checkout} disabled={!today.checked_in || !!today.checkout_time}>Check-out</button>
        <div className="text-xs text-gray-600 ml-auto">In: {today.checkin_time? new Date(today.checkin_time).toLocaleTimeString(): '-'} • Out: {today.checkout_time? new Date(today.checkout_time).toLocaleTimeString():'-'}</div>
      </div>
      <div className="bg-white border rounded p-3">
        <div className="font-semibold mb-2 text-sm">Last 7 days</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          {summary.map(d=> (
            <div key={d.date} className="border rounded p-2">{d.date}: {d.checked_in? '✓' : '—'}</div>
          ))}
        </div>
      </div>
    </div>
  )
}
