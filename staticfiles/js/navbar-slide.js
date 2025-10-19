let lastScrollTop = 0;
const nav = document.querySelector('.sticky-navigation');
const scrollThreshold = 10; // minimum scroll before hide/show

window.addEventListener('scroll', function() {
  // Skip hiding on mobile
  if (window.innerWidth < 992) return; // Bootstrap lg breakpoint

  let st = window.pageYOffset || document.documentElement.scrollTop;

  if (Math.abs(st - lastScrollTop) <= scrollThreshold) {
    return; // ignore tiny scrolls
  }

  if (st > lastScrollTop) {
    // Scrolling down
    nav.style.transform = 'translateY(-100%)';
  } else {
    // Scrolling up
    nav.style.transform = 'translateY(0)';
  }

  lastScrollTop = st <= 0 ? 0 : st; // Reset for mobile
}, false);