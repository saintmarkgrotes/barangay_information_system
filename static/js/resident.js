// static/js/resident.js - Fixed Modal Logic

function openAddModal() {
    const modal = document.getElementById('addResidentModal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';
        
        // Reset form
        const form = document.getElementById('addResidentForm');
        if (form) form.reset();
        
        // Hide household fields
        const householdFields = document.getElementById('new_household_fields');
        if (householdFields) {
            householdFields.classList.add('hidden');
        }
    }
}

function closeAddModal() {
    const modal = document.getElementById('addResidentModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = 'auto';
    }
}

function openEditModal(residentId) {
    const resident = residents.find(r => r.id === residentId);
    if (!resident) return;
    
    const modal = document.getElementById('editResidentModal');
    if (!modal) return;
    
    // Populate form fields
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
    const form = document.getElementById('editResidentForm');
    if (form) {
        form.action = `/edit_resident/${residentId}`;
    }
    
    // Show modal
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';
}

function closeEditModal() {
    const modal = document.getElementById('editResidentModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = 'auto';
        
        // Hide household fields
        const householdFields = document.getElementById('edit_new_household_fields');
        if (householdFields) {
            householdFields.classList.add('hidden');
        }
    }
}

function toggleNewHousehold(value) {
    const fields = document.getElementById('new_household_fields');
    if (fields) {
        if (value === 'new') {
            fields.classList.remove('hidden');
        } else {
            fields.classList.add('hidden');
        }
    }
}

function toggleEditNewHousehold(value) {
    const fields = document.getElementById('edit_new_household_fields');
    if (fields) {
        if (value === 'new') {
            fields.classList.remove('hidden');
        } else {
            fields.classList.add('hidden');
        }
    }
}

// Initialize modal functionality
document.addEventListener('DOMContentLoaded', function() {
    // Close modals when clicking outside
    const addModal = document.getElementById('addResidentModal');
    const editModal = document.getElementById('editResidentModal');
    
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
    
    // Auto-calculate age from date of birth
    const dobInput = document.getElementById('date_of_birth');
    const ageInput = document.getElementById('age');
    
    if (dobInput && ageInput) {
        dobInput.addEventListener('change', function() {
            const dob = new Date(this.value);
            const today = new Date();
            let age = today.getFullYear() - dob.getFullYear();
            const monthDiff = today.getMonth() - dob.getMonth();
            
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
                age--;
            }
            
            if (age >= 0 && age <= 150) {
                ageInput.value = age;
            } else if (age < 0) {
                alert('Date of birth cannot be in the future');
                dobInput.value = '';
                ageInput.value = '';
            }
        });
    }
    
    // Same for edit modal
    const editDobInput = document.getElementById('edit_date_of_birth');
    const editAgeInput = document.getElementById('edit_age');
    
    if (editDobInput && editAgeInput) {
        editDobInput.addEventListener('change', function() {
            const dob = new Date(this.value);
            const today = new Date();
            let age = today.getFullYear() - dob.getFullYear();
            const monthDiff = today.getMonth() - dob.getMonth();
            
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
                age--;
            }
            
            if (age >= 0 && age <= 150) {
                editAgeInput.value = age;
            } else if (age < 0) {
                alert('Date of birth cannot be in the future');
                editDobInput.value = '';
                editAgeInput.value = '';
            }
        });
    }
});