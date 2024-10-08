// TOC Toggle
const tocToggleBtn = document.querySelector('.toggle-toc');
const sidebar = document.querySelector('.sidebar');
const overlay = document.querySelector('.overlay');

tocToggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('hidden');
    sidebar.classList.toggle('open');
});

// Overlay Click to Close Sidebar
overlay.addEventListener('click', () => {
    sidebar.classList.add('hidden');
    sidebar.classList.remove('open');
});

// Theme Toggle
const themeSwitch = document.getElementById('theme-switch');
const sunIcon = document.querySelector('.sun-icon');
const moonIcon = document.querySelector('.moon-icon');

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

// Scroll to Top Button
const scrollToTopBtn = document.getElementById('scrollToTopBtn');

window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        scrollToTopBtn.style.display = 'block';
    } else {
        scrollToTopBtn.style.display = 'none';
    }
});

scrollToTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});
