// Residents Page Logic
function openAddModal() {
    ModalManager.open('addResidentModal');
}

function closeAddModal() {
    ModalManager.close('addResidentModal');
    ModalManager.resetForm('addResidentForm');
    toggleFieldVisibility('new_household_fields', false);
}

function openEditModal(residentId) {
    const resident = residents.find(r => r.id === residentId);
    if (!resident) return;
    
    // Populate basic fields
    const fields = [
        'last_name', 'first_name', 'middle_name', 'gender', 
        'date_of_birth', 'purok', 'age', 'place_of_birth',
        'civil_status', 'citizenship', 'occupation', 
        'voter_status', 'senior_citizen'
    ];
    
    fields.forEach(field => {
        const element = document.getElementById(`edit_${field}`);
        if (element) {
            element.value = resident[field] || '';
        }
    });
    
    // Set household
    const householdSelect = document.getElementById('edit_household_select');
    if (householdSelect) {
        householdSelect.value = resident.household_id || 'none';
    }
    
    // Set form action
    document.getElementById('editResidentForm').action = `/edit_resident/${residentId}`;
    
    ModalManager.open('editResidentModal');
}

function closeEditModal() {
    ModalManager.close('editResidentModal');
    toggleFieldVisibility('edit_new_household_fields', false);
}

function toggleNewHousehold(value) {
    toggleFieldVisibility('new_household_fields', value === 'new');
}

function toggleEditNewHousehold(value) {
    toggleFieldVisibility('edit_new_household_fields', value === 'new');
}

// Initialize modal click outside and escape key handlers
document.addEventListener('DOMContentLoaded', function() {
    ModalManager.setupClickOutside('addResidentModal');
    ModalManager.setupClickOutside('editResidentModal');
    ModalManager.setupEscapeKey(['addResidentModal', 'editResidentModal']);
});