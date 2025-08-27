document.addEventListener('DOMContentLoaded', function() {
    // Select all elements that have role="button" but are not actual buttons
    const customButtons = document.querySelectorAll('[role="button"]:not(button)');

    customButtons.forEach(button => {
        if (button.tabIndex < 0) {
            button.tabIndex = 0;
        }

        button.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                button.click();
            }
        });
    });
});