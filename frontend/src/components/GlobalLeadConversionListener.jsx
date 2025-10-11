import React, { useEffect } from 'react'
import { useTab } from '../contexts/TabContext'

export default function GlobalLeadConversionListener() {
  const { setActiveTab } = useTab()

  useEffect(() => {
    const onConverted = (e) => {
      try {
        // Ensure Leads tab becomes active
        setActiveTab('leads')
        // Signal TabContent to open AI Add Lead modal
        try { localStorage.setItem('OPEN_AI_ADD_LEAD','1') } catch {}
        try { window.dispatchEvent(new Event('open_ai_add_lead')) } catch {}
        // Ask App to refresh leads
        try { window.dispatchEvent(new Event('refresh_leads')) } catch {}
      } catch(err) {
        // no-op
      }
    }
    window.addEventListener('lead:converted', onConverted)
    return () => window.removeEventListener('lead:converted', onConverted)
  }, [setActiveTab])

  return null
}
