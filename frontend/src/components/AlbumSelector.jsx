import React, { useEffect, useState } from 'react'

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL

export default function AlbumSelector({ projectId, value, onChange }){
  const [albums, setAlbums] = useState([])
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')

  const load = async()=>{
    try{
      const url = `${API}/api/albums${projectId? ('?project_id='+encodeURIComponent(projectId)) : ''}`
      const res = await fetch(url)
      const data = await res.json()
      setAlbums(Array.isArray(data.items)? data.items : [])
    }catch(e){ console.warn('albums list', e) }
  }
  useEffect(()=>{ load() }, [projectId])

  const add = async()=>{
    try{
      if (!projectId || !name.trim()) return
      const res = await fetch(`${API}/api/albums`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ project_id: projectId, name, description: desc }) })
      if (!res.ok) throw new Error('Create album failed')
      setName(''); setDesc(''); await load()
    }catch(e){ alert('Add album failed: '+(e.message||e)) }
  }

  return (
    <div className="flex items-center gap-2 w-full">
      <select className="border rounded p-1" value={value||''} onChange={(e)=> onChange && onChange(e.target.value)} disabled={!projectId}>
        <option value="">All Albums</option>
        {albums.map(a=> <option key={a.id} value={a.id}>{a.name}</option>)}
      </select>
      <div className="flex items-center gap-1">
        <input value={name} onChange={(e)=>setName(e.target.value)} placeholder="New album name" className="border rounded p-1 text-sm" disabled={!projectId} />
        <button className="ghost" onClick={add} disabled={!projectId}>Add</button>
      </div>
    </div>
  )
}
