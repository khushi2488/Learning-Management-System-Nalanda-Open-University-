/**
 * Lenis Smooth Scrolling Implementation for Student Portal
 * Provides smooth scrolling experience in the student dashboard
 */

// Initialize Lenis smooth scrolling
const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  direction: 'vertical',
  gestureDirection: 'vertical',
  smooth: true,
  mouseMultiplier: 1,
  smoothTouch: false,
  touchMultiplier: 2,
  infinite: false,
});

// Animation frame for smooth scrolling
function raf(time) {
  lenis.raf(time);
  requestAnimationFrame(raf);
}

requestAnimationFrame(raf);

// Handle anchor links and dashboard navigation
document.addEventListener('DOMContentLoaded', function() {
  // Smooth scroll for anchor links
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  
  anchorLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      
      if (href === '#' || href === '') return;
      
      const target = document.querySelector(href);
      
      if (target) {
        e.preventDefault();
        lenis.scrollTo(target, {
          offset: -100,
          duration: 1.5,
        });
      }
    });
  });

  // Smooth scroll for sidebar navigation
  const sidebarLinks = document.querySelectorAll('.sidebar .nav-link');
  
  sidebarLinks.forEach(link => {
    link.addEventListener('click', function() {
      // Add small delay for page transitions in SPA-like behavior
      setTimeout(() => {
        const mainContent = document.querySelector('.main-panel, .content-wrapper');
        if (mainContent) {
          lenis.scrollTo(0, { duration: 0.8 });
        }
      }, 100);
    });
  });

  // Smooth scroll for form submissions
  const forms = document.querySelectorAll('form');
  
  forms.forEach(form => {
    form.addEventListener('submit', function() {
      setTimeout(() => {
        const errorElement = document.querySelector('.alert-danger, .error-message, .invalid-feedback');
        if (errorElement) {
          lenis.scrollTo(errorElement, {
            offset: -80,
            duration: 1.2,
          });
        }
      }, 100);
    });
  });
});

// Expose lenis instance globally
window.lenis = lenis;

// Clean up on page unload
window.addEventListener('beforeunload', () => {
  lenis.destroy();
});