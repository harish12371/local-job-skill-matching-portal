/**
 * Local Job & Skill Matching Portal - Client interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Form confirmation helpers
    const confirmActions = document.querySelectorAll('[data-confirm]');
    confirmActions.forEach(el => {
        el.addEventListener('click', (e) => {
            const message = el.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Dynamic role switch on registration page
    const roleRadioButtons = document.querySelectorAll('input[name="role_selector"]');
    if (roleRadioButtons.length > 0) {
        roleRadioButtons.forEach(radio => {
            radio.addEventListener('change', (e) => {
                const role = e.target.value;
                const workerFields = document.getElementById('worker-specific-fields');
                const employerFields = document.getElementById('employer-specific-fields');
                const roleInput = document.getElementById('form-role-input');

                if (roleInput) {
                    roleInput.value = role;
                }

                if (role === 'worker') {
                    if (workerFields) workerFields.classList.remove('d-none');
                    if (employerFields) employerFields.classList.add('d-none');
                } else {
                    if (workerFields) workerFields.classList.add('d-none');
                    if (employerFields) employerFields.classList.remove('d-none');
                }
            });
        });
    }
});
