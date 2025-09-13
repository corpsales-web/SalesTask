import React, { useState, useEffect } from 'react';
import axios from 'axios';

const LeadActionsPanel = ({ leadId, leadData, onActionComplete, initialActionType }) => {
  const [actions, setActions] = useState([]);
  const [actionHistory, setActionHistory] = useState([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [showActionModal, setShowActionModal] = useState(false);
  const [selectedAction, setSelectedAction] = useState(null);
  const [actionData, setActionData] = useState({});
  
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    if (leadId) {
      fetchAvailableActions();
      fetchActionHistory();
    }
  }, [leadId]);

  useEffect(() => {
    // If initialActionType is provided, auto-open the action modal
    if (initialActionType && actions.length > 0) {
      const action = actions.find(a => a.type === initialActionType);
      if (action) {
        handleActionClick(action);
      }
    }
  }, [initialActionType, actions]);

  const fetchAvailableActions = () => {
    // Get available actions based on lead data
    const availableActions = [];

    // Call action - always available if phone exists
    if (leadData?.phone) {
      availableActions.push({
        type: 'call',
        label: 'Call',
        icon: '📞',
        color: 'blue',
        enabled: true
      });
    }

    // WhatsApp action - available if phone exists
    if (leadData?.phone) {
      availableActions.push({
        type: 'whatsapp',
        label: 'WhatsApp',
        icon: '💬',
        color: 'green',
        enabled: true
      });
    }

    // Email action - available if email exists
    if (leadData?.email) {
      availableActions.push({
        type: 'email',
        label: 'Send Email',
        icon: '📧',
        color: 'red',
        enabled: true
      });
    }

    // Send Images - always available
    availableActions.push({
      type: 'send_images',
      label: 'Send Images',
      icon: '🖼️',
      color: 'purple',
      enabled: true
    });

    // Send Catalogue - always available
    availableActions.push({
      type: 'send_catalogue',
      label: 'Send Catalogue',
      icon: '📋',
      color: 'orange',
      enabled: true
    });

    // Meeting - available for qualified leads
    if (leadData?.status && ['qualified', 'proposal', 'negotiation'].includes(leadData.status)) {
      availableActions.push({
        type: 'meeting',
        label: 'Schedule Meeting',
        icon: '🤝',
        color: 'teal',
        enabled: true
      });
    }

    // Follow-up - always available
    availableActions.push({
      type: 'follow_up',
      label: 'Follow Up',
      icon: '🔄',
      color: 'gray',
      enabled: true
    });

    // Add Remark - always available
    availableActions.push({
      type: 'remark',
      label: 'Add Remark',
      icon: '💭',
      color: 'yellow',
      enabled: true
    });

    setActions(availableActions);
  };

  const fetchActionHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE_URL}/api/leads/${leadId}/actions`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      setActionHistory(response.data.actions || []);
    } catch (error) {
      console.error('Error fetching action history:', error);
    }
  };

  const handleActionClick = (action) => {
    setSelectedAction(action);
    setActionData({});
    setShowActionModal(true);
  };

  const executeAction = async () => {
    if (!selectedAction) return;

    setIsExecuting(true);
    try {
      const token = localStorage.getItem('token');
      
      const requestData = {
        action_type: selectedAction.type,
        ...actionData
      };

      const response = await axios.post(
        `${API_BASE_URL}/api/leads/${leadId}/actions`,
        requestData,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      // Refresh action history
      await fetchActionHistory();
      
      setShowActionModal(false);
      setSelectedAction(null);
      setActionData({});

      if (onActionComplete) {
        onActionComplete(response.data);
      }

      // Show success message
      alert(`${selectedAction.label} executed successfully!`);

    } catch (error) {
      console.error('Error executing action:', error);
      alert(`Error executing ${selectedAction.label}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsExecuting(false);
    }
  };

  const renderActionForm = () => {
    if (!selectedAction) return null;

    switch (selectedAction.type) {
      case 'call':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Call Duration (minutes)
              </label>
              <input
                type="number"
                min="0"
                value={actionData.duration || ''}
                onChange={(e) => setActionData({ ...actionData, duration: parseInt(e.target.value) })}
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder="Duration in minutes"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Call Outcome
              </label>
              <select
                value={actionData.outcome || ''}
                onChange={(e) => setActionData({ ...actionData, outcome: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="">Select outcome</option>
                <option value="answered">Answered</option>
                <option value="no_answer">No Answer</option>
                <option value="busy">Busy</option>
                <option value="voicemail">Voicemail</option>
                <option value="wrong_number">Wrong Number</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <textarea
                value={actionData.notes || ''}
                onChange={(e) => setActionData({ ...actionData, notes: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
                rows="3"
                placeholder="Call notes..."
              />
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={actionData.follow_up_required || false}
                onChange={(e) => setActionData({ ...actionData, follow_up_required: e.target.checked })}
                className="mr-2"
              />
              <label className="text-sm text-gray-700">Follow-up required</label>
            </div>
          </div>
        );

      case 'whatsapp':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Message *
              </label>
              <textarea
                value={actionData.message || ''}
                onChange={(e) => setActionData({ ...actionData, message: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
                rows="4"
                placeholder="WhatsApp message..."
                required
              />
            </div>
          </div>
        );

      case 'email':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject *
              </label>
              <input
                type="text"
                value={actionData.subject || ''}
                onChange={(e) => setActionData({ ...actionData, subject: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder="Email subject"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Message *
              </label>
              <textarea
                value={actionData.message || ''}
                onChange={(e) => setActionData({ ...actionData, message: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
                rows="6"
                placeholder="Email message..."
                required
              />
            </div>
          </div>
        );

      case 'send_images':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Delivery Method
              </label>
              <select
                value={actionData.method || 'whatsapp'}
                onChange={(e) => setActionData({ ...actionData, method: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="whatsapp">WhatsApp</option>
                <option value="email">Email</option>
                <option value="both">Both</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Message
              </label>
              <textarea
                value={actionData.message || 'Please find the attached images'}
                onChange={(e) => setActionData({ ...actionData, message: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
                rows="3"
                placeholder="Message to accompany images..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Images (Placeholder)
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                <p className="text-gray-500">Image selection will be integrated with file upload service</p>
              </div>
            </div>
          </div>
        );

      case 'send_catalogue':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Catalogue Type
              </label>
              <select
                value={actionData.catalogue_type || 'general'}
                onChange={(e) => setActionData({ ...actionData, catalogue_type: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="general">General Catalogue</option>
                <option value="residential">Residential Projects</option>
                <option value="commercial">Commercial Projects</option>
                <option value="luxury">Luxury Collection</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Delivery Method
              </label>
              <select
                value={actionData.method || 'email'}
                onChange={(e) => setActionData({ ...actionData, method: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="email">Email</option>
                <option value="whatsapp">WhatsApp</option>
                <option value="both">Both</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Message
              </label>
              <textarea
                value={actionData.message || 'Please find our product catalogue attached'}
                onChange={(e) => setActionData({ ...actionData, message: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
                rows="3"
                placeholder="Message to accompany catalogue..."
              />
            </div>
          </div>
        );

      case 'meeting':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Meeting Title *
              </label>
              <input
                type="text"
                value={actionData.title || `Meeting with ${leadData?.name || 'Client'}`}
                onChange={(e) => setActionData({ ...actionData, title: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder="Meeting title"
                required
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date *
                </label>
                <input
                  type="date"
                  value={actionData.date || ''}
                  onChange={(e) => setActionData({ ...actionData, date: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded-md"
                  required
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Time *
                </label>
                <input
                  type="time"
                  value={actionData.time || ''}
                  onChange={(e) => setActionData({ ...actionData, time: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded-md"
                  required
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Duration (minutes)
              </label>
              <input
                type="number"
                min="15"
                step="15"
                value={actionData.duration || 60}
                onChange={(e) => setActionData({ ...actionData, duration: parseInt(e.target.value) })}
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder="Duration in minutes"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Meeting Type
              </label>
              <select
                value={actionData.type || 'online'}
                onChange={(e) => setActionData({ ...actionData, type: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="online">Online</option>
                <option value="offline">In-Person</option>
              </select>
            </div>
            
            {actionData.type === 'offline' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <input
                  type="text"
                  value={actionData.location || ''}
                  onChange={(e) => setActionData({ ...actionData, location: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded-md"
                  placeholder="Meeting location"
                />
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Agenda
              </label>
              <textarea
                value={actionData.agenda || ''}
                onChange={(e) => setActionData({ ...actionData, agenda: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
                rows="3"
                placeholder="Meeting agenda..."
              />
            </div>
          </div>
        );

      case 'follow_up':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Follow-up Type
              </label>
              <select
                value={actionData.type || 'general'}
                onChange={(e) => setActionData({ ...actionData, type: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="general">General Follow-up</option>
                <option value="quotation">Quotation Follow-up</option>
                <option value="meeting">Meeting Follow-up</option>
                <option value="payment">Payment Follow-up</option>
                <option value="documentation">Documentation</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                value={actionData.priority || 'medium'}
                onChange={(e) => setActionData({ ...actionData, priority: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Due Date
              </label>
              <input
                type="date"
                value={actionData.due_date || ''}
                onChange={(e) => setActionData({ ...actionData, due_date: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <textarea
                value={actionData.notes || ''}
                onChange={(e) => setActionData({ ...actionData, notes: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
                rows="4"
                placeholder="Follow-up notes..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Reminder (minutes before due date)
              </label>
              <select
                value={actionData.reminder_before || 60}
                onChange={(e) => setActionData({ ...actionData, reminder_before: parseInt(e.target.value) })}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value={15}>15 minutes</option>
                <option value={30}>30 minutes</option>
                <option value={60}>1 hour</option>
                <option value={120}>2 hours</option>
                <option value={1440}>1 day</option>
              </select>
            </div>
          </div>
        );

      default:
        return (
          <div className="text-center py-4">
            <p className="text-gray-500">Action form not implemented yet</p>
          </div>
        );
    }
  };

  const formatDateTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getActionIcon = (actionType) => {
    const iconMap = {
      call: '📞',
      whatsapp: '💬',
      email: '📧',
      send_images: '🖼️',
      send_catalogue: '📋',
      meeting: '🤝',
      follow_up: '🔄',
      remark_added: '💭',
      update: '✏️'
    };
    return iconMap[actionType] || '📝';
  };

  return (
    <div className="lead-actions-panel">
      {/* Available Actions */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Available Actions</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {actions.map((action) => (
            <button
              key={action.type}
              onClick={() => handleActionClick(action)}
              disabled={!action.enabled}
              className={`
                p-3 rounded-lg text-center transition-all duration-200 border-2
                ${action.enabled
                  ? `bg-${action.color}-50 border-${action.color}-200 hover:bg-${action.color}-100 hover:border-${action.color}-300 text-${action.color}-700`
                  : 'bg-gray-50 border-gray-200 text-gray-400 cursor-not-allowed'
                }
              `}
            >
              <div className="text-2xl mb-1">{action.icon}</div>
              <div className="text-sm font-medium">{action.label}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Action History */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Actions</h3>
        {actionHistory.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">📝</div>
            <p>No actions recorded yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {actionHistory.slice(0, 10).map((action) => (
              <div key={action.id} className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">{getActionIcon(action.action_type)}</div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-900 capitalize">
                          {action.action_type.replace('_', ' ')}
                        </span>
                        <span className={`
                          px-2 py-1 text-xs rounded-full
                          ${action.status === 'completed' ? 'bg-green-100 text-green-800' :
                            action.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'}
                        `}>
                          {action.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {formatDateTime(action.timestamp)}
                      </p>
                      {action.user && (
                        <p className="text-xs text-gray-500">
                          by {action.user.full_name}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {actionHistory.length > 10 && (
              <div className="text-center py-2">
                <button className="text-sm text-blue-600 hover:text-blue-800">
                  View all actions ({actionHistory.length})
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Action Modal */}
      {showActionModal && selectedAction && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {selectedAction.icon} {selectedAction.label}
                </h3>
                <button
                  onClick={() => setShowActionModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="mb-6">
                {renderActionForm()}
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowActionModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                
                <button
                  onClick={executeAction}
                  disabled={isExecuting}
                  className={`
                    px-4 py-2 text-sm font-medium text-white rounded-md
                    ${isExecuting
                      ? 'bg-gray-400 cursor-not-allowed'
                      : `bg-${selectedAction.color}-600 hover:bg-${selectedAction.color}-700`
                    }
                  `}
                >
                  {isExecuting ? 'Executing...' : `Execute ${selectedAction.label}`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LeadActionsPanel;