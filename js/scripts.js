// Инициализация подсветки синтаксиса
document.querySelectorAll('pre code').forEach((el) => {
  hljs.highlightElement(el);
});

// Переключение видимости TOC
const toggleTocButton = document.getElementById('toggle-toc');
const toc = document.getElementById('toc');

toggleTocButton.addEventListener('click', () => {
  toc.classList.toggle('open');
});

// Кнопка "Наверх"
const backToTopBtn = document.getElementById('back-to-top');

window.addEventListener('scroll', () => {
  if (window.scrollY > 300) {
    backToTopBtn.style.display = 'block';
  } else {
    backToTopBtn.style.display = 'none';
  }
});

backToTopBtn.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Функционал копирования кода
document.querySelectorAll('.copy-button').forEach(button => {
  button.addEventListener('click', function () {
    const codeBlock = this.previousElementSibling.querySelector('code');
    navigator.clipboard.writeText(codeBlock.textContent).then(() => {
      button.textContent = 'Скопировано!';
      setTimeout(() => { button.textContent = 'Копировать'; }, 2000);
    }).catch(err => {
      console.error('Ошибка копирования: ', err);
    });
  });
});

// Переключение тем
const themeToggleButton = document.getElementById('theme-toggle');
const sunIcon = document.getElementById('sun-icon');
const moonIcon = document.getElementById('moon-icon');

themeToggleButton.addEventListener('click', () => {
  document.body.classList.toggle('dark-theme');
  document.body.classList.toggle('light-theme');
  sunIcon.classList.toggle('hidden');
  moonIcon.classList.toggle('hidden');
  // Сохранение темы в localStorage
  if (document.body.classList.contains('dark-theme')) {
    localStorage.setItem('theme', 'dark');
  } else {
    localStorage.setItem('theme', 'light');
  }
});

// Загрузка сохранённой темы при загрузке страницы
window.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    document.body.classList.add('dark-theme');
    document.body.classList.remove('light-theme');
    sunIcon.classList.add('hidden');
    moonIcon.classList.remove('hidden');
  } else {
    document.body.classList.add('light-theme');
    document.body.classList.remove('dark-theme');
    sunIcon.classList.remove('hidden');
    moonIcon.classList.add('hidden');
  }
});
