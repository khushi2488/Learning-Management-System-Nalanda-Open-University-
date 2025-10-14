// Slide navbar out on scroll down, slide in on scroll up
let lastScrollTop = 0;
const nav = document.querySelector('.sticky-navigation');
window.addEventListener('scroll', function() {
  let st = window.pageYOffset || document.documentElement.scrollTop;
  if (st > lastScrollTop) {
    // Scrolling down
    nav.style.transform = 'translateY(-100%)';
    nav.style.transition = 'transform 0.4s cubic-bezier(0.4,0,0.2,1)';
  } else {
    // Scrolling up
    nav.style.transform = 'translateY(0)';
    nav.style.transition = 'transform 0.4s cubic-bezier(0.4,0,0.2,1)';
  }
  lastScrollTop = st <= 0 ? 0 : st; // For Mobile or negative scrolling
}, false);
