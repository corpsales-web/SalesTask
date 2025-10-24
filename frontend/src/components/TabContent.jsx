
import React, { useMemo, useState, useEffect } from 'react';
import { useTab } from '../contexts/TabContext';
import VisualUpgradeStudio from './VisualUpgradeStudio';

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const TabContent = ({ dashboardStats, leads, tasks, selectedLead, setSelectedLead, onActionComplete }) => {
  const { activeTab, setActiveTab } = useTab();
  const [leadForStudio, setLeadForStudio] = useState(null);
  const [pastUpgrades, setPastUpgrades] = useState([]);

  // Preload lead for studio
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

  // Load past upgrades when lead changes
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
      case 'leads':
        return (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 p-3 rounded">Lead Management</div>
            <div className="grid gap-3">
              {(leads||[]).map(ld=> (
                <div key={ld.id} className="border rounded p-3 flex items-center justify-between">
                  <div>
                    <div className="font-semibold">{ld.name}</div>
                    <div className="text-xs text-gray-600">{ld.phone || ''} • {ld.email || ''}</div>
                  </div>
                  <div className="flex gap-2">
                    <button className="ghost" onClick={()=>{ try { localStorage.setItem('VISUAL_STUDIO_LEAD_ID', ld.id) } catch {}; setActiveTab('erp') }}>Open in Visual Studio</button>
                  </div>
                </div>
              ))}
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
            <div className="mt-4">
              <div className="text-sm font-semibold mb-2">Past Upgrades</div>
              {pastUpgrades.length===0 && (<div className="text-xs text-gray-600">No upgrades yet for this lead.</div>)}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {pastUpgrades.map(up => (
                  <div key={up.id} className="border rounded p-2">
                    <div className="text-xs text-gray-600 truncate" title={up.prompt}>{up.prompt}</div>
                    <div className="mt-1 border rounded overflow-hidden">
                      <img src={up.result?.url} alt="Upgrade" className="w-full h-auto" />
                    </div>
                    <div className="flex gap-2 mt-1">
                      <a className="underline text-blue-600 text-xs" href={up.result?.url} target="_blank" rel="noreferrer">Open</a>
                      <a className="underline text-xs" href={up.result?.url} download>Download</a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )
      default:
        return (
          <div className="p-4">Active tab: {activeTab}</div>
        )
    }
  }, [activeTab, leads, leadForStudio, pastUpgrades])

  return (
    <div>
      {content}
    </div>
  )
}

export default TabContent;
