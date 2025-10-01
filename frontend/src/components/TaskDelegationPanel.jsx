import React, { useState } from 'react'

// Minimal, stable Task Delegation panel wired to backend Tasks API
// Uses only environment variable for backend URL per platform rules
export default function TaskDelegationPanel() {
  const BASE = String(process.env.REACT_APP_BACKEND_URL || '').replace(/\/$/, '')

  const [title, setTitle] = useState('')
  const [assignee, setAssignee] = useState('')
  const [due, setDue] = useState('')
  const [loading, setLoading] = useState(false)
  const [log, setLog] = useState([])

  const write = (m) => setLog((p) => [...p, `${new Date().toLocaleTimeString()} - ${m}`])

  const createTask = async (e) => {
    e.preventDefault()
    if (!title.trim()) return
    try {
      setLoading(true)
      const res = await fetch(`${BASE}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title.trim(), assignee: assignee || undefined, due_date: due || undefined })
      })
      if (!res.ok) throw new Error(`Create failed (${res.status})`)
      const data = await res.json()
      write(`Created task: ${data?.task?.id || 'unknown'}`)
      setTitle('')
      setAssignee('')
      setDue('')
    } catch (err) {
      write(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={createTask} className="flex flex-col sm:flex-row gap-2">
        <input
          className="border rounded px-3 py-2 flex-1"
          placeholder="Quick task title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input
          className="border rounded px-3 py-2 w-40"
          placeholder="Assignee (optional)"
          value={assignee}
          onChange={(e) => setAssignee(e.target.value)}
        />
        <input
          type="date"
          className="border rounded px-3 py-2 w-40"
          value={due}
          onChange={(e) => setDue(e.target.value)}
        />
        <button
          type="submit"
          disabled={loading || !title.trim()}
          className="bg-emerald-600 text-white px-4 py-2 rounded hover:bg-emerald-700 disabled:opacity-50"
        >
          {loading ? 'Creating...' : 'Create'}
        </button>
      </form>
      {log.length > 0 && (
        <div className="mt-2 text-xs text-gray-600">
          {log.map((l, i) => (
            <div key={i}>{l}</div>
          ))}
        </div>
      )}
    </div>
  )
}
