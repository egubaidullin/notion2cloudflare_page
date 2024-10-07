// Theme switcher with sun and moon icons
const sunIcon = document.getElementById('sun-icon');
const moonIcon = document.getElementById('moon-icon');
const toggleSwitch = document.querySelector('.theme-switch-wrapper');

function switchTheme() {
    if (document.body.classList.contains('dark-theme')) {
        document.body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
        moonIcon.style.display = 'block';
        sunIcon.style.display = 'none';
    } else {
        document.body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');
        moonIcon.style.display = 'none';
        sunIcon.style.display = 'block';
    }
}

toggleSwitch.addEventListener('click', switchTheme, false);

// Check for saved user preference
const currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : null;

if (currentTheme === 'dark') {
    document.body.classList.add('dark-theme');
    moonIcon.style.display = 'none';
    sunIcon.style.display = 'block';
} else {
    moonIcon.style.display = 'block';
    sunIcon.style.display = 'none';
}

// Scroll to top button functionality
const scrollToTopBtn = document.getElementById("scrollToTopBtn");

window.onscroll = function() {scrollFunction()};

function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        scrollToTopBtn.style.display = "block";
    } else {
        scrollToTopBtn.style.display = "none";
    }
}

scrollToTopBtn.addEventListener("click", function() {
    window.scrollTo({top: 0, behavior: 'smooth'});
});

// TOC toggle functionality
const toggleTocBtn = document.querySelector('.toggle-toc');
const sidebar = document.querySelector('.sidebar');

toggleTocBtn.addEventListener('click', () => {
    sidebar.classList.toggle('hidden');
    toggleTocBtn.textContent = sidebar.classList.contains('hidden') ? 'Show TOC' : 'Hide TOC';
});
