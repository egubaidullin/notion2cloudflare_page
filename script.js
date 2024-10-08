// TOC Toggle
const tocToggleBtn = document.getElementById('toc-toggle');
const tocPanel = document.getElementById('toc-panel');

tocToggleBtn.addEventListener('click', () => {
    tocPanel.classList.toggle('open');
});

// Mobile Menu Toggle
const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
const mobileMenu = document.getElementById('mobile-menu');

mobileMenuToggle.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
    tocPanel.classList.remove('open');
});

// Theme Toggle
const themeSwitch = document.getElementById('theme-switch');

themeSwitch.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    document.body.classList.toggle('light');
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
            console.error('Failed to copy text: ', err);
        });
    });
});

// Hide/Show Navbar on Scroll
let hideNavTimeout;
const navBar = document.querySelector('nav');

window.addEventListener('scroll', () => {
    navBar.classList.remove('hidden');
    clearTimeout(hideNavTimeout);
    hideNavTimeout = setTimeout(() => {
        navBar.classList.add('hidden');
    }, 3000);
});

// Scroll to Top Button
const scrollToTopBtn = document.getElementById('scrollToTopBtn');

window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        scrollToTopBtn.classList.add('show');
        scrollToTopBtn.classList.remove('hidden');
    } else {
        scrollToTopBtn.classList.add('hidden');
        scrollToTopBtn.classList.remove('show');
    }
});

scrollToTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// TOC Scroll Functionality
tocPanel.addEventListener('wheel', (e) => {
    e.preventDefault();
    tocPanel.scrollBy({ top: e.deltaY, left: 0, behavior: 'smooth' });
});
