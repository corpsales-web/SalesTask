import React, { useEffect, useState } from 'react'

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL

export default function TrainingCenter(){
  const [q, setQ] = useState('')
  const [feature, setFeature] = useState('')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)

  const load = async()=>{
    try{
      setLoading(true)
      const ps = new URLSearchParams(); if (q) ps.set('q', q); if (feature) ps.set('feature', feature)
      const res = await fetch(`${API}/api/training/modules${ps.toString()? ('?'+ps.toString()):''}`)
      const data = await res.json()
      setItems(Array.isArray(data.items)? data.items : [])
    }catch(e){ console.warn('training list', e) } finally{ setLoading(false) }
  }
  useEffect(()=>{ load() },[])

  const add = async()=>{
    const title = prompt('Title?')
    if (!title) return
    const type = prompt('Type? (pdf|video|link)','pdf')
    if (type==='pdf'){
      try{
        const f = document.createElement('input'); f.type='file'; f.accept='application/pdf';
        f.onchange = async()=>{
          const file = f.files?.[0]; if (!file) return
          const fd = new FormData(); fd.append('file', file); fd.append('title', title); fd.append('feature', feature||'general')
          const r = await fetch(`${API}/api/training/upload`, { method:'POST', body: fd })
          if(!r.ok) throw new Error('Upload failed')
          await load()
        }
        f.click()
      }catch(e){ alert('Upload failed') }
    } else {
      const url = prompt('URL?','https://')
      try{ await fetch(`${API}/api/training/modules`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ title, type, url, feature: feature||'general' }) }); await load() }catch(e){ alert('Add failed') }
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <input className="border rounded px-2 py-1" placeholder="Search modules" value={q} onChange={(e)=>setQ(e.target.value)} />
        <select className="border rounded p-1" value={feature} onChange={(e)=>setFeature(e.target.value)}>
          <option value="">All features</option>
          <option value="leads">Leads</option>
          <option value="inbox">Inbox</option>
          <option value="visual">Visual Studio</option>
          <option value="tasks">Tasks</option>
          <option value="hrms">HRMS</option>
          <option value="admin">Admin</option>
        </select>
        <button className="primary" onClick={load} disabled={loading}>{loading? 'Loading...' : 'Search'}</button>
        <button className="ghost" onClick={add}>Add Module</button>
      </div>
      <div className="grid gap-2">
        {items.map(m=> (
          <div key={m.id} className="border rounded p-2">
            <div className="font-medium text-sm">{m.title}</div>
            <div className="text-xs text-gray-600">{m.type} • {m.feature || 'general'} • {new Date(m.created_at).toLocaleString()}</div>
            <div className="mt-1">
              {(m.type==='pdf' || m.type==='link') && (
                <a className="text-blue-600 underline text-sm" href={m.url} target="_blank" rel="noreferrer">{m.type==='pdf'? 'Download PDF':'Open Link'}</a>
              )}
            </div>
          </div>
        ))}
        {(!items || items.length===0) && <div className="text-xs text-gray-600">No modules</div>}
      </div>
    </div>
  )
}
