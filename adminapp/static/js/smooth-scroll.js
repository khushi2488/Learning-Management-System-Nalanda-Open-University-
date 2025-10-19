/**
 * Lenis Smooth Scrolling Implementation for Admin Portal
 * Provides smooth scrolling experience in the admin dashboard
 */

// Initialize Lenis smooth scrolling
const lenis = new Lenis({
    duration: 1.9,
    smooth: true,
    smoothTouch: false, // Disable smooth scrolling on touch devices for better performance
    touchMultiplier: 2,
});

// Animation frame for smooth scrolling
function raf(time) {
  lenis.raf(time);
  requestAnimationFrame(raf);
}

requestAnimationFrame(raf);

// Handle admin dashboard specific smooth scrolling
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

  // Smooth scroll for admin sidebar navigation
  const sidebarLinks = document.querySelectorAll('.sidebar .nav-link, .menu-item');
  
  sidebarLinks.forEach(link => {
    link.addEventListener('click', function() {
      setTimeout(() => {
        const mainContent = document.querySelector('.main-panel, .content-wrapper, .page-body-wrapper');
        if (mainContent) {
          lenis.scrollTo(0, { duration: 0.8 });
        }
      }, 100);
    });
  });

  // Smooth scroll for admin forms and tables
  const forms = document.querySelectorAll('form');
  const tables = document.querySelectorAll('table');
  
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

  // Smooth scroll for table pagination
  const paginationLinks = document.querySelectorAll('.pagination a');
  
  paginationLinks.forEach(link => {
    link.addEventListener('click', function() {
      setTimeout(() => {
        const tableContainer = document.querySelector('.table-responsive, table');
        if (tableContainer) {
          lenis.scrollTo(tableContainer, {
            offset: -100,
            duration: 1.0,
          });
        }
      }, 200);
    });
  });
});

// Expose lenis instance globally
window.lenis = lenis;

// Clean up on page unload
window.addEventListener('beforeunload', () => {
  lenis.destroy();
});