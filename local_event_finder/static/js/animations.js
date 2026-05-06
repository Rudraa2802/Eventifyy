const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);
document.querySelectorAll('.scroll-fade').forEach(el => {
  observer.observe(el);
});
window.addEventListener('load', () => {
  document.querySelectorAll('.page-transition').forEach(el => {
    el.style.display = 'block';
  });
});
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});
function updateProgressBar(selector, percentage) {
  const bar = document.querySelector(selector);
  if (bar) {
    bar.style.width = percentage + '%';
  }
}
document.addEventListener('DOMContentLoaded', () => {
  const tooltips = document.querySelectorAll('.tooltip');
  tooltips.forEach(tooltip => {
    tooltip.style.cursor = 'help';
  });
});
function setActiveLink() {
  const links = document.querySelectorAll('.nav-links a');
  const currentLocation = location.pathname;
  
  links.forEach(link => {
    if (link.getAttribute('href') === currentLocation) {
      link.style.color = 'var(--primary)';
    }
  });
}
setActiveLink();
const fab = document.querySelector('.fab');
if (fab) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      fab.style.opacity = '1';
      fab.style.pointerEvents = 'auto';
    } else {
      fab.style.opacity = '0.5';
      fab.style.pointerEvents = 'none';
    }
  });
}
window.addEventListener('scroll', () => {
  const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
  document.documentElement.style.setProperty('--scroll-percent', scrollPercent);
});