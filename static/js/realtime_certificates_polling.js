// static/js/realtime_certificates_polling.js
// Lightweight polling-based real-time updates (no SSE blocking)

class RealtimeCertificatesPolling {
    constructor() {
        this.isAdmin = document.body.dataset.userRole === 'admin';
        this.isResident = document.body.dataset.userRole === 'resident';
        this.pollingInterval = null;
        this.lastCheckTime = new Date().toISOString();
        this.pollingFrequency = 10000; // 10 seconds (adjustable)
        this.isPolling = false;
    }

    init() {
        // Start polling after page fully loads
        if (document.readyState === 'complete') {
            this.startPolling();
        } else {
            window.addEventListener('load', () => {
                this.startPolling();
            });
        }
        
        this.setupVisibilityHandler();
    }

    startPolling() {
        // Initial check after 2 seconds
        setTimeout(() => {
            this.checkForUpdates();
        }, 2000);

        // Set up regular polling
        this.pollingInterval = setInterval(() => {
            this.checkForUpdates();
        }, this.pollingFrequency);

        console.log('✅ Real-time polling started');
    }

    async checkForUpdates() {
        if (this.isPolling) return; // Prevent concurrent requests
        
        this.isPolling = true;

        try {
            const endpoint = this.isAdmin 
                ? '/api/certificate-updates'
                : '/api/resident-updates';

            const response = await fetch(endpoint + '?since=' + encodeURIComponent(this.lastCheckTime), {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                
                if (data.updates && data.updates.length > 0) {
                    this.handleUpdates(data.updates);
                }
                
                // Update last check time
                this.lastCheckTime = data.current_time || new Date().toISOString();
            }
        } catch (error) {
            console.error('Polling error:', error);
            // Continue polling even on error
        } finally {
            this.isPolling = false;
        }
    }

    handleUpdates(updates) {
        updates.forEach(update => {
            if (update.type === 'new_request' && this.isAdmin) {
                this.handleNewRequest(update);
            } else if (update.type === 'status_update') {
                this.handleStatusUpdate(update);
            }
        });
    }

    handleNewRequest(data) {
        // Show notification
        this.showNotification('New Certificate Request', 
            `${data.requester_name} requested ${data.certificate_type}`);

        // Play sound
        this.playNotificationSound();

        // Update statistics
        this.updateStatistics('pending', 1);
        this.updateStatistics('total', 1);

        // Add to table if on admin page
        if (window.location.pathname.includes('/admin/certificates')) {
            this.addNewRequestToTable(data);
        }

        // Update badge
        this.updateBadgeCount('pending', 1);
    }

    handleStatusUpdate(data) {
        // Update table row
        const row = document.querySelector(`tr[data-request-id="${data.id}"]`);
        if (row) {
            const statusBadge = row.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = 'status-badge inline-flex rounded-full px-3 py-1 text-xs font-bold uppercase';
                
                if (data.status === 'approved') {
                    statusBadge.classList.add('bg-green-100', 'text-green-800');
                    statusBadge.textContent = 'approved';
                } else if (data.status === 'rejected') {
                    statusBadge.classList.add('bg-red-100', 'text-red-800');
                    statusBadge.textContent = 'rejected';
                }

                if (data.certificate_number) {
                    const certNumCell = row.querySelector('.cert-number');
                    if (certNumCell) {
                        certNumCell.textContent = data.certificate_number;
                    } else {
                        const refCell = row.querySelector('td:first-child div:first-child');
                        if (refCell) {
                            const certDiv = document.createElement('div');
                            certDiv.className = 'cert-number text-xs font-mono text-gray-500';
                            certDiv.textContent = data.certificate_number;
                            refCell.parentElement.appendChild(certDiv);
                        }
                    }
                }
            }
        }

        // Resident notification
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
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/logo.png',
                badge: '/static/images/logo.png'
            });
        } else {
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

        setTimeout(() => {
            notification.style.transition = 'opacity 0.3s ease';
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    playNotificationSound() {
        try {
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
        } catch (e) {
            // Silent fail
        }
    }

    setupVisibilityHandler() {
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && !this.pollingInterval) {
                this.startPolling();
            } else if (document.hidden && this.pollingInterval) {
                // Optional: pause polling when tab is hidden to save resources
                // Uncomment below to enable
                // this.stopPolling();
            }
        });
    }

    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
            console.log('⏸️ Polling paused');
        }
    }

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
    const needsRealtime = 
        window.location.pathname.includes('/admin/certificates') ||
        window.location.pathname.includes('/certificates') ||
        window.location.pathname.includes('/resident-portal');

    if (needsRealtime) {
        const realtimeClient = new RealtimeCertificatesPolling();
        realtimeClient.init();

        RealtimeCertificatesPolling.requestNotificationPermission();

        window.addEventListener('beforeunload', () => {
            realtimeClient.stopPolling();
        });

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