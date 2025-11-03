import React, { useEffect, useState } from 'react'

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL

export default function TrainingCenter(){
  const [q, setQ] = useState('')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)

  const load = async()=>{
    try{
      setLoading(true)
      const res = await fetch(`${API}/api/training/modules${q? ('?q='+encodeURIComponent(q)) : ''}`)
      const data = await res.json()
      setItems(Array.isArray(data.items)? data.items : [])
    }catch(e){ console.warn('training list', e) } finally{ setLoading(false) }
  }
  useEffect(()=>{ load() },[])

  const add = async()=>{
    const title = prompt('Title?')
    if (!title) return
    const type = prompt('Type? (pdf|video|link)','link')
    const url = prompt('URL?','https://')
    try{
      await fetch(`${API}/api/training/modules`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ title, type, url }) })
      await load()
    }catch(e){ alert('Add failed') }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <input className="border rounded px-2 py-1" placeholder="Search modules" value={q} onChange={(e)=>setQ(e.target.value)} />
        <button className="primary" onClick={load}>Search</button>
        <button className="ghost" onClick={add}>Add Module</button>
      </div>
      <div className="grid gap-2">
        {items.map(m=> (
          <div key={m.id} className="border rounded p-2">
            <div className="font-medium text-sm">{m.title}</div>
            <div className="text-xs text-gray-600">{m.type} • {new Date(m.created_at).toLocaleString()}</div>
            <div className="mt-1"><a className="text-blue-600 underline text-sm" href={m.url} target="_blank" rel="noreferrer">Open</a></div>
          </div>
        ))}
        {(!items || items.length===0) && <div className="text-xs text-gray-600">No modules</div>}
      </div>
    </div>
  )
}
