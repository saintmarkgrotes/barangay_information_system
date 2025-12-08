// elected_officials.js - FIXED VERSION

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
    
    // Populate form fields
    document.getElementById('edit_name').value = name || '';
    document.getElementById('edit_position').value = position || '';
    document.getElementById('edit_order').value = order || '';
    
    // Show current photo
    const photoPreview = document.getElementById('currentPhotoPreview');
    if (photoPreview) {
        if (photoFilename) {
            const staticPath = document.body.dataset.staticUrl || '/static';
            photoPreview.innerHTML = `
                <div class="mb-2 text-sm font-semibold text-gray-700">Current Photo:</div>
                <img 
                    src="${staticPath}/uploads/elected_officials/${photoFilename}" 
                    alt="Current photo" 
                    class="h-24 w-24 rounded-lg border-3 border-blue-600 object-cover"
                    onerror="this.style.display='none'">
            `;
        } else {
            photoPreview.innerHTML = '';
        }
    }
    
    // Set form action
    const form = document.getElementById('editOfficialForm');
    if (form) {
        const baseUrl = document.body.dataset.baseUrl || '';
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

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const addModal = document.getElementById('addOfficialModal');
    const editModal = document.getElementById('editOfficialModal');
    
    // Close modals when clicking outside
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