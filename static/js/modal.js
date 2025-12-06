// Reusable Modal Functions
const ModalManager = {
    open: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    },

    close: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    },

    setupClickOutside: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    ModalManager.close(modalId);
                }
            });
        }
    },

    setupEscapeKey: function(modalIds) {
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                modalIds.forEach(id => ModalManager.close(id));
            }
        });
    },

    resetForm: function(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
        }
    }
};

// Form Field Toggle Utility
function toggleFieldVisibility(fieldId, show) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.style.display = show ? 'block' : 'none';
    }
}

// Populate form fields from data object
function populateForm(formPrefix, data) {
    Object.keys(data).forEach(key => {
        const element = document.getElementById(`${formPrefix}_${key}`);
        if (element) {
            element.value = data[key] || '';
        }
    });
}