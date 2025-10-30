import React, { useEffect, useState } from 'react'

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL

export default function ProjectSelector({ value, onChange }){
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')

  const load = async()=>{
    try{ setLoading(true)
      const res = await fetch(`${API}/api/projects`)
      const data = await res.json()
      setProjects(Array.isArray(data.items)? data.items : [])
    }catch(e){ console.warn('projects list', e) } finally{ setLoading(false) }
  }
  useEffect(()=>{ load() },[])

  const addProject = async()=>{
    try{
      if (!name.trim()) return
      const res = await fetch(`${API}/api/projects`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ name, description: desc }) })
      if (!res.ok) throw new Error('Create failed')
      setName(''); setDesc(''); await load()
    }catch(e){ alert('Add project failed: '+ (e.message||e)) }
  }

  return (
    <div className="flex items-center gap-2 w-full">
      <select className="border rounded p-1" value={value||''} onChange={(e)=> onChange && onChange(e.target.value)}>
        <option value="">All Projects</option>
        {projects.map(p=> <option key={p.id} value={p.id}>{p.name}</option>)}
      </select>
      <div className="flex items-center gap-1">
        <input value={name} onChange={(e)=>setName(e.target.value)} placeholder="New project name" className="border rounded p-1 text-sm" />
        <button className="ghost" onClick={addProject}>Add</button>
      </div>
    </div>
  )
}
