document.addEventListener('DOMContentLoaded', function () {
    // Modal elements
    const filterModal = document.getElementById('filter-modal');
    const openFilterModalBtn = document.getElementById('open-filter-modal');
    const mobileOpenFilterModalBtn = document.getElementById('mobile-open-filter-modal');
    const closeFilterModalBtn = document.getElementById('close-filter-modal');
    const salarySlider = document.getElementById('salary-slider-modal');
    const salaryValue = document.getElementById('salary-value-modal');

    // Open modal handler for desktop
    if (openFilterModalBtn) {
        openFilterModalBtn.addEventListener('click', function () {
            if (filterModal) {
                filterModal.classList.remove('hidden');
                document.body.style.overflow = 'hidden'; // Prevent scrolling
            }
        });
    }

    // Open modal handler for mobile
    if (mobileOpenFilterModalBtn) {
        mobileOpenFilterModalBtn.addEventListener('click', function () {
            if (filterModal) {
                filterModal.classList.remove('hidden');
                document.body.style.overflow = 'hidden'; // Prevent scrolling
            }
        });
    }

    // Close modal handler
    if (closeFilterModalBtn) {
        closeFilterModalBtn.addEventListener('click', function () {
            if (filterModal) {
                filterModal.classList.add('hidden');
                document.body.style.overflow = ''; // Restore scrolling
            }
        });
    }

    // Close modal when clicking outside
    if (filterModal) {
        filterModal.addEventListener('click', function (e) {
            if (e.target === filterModal) {
                filterModal.classList.add('hidden');
                document.body.style.overflow = ''; // Restore scrolling
            }
        });
    }

    // Escape key to close modal
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && filterModal && !filterModal.classList.contains('hidden')) {
            filterModal.classList.add('hidden');
            document.body.style.overflow = ''; // Restore scrolling
        }
    });

    // Salary slider value display
    if (salarySlider && salaryValue) {
        salarySlider.addEventListener('input', function () {
            salaryValue.textContent = '₾ ' + this.value;
        });
    }
});