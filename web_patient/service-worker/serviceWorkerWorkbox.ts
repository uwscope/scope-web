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

// @link https://flaviocopes.com/push-api/
// @link https://web.dev/push-notifications-handling-messages/
self.addEventListener('push', function (event) {
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
