import React, { useState, useEffect, useRef } from 'react';
import { Bell, X, CheckCircle, AlertTriangle, Info, MessageCircle, Mail, Smartphone } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

const NotificationSystem = ({ showTestingPanel = false }) => {
  const [notifications, setNotifications] = useState([]);
  const [isNotificationPanelOpen, setIsNotificationPanelOpen] = useState(false); // Keep closed by default
  const [notificationPermission, setNotificationPermission] = useState('default');
  const [serviceWorkerReady, setServiceWorkerReady] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    initializeNotificationSystem();
    loadDemoNotifications();
    checkServiceWorker();

    const handleClickOutside = (event) => {
      if (isNotificationPanelOpen && !event.target.closest('.notification-system')) {
        setIsNotificationPanelOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);

    // Global event to trigger notifications
    const globalNotify = (e) => {
      const detail = e.detail || {};
      const payload = {
        type: detail.type || 'system',
        title: detail.title || 'Notification',
        message: detail.message || '',
        priority: detail.priority || 'low',
        channel: detail.channel || ['push']
      };
      sendNotification(payload);
    };
    window.addEventListener('crm:notify', globalNotify);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      window.removeEventListener('crm:notify', globalNotify);
    };
  }, [isNotificationPanelOpen]);

  const initializeNotificationSystem = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      setNotificationPermission(permission);
    }
    if (audioRef.current) audioRef.current.volume = 0.5;
  };

  const checkServiceWorker = () => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then(() => setServiceWorkerReady(true));
    }
  };

  const loadDemoNotifications = () => {
    setNotifications([]);
  };

  const playNotificationSound = () => {
    if (audioRef.current) {
      audioRef.current.play().catch(()=>{});
    }
  };

  const showPushNotification = (notification) => {
    if (notificationPermission === 'granted' && 'Notification' in window) {
      const options = {
        body: notification.message,
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        tag: notification.id,
        requireInteraction: notification.priority === 'high',
        data: notification
      };
      const pushNotification = new Notification(notification.title, options);
      pushNotification.onclick = () => {
        window.focus();
        setIsNotificationPanelOpen(true);
        pushNotification.close();
      };
      const autoCloseDelay = notification.priority === 'high' ? 10000 : 5000;
      setTimeout(() => pushNotification.close(), autoCloseDelay);
    }
  };

  const addSystemNotification = (notificationData) => {
    const newNotification = {
      id: Date.now().toString(),
      timestamp: new Date(),
      status: 'unread',
      channel: ['push'],
      ...notificationData
    };
    setNotifications(prev => [newNotification, ...prev]);
  };

  const sendNotification = (notificationData) => {
    const notification = {
      id: Date.now().toString(),
      timestamp: new Date(),
      status: 'unread',
      ...notificationData
    };
    setNotifications(prev => [notification, ...prev]);
    playNotificationSound();
    if ((notification.channel||[]).includes('push')) showPushNotification(notification);
    return notification;
  };

  const markAsRead = (notificationId) => {
    setNotifications(prev => prev.map(n => n.id === notificationId ? { ...n, status: 'read' } : n));
  };

  const clearAllNotifications = () => setNotifications([]);

  const unreadCount = notifications.filter(n => n.status === 'unread').length;

  return (
    <div className="notification-system">
      <audio ref={audioRef} preload="auto">
        <source src="/sounds/notification.mp3" type="audio/mpeg" />
      </audio>
      <div className="relative">
        <Button variant="ghost" size="sm" className="relative" onClick={() => setIsNotificationPanelOpen(!isNotificationPanelOpen)}>
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge className="absolute -top-2 -right-2 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </Badge>
          )}
        </Button>
        {isNotificationPanelOpen && (
          <div className="absolute right-0 top-12 w-96 max-h-96 overflow-y-auto bg-white border border-gray-200 rounded-lg shadow-lg z-[9999]">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
              <div className="flex gap-2">
                {notifications.length>0 && <Button variant="outline" size="sm" onClick={clearAllNotifications}>Clear All</Button>}
                <Button variant="ghost" size="sm" onClick={()=>setIsNotificationPanelOpen(false)}><X className="h-4 w-4" /></Button>
              </div>
            </div>
            <div className="max-h-80 overflow-y-auto">
              {notifications.length===0 ? (
                <div className="p-6 text-center text-gray-500">No notifications</div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {notifications.map(n => (
                    <div key={n.id} className={`p-3 ${n.status==='unread'?'bg-blue-50':''}`} onClick={()=>markAsRead(n.id)}>
                      <div className="text-sm font-medium">{n.title}</div>
                      <div className="text-xs text-gray-600">{n.message}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default NotificationSystem
