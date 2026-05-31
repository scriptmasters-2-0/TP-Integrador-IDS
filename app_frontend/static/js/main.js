document.addEventListener('DOMContentLoaded', () => {
    const faqItems = document.querySelectorAll('.faq-item');

    // Default to open for the demo as shown in screenshots
    faqItems.forEach(item => {
        item.classList.add('active'); // Since screenshots show them open
        
        const questionBtn = item.querySelector('.faq-question');
        questionBtn.addEventListener('click', () => {
            item.classList.toggle('active');
        });
    });

    // Dynamic Greeting Logic for Dashboard
    const greetingElement = document.getElementById('greeting');
    const dateElement = document.getElementById('current-date');
    
    if (greetingElement && dateElement) {
        const now = new Date();
        const hour = now.getHours();
        let greeting = 'Buenas noches';
        
        if (hour >= 5 && hour < 12) {
            greeting = 'Buenos días';
        } else if (hour >= 12 && hour < 19) {
            greeting = 'Buenas tardes';
        }
        
        const userNameElement = document.getElementById('dashboard-user-name');
        const userName = userNameElement ? userNameElement.textContent.trim() : 'Usuario';
        
        greetingElement.textContent = `${greeting}, ${userName}`;
        
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        // Primera letra mayúscula para el día
        let dateString = now.toLocaleDateString('es-ES', options);
        dateString = dateString.charAt(0).toUpperCase() + dateString.slice(1);
        dateElement.textContent = dateString;
    }

    // Auto-add reveal class and staggered delays to elements
    const elementsToReveal = document.querySelectorAll('.step-card, .benefit-card, .rule-item, .faq-item, section h2, .subtitle');
    elementsToReveal.forEach(el => {
        el.classList.add('reveal');
        let delayIndex = Array.from(el.parentNode.children).indexOf(el);
        // Limit delay to prevent excessive waits
        if (delayIndex > 5) delayIndex = 5;
        el.style.transitionDelay = (delayIndex * 0.15) + 's';
    });

    // Scroll Reveal Animation Logic
    const reveals = document.querySelectorAll('.reveal');
    const revealOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const revealOnScroll = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, revealOptions);

    reveals.forEach(reveal => {
        revealOnScroll.observe(reveal);
    });
});
