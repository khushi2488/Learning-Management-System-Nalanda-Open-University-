// Slide navbar out on scroll down, slide in on scroll up
// Enhanced to work with Lenis smooth scrolling
let lastScrollTop = 0;
const nav = document.querySelector('.sticky-navigation');

// Function to handle navbar visibility
function handleNavbar(scrollY) {
  if (scrollY > lastScrollTop && scrollY > 100) {
    // Scrolling down
    nav.style.transform = 'translateY(-100%)';
    nav.style.transition = 'transform 0.4s cubic-bezier(0.4,0,0.2,1)';
  } else {
    // Scrolling up
    nav.style.transform = 'translateY(0)';
    nav.style.transition = 'transform 0.4s cubic-bezier(0.4,0,0.2,1)';
  }
  lastScrollTop = scrollY <= 0 ? 0 : scrollY;
}

// Use Lenis scroll event if available, otherwise fallback to native scroll
if (typeof window.lenis !== 'undefined') {
  // Wait for Lenis to be initialized
  document.addEventListener('DOMContentLoaded', function() {
    if (window.lenis) {
      window.lenis.on('scroll', ({ scroll }) => {
        handleNavbar(scroll);
      });
    }
  });
} else {
  // Fallback to native scroll event
  window.addEventListener('scroll', function() {
    const st = window.pageYOffset || document.documentElement.scrollTop;
    handleNavbar(st);
  }, false);
}
