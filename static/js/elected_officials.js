// elected_officials.js

function openAddModal() {
    document.getElementById('addOfficialModal').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeAddModal() {
    document.getElementById('addOfficialModal').classList.remove('active');
    document.body.style.overflow = 'auto';
}

function openEditModal(id, name, position, order, photoFilename) {
    document.getElementById('edit_name').value = name;
    document.getElementById('edit_position').value = position;
    document.getElementById('edit_order').value = order || '';
    
    // Show current photo
    const photoPreview = document.getElementById('currentPhotoPreview');
    if (photoFilename) {
        const staticPath = document.body.dataset.staticUrl || '/static';
        photoPreview.innerHTML = '<img src="' + staticPath + '/uploads/elected_officials/' + photoFilename + '" alt="Current photo" onerror="this.style.display=\'none\'">';
    } else {
        photoPreview.innerHTML = '';
    }
    
    const baseUrl = document.body.dataset.baseUrl || '';
    document.getElementById('editOfficialForm').action = baseUrl + '/elected_officials/edit/' + id;
    document.getElementById('editOfficialModal').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeEditModal() {
    document.getElementById('editOfficialModal').classList.remove('active');
    document.body.style.overflow = 'auto';
}

// Close modals when clicking outside
document.addEventListener('DOMContentLoaded', function() {
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