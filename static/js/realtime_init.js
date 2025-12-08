// static/js/realtime_init.js (Optional - for even faster loading)
// This tiny script starts real-time updates asynchronously without blocking

(function() {
    'use strict';
    
    // Check if we need real-time updates
    const needsRealtime = 
        window.location.pathname.includes('/admin/certificates') ||
        window.location.pathname.includes('/certificates') ||
        window.location.pathname.includes('/resident-portal');
    
    if (!needsRealtime) return;
    
    // Load the main script asynchronously after page is interactive
    const loadRealtime = () => {
        const script = document.createElement('script');
        script.src = '/static/js/realtime_certificates_polling.js';
        script.async = true;
        script.defer = true;
        
        script.onerror = () => {
            console.warn('Could not load real-time updates. Running in offline mode.');
        };
        
        document.body.appendChild(script);
    };
    
    // Load after DOM is interactive (before complete)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadRealtime);
    } else {
        // Page already interactive/complete
        loadRealtime();
    }
})();