// Officials Page Logic
function openAddModal() {
    ModalManager.open('addOfficialModal');
}

function closeAddModal() {
    ModalManager.close('addOfficialModal');
}

function openEditModal(id, name, position, order, photoFilename) {
    document.getElementById('edit_name').value = name;
    document.getElementById('edit_position').value = position;
    document.getElementById('edit_order').value = order || '';
    
    // Show current photo
    const photoPreview = document.getElementById('currentPhotoPreview');
    if (photoFilename) {
        photoPreview.innerHTML = `<img src="/static/uploads/elected_officials/${photoFilename}" alt="Current photo" onerror="this.style.display='none'">`;
    } else {
        photoPreview.innerHTML = '';
    }
    
    document.getElementById('editOfficialForm').action = `/elected_officials/edit/${id}`;
    ModalManager.open('editOfficialModal');
}

function closeEditModal() {
    ModalManager.close('editOfficialModal');
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    ModalManager.setupClickOutside('addOfficialModal');
    ModalManager.setupClickOutside('editOfficialModal');
    ModalManager.setupEscapeKey(['addOfficialModal', 'editOfficialModal']);
});