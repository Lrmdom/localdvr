import { useState, useEffect } from 'react';

export const NotificationToggle = () => {
  const [permission, setPermission] = useState(Notification.permission);
  const [subscribed, setSubscribed] = useState(false);

  const requestNotificationPermission = async () => {
    const result = await Notification.requestPermission();
    setPermission(result);
    if (result === 'granted') {
      subscribeToPush();
    }
  };

  const subscribeToPush = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const vapidResponse = await fetch('/api/notifications/vapid-public-key');
      const { publicKey } = await vapidResponse.json();

      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: publicKey,
      });

      await fetch('/api/notifications/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscription),
      });

      setSubscribed(true);
    } catch (err) {
      console.error('Failed to subscribe to push:', err);
    }
  };

  return (
    <div className="notification-toggle">
      {permission !== 'granted' ? (
        <button onClick={requestNotificationPermission}>Enable Notifications</button>
      ) : (
        <span>{subscribed ? 'Notifications Enabled' : 'Notifications Permission Granted'}</span>
      )}
    </div>
  );
};
