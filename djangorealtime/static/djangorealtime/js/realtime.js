(function() {
    'use strict';

    window.DjangoRealtime = {
        connect: function(options) {
            options = options || {};
            const endpoint = options.endpoint || '/realtime/sse/';
            const onMessage = options.onMessage || function() {};
            const onError = options.onError || function() {};
            const onConnect = options.onConnect || function() {};
            const debug = options.debug || false;

            let retryCount = 0;
            const eventSource = new EventSource(endpoint);

            eventSource.onmessage = function(event) {
                retryCount = 0; // Reset on successful message
                if (debug) {
                    console.log('DjangoRealtime - Received:', event.data);
                }

                try {
                    const eventData = JSON.parse(event.data);
                    const eventType = eventData.type || 'message';
                    const eventKey = `djr:${eventType}`;
                    const eventDetail = eventData || {};

                    if (debug) {
                        console.log('DjangoRealtime - Dispatching Event:', eventKey, eventDetail);
                    }

                    // Dispatch custom event
                    const docEvent = new CustomEvent(eventKey, { detail: eventDetail });
                    window.dispatchEvent(docEvent);

                    // If :id is present, also dispatch an id-specific event
                    if (eventDetail[':id'] !== undefined) {
                        const idKey = `${eventKey}:${eventDetail[':id']}`;
                        const idEvent = new CustomEvent(idKey, { detail: eventDetail });
                        window.dispatchEvent(idEvent);

                        if (debug) {
                            console.log('DjangoRealtime - Also dispatching:', idKey);
                        }
                    }

                    // Call user callback
                    onMessage(eventData);

                    // Handle connection event
                    if (eventType === 'connected') {
                        onConnect();
                    }
                } catch (e) {
                    console.error('DjangoRealtime - Error parsing message:', e);
                }
            };

            eventSource.onerror = function(error) {
                console.error('DjangoRealtime - SSE Error:', error);
                onError(error);

                // Manual reconnect backup with exponential backoff
                if (eventSource.readyState === EventSource.CLOSED) {
                    const delay = Math.min(1000 * Math.pow(2, retryCount), 64000);
                    if (debug) {
                        console.log(`DjangoRealtime - Attempting to reconnect in ${delay} ms`);
                    }
                    retryCount++;
                    setTimeout(function() {
                        DjangoRealtime.connect(options);
                    }, delay);
                }
            };

            return eventSource;
        },

        subscribe: function(eventType, callback) {
            const eventKey = `djr:${eventType}`;
            window.addEventListener(eventKey, function(e) {
                callback(e.detail);
            });
        }
    };

    // Auto-connect configuration, __AUTO_CONNECT__ is replaced server-side
    const autoConnect = __AUTO_CONNECT__;

    // Auto-connect if enabled
    if (autoConnect) {
        document.addEventListener('DOMContentLoaded', function() {
            window.djangoRealtimeConnection = DjangoRealtime.connect();
        });
    }
})();