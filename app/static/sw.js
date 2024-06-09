'use strict';

/* eslint-enable max-len */

self.addEventListener('install', function(event) {
  console.log('Service Worker installing.');
});

self.addEventListener('activate', function(event) {
  console.log('Service Worker activating.');
});

self.addEventListener('push', function(event) {
  console.log('[Service Worker] Push Received.');
  const pushData = event.data.text();
  console.log([Service Worker] Push received this data - "${pushData}");
  let data, title, body;
  try {
    data = JSON.parse(pushData);
    title = data.title;
    body = data.body;
  } catch(e) {
    title = "Untitled";
    body = pushData;
  }
  const options = {
    body: body
  };
  console.log(title, options);

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

self.addEventListener('pushsubscriptionchange', function(event) {
  console.log('[Service Worker]: \'pushsubscriptionchange\' event fired.');
  const applicationServerPublicKey = localStorage.getItem('applicationServerPublicKey');
  const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
  event.waitUntil(
    self.registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: applicationServerKey
    })
    .then(function(newSubscription) {
      fetch('/api/update-subscription', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          old_endpoint: event.oldSubscription ? event.oldSubscription.endpoint : null,
          new_endpoint: event.newSubscription ? event.newSubscription.endpoint : null,
          new_p256dh: event.newSubscription ? event.newSubscription.toJSON().keys.p256dh : null,
          new_auth: event.newSubscription ? event.newSubscription.toJSON().keys.auth : null
        })
      })
      console.log('[Service Worker] New subscription: ', newSubscription);
    })
  );
});