/**
 * NagarMitra — Main JavaScript
 * Handles responsive navigation toggle and minor UI enhancements.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('active');
        });

        // Close menu when clicking a link (mobile)
        navLinks.querySelectorAll('.nav-link').forEach(function (link) {
            link.addEventListener('click', function () {
                navLinks.classList.remove('active');
            });
        });
    }

    // Auto-dismiss flash messages after 5 seconds
    document.querySelectorAll('.flash-message').forEach(function (msg) {
        setTimeout(function () {
            msg.style.transition = 'opacity 0.3s';
            msg.style.opacity = '0';
            setTimeout(function () { msg.remove(); }, 300);
        }, 5000);
    });
});
