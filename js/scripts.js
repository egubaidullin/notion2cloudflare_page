// TOC Toggle
const tocToggleBtn = document.getElementById('toc-toggle');
const tocPanel = document.getElementById('toc-panel');
const contentWrapper = document.getElementById('content-wrapper');

// Mobile Menu Toggle
const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
const mobileMenu = document.getElementById('mobile-menu');

// Theme Toggle
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');
const moonIcon = document.getElementById('moon-icon');

// Back to Top Button
const backToTopButton = document.getElementById('back-to-top');

// TOC Toggle Event
tocToggleBtn.addEventListener('click', () => {
  const isOpen = tocPanel.classList.toggle('open');
  
  if (isOpen) {
    tocToggleBtn.innerHTML = '&lt;'; // Изменяем иконку при открытии
    contentWrapper.classList.add('shifted');
  } else {
    tocToggleBtn.innerHTML = '&gt;'; // Изменяем иконку при закрытии
    contentWrapper.classList.remove('shifted');
  }
});

// Mobile Menu Toggle Event
mobileMenuToggle.addEventListener('click', () => {
  mobileMenu.classList.toggle('hidden');
  tocPanel.classList.remove('open');
  tocToggleBtn.innerHTML = '&gt;';
  contentWrapper.classList.remove('shifted');
});

// Theme Toggle Event
themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  document.body.classList.toggle('light');

  if (document.body.classList.contains('dark')) {
    moonIcon.setAttribute('d', 'M12 3v1m0 16v1m8.66-8.66h-1M4.34 12h-1m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707');
  } else {
    moonIcon.setAttribute('d', 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z');
  }
});

// Copy to Clipboard
const copyButtons = document.querySelectorAll('.copy-button');

copyButtons.forEach(button => {
  button.addEventListener('click', () => {
    const codeBlock = button.parentElement.querySelector('pre code');
    const codeText = codeBlock.innerText;
    navigator.clipboard.writeText(codeText).then(() => {
      button.classList.add('copied');
      setTimeout(() => {
        button.classList.remove('copied');
      }, 2000);
    }).catch(err => {
      console.error('Не удалось скопировать текст: ', err);
    });
  });
});

// Hide/Show Navbar on Scroll
let lastScrollY = window.scrollY;
const navBar = document.querySelector('nav');
let hideNavTimeout;

window.addEventListener('scroll', () => {
  if (window.scrollY > lastScrollY && window.scrollY > 100) {
    // Пользователь скроллит вниз и прошёл определённое расстояние
    navBar.classList.add('hidden');
  } else {
    // Пользователь скроллит вверх
    navBar.classList.remove('hidden');
  }
  
  lastScrollY = window.scrollY;
  
  clearTimeout(hideNavTimeout);
  hideNavTimeout = setTimeout(() => {
    if (window.scrollY > 100) { // Скрываем только если прокрутили больше 100px
      navBar.classList.add('hidden');
    }
  }, 3000);
});

// Back to Top Button Visibility
window.addEventListener('scroll', () => {
  if (window.scrollY > 300) {
    backToTopButton.classList.add('show');
    backToTopButton.classList.remove('hidden');
  } else {
    backToTopButton.classList.add('hidden');
    backToTopButton.classList.remove('show');
  }
});

// Back to Top Button Click Event
backToTopButton.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// TOC Scroll Functionality
const toc = document.getElementById('toc-panel');

toc.addEventListener('wheel', (e) => {
  e.preventDefault();
  toc.scrollBy({ top: e.deltaY, left: 0, behavior: 'smooth' });
});
