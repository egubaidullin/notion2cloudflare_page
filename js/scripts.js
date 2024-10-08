// Syntax highlighting for code blocks
document.querySelectorAll('pre code').forEach((el) => {
  hljs.highlightElement(el);
});

// Toggle TOC visibility on mobile
document.getElementById('toggle-toc').addEventListener('click', () => {
  const toc = document.getElementById('toc');
  toc.style.display = toc.style.display === 'none' ? 'block' : 'none';
});

// Back to top button functionality
const backToTopBtn = document.getElementById('back-to-top');
window.addEventListener('scroll', () => {
  if (window.scrollY > 200) {
    backToTopBtn.style.display = 'block';
  } else {
    backToTopBtn.style.display = 'none';
  }
});

backToTopBtn.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Copy code functionality
document.querySelectorAll('.copy-button').forEach(button => {
  button.addEventListener('click', function () {
    const codeBlock = this.previousElementSibling.querySelector('code');
    navigator.clipboard.writeText(codeBlock.textContent).then(() => {
      const tooltip = this.querySelector('.copied-tooltip');
      tooltip.style.display = 'inline';
      setTimeout(() => { tooltip.style.display = 'none'; }, 1000);
    });
  });
});
