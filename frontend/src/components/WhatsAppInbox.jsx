import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { useToast } from '../hooks/use-toast';
import EnhancedLeadEditModal from './EnhancedLeadEditModal';
import { useTab } from '../contexts/TabContext';

const API = process.env.REACT_APP_BACKEND_URL;

function Badge({ children, color }) {
  const cls = color === 'red' ? 'bg-red-100 text-red-800' : color === 'yellow' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'
  return <span className={`text-xs px-2 py-1 rounded ${cls}`}>{children}</span>
}

function normalizePhoneUI(raw) {
  if (!raw) return ''
  const digits = String(raw).replace(/\D/g, '')
  if (!digits) return ''
  if (digits.startsWith('0') && digits.length === 11) return '+91' + digits.slice(1)
  if (digits.startsWith('91') && digits.length >= 12) return '+' + digits.slice(0,12)
  if (digits.length === 10) return '+91' + digits
  return raw.startsWith('+') ? raw : ('+' + digits)
}

export default function WhatsAppInbox() {
  const { toast } = useToast();
  const { setActiveTab } = useTab();
  const [items, setItems] = useState([]); // conversations
  const [loading, setLoading] = useState(false);
  const [leadModalOpen, setLeadModalOpen] = useState(false)
  const [leadForModal, setLeadForModal] = useState(null)
  const [sendText, setSendText] = useState('')
  const [sessionOk, setSessionOk] = useState(true)
  const [activeContact, setActiveContact] = useState('')
  const [templateName, setTemplateName] = useState('hello_world')
  const [linkingContact, setLinkingContact] = useState('')
  const [linkLeadId, setLinkLeadId] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [expandedContact, setExpandedContact] = useState('')
  const [previewMap, setPreviewMap] = useState({})
  const [filter, setFilter] = useState('all')
  const [ownerFilter, setOwnerFilter] = useState('')
  const [convertBusy, setConvertBusy] = useState('')

  const load = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/api/whatsapp/conversations?limit=50`);
      setItems(res.data || []);
    } catch (e) {
      toast({ title: 'Failed to load WhatsApp conversations', description: e.message, variant: 'destructive' });
      console.error('Conversations load error', e?.response?.status, e?.response?.data || e.message)
    } finally { setLoading(false); }
  };

  useEffect(()=>{ load(); },[]);

  const checkSession = async (contact) => {
    try {
      const res = await axios.get(`${API}/api/whatsapp/session_status`, { params: { contact } })
      setSessionOk(Boolean(res.data?.within_24h))
    } catch (e) {
      setSessionOk(false)
      console.warn('Session status error', e?.response?.status, e?.response?.data)
    }
  }

  const markRead = async (contact) => {
    try {
      await axios.post(`${API}/api/whatsapp/conversations/${encodeURIComponent(contact)}/read`)
      await load()
    } catch(e) {
      console.warn('Mark read failed', e?.response?.status, e?.response?.data)
    }
  }

  const reply = async (to) => {
    try {
      if (!sendText.trim() && sessionOk) return
      if (!sessionOk) {
        await axios.post(`${API}/api/whatsapp/send_template`, { to, template_name: templateName, language_code: 'en' })
        toast({ title: 'Template sent (stub/live based on config)' })
      } else {
        await axios.post(`${API}/api/whatsapp/send`, { to, text: sendText })
        toast({ title: 'Reply sent' })
        setSendText('')
      }
      await markRead(to)
    } catch (e) {
      toast({ title: 'Reply failed', description: e.message, variant: 'destructive' });
      console.error('Reply error', e?.response?.status, e?.response?.data || e.message)
    }
  }

  const openLead = async (leadId) => {
    try {
      const res = await axios.get(`${API}/api/leads/${leadId}`)
      const lead = res.data?.lead
      if (lead) {
        setLeadForModal(lead)
        setLeadModalOpen(true)
      } else {
        toast({ title: 'Lead not found', variant: 'destructive' })
      }
    } catch (e) {
      toast({ title: 'Load lead failed', description: e.message, variant: 'destructive' })
      console.error('Open lead error', e?.response?.status, e?.response?.data || e.message)
    }
  }

  const ageBadge = (sec) => {
    if (sec >= 1800) return <Badge color='red'>Late (30m+)</Badge>
    if (sec >= 300) return <Badge color='yellow'>Due soon (5m+)</Badge>
    return null
  }
  const ageChip = (sec) => {
    const m = Math.floor(sec/60)
    return <span className="text-xs text-gray-500 border rounded px-1 py-0.5">{m}m</span>
  }

  const handleConvert = async (rawContact) => {
    const contact = normalizePhoneUI(rawContact)
    try {
      setConvertBusy(contact)
      // duplicate check by phone
      const sr = await axios.get(`${API}/api/leads/search`, { params: { q: contact } })
      const results = Array.isArray(sr.data.items) ? sr.data.items : []
      const last10 = contact.replace(/\D/g, '').slice(-10)
      const exact = results.find(r => (String(r.phone||'').replace(/\D/g,'').slice(-10) === last10))
      if (exact) {
        if (window.confirm(`Lead with this phone already exists (ID: ${exact.id}). Link conversation to this lead instead?`)) {
          await axios.post(`${API}/api/whatsapp/conversations/${encodeURIComponent(contact)}/link_lead`, { lead_id: exact.id })
          await load()
          toast({ title: 'Conversation linked to existing lead' })
          return
        }
      }
      // create
      const res = await axios.post(`${API}/api/leads`, { name: 'WhatsApp Contact', phone: contact, source: 'WhatsApp' })
      const newLead = res.data?.lead
      if (!newLead?.id) throw new Error('Invalid create lead response')
      // link
      await axios.post(`${API}/api/whatsapp/conversations/${encodeURIComponent(contact)}/link_lead`, { lead_id: newLead.id })
      // Immediately trigger AI modal + tab switch BEFORE any further awaits
      try {
        localStorage.setItem('OPEN_AI_ADD_LEAD','1');
        window.location.hash = '#open_ai_add_lead';
        window.dispatchEvent(new Event('open_ai_add_lead'));
      } catch(e) { console.warn('AI flag set failed', e) }
      // Force deterministic navigation and modal open via hash + reload (Option A)
      try {
        setActiveTab('leads')
      } catch {}
      try {
        const base = window.location.pathname || '/'
        window.location.replace(base + '#open_ai_add_lead')
        setTimeout(()=> { try { window.location.reload() } catch {} }, 50)
      } catch {}
      // No further awaits after scheduling reload
      toast({ title: 'Lead Created & Linked' })
      return
    } catch (e) {
      console.error('Convert to Lead error', e?.response?.status, e?.response?.data || e.message)
      const msg = e?.response?.data?.detail || e?.response?.data?.message || e.message
      toast({ title: 'Convert failed', description: msg, variant: 'destructive' })
    } finally {
      setConvertBusy('')
    }
  }

  return (
    <div className="panel">
      <div className="panel-title flex items-center justify-between">
        <div>WhatsApp Inbox</div>
        <div className="flex gap-2 items-center">
          <select className="border rounded px-2 py-1 text-sm" value={filter} onChange={(e)=>setFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="unread">Unread</option>
            <option value="late">Late (30m+)</option>
            <option value="due">Due soon (5m+)</option>
            <option value="owner">Owner</option>
          </select>
          {filter==='owner' && (
            <input className="border rounded px-2 py-1 text-sm" placeholder="Owner mobile e.g. +919999139938" value={ownerFilter} onChange={(e)=>setOwnerFilter(e.target.value)} />
          )}
          <button className="ghost" onClick={async ()=>{
            try {
              const ts = Math.floor(Date.now()/1000)
              const payload = {
                object: 'whatsapp_business_account',
                entry: [{
                  id: 'demo_waba',
                  changes: [{
                    value: {
                      messaging_product: 'whatsapp',
                      metadata: { display_phone_number: '+911234567890' },
                      messages: [{
                        from: '919876543210',
                        id: `wamid.DEMO.${ts}`,
                        timestamp: ts.toString(),
                        type: 'text',
                        text: { body: 'Hello from demo inbound 👋' }
                      }]
                    }
                  }]
                }]
              }
              await axios.post(`${API}/api/whatsapp/webhook`, payload)
              await load()
            } catch (e) { /* ignore */ }
          }}>Add Sample</button>
          <button className="ghost" onClick={load}>{loading? 'Loading...' : 'Refresh'}</button>
        </div>
      </div>
      <div className="panel-body">
        <div className="space-y-2">
          {(!items || items.length===0) && (
            <div className="text-sm text-gray-600">No conversations yet. Post a sample inbound to /api/whatsapp/webhook or wait for live messages.</div>
          )}
          {(items||[]).filter(it=>{
            if (filter==='unread') return (it.unread_count||0)>0
            if (filter==='late') return (it.age_sec||0)>=1800
            if (filter==='due') return (it.age_sec||0)>=300 && (it.age_sec||0)<1800
            if (filter==='owner') return ownerFilter ? (it.owner_mobile||'').includes(ownerFilter) : true
            return true
          }).map((it)=>{
            const contact = it.contact
            const converting = convertBusy === normalizePhoneUI(contact)
            return (
              <div key={contact} className="border rounded-lg p-3">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-semibold flex items-center gap-2">
                      <span>{contact}</span>
                      {it.lead_name && <span className="text-gray-600">• {it.lead_name}</span>}
                      {ageBadge(it.age_sec)}
                      <span className="ml-1">{ageChip(it.age_sec)}</span>
                      {it.unread_count > 0 && <Badge color='yellow'>{it.unread_count} unread</Badge>}
                    </div>
                    <div className="text-xs text-gray-500">Owner: {it.owner_mobile || 'Unassigned'} • Last: {new Date(it.last_message_at).toLocaleString()}</div>
                    {it.last_message_text && (
                      <div className="text-sm text-gray-800 mt-1 truncate">{it.last_message_dir==='out' ? 'You: ' : ''}{it.last_message_text}</div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {it.lead_id && (
                      <button className="ghost" onClick={()=>openLead(it.lead_id)}>View Lead</button>
                    )}
                    {!it.lead_id && (
                      <>
                        <button className="ghost" disabled={converting} onClick={()=>handleConvert(contact)}>{converting ? 'Converting...' : 'Convert to Lead'}</button>
                        <button className="ghost" onClick={async ()=>{
                          try {
                            const norm = normalizePhoneUI(contact)
                            setLinkingContact(norm); setLinkLeadId(''); setSearchQuery(norm); setSearching(true)
                            const res = await axios.get(`${API}/api/leads/search`, { params: { q: norm } })
                            setSearchResults(Array.isArray(res.data.items) ? res.data.items : [])
                            setSearching(false)
                          } catch { setSearching(false) }
                        }}>Link to Lead</button>
                        <button className="ghost" onClick={async ()=>{
                          try {
                            const norm = normalizePhoneUI(contact)
                            setLinkingContact(norm); setLinkLeadId(''); setSearchQuery(norm); setSearching(true)
                            const res = await axios.get(`${API}/api/leads/search`, { params: { q: norm } })
                            setSearchResults(Array.isArray(res.data.items) ? res.data.items : [])
                            setSearching(false)
                          } catch { setSearching(false) }
                        }}>Check Duplicate</button>
                      </>
                    )}
                    <button className="ghost" onClick={()=>markRead(contact)}>Mark Read</button>
                  </div>
                </div>
                {/* Expandable last 3 messages preview */}
                <div className="mt-2">
                  <button className="text-xs underline" onClick={async ()=>{
                    try {
                      const res = await axios.get(`${API}/api/whatsapp/contact_messages`, { params: { contact } })
                      const items = Array.isArray(res.data.items) ? res.data.items : []
                      const lines = items.map(m=>`${m.direction==='inbound'?'From':'You'} • ${new Date(m.timestamp).toLocaleString()}\n${m.text || '['+m.type+']'}`).join('\n\n')
                      alert(lines || 'No recent messages')
                    } catch { /* ignore */ }
                  }}>Show last 3 messages</button>
                </div>

                <div className="mt-2 flex gap-2 items-center">
                  <input
                    value={activeContact === contact ? sendText : ''}
                    onChange={(e)=>{ setActiveContact(contact); setSendText(e.target.value) }}
                    onFocus={async ()=>{ setActiveContact(contact); await checkSession(contact) }}
                    placeholder={sessionOk ? 'Type a reply...' : 'Session expired - send a template'}
                    className="border rounded px-2 py-1 flex-1"
                    disabled={!sessionOk && activeContact===contact}
                  />
                  {!sessionOk && activeContact===contact && (
                    <select value={templateName} onChange={(e)=>setTemplateName(e.target.value)} className="border rounded px-2 py-1">
                      <option value="hello_world">hello_world</option>
                    </select>
                  )}
                  <button className="primary" onClick={()=>reply(contact)}>
                    {sessionOk && activeContact===contact ? 'Send' : 'Send Template'}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
      {leadForModal && (
        <EnhancedLeadEditModal
          isOpen={leadModalOpen}
          onClose={()=>{ setLeadModalOpen(false); setLeadForModal(null) }}
          leadData={leadForModal}
          onLeadUpdated={()=>{ setLeadModalOpen(false); setLeadForModal(null); load() }}
        />
      )}

      {linkingContact && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white p-4 rounded shadow w-full max-w-md">
            <div className="font-semibold mb-2">Link conversation to a Lead</div>
            <div className="text-xs text-gray-600 mb-2">Contact: {linkingContact}</div>

            <div className="mb-2">
              <input
                className="border rounded px-2 py-1 w-full"
                placeholder="Search lead by name, email or phone"
                value={searchQuery}
                onChange={async (e)=>{
                  const q = e.target.value; setSearchQuery(q)
                  if (!q.trim()) { setSearchResults([]); return }
                  try {
                    setSearching(true)
                    const res = await axios.get(`${API}/api/leads/search`, { params: { q } })
                    setSearchResults(Array.isArray(res.data.items) ? res.data.items : [])
                  } catch { setSearchResults([]) } finally { setSearching(false) }
                }}
              />
              <div className="max-h-40 overflow-auto border rounded mt-1">
                {searching && <div className="text-xs p-2">Searching...</div>}
                {!searching && searchResults.length===0 && <div className="text-xs p-2 text-gray-500">No results</div>}
                {searchResults.map(ld=> (
                  <div key={ld.id} className="p-2 hover:bg-gray-50 cursor-pointer flex justify-between items-center" onClick={()=>{ setLinkLeadId(ld.id) }}>
                    <div>
                      <div className="text-sm font-medium">{ld.name}</div>
                      <div className="text-xs text-gray-600">{ld.email || ''} • {ld.phone || ''}</div>
                    </div>
                    <div className="text-xs">{ld.id}</div>
                  </div>
                ))}
              </div>
            </div>

            <input
              className="border rounded px-2 py-1 w-full mb-3"
              placeholder="Or paste Lead ID"
              value={linkLeadId}
              onChange={(e)=>setLinkLeadId(e.target.value)}
            />

            <div className="flex gap-2 justify-end">
              <button className="ghost" onClick={()=>{ setLinkingContact(''); setLinkLeadId(''); setSearchQuery(''); setSearchResults([]) }}>Cancel</button>
              <button className="primary" onClick={async ()=>{
                try {
                  await axios.post(`${API}/api/whatsapp/conversations/${encodeURIComponent(linkingContact)}/link_lead`, { lead_id: linkLeadId })
                  toast({ title: 'Linked to Lead' })
                  setLinkingContact(''); setLinkLeadId(''); setSearchQuery(''); setSearchResults([])
                  await load()
                } catch(e) { toast({ title: 'Failed to link', description: e.message, variant: 'destructive' }) }
              }}>Link</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
