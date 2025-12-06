// static/js/officials.js - Fixed Modal Logic

function openAddModal() {
    const modal = document.getElementById('addOfficialModal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';
        
        // Reset form
        const form = document.getElementById('addOfficialForm');
        if (form) form.reset();
    }
}

function closeAddModal() {
    const modal = document.getElementById('addOfficialModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = 'auto';
    }
}

function openEditModal(id, name, position, order, photoFilename) {
    const modal = document.getElementById('editOfficialModal');
    if (!modal) return;
    
    // Set form values
    document.getElementById('edit_name').value = name || '';
    document.getElementById('edit_position').value = position || '';
    document.getElementById('edit_order').value = order || '';
    
    // Show current photo if exists
    const photoPreview = document.getElementById('currentPhotoPreview');
    if (photoPreview) {
        if (photoFilename) {
            const staticPath = document.body.dataset.staticUrl || '/static';
            photoPreview.innerHTML = `
                <div class="rounded-lg border-2 border-blue-200 bg-blue-50 p-4">
                    <p class="mb-2 text-sm font-semibold text-gray-700">Current Photo:</p>
                    <img 
                        src="${staticPath}/uploads/elected_officials/${photoFilename}" 
                        alt="Current photo" 
                        class="h-32 w-32 rounded-xl border-4 border-blue-600 object-cover shadow-md"
                        onerror="this.parentElement.style.display='none'">
                </div>
            `;
        } else {
            photoPreview.innerHTML = '';
        }
    }
    
    // Set form action
    const baseUrl = document.body.dataset.baseUrl || '';
    const form = document.getElementById('editOfficialForm');
    if (form) {
        form.action = `${baseUrl}/elected_officials/edit/${id}`;
    }
    
    // Show modal
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';
}

function closeEditModal() {
    const modal = document.getElementById('editOfficialModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = 'auto';
    }
}

// Initialize modal functionality
document.addEventListener('DOMContentLoaded', function() {
    // Close modals when clicking outside
    const addModal = document.getElementById('addOfficialModal');
    const editModal = document.getElementById('editOfficialModal');
    
    if (addModal) {
        addModal.addEventListener('click', function(e) {
            if (e.target === this) closeAddModal();
        });
    }
    
    if (editModal) {
        editModal.addEventListener('click', function(e) {
            if (e.target === this) closeEditModal();
        });
    }
    
    // Close modals with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAddModal();
            closeEditModal();
        }
    });
});