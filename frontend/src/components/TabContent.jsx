import React, { useMemo } from 'react';
import { useTab } from '../contexts/TabContext';

// Import all the existing components
import FaceCheckInComponent from './FaceCheckInComponent';
import LeadActionsPanel from './LeadActionsPanel';
import VoiceSTTComponent from './VoiceSTTComponent';
import RoleManagementPanel from './RoleManagementPanel';
import FileUploadComponent from './FileUploadComponent';
import WorkflowAuthoringPanel from './WorkflowAuthoringPanel';
import LeadRoutingPanel from './LeadRoutingPanel';
import DigitalMarketingDashboard from './DigitalMarketingDashboard';
import BulkExcelUploadComponent from './BulkExcelUploadComponent';
import NotificationSystem from './NotificationSystem';
import CameraComponent from './CameraComponent';
import EnhancedPipelineSystem from './EnhancedPipelineSystem';

const TabContent = ({ 
  dashboardStats,
  leads,
  tasks,
  showLeadActionsPanel,
  selectedLead,
  setShowLeadActionsPanel,
  onActionComplete
}) => {
  const { activeTab, lastUpdated } = useTab();
  
  console.log(`🎯 TAB CONTENT RENDERING: ${activeTab} at ${new Date(lastUpdated).toLocaleTimeString()}`);
  
  // Memoize content to ensure it updates when activeTab changes
  const content = useMemo(() => {
    console.log(`📝 GENERATING CONTENT FOR: ${activeTab}`);
    
    switch(activeTab) {
      case 'dashboard':
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <div className="flex items-center">
                <span className="text-blue-600 text-lg mr-2">📊</span>
                <div>
                  <h3 className="font-semibold text-blue-800">Dashboard Active</h3>
                  <p className="text-blue-600 text-sm">Showing overview and statistics</p>
                </div>
              </div>
            </div>
            
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow border">
                <div className="flex items-center">
                  <div className="text-2xl font-bold text-blue-600">{dashboardStats?.totalLeads || 0}</div>
                  <div className="ml-2 text-sm text-gray-600">Total Leads</div>
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow border">
                <div className="flex items-center">
                  <div className="text-2xl font-bold text-green-600">{dashboardStats?.activeLeads || 0}</div>
                  <div className="ml-2 text-sm text-gray-600">Active Leads</div>
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow border">
                <div className="flex items-center">
                  <div className="text-2xl font-bold text-purple-600">{dashboardStats?.conversionRate || 0}%</div>
                  <div className="ml-2 text-sm text-gray-600">Conversion Rate</div>
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow border">
                <div className="flex items-center">
                  <div className="text-2xl font-bold text-orange-600">{dashboardStats?.pendingTasks || 0}</div>
                  <div className="ml-2 text-sm text-gray-600">Pending Tasks</div>
                </div>
              </div>
            </div>
            
            {/* Recent Leads */}
            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold mb-4">Recent Leads</h3>
              <div className="space-y-3">
                {leads?.slice(0, 5).map((lead) => (
                  <div key={lead.id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <div>
                      <div className="font-medium">{lead.name}</div>
                      <div className="text-sm text-gray-600">{lead.email}</div>
                    </div>
                    <div className="text-sm text-gray-500">{lead.status}</div>
                  </div>
                )) || <div className="text-gray-500">No leads available</div>}
              </div>
            </div>
          </div>
        );
        
      case 'leads':
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <div className="flex items-center">
                <span className="text-blue-600 text-lg mr-2">🎯</span>
                <div>
                  <h3 className="font-semibold text-blue-800">Lead Management Active</h3>
                  <p className="text-blue-600 text-sm">Managing leads and prospects</p>
                </div>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Lead Management</h2>
                <p className="text-gray-600">Manage your leads and prospects</p>
              </div>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                Add Lead
              </button>
            </div>
            
            <div className="grid gap-4">
              {leads?.map((lead) => (
                <div key={lead.id} className="bg-white p-4 rounded-lg shadow border">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold">{lead.name}</h3>
                      <p className="text-gray-600">{lead.email}</p>
                      <p className="text-sm text-gray-500">{lead.phone}</p>
                    </div>
                    <div className="flex space-x-2">
                      <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                        Call
                      </button>
                      <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                        Email
                      </button>
                      <button className="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700">
                        Images
                      </button>
                    </div>
                  </div>
                </div>
              )) || <div className="text-gray-500 p-4">No leads available</div>}
            </div>
          </div>
        );
      
      case 'pipeline':
        return (
          <div className="space-y-6">
            <div className="bg-orange-50 p-3 rounded-lg border border-orange-200">
              <div className="flex items-center">
                <span className="text-orange-600 text-lg mr-2">📊</span>
                <div>
                  <h3 className="font-semibold text-orange-800">Enhanced Sales Pipeline</h3>
                  <p className="text-orange-600 text-sm">AI-powered pipeline with deal prediction and advanced analytics</p>
                </div>
              </div>
            </div>
            
            {/* Enhanced Pipeline System */}
            <EnhancedPipelineSystem />
          </div>
        );
      
      case 'tasks':
        return (
          <div className="space-y-6">
            <div className="bg-green-50 p-3 rounded-lg border border-green-200">
              <div className="flex items-center">
                <span className="text-green-600 text-lg mr-2">✅</span>
                <div>
                  <h3 className="font-semibold text-green-800">Enhanced Task Management</h3>
                  <p className="text-green-600 text-sm">Multi-user collaboration with AI automation and voice tasks</p>
                </div>
              </div>
            </div>
            
            {/* Enhanced Task System */}
            <EnhancedTaskSystem />
          </div>
        );
        
      case 'hrms':
        return (
          <div className="space-y-6">
            <div className="bg-purple-50 p-3 rounded-lg border border-purple-200">
              <div className="flex items-center">
                <span className="text-purple-600 text-lg mr-2">👥</span>
                <div>
                  <h3 className="font-semibold text-purple-800">Enhanced HRMS - Full Suite!</h3>
                  <p className="text-purple-600 text-sm">Complete HR management with face check-in, leave management, and reporting</p>
                </div>
              </div>
            </div>
            
            {/* Enhanced HRMS System */}
            <EnhancedHRMSSystem />
          </div>
        );
        
      case 'erp':
        return (
          <div className="space-y-6">
            <div className="bg-indigo-50 p-3 rounded-lg border border-indigo-200">
              <div className="flex items-center">
                <span className="text-indigo-600 text-lg mr-2">🏢</span>
                <div>
                  <h3 className="font-semibold text-indigo-800">ERP Active</h3>
                  <p className="text-indigo-600 text-sm">Business management and operations</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Business Management & Operations</h2>
                <p className="text-gray-600">Manage business processes and operations</p>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold mb-4">File Upload</h3>
              <FileUploadComponent />
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow border">
                <h3 className="text-lg font-semibold mb-4">Project Gallery</h3>
                <p className="text-gray-600">Manage project files and documents</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow border">
                <h3 className="text-lg font-semibold mb-4">Product Catalog</h3>
                <p className="text-gray-600">Manage product information and inventory</p>
              </div>
            </div>
          </div>
        );
        
      case 'ai':
        return (
          <div className="space-y-6">
            <div className="bg-cyan-50 p-3 rounded-lg border border-cyan-200">
              <div className="flex items-center">
                <span className="text-cyan-600 text-lg mr-2">🤖</span>
                <div>
                  <h3 className="font-semibold text-cyan-800">AI Assistant Active</h3>
                  <p className="text-cyan-600 text-sm">AI-powered insights and automation</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">AI Assistant</h2>
                <p className="text-gray-600">AI-powered insights and automation</p>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow border">
              <WorkflowAuthoringPanel />
            </div>
          </div>
        );
        
      case 'admin':
        return (
          <div className="space-y-6">
            <div className="bg-red-50 p-3 rounded-lg border border-red-200">
              <div className="flex items-center">
                <span className="text-red-600 text-lg mr-2">⚙️</span>
                <div>
                  <h3 className="font-semibold text-red-800">Admin Panel Active</h3>
                  <p className="text-red-600 text-sm">System administration and settings</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Super Admin Panel</h2>
                <p className="text-gray-600">System administration and settings</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow border">
                <RoleManagementPanel />
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow border">
                <NotificationSystem showTestingPanel={true} />
              </div>
            </div>
          </div>
        );
        
      default:
        return (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">❓</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Unknown Tab</h2>
            <p className="text-gray-600">The tab "{activeTab}" is not recognized.</p>
          </div>
        );
    }
  }, [activeTab, dashboardStats, leads, tasks, lastUpdated]);
  
  return (
    <div key={`${activeTab}-${lastUpdated}`} className="tab-content-wrapper">
      {content}
      
      {/* Lead Actions Panel Modal */}
      {showLeadActionsPanel && selectedLead && (
        <LeadActionsPanel 
          leadId={selectedLead.id}
          leadData={selectedLead}
          onActionComplete={onActionComplete}
        />
      )}
    </div>
  );
};

export default TabContent;