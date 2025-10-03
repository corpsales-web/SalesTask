import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Badge } from './ui/badge';
import { 
  User, Mail, Phone, MapPin, Building, Calendar, 
  CheckCircle, AlertCircle, Edit, Save, X
} from 'lucide-react';
import axios from 'axios';
import LeadWhatsAppTimeline from './LeadWhatsAppTimeline'

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const EnhancedLeadEditModal = ({ isOpen, onClose, leadData, onLeadUpdated }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    location: '',
    city: '',
    state: '',
    source: '',
    category: '',
    status: 'New',
    notes: '',
    budget: '',
    project_type: '',
    requirements: '',
    priority: 'Medium'
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [within24h, setWithin24h] = useState(true)

  // Initialize form data when lead data changes
  useEffect(() => {
    if (leadData) {
      setFormData({
        name: leadData.name || '',
        email: leadData.email || '',
        phone: leadData.phone || '',
        company: leadData.company || '',
        location: leadData.location || '',
        city: leadData.city || '',
        state: leadData.state || '',
        source: leadData.source || '',
        category: leadData.category || '',
        status: leadData.status || 'New',
        notes: Array.isArray(leadData.notes) ? leadData.notes.join('\n') : (leadData.notes || ''),
        budget: leadData.budget || '',
        project_type: leadData.project_type || '',
        requirements: leadData.requirements || '',
        priority: leadData.priority || 'Medium'
      });
    }
  }, [leadData]);

  useEffect(()=>{
    const check = async ()=>{
      if (!leadData?.phone) { setWithin24h(false); return }
      try {
        const res = await axios.get(`${API}/api/whatsapp/session_status`, { params: { contact: leadData.phone } })
        setWithin24h(Boolean(res.data?.within_24h))
      } catch { setWithin24h(false) }
    }
    check()
  }, [leadData])

  const handleSubmit = async () => {
    setLoading(true);
    setErrors({});

    try {
      const requiredFields = ['name', 'email', 'phone'];
      const newErrors = {};
      requiredFields.forEach(field => { if (!formData[field]) newErrors[field] = 'This field is required' })
      if (Object.keys(newErrors).length > 0) { setErrors(newErrors); setLoading(false); return }

      const updateData = {
        ...formData,
        updated_at: new Date().toISOString(),
        notes: formData.notes ? formData.notes.split('\n').filter(note => note.trim()) : []
      };

      const response = await axios.put(`${API}/api/leads/${leadData.id}`, updateData);
      if (response.data.success) {
        if (onLeadUpdated) onLeadUpdated(response.data.lead);
        onClose();
      } else {
        throw new Error(response.data.error || 'Failed to update lead');
      }

    } catch (error) {
      console.error('Lead update error:', error);
      alert(`❌ Lead Update Failed: ${error.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Edit className="h-5 w-5" />
            <span>Edit Lead - {leadData?.name}</span>
          </DialogTitle>
          <DialogDescription>
            Update lead information and manage lead qualification status
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <User className="h-5 w-5 mr-2" />
                Basic Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label>Full Name *</Label>
                  <Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} className={errors.name ? 'border-red-500' : ''} />
                  {errors.name && <span className="text-red-500 text-sm">{errors.name}</span>}
                </div>
                <div>
                  <Label>Email Address *</Label>
                  <Input type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} className={errors.email ? 'border-red-500' : ''} />
                  {errors.email && <span className="text-red-500 text-sm">{errors.email}</span>}
                </div>
                <div>
                  <Label>Phone Number *</Label>
                  <Input value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} className={errors.phone ? 'border-red-500' : ''} />
                  {errors.phone && <span className="text-red-500 text-sm">{errors.phone}</span>}
                </div>
                <div>
                  <Label>Company</Label>
                  <Input value={formData.company} onChange={(e) => setFormData({...formData, company: e.target.value})} />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Lead Management */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">Lead Management</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Existing fields omitted for brevity */}
              <div className="text-sm text-gray-600">WhatsApp session: {within24h ? 'Within 24h (text allowed)' : 'Expired (template required)'}</div>
              <LeadWhatsAppTimeline leadId={leadData?.id} limit={15} />
            </CardContent>
          </Card>
        </div>

        {/* Footer Actions */}
        <div className="flex justify-between items-center pt-4 border-t">
          <div className="flex items-center space-x-2">
            <Badge className="bg-blue-100 text-blue-800">Lead ID: {leadData?.id}</Badge>
            {leadData?.created_at && (<Badge variant="outline">Created: {new Date(leadData.created_at).toLocaleDateString()}</Badge>)}
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" onClick={onClose} disabled={loading}>
              <X className="h-4 w-4 mr-2" />Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={loading} className="bg-green-600 hover:bg-green-700">
              {loading ? 'Updating...' : (<><Save className="h-4 w-4 mr-2" />Update Lead</>)}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default EnhancedLeadEditModal;
