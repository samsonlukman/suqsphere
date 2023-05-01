if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/static/network/service-worker.js').then(function(registration) {
      console.log('ServiceWorker registration successful with scope: ', registration.scope);
      if (Notification.permission === 'granted') {
        registration.pushManager.subscribe({userVisibleOnly: true})
          .then(function(subscription) {
            console.log(subscription.endpoint);
            console.log(subscription.getKey('p256dh'));
            console.log(subscription.getKey('auth'));
          })
          .catch(function(error) {
            console.error('Error occurred while subscribing to push notifications:', error);
          });
      }
    }, function(err) {
      console.log('ServiceWorker registration failed: ', err);
    });
  });
}

self.addEventListener('push', event => {
  const payload = event.data.json();
  const title = payload.title;
  const options = {
    body: payload.body,
    icon: payload.icon,
    badge: payload.badge,
    data: { url: payload.url }
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', event => {
  const url = event.notification.data.url;
  event.waitUntil(clients.openWindow(url));
});

self.addEventListener('pushsubscriptionchange', event => {
  event.waitUntil(
    self.registration.pushManager.subscribe(event.oldSubscription.options)
      .then(subscription => {
        fetch('/subscribe', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(subscription)
        });
      })
  );
});
