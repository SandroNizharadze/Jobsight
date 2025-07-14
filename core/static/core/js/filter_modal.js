document.addEventListener('DOMContentLoaded', function () {
    // Modal elements
    const filterModal = document.getElementById('filter-modal');
    const openFilterModalBtn = document.getElementById('open-filter-modal');
    const mobileOpenFilterModalBtn = document.getElementById('mobile-open-filter-modal');
    const closeFilterModalBtn = document.getElementById('close-filter-modal');
    const salarySlider = document.getElementById('salary-slider-modal');
    const salaryValue = document.getElementById('salary-value-modal');
    const modalBody = filterModal ? filterModal.querySelector('.modal-body') : null;
    const isMobile = window.innerWidth < 768;
    const filterFormModal = document.getElementById('filter-form-modal');

    // Function to open modal with animation
    function openModal() {
        if (filterModal) {
            filterModal.classList.remove('hidden');
            document.documentElement.classList.add('modal-open');

            // Trigger animations after a small delay to ensure the display change has taken effect
            setTimeout(() => {
                filterModal.classList.add('show');
                filterModal.classList.add('modal-show');

                // Reset scroll position
                if (modalBody) {
                    modalBody.scrollTop = 0;
                }
            }, 10);
        }
    }

    // Function to close modal with animation
    function closeModal() {
        if (filterModal) {
            filterModal.classList.remove('show');
            filterModal.classList.remove('modal-show');

            // Wait for animation to complete before hiding
            setTimeout(() => {
                filterModal.classList.add('hidden');
                document.documentElement.classList.remove('modal-open');
            }, 300);
        }
    }

    // Open modal handler for desktop
    if (openFilterModalBtn) {
        openFilterModalBtn.addEventListener('click', openModal);
    }

    // Open modal handler for mobile
    if (mobileOpenFilterModalBtn) {
        mobileOpenFilterModalBtn.addEventListener('click', openModal);
    }

    // Close modal handler
    if (closeFilterModalBtn) {
        closeFilterModalBtn.addEventListener('click', closeModal);
    }

    // Close modal when clicking outside
    if (filterModal) {
        filterModal.addEventListener('click', function (e) {
            // Only close if clicking the backdrop, not the modal content
            if (e.target === filterModal || e.target.classList.contains('modal-container')) {
                closeModal();
            }
        });
    }

    // Escape key to close modal
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && filterModal && !filterModal.classList.contains('hidden')) {
            closeModal();
        }
    });

    // Salary slider value display
    if (salarySlider && salaryValue) {
        salarySlider.addEventListener('input', function () {
            salaryValue.textContent = '₾ ' + this.value;
        });
    }

    // Close modal after form submission
    if (filterFormModal) {
        filterFormModal.addEventListener('submit', function (e) {
            closeModal();
            // Allow form to submit naturally
        });
    }

    // Handle touch events for mobile modal
    if (isMobile && modalBody) {
        let startY;

        // Prevent default on touchmove to avoid body scrolling on iOS
        modalBody.addEventListener('touchstart', function (e) {
            startY = e.touches[0].clientY;
        }, { passive: false });

        modalBody.addEventListener('touchmove', function (e) {
            const currentY = e.touches[0].clientY;
            const scrollTop = modalBody.scrollTop;
            const scrollHeight = modalBody.scrollHeight;
            const clientHeight = modalBody.clientHeight;

            // Prevent overscroll at the top
            if (scrollTop === 0 && currentY > startY) {
                e.preventDefault();
            }

            // Prevent overscroll at the bottom
            if (scrollHeight - scrollTop === clientHeight && currentY < startY) {
                e.preventDefault();
            }

            startY = currentY;
        }, { passive: false });
    }
});