// Theme switcher
const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
const sunIcon = document.querySelector('.sun-icon');
const moonIcon = document.querySelector('.moon-icon');

function switchTheme(e) {
    if (e.target.checked) {
        document.body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');
    } else {
        document.body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
    }    
}

toggleSwitch.addEventListener('change', switchTheme, false);

// Check for saved user preference, if any, on load of the website
const currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : null;

if (currentTheme) {
    if (currentTheme === 'dark') {
        toggleSwitch.checked = true;
        document.body.classList.add('dark-theme');
    }
}

// Scroll to top button
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

// TOC toggle
const toggleTocBtn = document.querySelector('.toggle-toc');
const sidebar = document.querySelector('.sidebar');
const overlay = document.createElement('div');
overlay.classList.add('overlay');
document.body.appendChild(overlay);

toggleTocBtn.addEventListener('click', () => {
    sidebar.classList.toggle('hidden');
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');

    if (window.innerWidth <= 768) {
        toggleTocBtn.innerHTML = sidebar.classList.contains('active') 
            ? '<i class="fas fa-times"></i>' 
            : '<i class="fas fa-bars"></i>';
    }
});

// Close TOC when clicking on overlay
overlay.addEventListener('click', () => {
    sidebar.classList.add('hidden');
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
    toggleTocBtn.innerHTML = '<i class="fas fa-bars"></i>';
});

// Add copy buttons to code blocks
document.querySelectorAll('pre').forEach((block) => {
    const button = document.createElement('button');
    button.className = 'copy-btn';
    button.innerHTML = '<i class="fas fa-copy"></i>';
    button.title = 'Copy code';
    
    button.addEventListener('click', () => {
        navigator.clipboard.writeText(block.textContent).then(() => {
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i>';
            button.disabled = true;
            setTimeout(() => {
                button.innerHTML = originalHTML;
                button.disabled = false;
            }, 2000);
        }, (err) => {
            console.error('Could not copy text: ', err);
        });
    });
    
    block.appendChild(button);
});

// Smooth scrolling for TOC links
document.querySelectorAll('.toc a').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        // Close TOC on mobile after clicking
        if (window.innerWidth <= 768) {
            sidebar.classList.add('hidden');
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
            toggleTocBtn.innerHTML = '<i class="fas fa-bars"></i>';
        }

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Highlight active TOC item
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.5
};

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        const id = entry.target.getAttribute('id');
        if (entry.isIntersecting) {
            document.querySelector(`.toc a[href="#${id}"]`).classList.add('active');
        } else {
            document.querySelector(`.toc a[href="#${id}"]`).classList.remove('active');
        }
    });
}, observerOptions);

document.querySelectorAll('h2[id], h3[id], h4[id], h5[id], h6[id]').forEach((section) => {
    observer.observe(section);
});
