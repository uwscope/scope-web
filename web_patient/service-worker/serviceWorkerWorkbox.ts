/// <reference lib="webworker" />
import { createHandlerBoundToURL, precacheAndRoute } from 'workbox-precaching';
import { registerRoute, NavigationRoute } from 'workbox-routing';

import { skipWaiting, clientsClaim } from 'workbox-core';

// ServiceWorkerGlobalScope is a type from the workbox-precaching module
declare const self: Window & ServiceWorkerGlobalScope;

// tells the Service Worker to skip the waiting state and become active.
skipWaiting();
clientsClaim();

precacheAndRoute(self.__WB_MANIFEST);

const handler = createHandlerBoundToURL('/index.html');
const navigationRoute = new NavigationRoute(handler, {
    denylist: [/^\/_/, /\/[^/?]+\.[^/]+$/],
});
registerRoute(navigationRoute);

self.addEventListener('install', function (event) {
    console.info('Service Worker installing.');
});

self.addEventListener('activate', function (event) {
    console.info('Service Worker activating.');
});

// @link https://flaviocopes.com/push-api/
// @link https://web.dev/push-notifications-handling-messages/
self.addEventListener('push', function (event) {
    console.info('Push event called.');
    if (!event.data) {
        console.log('This push event has no data.');
        return;
    }
    if (!self.registration) {
        console.log('Service worker does not control the page');
        return;
    }
    if (!self.registration || !self.registration.pushManager) {
        console.log('Push is not supported');
        return;
    }

    const eventText = event.data.text();
    // Specify default options
    let options = {};
    let title = '';

    // Support both plain text notification and json
    if (eventText.substr(0, 1) === '{') {
        const eventData = JSON.parse(eventText);
        title = eventData.title;

        // Set specific options
        // @link https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration/showNotification#parameters
        if (eventData.options) {
            options = Object.assign(options, eventData.options);
        }

        // Check expiration if specified
        if (eventData.expires && Date.now() > eventData.expires) {
            console.log('Push notification has expired');
            return;
        }
    } else {
        title = eventText;
    }

    // Warning: this can fail silently if notifications are disabled at system level
    // The promise itself resolve to undefined and is not helpful to see if it has been displayed properly
    const promiseChain = self.registration.showNotification(title, options);

    // With this, the browser will keep the service worker running until the promise you passed in has settled.
    event.waitUntil(promiseChain);
});

self.addEventListener('pushsubscriptionchange', (event) => {
    // TODO: Renew your subscription here.
    // Implementation Idea: postMessage with new subscription information to NotificationsPage componenent and updateSubscription.
    // TODO: Unclear how to test this logic.
    console.log('pushsubscriptionchange');
    console.log(event);
});

// TODO: Investigate if app can be opened when clicked on notification.
// self.addEventListener('notificationclick', (event) => {
//     console.log('This is custom service worker notificationclick method.');
//     console.log('Notification details: ', event.notification);
//     // Write the code to open
//     if (event.notification.data.url) {
//         event.waitUntil(self.clients.openWindow(event.notification.data.url));
//     }
// });

// self.addEventListener('pushsubscriptionchange', function (event) {
//     event.waitUntil(
//         fetch('https://pushpad.xyz/pushsubscriptionchange', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({
//                 old_endpoint: event.oldSubscription ? event.oldSubscription.endpoint : null,
//                 new_endpoint: event.newSubscription ? event.newSubscription.endpoint : null,
//                 new_p256dh: event.newSubscription ? event.newSubscription.toJSON().keys.p256dh : null,
//                 new_auth: event.newSubscription ? event.newSubscription.toJSON().keys.auth : null,
//             }),
//         }),
//     );
// });
