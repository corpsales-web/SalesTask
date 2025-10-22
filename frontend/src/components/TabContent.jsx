
import React, { useMemo, useState, useEffect } from 'react';
import { useTab } from '../contexts/TabContext';
import VisualUpgradeStudio from './VisualUpgradeStudio';
// NOTE: This TabContent is the streamlined version focused on base tabs + Visual Studio

const TabContent = ({ dashboardStats, leads, tasks, selectedLead, setSelectedLead, onActionComplete }) => {
  const { activeTab } = useTab();
  const [leadForStudio, setLeadForStudio] = useState(null)

  useEffect(()=>{
    if (!leadForStudio && Array.isArray(leads) && leads.length>0) {
      setLeadForStudio(leads[0])
    }
  }, [leads])

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
                    <button className="ghost" onClick={()=> setLeadForStudio(ld)}>Open in Visual Studio</button>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <VisualUpgradeStudio leadId={leadForStudio?.id} />
            </div>
          </div>
        )
      case 'erp':
        return (
          <div className="space-y-4">
            <div className="bg-indigo-50 border border-indigo-200 p-3 rounded">ERP</div>
            {/* Existing ERP content remains elsewhere */}
          </div>
        )
      case 'inbox':
        return (
          <div className="space-y-4">
            <div className="bg-emerald-50 border border-emerald-200 p-3 rounded">WhatsApp Inbox</div>
            {/* WhatsAppInbox component is rendered in main App elsewhere */}
          </div>
        )
      default:
        return (
          <div className="p-4">Active tab: {activeTab}</div>
        )
    }
  }, [activeTab, leads, leadForStudio])

  return (
    <div>
      {content}
    </div>
  )
}

export default TabContent;
