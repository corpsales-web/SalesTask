import React, { useEffect, useState } from 'react'

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL

export default function AdminSettings(){
  const [sla, setSla] = useState(300)
  const [waMode, setWaMode] = useState('stub')
  const [roles, setRoles] = useState([])
  const [saving, setSaving] = useState(false)

  const load = async()=>{
    try{
      const r = await fetch(`${API}/api/admin/settings`)
      const d = await r.json()
      if (d){ setSla(d.sla_minutes || 300); setWaMode(d.whatsapp_mode || 'stub') }
      const rr = await fetch(`${API}/api/admin/roles`)
      const dr = await rr.json()
      setRoles(Array.isArray(dr.items)? dr.items : [])
    }catch(e){ console.warn('admin settings', e) }
  }
  useEffect(()=>{ load() },[])

  const save = async()=>{
    try{ setSaving(true)
      await fetch(`${API}/api/admin/settings`, { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ sla_minutes: Number(sla)||0, whatsapp_mode: waMode }) })
      try{ window.dispatchEvent(new CustomEvent('crm:notify', { detail: { title: 'Settings Saved', message: 'Admin settings updated', type: 'system', priority:'low', channel:['push'] } })) }catch{}
    }catch(e){ alert('Save failed') } finally{ setSaving(false) }
  }

  return (
    <div className="space-y-4">
      <div className="bg-white border rounded p-3">
        <div className="font-semibold mb-2">SLA & WhatsApp</div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 items-center">
          <label className="text-sm">Reply SLA (minutes)</label>
          <input className="border rounded p-1" type="number" value={sla} onChange={(e)=>setSla(e.target.value)} />
          <div />
          <label className="text-sm">WhatsApp Mode</label>
          <select className="border rounded p-1" value={waMode} onChange={(e)=>setWaMode(e.target.value)}>
            <option value="stub">Stub</option>
            <option value="live">Live</option>
          </select>
          <div />
        </div>
        <div className="mt-2"><button className="primary" onClick={save} disabled={saving}>{saving? 'Saving...' : 'Save'}</button></div>
      </div>
      <div className="bg-white border rounded p-3">
        <div className="font-semibold mb-2">Roles</div>
        <div className="grid gap-2">
          {roles.map(r=> (<div key={r.id} className="border rounded p-2 text-sm">{r.name}</div>))}
          {roles.length===0 && <div className="text-xs text-gray-600">No roles</div>}
        </div>
      </div>
    </div>
  )
}
