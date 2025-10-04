import React, { useEffect, useMemo, useState } from 'react'

const API = process.env.REACT_APP_BACKEND_URL

export default function CatalogueManager({ isEmbeded=false }){
  const [catalogues, setCatalogues] = useState([])
  const [uploadModalOpen, setUploadModalOpen] = useState(false)
  const [uploadFile, setUploadFile] = useState(null)
  const [uploadCategory, setUploadCategory] = useState('general')
  const [uploadTags, setUploadTags] = useState('')
  const [progress, setProgress] = useState(0)
  const [sendingTo, setSendingTo] = useState('')

  const load = async()=>{
    try{
      const res = await fetch(`${API}/api/uploads/catalogue/list`)
      const data = await res.json()
      setCatalogues(Array.isArray(data.catalogues) ? data.catalogues : [])
    }catch(e){ console.error('catalogue list', e) }
  }
  useEffect(()=>{ load() },[])

  const chunkedUpload = async(file)=>{
    const initRes = await fetch(`${API}/api/uploads/catalogue/init`,{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ filename: file.name, category: uploadCategory, tags: uploadTags })})
    if(!initRes.ok) throw new Error('init failed')
    const init = await initRes.json()
    const id = init.upload_id
    const chunkSize = 1024*1024*2 // 2MB
    const total = Math.ceil(file.size/chunkSize)
    let sent = 0
    for(let i=0; i<total; i++){
      const start = i*chunkSize
      const end = Math.min(file.size, start+chunkSize)
      const blob = file.slice(start, end)
      const fd = new FormData()
      fd.append('upload_id', id)
      fd.append('index', String(i))
      fd.append('total', String(total))
      fd.append('chunk', new File([blob], `chunk_${i}`))
      const r = await fetch(`${API}/api/uploads/catalogue/chunk`, { method:'POST', body: fd })
      if(!r.ok) throw new Error('chunk failed')
      sent++
      setProgress(Math.round((sent/total)*100))
    }
    const compRes = await fetch(`${API}/api/uploads/catalogue/complete`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ upload_id: id, filename: file.name, category: uploadCategory, tags: uploadTags }) })
    if(!compRes.ok) throw new Error('complete failed')
    const out = await compRes.json()
    return out.file
  }

  const handleUpload = async()=>{
    if(!uploadFile){ alert('Select a file'); return }
    try{
      setProgress(1)
      const file = await chunkedUpload(uploadFile)
      setProgress(100)
      alert(`Uploaded ${file.original_name}`)
      setUploadModalOpen(false)
      setUploadFile(null)
      setUploadCategory('general')
      setUploadTags('')
      await load()
    }catch(e){
      console.error('upload error', e)
      alert('Upload failed: '+ e.message)
      setProgress(0)
    }
  }

  const sendViaWhatsApp = async (file, to)=>{
    try{
      setSendingTo(to)
      const mediaType = (file.url||'').toLowerCase().match(/\.pdf|\.docx|\.doc$/) ? 'document' : 'image'
      const res = await fetch(`${API}/api/whatsapp/send_media`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ to, media_url: file.url, media_type: mediaType }) })
      if(!res.ok){ const t = await res.text(); throw new Error(t) }
      alert('Shared via WhatsApp (stub/live based on config)')
    }catch(e){ alert('Share failed: '+ e.message) }
    finally{ setSendingTo('') }
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
              <button className="text-sm underline" disabled={!!sendingTo} onClick={()=>{
                const to = prompt('Enter recipient mobile (+91xxxxxxxxxx)')
                if(to) sendViaWhatsApp(c, to)
              }}>{sendingTo? 'Sharing...' : 'Share via WhatsApp'}</button>
            </div>
          </div>
        ))}
      </div>

      {uploadModalOpen && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white p-4 rounded shadow w-full max-w-md">
            <div className="font-semibold mb-2">Upload Catalogue</div>
            <input type="file" onChange={(e)=> setUploadFile(e.target.files?.[0]||null)} className="mb-2" />
            <input value={uploadCategory} onChange={(e)=>setUploadCategory(e.target.value)} placeholder="Category" className="border rounded px-2 py-1 w-full mb-2" />
            <input value={uploadTags} onChange={(e)=>setUploadTags(e.target.value)} placeholder="Tags (comma separated)" className="border rounded px-2 py-1 w-full mb-2" />
            {progress>0 && (
              <div className="w-full bg-gray-200 rounded h-2 mb-2">
                <div className="bg-emerald-600 h-2 rounded" style={{width: `${progress}%`}} />
              </div>
            )}
            <div className="flex gap-2 justify-end">
              <button className="ghost" onClick={()=>{ setUploadModalOpen(false); setProgress(0) }}>Cancel</button>
              <button className="bg-emerald-600 text-white px-3 py-1 rounded" onClick={handleUpload}>Upload</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
