import React, { useEffect, useMemo, useRef, useState } from 'react'

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL

export default function CatalogueManager({ isEmbeded=false, projectId: externalProjectId=null }){
  const [catalogues, setCatalogues] = useState([])
  const [uploadModalOpen, setUploadModalOpen] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState([]) // FileList -> Array<File>
  const [uploadCategory, setUploadCategory] = useState('general')
  const [uploadTags, setUploadTags] = useState('')
  const [jobs, setJobs] = useState([]) // per file jobs
  const controllersRef = useRef({}) // key: jobId -> AbortController

  const load = async()=>{
  useEffect(()=>{ setProjectId(externalProjectId) }, [externalProjectId])

    try{
      const res = await fetch(`${API}/api/uploads/catalogue/list${projectId? ('?project_id='+encodeURIComponent(projectId)) : ''}`)
      const data = await res.json()
      setCatalogues(Array.isArray(data.catalogues) ? data.catalogues : [])
    }catch(e){ console.error('catalogue list', e) }
  }
  const [projectId, setProjectId] = useState(externalProjectId)

  useEffect(()=>{ load() },[])

  const createJob = (file)=>({
    id: `${file.name}-${file.size}-${Date.now()}`,
    file,
    uploadId: null,
    progress: 0,
    sent: 0,
    total: Math.ceil(file.size / (1024*1024)), // 1MB chunks
    status: 'queued', // queued|uploading|paused|completed|error|canceled
    error: null,
    chunkSize: 1024*1024,
    lastUpdated: Date.now()
  })

  const startUpload = async (job) => {
    const file = job.file
    try{
      // init if not already
      let uploadId = job.uploadId
      if (!uploadId) {
        const initRes = await fetch(`${API}/api/uploads/catalogue/init`,{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ filename: file.name, category: uploadCategory, tags: uploadTags, project_id: projectId })})
        if(!initRes.ok) throw new Error('init failed')
        const init = await initRes.json()
        uploadId = init.upload_id
        job.uploadId = uploadId
      }

      // resume state from server
      let stateParts = 0
      try{
        const st = await fetch(`${API}/api/uploads/catalogue/state?upload_id=${encodeURIComponent(uploadId)}`)
        const s = await st.json()
        stateParts = s.exists ? (s.parts || 0) : 0
      }catch{}

      // setup loop
      job.status = 'uploading'
      updateJob(job)

      const total = Math.ceil(file.size / job.chunkSize)
      job.total = total

      for(let i=stateParts; i<total; i++){
        // check paused/canceled
        const currJob = jobsRef.current.find(j=>j.id===job.id)
        if (!currJob || currJob.status === 'paused' || currJob.status === 'canceled' || currJob.status === 'error') break

        const start = i*job.chunkSize
        const end = Math.min(file.size, start+job.chunkSize)
        const blob = file.slice(start, end)
        const fd = new FormData()
        fd.append('upload_id', uploadId)
        fd.append('index', String(i))
        fd.append('total', String(total))
        fd.append('chunk', new File([blob], `chunk_${i}`))

        const controller = new AbortController()
        controllersRef.current[job.id] = controller
        const r = await fetch(`${API}/api/uploads/catalogue/chunk`, { method:'POST', body: fd, signal: controller.signal })
        if(!r.ok) throw new Error(`chunk ${i} failed`)
        job.sent = i+1
        job.progress = Math.round(((i+1)/total)*100)
        job.lastUpdated = Date.now()
        updateJob(job)
      }

      // if fully sent and not canceled/paused, complete
      const finalJob = jobsRef.current.find(j=>j.id===job.id)
      if (finalJob && finalJob.sent === finalJob.total && finalJob.status === 'uploading'){
        const compRes = await fetch(`${API}/api/uploads/catalogue/complete`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ upload_id: uploadId, filename: file.name, category: uploadCategory, tags: uploadTags, project_id: projectId, title: file.name, description: '' }) })
        if(!compRes.ok) throw new Error('complete failed')
        const out = await compRes.json()
        finalJob.status = 'completed'
        finalJob.progress = 100
        updateJob(finalJob)
        alert(`Uploaded ${out.file?.original_name || file.name}`)
        await load()
      }

    }catch(e){
      console.error('upload error', e)
      job.status = 'error'
      job.error = e.message || 'Upload failed'
      updateJob(job)
    }
  }

  const jobsRef = useRef([])
  const updateJob = (job) => {
    setJobs(prev=>{
      const next = prev.map(j=> j.id===job.id ? {...j, ...job} : j)
      jobsRef.current = next
      return next
    })
  }

  const pauseJob = (jobId) => {
    const job = jobsRef.current.find(j=>j.id===jobId)
    if (!job) return
    const controller = controllersRef.current[jobId]
    if (controller) { try{ controller.abort() }catch{} }
    job.status = 'paused'
    updateJob(job)
  }

  const resumeJob = async (jobId) => {
    const job = jobsRef.current.find(j=>j.id===jobId)
    if (!job) return
    job.status = 'uploading'
    updateJob(job)
    await startUpload(job)
  }

  const cancelJob = async (jobId) => {
    const job = jobsRef.current.find(j=>j.id===jobId)
    if (!job) return
    // abort any inflight
    const controller = controllersRef.current[jobId]
    if (controller) { try{ controller.abort() }catch{} }
    try{
      if (job.uploadId){
        const fd = new FormData()
        fd.append('upload_id', job.uploadId)
        await fetch(`${API}/api/uploads/catalogue/cancel`, { method:'POST', body: fd })
      }
    }catch{}
    job.status = 'canceled'
    updateJob(job)
  }

  const beginUploads = async()=>{
    if (!selectedFiles || selectedFiles.length===0){ alert('Select files'); return }
    // create jobs
    const newJobs = Array.from(selectedFiles).map(f=> createJob(f))
    setJobs(prev=>{
      const next = [...prev, ...newJobs]
      jobsRef.current = next
      return next
    })
    // sequentially start to reduce load; still allows multiple queued
    for(const j of newJobs){
      await startUpload(j)
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-3">
        <div className="text-lg font-semibold">Catalogue</div>
        <button className="bg-emerald-600 text-white px-3 py-1 rounded" onClick={()=>setUploadModalOpen(true)}>Upload</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {catalogues.map((c)=>(
          <div key={c.id} className="border rounded p-3">
            <div className="font-medium truncate" title={c.original_name}>{c.original_name}</div>
            <div className="text-xs text-gray-600">{c.category} • {new Date(c.uploaded_at).toLocaleString()}</div>
            <div className="mt-2 flex gap-2">
              <a className="text-blue-600 underline text-sm" href={c.url} target="_blank" rel="noreferrer">Open</a>
              <button className="text-sm underline" onClick={()=>{
                const to = prompt('Enter recipient mobile (+91xxxxxxxxxx)')
                if(to){
                  const mediaType = (c.url||'').toLowerCase().match(/\.pdf|\.docx|\.doc$/) ? 'document' : 'image'
                  fetch(`${API}/api/whatsapp/send_media`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ to, media_url: c.url, media_type: mediaType }) })
                    .then(r=>{ if(!r.ok) return r.text().then(t=>{throw new Error(t)}) })
                    .then(()=> alert('Shared via WhatsApp (stub/live based on config)'))
                    .catch(err=> alert('Share failed: '+ (err.message||err)))
                }
              }}>Share via WhatsApp</button>
            </div>
          </div>
        ))}
      </div>

      {uploadModalOpen && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white p-4 rounded shadow w-full max-w-2xl">
            <div className="font-semibold mb-2">Upload Catalogue</div>
            <input multiple type="file" onChange={(e)=> setSelectedFiles(Array.from(e.target.files||[]))} className="mb-2" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-2">
              <input value={uploadCategory} onChange={(e)=>setUploadCategory(e.target.value)} placeholder="Category" className="border rounded px-2 py-1 w-full" />
              <input value={uploadTags} onChange={(e)=>setUploadTags(e.target.value)} placeholder="Tags (comma separated)" className="border rounded px-2 py-1 w-full" />
            </div>

            {/* Jobs List */}
            <div className="max-h-64 overflow-auto border rounded p-2 mb-2">
              {jobs.length===0 && <div className="text-xs text-gray-600">No uploads yet. Select files then click Start Upload.</div>}
              {jobs.map(j=> (
                <div key={j.id} className="border rounded p-2 mb-2">
                  <div className="flex justify-between items-center">
                    <div className="text-sm font-medium truncate" title={j.file.name}>{j.file.name} • {(j.file.size/1024/1024).toFixed(1)} MB</div>
                    <div className="text-xs text-gray-600">{j.status}</div>
                  </div>
                  <div className="w-full bg-gray-200 rounded h-2 mt-2">
                    <div className="bg-emerald-600 h-2 rounded" style={{width: `${j.progress}%`}} />
                  </div>
                  <div className="flex gap-2 justify-end mt-2">
                    {(j.status==='uploading') && (
                      <button className="ghost" onClick={()=>pauseJob(j.id)}>Pause</button>
                    )}
                    {(j.status==='paused' || j.status==='error') && (
                      <button className="ghost" onClick={()=>resumeJob(j.id)}>Resume</button>
                    )}
                    {(j.status!=='completed' && j.status!=='canceled') && (
                      <button className="ghost" onClick={()=>cancelJob(j.id)}>Cancel</button>
                    )}
                  </div>
                  {j.error && <div className="text-xs text-red-600 mt-1">{j.error}</div>}
                </div>
              ))}
            </div>

            <div className="flex gap-2 justify-end">
              <button className="ghost" onClick={()=>{ setUploadModalOpen(false) }}>Close</button>
              <button className="bg-emerald-600 text-white px-3 py-1 rounded" onClick={beginUploads}>Start Upload</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
