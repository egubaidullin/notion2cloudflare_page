// Theme switcher
const themeSwitchBtn = document.getElementById('theme-switch');
const sunIcon = document.querySelector('.sun-icon');
const moonIcon = document.querySelector('.moon-icon');

// Функция переключения темы
function switchTheme() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    if (isDark) {
        localStorage.setItem('theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
    }
    updateThemeIcon(isDark);
}

// Обновление иконки переключателя темы
function updateThemeIcon(isDark) {
    if (isDark) {
        sunIcon.style.opacity = '0';
        moonIcon.style.opacity = '1';
    } else {
        sunIcon.style.opacity = '1';
        moonIcon.style.opacity = '0';
    }
}

// Инициализация темы при загрузке страницы
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        updateThemeIcon(true);
    } else {
        document.body.classList.remove('dark-theme');
        updateThemeIcon(false);
    }
}

// Добавление обработчика события на кнопку переключения темы
themeSwitchBtn.addEventListener('click', switchTheme);

// Инициализация при загрузке
initTheme();

// Scroll to top button
const scrollToTopBtn = document.getElementById("scrollToTopBtn");

window.addEventListener('scroll', scrollFunction);

function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        scrollToTopBtn.style.display = "block";
    } else {
        scrollToTopBtn.style.display = "none";
    }
}

scrollToTopBtn.addEventListener("click", () => {
    window.scrollTo({top: 0, behavior: 'smooth'});
});

// TOC toggle
const toggleTocBtn = document.querySelector('.toggle-toc');
const sidebar = document.querySelector('.sidebar');
const overlay = document.querySelector('.overlay');

toggleTocBtn.addEventListener('click', () => {
    const isMobile = window.innerWidth <= 768;
    if (isMobile) {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
        toggleTocBtn.innerHTML = sidebar.classList.contains('active') ? '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
    } else {
        sidebar.classList.toggle('hidden');
        toggleTocBtn.innerHTML = sidebar.classList.contains('hidden') ? '<i class="fas fa-chevron-right"></i>' : '<i class="fas fa-bars"></i>';
    }
});

// Закрытие TOC при клике на overlay
overlay.addEventListener('click', () => {
    sidebar.classList.add('hidden');
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
    toggleTocBtn.innerHTML = '<i class="fas fa-bars"></i>';
});

// Добавление кнопок копирования к блокам кода
document.querySelectorAll('pre').forEach((block) => {
    const button = document.createElement('button');
    button.className = 'copy-btn';
    button.innerHTML = '<i class="fas fa-copy"></i>';
    button.title = 'Copy code';

    button.addEventListener('click', () => {
        navigator.clipboard.writeText(block.textContent).then(() => {
            button.innerHTML = '<i class="fas fa-check"></i>';
            button.disabled = true;
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-copy"></i>';
                button.disabled = false;
            }, 2000);
        }).catch((err) => {
            console.error('Could not copy text: ', err);
        });
    });

    block.appendChild(button);
});

// Плавная прокрутка для ссылок TOC
document.querySelectorAll('.toc a').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth' });
        }

        // Закрыть TOC на мобильных устройствах после клика
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
            toggleTocBtn.innerHTML = '<i class="fas fa-bars"></i>';
        }
    });
});

// Подсветка активного пункта TOC при прокрутке
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.5
};

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        const id = entry.target.getAttribute('id');
        const tocLink = document.querySelector(`.toc a[href="#${id}"]`);
        if (entry.isIntersecting) {
            tocLink.classList.add('active');
        } else {
            tocLink.classList.remove('active');
        }
    });
}, observerOptions);

document.querySelectorAll('h2[id], h3[id], h4[id], h5[id], h6[id]').forEach((section) => {
    observer.observe(section);
});
