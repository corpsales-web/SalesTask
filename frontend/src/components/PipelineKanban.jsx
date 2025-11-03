import React, { useEffect, useState } from 'react'

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL
const STAGES = ['New','Qualified','Proposal','Won','Lost']

export default function PipelineKanban(){
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(false)

  const load = async()=>{
    try{
      setLoading(true)
      const res = await fetch(`${API}/api/leads?page=1&limit=200`)
      const data = await res.json()
      const items = Array.isArray(data.items)? data.items : (Array.isArray(data)? data : [])
      setLeads(items)
    }catch(e){ console.warn('pipeline load', e) } finally{ setLoading(false) }
  }
  useEffect(()=>{ load() },[])

  const updateStatus = async(id, status)=>{
    try{
      await fetch(`${API}/api/leads/${id}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ status }) })
      setLeads(prev=> prev.map(l=> l.id===id? {...l, status} : l))
      // notify
      try{ window.dispatchEvent(new CustomEvent('crm:notify', { detail: { title: 'Pipeline Update', message: `Moved lead to ${status}`, type: 'system', priority: 'low', channel: ['push'] } })) }catch{}
    }catch(e){ alert('Failed to update status') }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
      {STAGES.map(stage=> (
        <div key={stage} className="bg-white border rounded p-2 min-h-[300px]">
          <div className="font-semibold mb-2">{stage}</div>
          {(leads.filter(l=> (l.status||'New')===stage)).map(ld=> (
            <div key={ld.id} className="border rounded p-2 mb-2 bg-gray-50">
              <div className="font-medium text-sm truncate">{ld.name}</div>
              <div className="text-xs text-gray-600 truncate">{ld.phone||''} {ld.email? `• ${ld.email}`:''}</div>
              <div className="flex gap-1 mt-2">
                {STAGES.filter(s=> s!==stage).slice(0,2).map(s=> (
                  <button key={s} className="ghost text-xs" onClick={()=>updateStatus(ld.id, s)}>{s}</button>
                ))}
                <select className="ml-auto text-xs border rounded" value={stage} onChange={(e)=>updateStatus(ld.id, e.target.value)}>
                  {STAGES.map(s=> <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>
          ))}
          {loading && <div className="text-xs text-gray-500">Loading...</div>}
        </div>
      ))}
    </div>
  )
}
