import React, { useState } from 'react'

export default function OpsSmoke() {
  const BASE = String(process.env.REACT_APP_BACKEND_URL || '').replace(/\/$/, '')
  const [log, setLog] = useState([])
  const [leadId, setLeadId] = useState('')
  const [taskId, setTaskId] = useState('')
  const [loading, setLoading] = useState(false)

  const write = (msg) => setLog((prev) => [...prev, `${new Date().toLocaleTimeString()} - ${msg}`])

  const get = async (path) => {
    const res = await fetch(`${BASE}/api${path}`)
    if (!res.ok) throw new Error(`GET ${path} -> ${res.status}`)
    return res.json()
  }
  const post = async (path, data) => {
    const res = await fetch(`${BASE}/api${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data || {})
    })
    if (!res.ok) throw new Error(`POST ${path} -> ${res.status}`)
    return res.json()
  }
  const del = async (path) => {
    const res = await fetch(`${BASE}/api${path}`, { method: 'DELETE' })
    if (!res.ok) throw new Error(`DELETE ${path} -> ${res.status}`)
    return res.json()
  }
  const put = async (path, data) => {
    const res = await fetch(`${BASE}/api${path}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data || {})
    })
    if (!res.ok) throw new Error(`PUT ${path} -> ${res.status}`)
    return res.json()
  }

  const runHealth = async () => {
    try {
      setLoading(true)
      const data = await get('/health')
      write(`Health OK: service=${data.service}, time=${data.time}`)
    } catch (e) {
      write(`Health FAIL: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  const runLeads = async () => {
    try {
      setLoading(true)
      // Create
      const created = await post('/leads', { name: `Smoke Lead ${Date.now()}` })
      const id = created?.lead?.id
      setLeadId(id)
      write(`Lead created: ${id}`)
      // List
      const list = await get('/leads')
      write(`Leads list OK: count=${Array.isArray(list.items) ? list.items.length : 'n/a'}`)
      // Update
      await put(`/leads/${id}`, { status: 'Contacted', notes: 'Updated by smoke test' })
      write(`Lead updated: ${id}`)
      // Delete
      await del(`/leads/${id}`)
      write(`Lead deleted: ${id}`)
      setLeadId('')
    } catch (e) {
      write(`Leads flow FAIL: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  const runTasks = async () => {
    try {
      setLoading(true)
      // Create
      const created = await post('/tasks', { title: `Smoke Task ${Date.now()}` })
      const id = created?.task?.id
      setTaskId(id)
      write(`Task created: ${id}`)
      // List
      const list = await get('/tasks')
      write(`Tasks list OK: count=${Array.isArray(list.items) ? list.items.length : 'n/a'}`)
      // Update
      await put(`/tasks/${id}`, { status: 'In Progress' })
      write(`Task updated: ${id}`)
      // Delete
      await del(`/tasks/${id}`)
      write(`Task deleted: ${id}`)
      setTaskId('')
    } catch (e) {
      write(`Tasks flow FAIL: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{padding: 16, maxWidth: 900, margin: '40px auto', fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto'}}>
      <h1>CRM Ops Smoke</h1>
      <p>Backend: <code>{BASE || '(REACT_APP_BACKEND_URL not set)'}</code></p>
      <div style={{display:'flex', gap:8, flexWrap:'wrap', margin:'12px 0'}}>
        <button onClick={runHealth} disabled={loading} style={{padding:'8px 12px'}}>Test Health</button>
        <button onClick={runLeads} disabled={loading} style={{padding:'8px 12px'}}>Leads Round-Trip</button>
        <button onClick={runTasks} disabled={loading} style={{padding:'8px 12px'}}>Tasks Round-Trip</button>
      </div>
      <div style={{marginTop:12, padding:12, border:'1px solid #ddd', borderRadius:8, background:'#fafafa'}}>
        <h3>Log</h3>
        <pre style={{whiteSpace:'pre-wrap'}}>
{log.join('\n')}
        </pre>
      </div>
    </div>
  )
}