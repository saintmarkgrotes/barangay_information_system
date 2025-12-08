// Real-time certificate updates using Server-Sent Events (SSE)

class RealtimeCertificates {
    constructor() {
        this.eventSource = null;
        this.isAdmin = document.body.dataset.userRole === 'admin';
        this.isResident = document.body.dataset.userRole === 'resident';
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3 seconds
    }

    init() {
        this.connect();
        this.setupVisibilityHandler();
    }

    connect() {
        if (this.eventSource) {
            this.eventSource.close();
        }

        // Choose the appropriate stream based on user role
        const streamUrl = this.isAdmin 
            ? '/stream/certificate-updates'
            : '/stream/resident-updates';

        this.eventSource = new EventSource(streamUrl);

        this.eventSource.onopen = () => {
            console.log('Connected to real-time updates');
            this.reconnectAttempts = 0;
            this.showConnectionStatus('connected');
        };

        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleUpdate(data);
            } catch (error) {
                console.error('Error parsing SSE data:', error);
            }
        };

        this.eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
            this.eventSource.close();
            this.showConnectionStatus('disconnected');
            this.attemptReconnect();
        };
    }

    handleUpdate(data) {
        switch (data.type) {
            case 'connected':
                console.log('Connection established');
                break;

            case 'new_request':
                if (this.isAdmin) {
                    this.handleNewRequest(data);
                }
                break;

            case 'status_update':
                this.handleStatusUpdate(data);
                break;

            case 'heartbeat':
                // Keep-alive, no action needed
                break;

            case 'error':
                console.error('Server error:', data.message);
                break;

            default:
                console.log('Unknown update type:', data.type);
        }
    }

    handleNewRequest(data) {
        // Show notification
        this.showNotification('New Certificate Request', 
            `${data.requester_name} requested ${data.certificate_type}`);

        // Play sound (optional)
        this.playNotificationSound();

        // Update statistics
        this.updateStatistics('pending', 1);
        this.updateStatistics('total', 1);

        // Add new row to table if we're on the admin list page
        if (window.location.pathname.includes('/admin/certificates')) {
            this.addNewRequestToTable(data);
        }

        // Show badge notification
        this.updateBadgeCount('pending', 1);
    }

    handleStatusUpdate(data) {
        // Update the specific request in the table
        const row = document.querySelector(`tr[data-request-id="${data.id}"]`);
        if (row) {
            const statusBadge = row.querySelector('.status-badge');
            if (statusBadge) {
                // Update status badge
                statusBadge.className = 'status-badge inline-flex rounded-full px-3 py-1 text-xs font-bold uppercase';
                
                if (data.status === 'approved') {
                    statusBadge.classList.add('bg-green-100', 'text-green-800');
                    statusBadge.textContent = 'approved';
                } else if (data.status === 'rejected') {
                    statusBadge.classList.add('bg-red-100', 'text-red-800');
                    statusBadge.textContent = 'rejected';
                } else {
                    statusBadge.classList.add('bg-yellow-100', 'text-yellow-800');
                    statusBadge.textContent = data.status;
                }

                // Add certificate number if available
                if (data.certificate_number) {
                    const certNumCell = row.querySelector('.cert-number');
                    if (certNumCell) {
                        certNumCell.textContent = data.certificate_number;
                    }
                }
            }
        }

        // Show notification for residents
        if (this.isResident) {
            const statusText = data.status === 'approved' ? 'approved' : 'updated';
            this.showNotification('Certificate Request Update', 
                `Your ${data.certificate_type} request has been ${statusText}`);
            this.playNotificationSound();
        }
    }

    addNewRequestToTable(data) {
        const tbody = document.querySelector('table tbody');
        if (!tbody) return;

        // Create new row
        const row = document.createElement('tr');
        row.className = 'transition-colors hover:bg-gray-50 animate-slide-in';
        row.dataset.requestId = data.id;
        
        row.innerHTML = `
            <td class="px-6 py-4">
                <div class="text-sm font-mono font-semibold text-gray-900">
                    ${data.reference_number}
                </div>
            </td>
            <td class="px-6 py-4">
                <div class="text-sm font-semibold text-gray-900">
                    ${data.requester_name}
                </div>
                <div class="text-xs text-gray-500">
                    by ${data.requested_by}
                </div>
            </td>
            <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">
                    ${data.certificate_type}
                </div>
            </td>
            <td class="px-6 py-4">
                <div class="text-sm text-gray-900">
                    ${data.requested_at}
                </div>
            </td>
            <td class="px-6 py-4">
                <span class="status-badge inline-flex rounded-full px-3 py-1 text-xs font-bold uppercase bg-yellow-100 text-yellow-800">
                    ${data.status}
                </span>
            </td>
            <td class="px-6 py-4">
                <div class="flex gap-2">
                    <a href="/certificates/${data.id}" 
                       class="rounded-lg bg-blue-100 px-3 py-1.5 text-xs font-bold text-blue-700 transition-colors hover:bg-blue-200">
                        View
                    </a>
                    <button onclick="openApproveModal(${data.id})"
                            class="rounded-lg bg-green-100 px-3 py-1.5 text-xs font-bold text-green-700 transition-colors hover:bg-green-200">
                        Approve
                    </button>
                    <button onclick="openRejectModal(${data.id})"
                            class="rounded-lg bg-red-100 px-3 py-1.5 text-xs font-bold text-red-700 transition-colors hover:bg-red-200">
                        Reject
                    </button>
                </div>
            </td>
        `;

        // Insert at the beginning
        tbody.insertBefore(row, tbody.firstChild);

        // Highlight animation
        row.style.backgroundColor = '#fef3c7';
        setTimeout(() => {
            row.style.transition = 'background-color 1s ease';
            row.style.backgroundColor = '';
        }, 100);
    }

    updateStatistics(type, increment) {
        const statElement = document.querySelector(`[data-stat="${type}"]`);
        if (statElement) {
            const currentValue = parseInt(statElement.textContent) || 0;
            statElement.textContent = currentValue + increment;
            
            // Animate the change
            statElement.classList.add('animate-pulse');
            setTimeout(() => {
                statElement.classList.remove('animate-pulse');
            }, 1000);
        }
    }

    updateBadgeCount(type, increment) {
        const badge = document.querySelector(`[data-badge="${type}"]`);
        if (badge) {
            const currentValue = parseInt(badge.textContent) || 0;
            const newValue = currentValue + increment;
            badge.textContent = newValue;
            
            if (newValue > 0) {
                badge.style.display = 'inline-block';
            }
        }
    }

    showNotification(title, message) {
        // Check if browser supports notifications
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/logo.png',
                badge: '/static/images/logo.png'
            });
        } else {
            // Fallback to in-page notification
            this.showInPageNotification(title, message);
        }
    }

    showInPageNotification(title, message) {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 z-50 max-w-sm rounded-lg bg-white p-4 shadow-2xl animate-slide-in-right';
        notification.innerHTML = `
            <div class="flex items-start gap-3">
                <div class="flex-shrink-0">
                    <div class="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100">
                        <span class="text-xl">🔔</span>
                    </div>
                </div>
                <div class="flex-1">
                    <h4 class="text-sm font-bold text-gray-900">${title}</h4>
                    <p class="mt-1 text-sm text-gray-600">${message}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" 
                        class="flex-shrink-0 text-gray-400 hover:text-gray-600">
                    <span class="text-xl">&times;</span>
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.transition = 'opacity 0.3s ease';
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    playNotificationSound() {
        // Create and play a simple notification sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    }

    showConnectionStatus(status) {
        let indicator = document.getElementById('connection-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'connection-indicator';
            indicator.className = 'fixed bottom-4 right-4 z-50 rounded-full px-4 py-2 text-xs font-semibold shadow-lg';
            document.body.appendChild(indicator);
        }

        if (status === 'connected') {
            indicator.className = indicator.className.replace(/bg-\w+-\d+/g, '');
            indicator.className += ' bg-green-100 text-green-800';
            indicator.innerHTML = '🟢 Live updates active';
            
            // Hide after 3 seconds
            setTimeout(() => {
                indicator.style.transition = 'opacity 0.3s ease';
                indicator.style.opacity = '0';
                setTimeout(() => indicator.style.display = 'none', 300);
            }, 3000);
        } else {
            indicator.className = indicator.className.replace(/bg-\w+-\d+/g, '');
            indicator.className += ' bg-red-100 text-red-800';
            indicator.innerHTML = '🔴 Reconnecting...';
            indicator.style.opacity = '1';
            indicator.style.display = 'block';
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
            this.showInPageNotification('Connection Lost', 
                'Real-time updates are unavailable. Please refresh the page.');
        }
    }

    setupVisibilityHandler() {
        // Reconnect when page becomes visible again
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.eventSource.readyState === EventSource.CLOSED) {
                this.reconnectAttempts = 0;
                this.connect();
            }
        });
    }

    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
    }

    // Request notification permission
    static async requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }
        return Notification.permission === 'granted';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on a page that needs real-time updates
    const needsRealtime = 
        window.location.pathname.includes('/admin/certificates') ||
        window.location.pathname.includes('/certificates') ||
        window.location.pathname.includes('/resident-portal');

    if (needsRealtime) {
        const realtimeClient = new RealtimeCertificates();
        realtimeClient.init();

        // Request notification permission
        RealtimeCertificates.requestNotificationPermission();

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            realtimeClient.disconnect();
        });

        // Make it globally accessible for debugging
        window.realtimeClient = realtimeClient;
    }
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slide-in {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slide-in-right {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    .animate-slide-in {
        animation: slide-in 0.3s ease-out;
    }

    .animate-slide-in-right {
        animation: slide-in-right 0.3s ease-out;
    }
`;
document.head.appendChild(style);