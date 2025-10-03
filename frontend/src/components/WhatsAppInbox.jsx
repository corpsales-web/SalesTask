import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { useToast } from '../hooks/use-toast';
import EnhancedLeadEditModal from './EnhancedLeadEditModal';

const API = process.env.REACT_APP_BACKEND_URL;

function Badge({ children, color }) {
  const cls = color === 'red' ? 'bg-red-100 text-red-800' : color === 'yellow' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'
  return <span className={`text-xs px-2 py-1 rounded ${cls}`}>{children}</span>
}

export default function WhatsAppInbox() {
  const { toast } = useToast();
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

  const load = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/api/whatsapp/conversations?limit=50`);
      setItems(res.data || []);
    } catch (e) {
      toast({ title: 'Failed to load WhatsApp conversations', description: e.message, variant: 'destructive' });
    } finally { setLoading(false); }
  };

  useEffect(()=>{ load(); },[]);

  const checkSession = async (contact) => {
    try {
      const res = await axios.get(`${API}/api/whatsapp/session_status`, { params: { contact } })
      setSessionOk(Boolean(res.data?.within_24h))
    } catch (e) {
      setSessionOk(false)
    }
  }

  const markRead = async (contact) => {
    try {
      await axios.post(`${API}/api/whatsapp/conversations/${encodeURIComponent(contact)}/read`)
      await load()
    } catch(e) {
      // ignore
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
    }
  }

  const ageBadge = (sec) => {
    if (sec >= 1800) return <Badge color='red'>Late (30m+)</Badge>
    if (sec >= 300) return <Badge color='yellow'>Due soon (5m+)</Badge>
    return null
  }

  return (
    <div className="panel">
      <div className="panel-title flex items-center justify-between">
        <div>WhatsApp Inbox</div>
        <div className="flex gap-2 items-center">
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
          {(items||[]).map((it)=>{
            const contact = it.contact
            return (
              <div key={contact} className="border rounded-lg p-3">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-semibold flex items-center gap-2">
                      <span>{contact}</span>
                      {it.lead_name && <span className="text-gray-600">• {it.lead_name}</span>}
                      {ageBadge(it.age_sec)}
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
                      <button className="ghost" onClick={async ()=>{
                        try {
                          const res = await axios.post(`${API}/api/leads`, { name: 'WhatsApp Contact', phone: contact, source: 'WhatsApp' })
                          await load()
                          toast({ title: 'Lead Created' })
                        } catch(e) { toast({ title: 'Lead creation failed', description: e.message, variant: 'destructive' }) }
                      }}>Convert to Lead</button>
                    )}
                    <button className="ghost" onClick={()=>markRead(contact)}>Mark Read</button>
                  </div>
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
    </div>
  );
}
