import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { useToast } from '../hooks/use-toast';
import EnhancedLeadEditModal from './EnhancedLeadEditModal';
import { useTab } from '../contexts/TabContext';

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

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
      console.error('Conversations load error', e?.response?.status, e?.response?.data || e.message)
    } finally { setLoading(false); }
  };

  useEffect(()=>{ load(); },[]);

  const checkSession = async (contact) => {
    try {
      const res = await axios.get(`${API}/api/whatsapp/session_status`, { params: { contact } })
      setSessionOk(Boolean(res.data?.within_24h))
    } catch (e) { setSessionOk(false) }
  }

  const markRead = async (contact) => {
    try {
      await axios.post(`${API}/api/whatsapp/conversations/${encodeURIComponent(contact)}/read`)
      await load()
    } catch(e) {}
  }

  const reply = async (to) => {
    try {
      if (!sendText.trim() && sessionOk) return
      if (!sessionOk) {
        await axios.post(`${API}/api/whatsapp/send_template`, { to, template_name: templateName, language_code: 'en' })
      } else {
        await axios.post(`${API}/api/whatsapp/send`, { to, text: sendText })
        setSendText('')
      }
      await markRead(to)
    } catch (e) {}
  }

  const openLead = async (leadId) => {
    try {
      const res = await axios.get(`${API}/api/leads/${leadId}`)
      const lead = res.data?.lead
      if (lead) { setLeadForModal(lead); setLeadModalOpen(true) }
    } catch (e) {}
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
    console.debug('[Inbox] Convert start for', contact)
    try {
      setConvertBusy(contact)
      const sr = await axios.get(`${API}/api/leads/search`, { params: { q: contact } })
      const results = Array.isArray(sr.data.items) ? sr.data.items : []
      const last10 = contact.replace(/\D/g, '').slice(-10)
      const exact = results.find(r => (String(r.phone||'').replace(/\D/g,'').slice(-10) === last10))
      if (exact) {
        console.debug('[Inbox] Existing lead found', exact.id)
        await axios.post(`${API}/api/whatsapp/conversations/${encodeURIComponent(contact)}/link_lead`, { lead_id: exact.id })
        await load()
        try{ window.dispatchEvent(new CustomEvent('crm:notify', { detail: { title: 'Conversation Linked', message: `${contact} → ${exact.name}`, type: 'lead', priority:'low', channel:['push'] } })) }catch{}
        return
      }
      const res = await axios.post(`${API}/api/leads`, { name: `WhatsApp Contact ${new Date().toLocaleTimeString()}`, phone: contact, source: 'WhatsApp' })
      const newLead = res.data?.lead
      console.debug('[Inbox] Lead created response', res.status, newLead)
      if (!newLead?.id) throw new Error('Invalid create lead response')
      await axios.post(`${API}/api/whatsapp/conversations/${encodeURIComponent(contact)}/link_lead`, { lead_id: newLead.id })
      console.debug('[Inbox] Conversation linked to lead', newLead.id)
      // Notify + trigger AI modal
      try {
        window.dispatchEvent(new CustomEvent('crm:notify', { detail: { title: 'Lead Created', message: `${newLead.name} (${newLead.phone})`, type: 'lead', priority:'high', channel:['push'] } }))
        const ts = String(Date.now())
        localStorage.setItem('OPEN_AI_ADD_LEAD','1');
        localStorage.setItem('POST_CONVERT_LEAD_ID', newLead.id);
        localStorage.setItem('POST_CONVERT_CHAIN', 'open_edit_after_ai');
        localStorage.setItem('POST_CONVERT_TS', ts);
        console.debug('[Inbox] Flags set', {
          OPEN_AI_ADD_LEAD: localStorage.getItem('OPEN_AI_ADD_LEAD'),
          POST_CONVERT_LEAD_ID: localStorage.getItem('POST_CONVERT_LEAD_ID'),
          POST_CONVERT_CHAIN: localStorage.getItem('POST_CONVERT_CHAIN'),
          POST_CONVERT_TS: localStorage.getItem('POST_CONVERT_TS')
        })
        window.location.hash = '#open_ai_add_lead';
        console.debug('[Inbox] Hash set to', window.location.hash)
        window.dispatchEvent(new Event('open_ai_add_lead'));
        console.debug('[Inbox] open_ai_add_lead event dispatched')
      } catch(e) { console.warn('[Inbox] Trigger flags error', e) }
      // Do not activate tab here; let TabNavigation/TabContent handle via event/hash to avoid double triggers
      return
    } catch (e) {
      console.error('[Inbox] Convert error', e?.response?.status, e?.response?.data || e)
    } finally { setConvertBusy('') }
  }

  return (
    <div className="panel">
      <div className="panel-title flex items-center justify-between">
        <div>WhatsApp Inbox</div>
        <div className="flex gap-2 items-center">
          <button className="ghost" onClick={async ()=>{
            try {
              const ts = Math.floor(Date.now()/1000)
              const rand10 = String(Math.floor(6000000000 + Math.random()*3999999999))
              const demoFrom = '91' + rand10
              const payload = { object:'whatsapp_business_account', entry:[{ id:'demo_waba', changes:[{ value:{ messaging_product:'whatsapp', metadata:{ display_phone_number:'+911234567890' }, messages:[{ from: demoFrom, id:`wamid.DEMO.${ts}`, timestamp: ts.toString(), type:'text', text:{ body:'Hello from demo inbound' } }] } }]}] }
              await axios.post(`${API}/api/whatsapp/webhook`, payload)
              await load()
            } catch (e) { }
          }}>Add Sample</button>
          <button className="ghost" onClick={load}>{loading? 'Loading...' : 'Refresh'}</button>
        </div>
      </div>
      <div className="panel-body">
        <div className="space-y-2">
          {(!items || items.length===0) && (
            <div className="text-sm text-gray-600">No conversations yet.</div>
          )}
          {(items||[]).map((it)=>{
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
                      </>
                    )}
                    <button className="ghost" onClick={()=>markRead(contact)}>Mark Read</button>
                  </div>
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
    </div>
  );
}
