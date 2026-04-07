// Modal functionality for demo video

document.addEventListener('DOMContentLoaded', function() {
    const demoBtn = document.getElementById('demo-btn');
    const demoModal = document.getElementById('demo-modal');
    const modalOverlay = document.querySelector('.modal-overlay');
    const modalCloseBtn = document.getElementById('modal-close');
    const demoVideo = document.getElementById('demo-video');

    // Open modal when demo button is clicked
    if (demoBtn) {
        demoBtn.addEventListener('click', function(e) {
            e.preventDefault();
            demoModal.classList.add('active');
        });
    }

    // Close modal when close button is clicked
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', closeModal);
    }

    // Close modal when overlay is clicked
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeModal);
    }

    // Close modal and stop video
    function closeModal() {
        demoModal.classList.remove('active');
        // Stop the video by replacing the src temporarily
        const videoSrc = demoVideo.src;
        demoVideo.src = '';
        demoVideo.src = videoSrc;
    }

    // Close modal when Escape key is pressed
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && demoModal.classList.contains('active')) {
            closeModal();
        }
    });
});
