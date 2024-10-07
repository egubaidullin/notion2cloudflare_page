document.addEventListener('DOMContentLoaded', function() {
    const scrollToTopButton = document.getElementById('scrollToTopButton');
    const checkbox = document.getElementById('checkbox');
    const toc = document.querySelector('.toc');
    const tocLinks = toc.getElementsByTagName('a');
    const toggleTocButton = document.querySelector('.toggle-toc');

    // Theme Switch functionality
    function setTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark-theme');
            checkbox.checked = true;
        } else {
            document.documentElement.classList.remove('dark-theme');
            checkbox.checked = false;
        }
        localStorage.setItem('theme', theme);
    }

    // Check for saved theme preference or use user's system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        setTheme('dark');
    } else {
        setTheme('light');
    }

    // Theme switch event listener
    checkbox.addEventListener('change', function() {
        setTheme(this.checked ? 'dark' : 'light');
    });

    // Scroll to Top Button functionality
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 100) {
            scrollToTopButton.classList.add('visible');
        } else {
            scrollToTopButton.classList.remove('visible');
        }
    });

    scrollToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Smooth scrolling for ToC links
    Array.from(tocLinks).forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Active ToC link highlighting
    window.addEventListener('scroll', function() {
        let fromTop = window.scrollY + 100;

        Array.from(tocLinks).forEach(link => {
            let section = document.querySelector(link.hash);

            if (
                section.offsetTop <= fromTop &&
                section.offsetTop + section.offsetHeight > fromTop
            ) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    });

    // Updated code block copy functionality
    const codeBlocks = document.querySelectorAll('pre');

    codeBlocks.forEach((block, index) => {
        // Create wrapper for code block
        const wrapper = document.createElement('div');
        wrapper.className = 'code-wrapper';
        block.parentNode.insertBefore(wrapper, block);
        wrapper.appendChild(block);

        // Create copy button with SVG icon
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.setAttribute('aria-label', 'Copy code to clipboard');
        copyButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
        `;
        wrapper.appendChild(copyButton);

        // Create feedback element
        const feedback = document.createElement('span');
        feedback.textContent = 'Copied!';
        feedback.className = 'copy-feedback';
        wrapper.appendChild(feedback);

        // Add event listener for copying
        copyButton.addEventListener('click', () => {
            const code = block.textContent || block.innerText;
            navigator.clipboard.writeText(code).then(() => {
                feedback.classList.add('show');
                setTimeout(() => {
                    feedback.classList.remove('show');
                }, 2000);
            }, (err) => {
                console.error('Failed to copy: ', err);
            });
        });
    });

    // Toggle TOC visibility
    toggleTocButton.addEventListener('click', () => {
        toc.classList.toggle('collapsed');
        if (toc.classList.contains('collapsed')) {
            toc.style.maxHeight = '0';
            toc.style.transition = 'max-height 0.3s ease-out';
        } else {
            toc.style.maxHeight = '400px'; // Set this to the desired max height
            toc.style.transition = 'max-height 0.5s ease-in';
        }
    });
});
