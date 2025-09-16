import React from 'react';
import { useTab, TAB_CONFIG } from '../contexts/TabContext';

const TabNavigation = () => {
  const { activeTab, setActiveTab, loading } = useTab();
  
  const handleTabClick = (tabId) => {
    console.log(`🖱️ TAB CLICKED: ${tabId}`);
    setActiveTab(tabId);
  };
  
  return (
    <div className="border-b border-gray-200 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-0 overflow-x-auto">
          {Object.values(TAB_CONFIG).map((tab) => (
            <button
              key={tab.id}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                handleTabClick(tab.id);
              }}
              disabled={loading}
              className={`
                p-3 flex items-center justify-center transition-all duration-200 min-w-0 flex-1
                ${activeTab === tab.id 
                  ? "bg-emerald-100 text-emerald-700 font-bold border-b-2 border-emerald-500" 
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                }
                ${loading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
              `}
              title={tab.description}
            >
              <span className="text-lg mr-2">{tab.icon}</span>
              <span className="font-medium text-sm hidden sm:inline">{tab.label}</span>
              {/* Debug indicator */}
              {activeTab === tab.id && (
                <span className="ml-1 text-xs bg-emerald-200 px-1 rounded">●</span>
              )}
            </button>
          ))}
        </div>
      </div>
      
      {/* Debug info */}
      <div className="bg-yellow-50 px-4 py-1 text-xs text-yellow-700 border-t border-yellow-200">
        🎯 Active Tab: <strong>{activeTab}</strong> | 
        Status: {loading ? "Loading..." : "Ready"} | 
        Last Updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

export default TabNavigation;