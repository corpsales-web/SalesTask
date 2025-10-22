import React, { useEffect, useRef, useState } from 'react'

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL

export default function VisualUpgradeStudio({ leadId }){
  const [baseFile, setBaseFile] = useState(null)
  const [basePreview, setBasePreview] = useState(null)
  const [maskPreview, setMaskPreview] = useState(null)
  const [prompt, setPrompt] = useState('Add modern sofa and wall art matching natural tones')
  const [size, setSize] = useState('1024x1024')
  const [loading, setLoading] = useState(false)
  const [progressText, setProgressText] = useState('')
  const [resultUrl, setResultUrl] = useState('')
  const [error, setError] = useState('')
  const canvasRef = useRef(null)
  const imgRef = useRef(null)
  const drawing = useRef(false)
  const [brush, setBrush] = useState(30)

  useEffect(()=>{
    return ()=>{
      if (basePreview) URL.revokeObjectURL(basePreview)
      if (maskPreview) URL.revokeObjectURL(maskPreview)
    }
  }, [basePreview, maskPreview])

  const onBaseChange = (e)=>{
    const f = e.target.files?.[0]
    if (!f) return
    if (!f.type.startsWith('image/')) { setError('Select an image'); return }
    setBaseFile(f)
    const url = URL.createObjectURL(f)
    setBasePreview(url)
    setError('')
    setTimeout(()=> initCanvas(url), 50)
  }

  const initCanvas = (url)=>{
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const img = new Image()
    img.onload = ()=>{
      imgRef.current = img
      // Fit within 800x600 for UI
      const maxW = 800, maxH = 600
      let w = img.width, h = img.height
      const ratio = Math.min(maxW/w, maxH/h, 1)
      w = Math.round(w*ratio); h = Math.round(h*ratio)
      canvas.width = w; canvas.height = h
      ctx.clearRect(0,0,w,h)
      ctx.drawImage(img, 0, 0, w, h)
      // Create mask layer offscreen: start as opaque white
      const maskCanvas = document.createElement('canvas')
      maskCanvas.width = w; maskCanvas.height = h
      const mctx = maskCanvas.getContext('2d')
      mctx.fillStyle = 'white'
      mctx.fillRect(0,0,w,h)
      // store as dataset for later
      canvas.dataset.maskId = Date.now().toString()
      window.__maskCanvases = window.__maskCanvases || {}
      window.__maskCanvases[canvas.dataset.maskId] = maskCanvas
      setMaskPreview('')
    }
    img.src = url
  }

  const startDraw = (e)=>{ drawing.current = true; draw(e) }
  const endDraw = ()=>{ drawing.current = false }
  const getPos = (e)=>{
    const rect = canvasRef.current.getBoundingClientRect()
    const x = (e.touches? e.touches[0].clientX : e.clientX) - rect.left
    const y = (e.touches? e.touches[0].clientY : e.clientY) - rect.top
    return {x, y}
  }
  const draw = (e)=>{
    if (!drawing.current) return
    e.preventDefault()
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    const maskCanvas = window.__maskCanvases?.[canvas.dataset.maskId]
    const mctx = maskCanvas.getContext('2d')
    const {x,y} = getPos(e)
    // erase from mask to make transparent (areas to edit)
    mctx.globalCompositeOperation = 'destination-out'
    mctx.beginPath()
    mctx.arc(x, y, brush, 0, Math.PI*2)
    mctx.fill()

    // redraw visible preview: base image with semi-transparent red where erased
    const img = imgRef.current
    ctx.clearRect(0,0,canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
    // visualize mask holes
    ctx.save()
    ctx.globalAlpha = 0.3
    ctx.drawImage(maskCanvas, 0, 0)
    ctx.restore()
  }

  const exportMaskBlob = ()=>{
    const canvas = canvasRef.current
    const maskCanvas = window.__maskCanvases?.[canvas.dataset.maskId]
    return new Promise((resolve)=>{
      maskCanvas.toBlob((blob)=>{ resolve(blob) }, 'image/png')
    })
  }

  const resetMask = ()=>{
    const canvas = canvasRef.current
    const maskCanvas = window.__maskCanvases?.[canvas.dataset.maskId]
    if (!maskCanvas) return
    const mctx = maskCanvas.getContext('2d')
    mctx.globalCompositeOperation = 'source-over'
    mctx.fillStyle = 'white'
    mctx.fillRect(0,0,maskCanvas.width, maskCanvas.height)
    // redraw display
    if (imgRef.current) {
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0,0,canvas.width, canvas.height)
      ctx.drawImage(imgRef.current, 0, 0, canvas.width, canvas.height)
    }
  }

  const handleRender = async ()=>{
    try{
      if (!baseFile) { setError('Select base image'); return }
      if (!prompt.trim()) { setError('Enter prompt'); return }
      setLoading(true); setError(''); setResultUrl(''); setProgressText('Uploading...')
      const fd = new FormData()
      fd.append('image', baseFile)
      fd.append('prompt', prompt)
      fd.append('size', size)
      fd.append('response_format', 'url')
      if (leadId) fd.append('lead_id', leadId)
      // attach mask from canvas
      const blob = await exportMaskBlob()
      if (blob) {
        // convert mask white=preserve, transparent=edit (already done via destination-out)
        const maskFile = new File([blob], 'mask.png', { type: 'image/png' })
        fd.append('mask', maskFile)
      }
      const res = await fetch(`${API}/api/visual-upgrades/render`, { method:'POST', body: fd })
      if (!res.ok) {
        const t = await res.text()
        throw new Error(t || `HTTP ${res.status}`)
      }
      const data = await res.json()
      const url = data?.upgrade?.result?.url
      if (url) {
        setResultUrl(url)
        setProgressText('Done')
      } else {
        setError('No result URL returned')
      }
    }catch(e){
      setError(e.message || 'Render failed')
    }finally{
      setLoading(false)
    }
  }

  return (
    <div className="bg-white p-4 rounded shadow border">
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="text-lg font-semibold">Visual Upgrade Studio</div>
          <div className="text-xs text-gray-600">Upload a photo, paint mask (areas to transform), then run AI Render</div>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm">Brush</label>
          <input type="range" min={8} max={100} value={brush} onChange={(e)=>setBrush(parseInt(e.target.value||'30'))} />
          <button className="ghost" onClick={resetMask}>Reset Mask</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <div className="mb-2">
            <input type="file" accept="image/*" onChange={onBaseChange} disabled={loading} />
          </div>
          <div className="border rounded overflow-hidden max-w-full">
            <canvas ref={canvasRef}
              onMouseDown={startDraw}
              onMouseUp={endDraw}
              onMouseMove={draw}
              onMouseLeave={endDraw}
              onTouchStart={startDraw}
              onTouchEnd={endDraw}
              onTouchMove={draw}
              className="block w-full h-auto"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Prompt</label>
          <textarea className="w-full border rounded p-2 h-32" value={prompt} onChange={(e)=>setPrompt(e.target.value)} disabled={loading} />
          <div className="flex items-center gap-2 mt-2">
            <label className="text-sm">Size</label>
            <select className="border rounded p-1" value={size} onChange={(e)=>setSize(e.target.value)} disabled={loading}>
              <option value="1024x1024">1024x1024</option>
              <option value="1536x1024">1536x1024</option>
              <option value="1024x1536">1024x1536</option>
            </select>
            <button className="primary ml-auto" onClick={handleRender} disabled={loading || !baseFile || !prompt.trim()}>
              {loading ? 'Rendering...' : 'AI Render'}
            </button>
          </div>
          {progressText && <div className="text-xs text-gray-600 mt-1">{progressText}</div>}
          {error && <div className="text-sm text-red-600 mt-2">{error}</div>}
          {resultUrl && (
            <div className="mt-3">
              <div className="text-sm font-medium mb-1">Result</div>
              <div className="border rounded overflow-hidden">
                <img src={resultUrl} alt="Result" className="w-full h-auto" />
              </div>
              <div className="mt-2 flex gap-2">
                <a href={resultUrl} target="_blank" rel="noreferrer" className="underline text-blue-600 text-sm">Open</a>
                <a href={resultUrl} download className="underline text-sm">Download</a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
