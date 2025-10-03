import React from 'react'
import { useTab } from '../contexts/TabContext'

export default function HeaderInboxButton() {
  const { setActiveTab } = useTab()
  return (
    <button onClick={() => setActiveTab('inbox')} className="bg-emerald-600 text-white px-2 py-1 sm:px-4 sm:py-2 rounded-lg hover:bg-emerald-700 flex items-center text-xs sm:text-sm">
      <span className="mr-1">💬</span>
      <span className="hidden sm:inline">Inbox</span>
    </button>
  )
}
