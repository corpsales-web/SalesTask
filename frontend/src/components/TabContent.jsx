
import React, { useMemo, useState, useEffect } from 'react';
import { useTab } from '../contexts/TabContext';
import VisualUpgradeStudio from './VisualUpgradeStudio';
import WhatsAppInbox from './WhatsAppInbox';
import TaskDelegationPanel from './TaskDelegationPanel';
import CatalogueManager from './CatalogueManager';
import OptimizedLeadCreationForm from './OptimizedLeadCreationForm';
import EnhancedLeadEditModal from './EnhancedLeadEditModal';
import ProjectSelector from './ProjectSelector';
import PipelineKanban from './PipelineKanban';
import HRMSPanel from './HRMSPanel';
import TrainingCenter from './TrainingCenter';
import AdminSettings from './AdminSettings';

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const TabContent = ({ dashboardStats, leads, tasks, selectedLead, setSelectedLead, onActionComplete }) => {
  const openedRef = React.useRef(false);

  const { activeTab, setActiveTab } = useTab();
  const processedTSRef = React.useRef(null);
  const lockRef = React.useRef(false);
  const [leadForStudio, setLeadForStudio] = useState(null);
  const [pastUpgrades, setPastUpgrades] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('')

  // AI Add Lead auto-open + chain to edit modal
  const [showAIModal, setShowAIModal] = useState(false);
  const [postConvertLeadId, setPostConvertLeadId] = useState(null);
  const [leadEditOpen, setLeadEditOpen] = useState(false);
  const [leadEditData, setLeadEditData] = useState(null);

  // Listen for deterministic triggers
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const checkAndOpen = () => {
      try {
        const flag = localStorage.getItem('OPEN_AI_ADD_LEAD');
        const id = localStorage.getItem('POST_CONVERT_LEAD_ID');
        const chain = localStorage.getItem('POST_CONVERT_CHAIN');
        const ts = localStorage.getItem('POST_CONVERT_TS');
        console.debug('[TabContent] checkAndOpen', { flag, id, chain, ts, hash: window.location.hash, opened: openedRef.current })
        if (flag === '1') {
          if (processedTSRef.current === ts) { console.debug('[TabContent] already processed ts, skip'); return }
          processedTSRef.current = ts || 'na';
          setPostConvertLeadId(id || null);
          if (!openedRef.current) {
            console.debug('[TabContent] Opening AI modal')
            setShowAIModal(true); openedRef.current = true;
          }
          // Defer tab activation slightly to avoid render race
          setTimeout(()=>{ if (!lockRef.current) { lockRef.current = true; try { setActiveTab('leads'); console.debug('[TabContent] setActiveTab("leads")') } catch(e){ console.warn('[TabContent] setActiveTab failed', e) } setTimeout(()=>{ lockRef.current = false }, 100) } }, 30)
        }
      } catch (e) { console.warn('[TabContent] checkAndOpen error', e) }
    };
    checkAndOpen();
    const evt = () => checkAndOpen();
    window.addEventListener('open_ai_add_lead', evt);
    return () => window.removeEventListener('open_ai_add_lead', evt);
  }, [setActiveTab]);

  const handleAIModalClose = () => {
    console.debug('[TabContent] AI modal close')
    setShowAIModal(false);
    try {
      const chain = localStorage.getItem('POST_CONVERT_CHAIN');
      const id = localStorage.getItem('POST_CONVERT_LEAD_ID');
      localStorage.removeItem('OPEN_AI_ADD_LEAD');
      if (chain === 'open_edit_after_ai' && id) {
        const found = (leads || []).find(l => l.id === id);
        if (found) {
          console.debug('[TabContent] Opening lead edit for', id)
          setLeadEditData(found);
          setLeadEditOpen(true);
        } else {
          console.debug('[TabContent] Lead not found in list for', id)
        }
      }
    } catch (e) { console.warn('[TabContent] handleAIModalClose error', e) }
    try { if (window.location.hash === '#open_ai_add_lead') window.location.hash = ''; } catch {}
  };

  useEffect(()=>{
    const preload = typeof window !== 'undefined' ? localStorage.getItem('VISUAL_STUDIO_LEAD_ID') : null;
    if (activeTab === 'erp') {
      if (preload) {
        const target = (leads||[]).find(l=> l.id === preload);
        if (target) setLeadForStudio(target);
        try { localStorage.removeItem('VISUAL_STUDIO_LEAD_ID'); } catch {}
      } else if (!leadForStudio && Array.isArray(leads) && leads.length>0) {
        setLeadForStudio(leads[0]);
      }
    }
  }, [activeTab, leads]);

  useEffect(()=>{
    const load = async()=>{
      try{
        if (!leadForStudio?.id) { setPastUpgrades([]); return }
        const res = await fetch(`${API}/api/visual-upgrades/list?lead_id=${encodeURIComponent(leadForStudio.id)}`)
        const data = await res.json()
        setPastUpgrades(Array.isArray(data.items)? data.items : [])
      }catch(e){ setPastUpgrades([]) }
    }
    load()
  }, [leadForStudio?.id]);

  const content = useMemo(()=>{
    switch(activeTab){
      case 'dashboard':
        return (
          <div className="space-y-4 p-2">
            <div className="bg-white border rounded p-4">
              <div className="text-lg font-semibold">Dashboard Overview</div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 text-sm">
                <div className="border rounded p-3"><div className="text-gray-500">Total Leads</div><div className="text-xl font-bold">{dashboardStats?.totalLeads || 0}</div></div>
                <div className="border rounded p-3"><div className="text-gray-500">Active Leads</div><div className="text-xl font-bold">{dashboardStats?.activeLeads || 0}</div></div>
                <div className="border rounded p-3"><div className="text-gray-500">Pending Tasks</div><div className="text-xl font-bold">{dashboardStats?.pendingTasks || 0}</div></div>
                <div className="border rounded p-3"><div className="text-gray-500">Conversion Rate</div><div className="text-xl font-bold">{dashboardStats?.conversion_rate || 0}%</div></div>
              </div>
            </div>
          </div>
        )
      case 'leads':
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="bg-blue-50 border border-blue-200 p-3 rounded">Lead Management</div>
              <div className="flex gap-2">
                <button className="bg-emerald-600 text-white px-3 py-1 rounded" onClick={()=>{ try { localStorage.setItem('OPEN_AI_ADD_LEAD','1') } catch {}; setShowAIModal(true) }}>Add Lead (AI-Optimized)</button>
              </div>
            </div>
            <div className="grid gap-3">
              {(leads||[]).map(ld=> (
                <div key={ld.id} className="border rounded p-3 flex items-center justify-between">
                  <div>
                    <div className="font-semibold">{ld.name}</div>
                    <div className="text-xs text-gray-600">{ld.phone || ''} • {ld.email || ''}</div>
                    <div className="text-xs text-gray-500">Status: {ld.status || 'New'}</div>
                  </div>
                  <div className="flex gap-2">
                    <button className="ghost" onClick={()=>{ try { localStorage.setItem('VISUAL_STUDIO_LEAD_ID', ld.id) } catch {}; setActiveTab('erp') }}>Open in Visual Studio</button>
                    <button className="ghost" onClick={()=>{ setLeadEditData(ld); setLeadEditOpen(true) }}>✏️ Edit</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      case 'pipeline':
        return (<PipelineKanban />)
      case 'tasks':
        return (
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 p-3 rounded">Enhanced Task Management</div>
            <TaskDelegationPanel />
            <div className="mt-3">
              <div className="text-sm font-semibold mb-2">Recent Tasks</div>
              <div className="grid gap-2">
                {(tasks||[]).map(t => (
                  <div key={t.id} className="border rounded p-2 flex items-center justify-between">
                    <div>
                      <div className="font-medium text-sm">{t.title}</div>
                      <div className="text-xs text-gray-600">{t.status} {t.assignee? `• ${t.assignee}`:''}</div>
                    </div>
                    {t.due_date && <div className="text-xs">Due: {new Date(t.due_date).toLocaleDateString()}</div>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )
      case 'erp':
        return (
          <div className="space-y-4">
            <div className="bg-indigo-50 border border-indigo-200 p-3 rounded">Visual Studio</div>
            <div className="flex items-center gap-2">
              <label className="text-sm">Lead</label>
              <select className="border rounded p-1" value={leadForStudio?.id || ''} onChange={(e)=>{
                const id = e.target.value
                const found = (leads||[]).find(l=> l.id===id)
                setLeadForStudio(found || null)
              }}>
                <option value="">Select Lead</option>
                {(leads||[]).map(ld=> (
                  <option key={ld.id} value={ld.id}>{ld.name} • {ld.phone||''}</option>
                ))}
              </select>
            </div>
            <div>
              <VisualUpgradeStudio leadId={leadForStudio?.id} />
            </div>
            <div className="mt-6">
              <div className="text-sm font-semibold mb-2">Project Catalogue</div>
              <div className="flex items-center gap-2 mb-2">
                <ProjectSelector value={selectedProjectId} onChange={setSelectedProjectId} />
              </div>
              <CatalogueManager isEmbeded={true} projectId={selectedProjectId || null} />
            </div>
          </div>
        )
      case 'hrms':
        return (<HRMSPanel />)
      case 'ai':
        return (
          <div className="p-4">
            <div className="mb-2 text-sm">AI Assistant</div>
            <div className="border rounded p-3 text-sm">Open the assistant from the floating button or header. The chat now connects to backend endpoints.</div>
          </div>
        )
      case 'training':
        return (<TrainingCenter />)
      case 'admin':
        return (<AdminSettings />)
      case 'inbox':
        return (<WhatsAppInbox />)
      default:
        return (
          <div className="p-4">Active tab: {activeTab}</div>
        )
    }
  }, [activeTab, leads, tasks, leadForStudio, pastUpgrades, dashboardStats, selectedProjectId])

  return (
    <div>
      {content}
      <OptimizedLeadCreationForm
        isOpen={showAIModal}
        onClose={handleAIModalClose}
        onLeadCreated={(lead)=>{
          try { localStorage.setItem('POST_CONVERT_LEAD_ID', lead.id) } catch {}
        }}
      />
      {leadEditData && (
        <EnhancedLeadEditModal
          isOpen={leadEditOpen}
          onClose={()=>{ setLeadEditOpen(false); setLeadEditData(null) }}
          leadData={leadEditData}
          onLeadUpdated={()=>{ setLeadEditOpen(false); setLeadEditData(null) }}
        />
      )}
    </div>
  )
}

export default TabContent;
