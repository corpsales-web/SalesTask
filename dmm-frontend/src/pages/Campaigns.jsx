import React, { useState } from 'react'
import { api } from '../api'

const CHANNELS = [
  { id: 'google_ads', label: 'Google Ads', icon: '🔍' },
  { id: 'facebook_ads', label: 'Facebook Ads', icon: '📘' },
  { id: 'instagram_ads', label: 'Instagram Ads', icon: '📸' },
  { id: 'youtube_ads', label: 'YouTube Ads', icon: '📺' },
  { id: 'linkedin_ads', label: 'LinkedIn Ads', icon: '💼' },
  { id: 'email_marketing', label: 'Email Marketing', icon: '📧' },
  { id: 'sms_marketing', label: 'SMS Marketing', icon: '💬' },
  { id: 'influencer_marketing', label: 'Influencer Marketing', icon: '⭐' }
]

export default function Campaigns() {
  const [isLoading, setIsLoading] = useState(false)
  const [campaign, setCampaign] = useState(null)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    campaign_name: '',
    objective: '',
    target_audience: '',
    budget: '',
    channels: [],
    duration_days: 30
  })
  const [budgetSplits, setBudgetSplits] = useState({})

  const handleChannelToggle = (channelId) => {
    const isSelected = formData.channels.includes(channelId)
    const newChannels = isSelected
      ? formData.channels.filter(c => c !== channelId)
      : [...formData.channels, channelId]
    
    setFormData({...formData, channels: newChannels})
    
    // Auto-distribute budget equally among selected channels
    if (formData.budget && newChannels.length > 0) {
      const budgetPerChannel = parseFloat(formData.budget) / newChannels.length
      const newSplits = {}
      newChannels.forEach(channel => {
        newSplits[channel] = budgetPerChannel.toFixed(2)
      })
      setBudgetSplits(newSplits)
    }
  }

  const updateBudgetSplit = (channelId, amount) => {
    setBudgetSplits({...budgetSplits, [channelId]: amount})
  }

  const getTotalAllocated = () => {
    return Object.values(budgetSplits).reduce((sum, amount) => sum + parseFloat(amount || 0), 0)
  }

  const optimizeCampaign = async () => {
    if (!formData.campaign_name || !formData.objective || !formData.target_audience || !formData.budget || formData.channels.length === 0) {
      setError('Please fill in all required fields and select at least one channel')
      return
    }

    const totalBudget = parseFloat(formData.budget)
    const allocatedBudget = getTotalAllocated()
    
    if (Math.abs(totalBudget - allocatedBudget) > 1) {
      setError(`Budget mismatch: Total budget $${totalBudget} but allocated $${allocatedBudget.toFixed(2)}`)
      return
    }

    setIsLoading(true)
    setError('')
    
    try {
      const campaignData = {
        ...formData,
        budget: totalBudget,
        budget_splits: budgetSplits
      }
      
      const response = await api.post('/api/ai/optimize-campaign', campaignData)
      setCampaign(response.data.campaign)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to optimize campaign')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="campaigns-page">
      <div className="page-header">
        <h1>AI Campaign Manager</h1>
        <p>Optimize your marketing campaigns with GPT-5 beta intelligence</p>
      </div>

      <div className="campaign-form">
        <div className="form-grid">
          <div className="form-group">
            <label>Campaign Name *</label>
            <input
              type="text"
              value={formData.campaign_name}
              onChange={(e) => setFormData({...formData, campaign_name: e.target.value})}
              placeholder="Enter campaign name"
            />
          </div>

          <div className="form-group">
            <label>Campaign Objective *</label>
            <select
              value={formData.objective}
              onChange={(e) => setFormData({...formData, objective: e.target.value})}
            >
              <option value="">Select Objective</option>
              <option value="brand_awareness">Brand Awareness</option>
              <option value="lead_generation">Lead Generation</option>
              <option value="sales_conversion">Sales Conversion</option>
              <option value="traffic_increase">Website Traffic</option>
              <option value="engagement">Engagement</option>
              <option value="app_installs">App Installs</option>
            </select>
          </div>

          <div className="form-group">
            <label>Target Audience *</label>
            <input
              type="text"
              value={formData.target_audience}
              onChange={(e) => setFormData({...formData, target_audience: e.target.value})}
              placeholder="Describe your target audience"
            />
          </div>

          <div className="form-group">
            <label>Total Budget ($) *</label>
            <input
              type="number"
              value={formData.budget}
              onChange={(e) => setFormData({...formData, budget: e.target.value})}
              placeholder="Enter total budget"
            />
          </div>

          <div className="form-group">
            <label>Duration (Days)</label>
            <input
              type="number"
              value={formData.duration_days}
              onChange={(e) => setFormData({...formData, duration_days: parseInt(e.target.value)})}
              placeholder="Campaign duration"
            />
          </div>
        </div>

        <div className="form-group">
          <label>Marketing Channels *</label>
          <div className="channels-grid">
            {CHANNELS.map(channel => (
              <div 
                key={channel.id}
                className={`channel-card ${formData.channels.includes(channel.id) ? 'selected' : ''}`}
                onClick={() => handleChannelToggle(channel.id)}
              >
                <span className="channel-icon">{channel.icon}</span>
                <span className="channel-label">{channel.label}</span>
                {formData.channels.includes(channel.id) && (
                  <div className="budget-input" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="number"
                      value={budgetSplits[channel.id] || ''}
                      onChange={(e) => updateBudgetSplit(channel.id, e.target.value)}
                      placeholder="Budget"
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {formData.channels.length > 0 && formData.budget && (
          <div className="budget-summary">
            <p><strong>Total Budget:</strong> ${formData.budget}</p>
            <p><strong>Allocated:</strong> ${getTotalAllocated().toFixed(2)}</p>
            <p><strong>Remaining:</strong> ${(parseFloat(formData.budget) - getTotalAllocated()).toFixed(2)}</p>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        <button 
          onClick={optimizeCampaign}
          disabled={isLoading}
          className="optimize-btn"
        >
          {isLoading ? 'Optimizing Campaign...' : 'Optimize Campaign with AI'}
        </button>
      </div>

      {campaign && (
        <div className="campaign-result">
          <h2>Optimized Campaign</h2>
          <div className="campaign-content">
            <div className="campaign-meta">
              <p><strong>Campaign:</strong> {campaign.campaign_name}</p>
              <p><strong>Objective:</strong> {campaign.objective}</p>
              <p><strong>Budget:</strong> ${campaign.budget}</p>
              <p><strong>Duration:</strong> {campaign.duration_days} days</p>
              <p><strong>Optimized:</strong> {new Date(campaign.created_at).toLocaleString()}</p>
            </div>
            <div className="optimization-details">
              <pre>{campaign.ai_optimization}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}